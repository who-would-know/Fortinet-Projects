#!/usr/bin/python
'''Project: FortiManager Policy Import
   Date: 12-15-2020
   Python Version: 3.7.4
   FortiManager Version: v6.2.3 on Azure, compatible and tested with v6.0.9 GA
   Purpose: Program to Import in a Fortigate/VDOM Device Policy into a FortiManager ADOM

   Instructions for Creating API User Account: 
        - Add an API user in your FortiManager
            -Log into FortiManager with admin account, Go To:
                -System Settings => Admin => Administrators
                -Click "+ Create New"
                -Create a User Name
                -Set a Password
                -Admin Profile Super_User (or whatever Access you would like to grant to this API User Account)
                -JSON API Access set to Read-Write (or whatever Access via the API you would like to grant to this API User Account)
                -*Optional: Trusted Hosts, enabled and set IP address that your Python Script will be executed from to restrict access remotely to the API User.
                -Click OK, API User account is created
'''

## Define Modules
#For system calls like exit system, etc.
import sys
#For sleep command between tasks
import time
#To use getpass to hide passwd when user is inputting it
import getpass
#For making HTTPS Connections to the FortiManager API Server
import requests
import urllib3
#To ignore the FortiManager Self Signed Certificate warnings.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#To receive and format JSON requests as FortiManager uses JSON formatting in their API
import json


