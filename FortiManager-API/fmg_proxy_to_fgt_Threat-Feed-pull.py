#!/usr/bin/python
'''Project: FortiManager Proxy commands to FortiGate that are not available on FortiManager. In this example Threat Feed.
   Details: This example could be used to install CERTS onto FortiGate, pull local Traffic Stats, etc. without having to keep track of each FortiGate IP
            update ACL to access each from your script. As long as you can reach the FortiManager and FortiGate is managed by it, you can proxy your API calls.
   Date: 12-16-2020
   Functions: def threatfeedgetPROXYFMG, def threatfeedgetlistPROXYFMG
   Python Version: 3.7.4
   FortiManager Version: v6.2.3 on Azure, compatible and tested with v6.0.9 GA
   IDE: Visual Studio
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
        print ('<--Error Occured, check Hcode & Jmesg')
        #Exit Program, internal FortiManager error review Hcode & Jmesg
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print ()
        sys.exit(1)   

def threatfeedgetPROXYFMG(ADOM, fgtDEVNAME, VDOM):
    '''FortiManager Proxy to FortiGate pull Threat Feed Information
    Arguments:
    ADOM - ADOM that your FortiGate Exists in
    fgtDEVNAME- The FortiGate Device Name
    VDOM - If FortiGate has VDOM enabled, use this, if not, default to root vdom which is no VDOM enabled
    '''
    #Build API call Proxy JSON
    json_url = "/sys/proxy/json"
    #Build resource, the FortiGate local API
    resource = "/api/v2/cmdb/system/external-resource/?vdom=" + VDOM
    #Build target, the location of the FortiGate device in the FortiManager. ADOM + Device name
    target = "adom/" + ADOM + "/device/" + fgtDEVNAME
    body = {
        "id": 1,
        "method": "exec",
        "params": [{
                "data": {
                        "resource": resource,
                        "target": [target],
                        "action": "get",
                },
                "url": json_url
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
    #print(json_resp['result'][0]['data'][0]['status']['code'])
    if json_resp['result'][0]['data'][0]['status']['code'] == 0:
        print('--> Retrieving FortiGate Device Name %s Threat Feed information...' % fgtDEVNAME)
        print(json.dumps(json_resp['result'][0]['data'][0]['response']['results'], indent = 4, sort_keys=True))
    else:
        print('--> Retrieving FortiGate Device Name %s Threat Feed information...' % fgtDEVNAME)
        print ('<-- ERROR! Occured, check Hcode & Jmesg')
        #Exit Program, internal FortiManager error review Hcode & Jmesg
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['data'][0]['status']['message']))
        print

def threatfeedgetlistPROXYFMG(ADOM, fgtDEVNAME, tfENTRYNAME, VDOM):
    '''FortiManager Proxy to FortiGate pull Threat Feed List/Entries
    Arguments:
    ADOM - ADOM that your FortiGate Exists in
    fgtDEVNAME- The FortiGate Device Name
    tfENTRYNAME - Name of the Threat Feed on the FortiGate you would like to pull the Populated Entry List from
    VDOM - If FortiGate has VDOM enabled, use this, if not, default to VDOM=root vdom which is no VDOM enabled
    '''
    #Build API call Proxy JSON
    json_url = "/sys/proxy/json"
    #Build resource, the FortiGate local API
    resource = "/api/v2/monitor/system/external-resource/entry-list?mkey=" + tfENTRYNAME + "&vdom=" + VDOM
    #Build target, the location of the FortiGate device in the FortiManager. ADOM + Device name
    target = "adom/" + ADOM + "/device/" + fgtDEVNAME
    body = {
        "id": 1,
        "method": "exec",
        "params": [{
                "data": {
                        "resource": resource,
                        "target": [target],
                        "action": "get",
                },
                "url": json_url
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
    print(json_resp['result'][0]['data'][0]['status']['code'])
    if json_resp['result'][0]['data'][0]['status']['code'] == 0:
        print('--> Retrieving FortiGate Device Name %s Threat Feed Entry %s information...' % (fgtDEVNAME, tfENTRYNAME))
        #print(json.dumps(json_resp, indent = 4, sort_keys=True))
        print(json.dumps(json_resp['result'][0]['data'][0]['response']['results']['entries'], indent = 4, sort_keys=True))
    else:
        print('--> Retrieving FortiGate Device Name %s Threat Feed Entry %s information...' % (fgtDEVNAME, tfENTRYNAME))
        print ('<-- ERROR! Occured, check Hcode & Jmesg')
        #Exit Program, internal FortiManager error review Hcode & Jmesg
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['data'][0]['status']['message']))
        print   

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
    print('Please Enter the FortiGate Device Name you would like pull Threat Feed Info from:')
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
    
    # Prompt for Threat Feed Entry Name
    print('Please Enter the Threat Feed Name you would like to pull a list of the populated Entries:')
    ENTRYNAME = input()
    while not ENTRYNAME:
        print('Error, Please Enter the FortiGate Device Name you would like to Import Policy From:')
        ENTRYNAME = input()

    ## End User Input Section ##

    ## Call fmg_login Function
    fmg_login(hostAPIUSER, hostPASSWD, hostIP)

    ## Call Threat Feed pull all
    threatfeedgetPROXYFMG(hostADOM, fgtDEVNAME, vdomNAME)

    ## Call Threat Feed pull Entries
    threatfeedgetlistPROXYFMG(hostADOM, fgtDEVNAME, ENTRYNAME, vdomNAME)

    ## Call fmg_logout Function
    fmg_logout(hostIP)

    ''' End main function/program '''

## Run the main function/program
if __name__ == '__main__':
    main()