## Functions
def fmg_login(hostAPIUSER, hostPASSWD, hostIP):
    '''FortiManager Login & Create Session
    Arguments:
    hostAPIUSER - API User Account Name
    hostPASSWD - API User Passwd
    hostIP - IP addres of FortiManager. Note, if not on default HTTPS(443) port can input: 1.1.1.1:8080
    '''
    #Global Save Session ID
    global session
    #Create HTTPS URL
    global url
    url = 'https://' + hostIP + '/jsonrpc'
    #JSON Body to sent to API request
    body = {
    "id": 1,
            "method": "exec",
            "params": [{
                    "url": "sys/login/user",
                    "data": [{
                            "user": hostAPIUSER,
                            "passwd": hostPASSWD
                    }]
            }],
            "session": 1
    }
    #Test HTTPS connection to host then Capture and output any errors
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
        #Exit Program, Connection was not Successful
        sys.exit(1)
    #Save JSON response from FortiManager
    json_resp = json.loads(r.text)
    #Check if User & Passwd was valid, no code -11 means invalid
    if json_resp['result'][0]['status']['code'] != -11:
        session = json_resp['session']
        print ('--> Logging into FortiManager: %s' % hostIP)
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
    else:
        print ('<--Username or password is not valid, please try again, exiting...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        #Exit Program, Username or Password is not valided or internal FortiManager error review Hcode & Jmesg
        sys.exit(1)

def fmg_logout(hostIP):
    '''FortiManager logout
    Arguments:
    hostIP - IP addres of FortiManager. Note, if not on default HTTPS(443) port can input: 1.1.1.1:8080
    '''
    body = {
       "id": 1,
        "method": "exec",
        "params": [{
                "url": "sys/logout"
        }],
        "session": session
    }
    #Test HTTPS connection to host then Capture and output any errors
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e:
        print (SystemError(e))
        #Exit Program, Connection was not Successful
        sys.exit(1)
    #Save JSON response from FortiManager    
    json_resp = json.loads(r.text)
    #Check if any API Errors returned
    if json_resp['result'][0]['status']['code'] != -11:
        print ()
        print ('--> Logging out of FMG: %s' % hostIP)
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
    else:
        print ()
        print ('<--Error Occured, check Hcode & Jmesg')
        #Exit Program, internal FortiManager error review Hcode & Jmesg
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        sys.exit(1)   

def workspace_lock(lADOM):
    '''FortiManager Lock/Acquire ADOM 
    Arguments:
    lADOM - ADOM Name to Lock/Acquire
    '''
    #API Call
    json_url = "pm/config/adom/" + lADOM + "/_workspace/lock"
    body = {
    	"id": 1,
    	"method": "exec",
    	"params": [{
    		"url": json_url
    	}],
    	"session": session
    }
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
        #Exit Program, Connection was not Successful
        sys.exit(1)
    #Save JSON response from FortiManager
    json_resp = json.loads(r.text)
    #Check no code -11 means valid
    if json_resp['result'][0]['status']['code'] == -6:
        print(f'<-- Unable to Lock ADOM, ADOM name {lADOM} does not exist. Please check name & case sensitivity')
        print('<-- JSONmesg API output %s' % json_resp['result'][0]['status'])
        print
        #Exit Program, Unable to Lock ADOM
        sys.exit(1)
    elif json_resp['result'][0]['status']['code'] != -11:
        print ('--> Locking ADOM %s' % lADOM)
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
    else:
        print (f'<-- Unable to Lock ADOM {lADOM}, ADOM might be locked by a user, please check following JSONmesg for reason, exiting...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        #Exit Program, Unable to Lock ADOM
        sys.exit(1)

def workspace_unlock(uADOM):
    '''FortiManager unlock  ADOM 
    Arguments:
    uADOM - ADOM Name to unlock
    '''
    #API Call
    json_url = "pm/config/adom/" + uADOM + "/_workspace/unlock"
    body = {
    	"id": 1,
    	"method": "exec",
    	"params": [{
    		"url": json_url
    	}],
    	"session": session
    }
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
        #Exit Program, Connection was not Successful
        sys.exit(1)
    #Save JSON response from FortiManager
    json_resp = json.loads(r.text)
    #Check if no code -11 means valid
    if json_resp['result'][0]['status']['code'] != -11:
        print ('--> UnLocking ADOM %s' % uADOM)
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
    else:
        print (f'<--Unable to unlock ADOM {uADOM}, please check following JSONmesg for reason, exiting...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        #Exit Program, Unable to Lock ADOM
        sys.exit(1)

def workspace_commit(cADOM):
    '''FortiManager Commit/Save Changes to ADOM
    Arguments:
    cADOM - ADOM Name to Save Changes
    '''
    #API Call
    json_url = "pm/config/adom/" + cADOM + "/_workspace/commit"
    body = {
    	"id": 1,
    	"method": "exec",
    	"params": [{
    		"url": json_url
    	}],
    	"session": session
    }
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
        #Exit Program, Connection was not Successful
        sys.exit(1)
    #Save JSON response from FortiManager
    json_resp = json.loads(r.text)
    #Check if no code -11 means valid
    if json_resp['result'][0]['status']['code'] != -11:
        print ('--> Saving Changes to ADOM %s' % cADOM)
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
    else:
        print (f'<--Unable to Save Changes to ADOM {cADOM}, please check following JSONmesg for reason, will continue...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        pass

def status_taskid(taskID):
    ''' FortiManager Status TaskID Definiations & Actions
    Arguments:
    taskID - The Task ID returned from JSON API Response json_resp['result'][0]['data']['task']
    '''
    #Set Global State in order to track the State of the task
    global state
    #API Call to pull Task Status based on taskID
    json_url = "/task/task/" + str(taskID)
    body = {
        "id": 1,
        "method": "get",
        "params": [{
            "url": json_url
        }],
        "session": session
    }
    #Test HTTPS connection to host then Capture and output any errors
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e:
                print (f'Request for Task ID failed {SystemError(e)}')
    #Save Response from JSON Request
    json_resp = json.loads(r.text)
    #No code -11 means valid
    if json_resp['result'][0]['status']['code'] != -11:
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        state = json_resp['result'][0]['data']['state']
        totalPercent = json_resp['result'][0]['data']['tot_percent']
        if state == 0:
            print ('    Current task state (%d): pending' % state)
        if state == 1:
            print ('    Current task state (%d): running' % state)
        if state == 2:
            print ('    Current task state (%d): cancelling' % state)
        if state == 3:
            print ('    Current task state (%d): cancelled' % state)
        if state == 4:
            print ('    Current task state (%d): done' % state)
        if state == 5:
            print ('    Current task state (%d): error' % state)
        if state == 6:
            print ('    Current task state (%d): aborting' % state)
        if state == 7:
            print ('    Current task state (%d): aborted' % state)
        if state == 8:
            print ('    Current task state (%d): warning' % state)
        if state == 9:
            print ('    Current task state (%d): to_continue' % state)
        if state == 10:
            print ('    Current task state (%d): unknown' % state)
        if json_resp['result'][0]['status']['message'] == 'OK':
            print (f'    Current task percentage: {totalPercent}')
            print
    else:
        print ('Error, Request for Task ID failed JSON code -11')
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print        

def poll_taskid (taskID):
    ''' FortiManager poll task, then call function status_taskid to check the message.
    Arguments:
    taskID - The Task ID returned from JSON API Response json_resp['result'][0]['data']['task']
    '''
    global state
    state = 0
    while state not in [3,4,5,7]:
        print ('--> Polling task: %s' % taskID)
        time.sleep( 3 )
        status_taskid(taskID)
    if state == 4:
        print ('--> Task %s is done!' % taskID)
        print
    else:
        print ('--> Task %s is DIRTY, check FMG task manager for details!' % taskID)
        print

def policy_import(piADOM, piDEVICE,  piPACKNAME, piVDOM):
    ''' FortiManager Import Policy, if existing with the same name will Overwrite by default
    Arguments:
    piADOM - ADOM where the device/VDOM exist you want to import policy
    piDEVICE - FortiGate Device 
    piVDOM - VDOM in ADOM if available, if not set value to 'root', FortiManager will ignore it.
    piPACKNAME - Policy Package Name you want to call. If an existing Policy Package name exist, it will overwrite by default.
    '''
    ''' Step 1 - Policy Search Objects '''
    print()
    print('--> Starting Policy Package Import...')
    print('--> Step 1 - Policy Search for all Objects...')
    # API URL to start Import Object
    json_url = "/securityconsole/import/dev/objs"

    body = {
        "id": 1,
        "method": "exec",
        "params": [{
                "url": json_url,
                "data": {
                    "adom": piADOM,
                    "dst_name": piPACKNAME,
                    "if_all_policy": "enable",
                    "import_action": "policy_search",
                    "name": piDEVICE,
                    "vdom": piVDOM,
                    "if_all_objs": "all",
                    "add_mappings": "enable"
                    }
        }],
        "session": session
    }
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
    json_resp = json.loads(r.text)
    if json_resp['result'][0]['status']['code'] != -11:
        taskID = json_resp['result'][0]['data']['task']
        print ()
        print ('--> Perform dynamic interface mapping for  VDOM %s to  ADOM %s' % (piVDOM, piADOM))
        print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ("Task ID: " + str(taskID))
        print ()
        time.sleep( 0.3 )
        poll_taskid(taskID)
        workspace_commit(piADOM)
    else:
        print ('<--Error, unable to get API Request Step1 policy_search, existing...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        #Exit Program
        sys.exit(1)

    ''' Step 2 Import in Dynamic Object Mappings '''
    print ()
    print ('--> Step 2 Moving to import dynamic objects mappings...')
    ##import dynamic objects mappings
    body = {
    "id": 1,
            "method": "exec",
            "params": [{
                    "url": json_url,
                    "data": {
                            "adom": piADOM,
                            "dst_name": piPACKNAME,
                            "if_all_policy": "enable",
                            "import_action": "obj_search",
                            "name": piDEVICE,
                            "vdom": piVDOM,
                            "if_all_objs": "all",
                            "add_mappings": "enable"
                    }
            }],
            "session": session
    }
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
    # Save JSON Response
    json_resp = json.loads(r.text)
    if json_resp['result'][0]['status']['code'] != -11:
        taskID = json_resp['result'][0]['data']['task']
        print ()
        print ('--> Perform dynamic object mappings for  VDOM %s to  ADOM %s' % (piVDOM, piADOM))
        print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        time.sleep( 0.3 )
        poll_taskid(taskID)
        workspace_commit(piADOM)
    else:
        print ('<--Error, unable to get API Request Step2 mport in Dynamic Object Mappings, existing...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        #Exit Program
        sys.exit(1)

    ''' Step 3 Moving to import policy & dependant dynamic interfaces & objects '''
    print ()
    print ('--> Step 3 - Moving to importing policy & dependant dynamic interfaces & objects...')
	##importing policy & dependant dynamic interfaces & Objects
    body = {
    "id": 1,
            "method": "exec",
            "params": [{
                    "url": json_url,
                    "data": {
                            "adom": piADOM,
                            "dst_name": piPACKNAME,
                            "if_all_policy": "enable",
                            "import_action": "do",
                            "name": piDEVICE,
                            "vdom": piVDOM,
                            "if_all_objs": "all"
                    }
            }],
            "session": session
    }
    try:
        r = requests.post(url, json=body, verify=False)
    except requests.exceptions.RequestException as e: 
        print (SystemError(e))
    # Save JSON Response
    json_resp = json.loads(r.text)
    if json_resp['result'][0]['status']['code'] != -11:
        taskID = json_resp['result'][0]['data']['task']
        print ()
        print ('--> Perform importing policy & dynamic interfaces & objects for  VDOM %s to  ADOM %s' % (piVDOM, piADOM))
        print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        time.sleep( 0.3 )
        poll_taskid(taskID)
        #Save/Commit Changes
        workspace_commit(piADOM)
    else:
        print ('<--Error, unable to get API Request Step 3 Moving to import policy & dependant dynamic interfaces & objects, existing...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        #Exit Program
        sys.exit(1)

## Main Function
def main():
    ''' The main function/program '''
    ## User Input Section ##
    # Prompt for IP Address of FortiManager
    print('Please Enter FortiManager IP Address:')
    hostIP = input()
    #Check User put in data
    while not hostIP:
        print('Error, Please Enter FortiManager IP Address:')
        hostIP = input()
    
    # Prompt for API User Name
    print('Please Enter FortiManager API User name:')
    hostAPIUSER = input()
    #Check User put in data
    while not hostAPIUSER:
        print('Error, Please Enter FortiManager API User name:')
        hostAPIUSER = input()
    
    # Prompt for API User password. use getpass() module to hide it being displayed
    hostPASSWD = getpass.getpass('Please Enter FortiManager API User password:')
    #Check User put in data
    while not hostPASSWD:
        hostPASSWD = getpass.getpass('Error, Please Enter FortiManager API User password:')
    
    # Prompt for ADOM
    print('Please Enter the ADOM Name where your Device and/or VDOM exists:')
    hostADOM = input()
    while not hostADOM:
        print('Error, Please Enter the ADOM Name where your Device and/or VDOM exsts:')
        hostADOM = input()
    
    # Prompt for Device
    print('Please Enter the FortiGate Device Name you would like to Import Policy From:')
    fgtDEVNAME = input()
    while not fgtDEVNAME:
        print('Error, Please Enter the FortiGate Device Name you would like to Import Policy From:')
        fgtDEVNAME = input()
    
    # Prompt for VDOM if exist
    print('Please Enter the VDOM name if VDOMs is being used, if not using VDOMs, just hit Enter and it will use the default:')
    vdomNAME = input()
    if vdomNAME == '':
        vdomNAME = 'root'
        print('     VDOMs not used, using default')
    else:
        print(f'    Using VDOM {vdomNAME}')

    # Prompt for Policy Package Name
    print('Please Enter the Policy Package Name you would like to use. **NOTE: If you have an existing Policy Package and use the same name it will Overwrite that Package:')
    policyNAME = input()
    while not policyNAME:
        print('Error, Please Enter the Policy Package Name you would like to use:')
        policyNAME = input()
    print ()

    ## End User Input Section ##

    ## Call fmg_login Function
    fmg_login(hostAPIUSER, hostPASSWD, hostIP)

    ## Locking ADOM
    workspace_lock(hostADOM)

    ## Import Policy Package
    policy_import(hostADOM, fgtDEVNAME, policyNAME, vdomNAME)

    ## UnLocking ADOM
    workspace_unlock(hostADOM)

    ## Call fmg_logout Function
    fmg_logout(hostIP)

    ''' End main function/program '''

## Run the main function/program
if __name__ == '__main__':
    main()