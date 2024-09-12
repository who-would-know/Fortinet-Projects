
#!/usr/bin/python
'''Project: FortiManager - With device name of FortiGate, return VDOM to ADOM mapping in FortiManager
   Details: Example functions that can be used to pull from a device name in FortiManager the device VDOM to ADOM mapping. Example - to upgrade ADOMs that have VDOMs from a FortiGate Device.
   Date: 2024
   Functions: def fmg_login, fmg_logout, get_adom, get_vdom, list_filtered_adom_vdom
   Python Version: 3.10.11
   FortiManager Version: v7.0.8, should be compatible with 7.x branch.
   Instructions for Creating API User Account, Read Only api is the minimum requirement: 
        - Add an API user in your FortiManager
            -Log into FortiManager with admin account, Go To:
                -System Settings => Admin => Administrators
                -Click "+ Create New"
                -Create a User Name
                -Set a Password
                -Admin Profile Standard_User (or whatever Access you would like to grant to this API User Account)
                -JSON API Access set to Read (or whatever Access via the API you would like to grant to this API User Account)
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
#To receive and format JSON requests
import json


## Functions
def fmg_login(host_apiuser, host_passwd, host_ip):
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
    url = 'https://' + host_ip + '/jsonrpc'
    #JSON Body to sent to API request
    body = {
    "id": 1,
            "method": "exec",
            "params": [{
                    "url": "sys/login/user",
                    "data": [{
                            "user": host_apiuser,
                            "passwd": host_passwd
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
        print ('--> Logging into FortiManager: %s' % host_ip)
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s \n' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
    else:
        print ('<--Username or password is not valid, please try again, exiting...')
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s\n' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        #Exit Program, Username or Password is not valided or internal FortiManager error review Hcode & Jmesg
        sys.exit(1)

def fmg_logout(host_ip):
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
        print ('\n--> Logging out of FMG: %s' % host_ip)
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s \n' % (r.status_code, json_resp['result'][0]['status']['message']))
    else:
        print ('\n<--Error Occured, check Hcode & Jmesg')
        #Exit Program, internal FortiManager error review Hcode & Jmesg
        print ('<-- HTTPcode: %d JSONmesg: %s \n' % (r.status_code, json_resp['result'][0]['status']['message']))
        sys.exit(1)   

def get_adom(fgt_device_name):
    '''Get ADOMs
    Arguments:
    fgt_device_name - Device Name of the Fortigate(or cluster) listed in FortiManager under Device Manager

    Returns:
    adom_list - list of adoms from FortiGate Device
    '''
    adom_list = []
    json_url = "dvmdb/adom"
    body = {
            "id": 1,
            "method": "get",
            "params": [{
                    "expand member": [
                        {
                            "fields": [
                                "name",
                            ],
                            "filter": [
                                "name", "==", fgt_device_name
                            ],
                            "url": "/device"
                        }
                    ],
                    "fields": [
                        "name",
                    ],
                    "url": json_url
            }],
            "session": session,
            #"verbose": 1
    }
    r = requests.post(url, json=body, verify=False)
    json_resp = json.loads(r.text)
    # print(json.dumps(json_resp, indent=2))
    for entry in json_resp['result'][0]['data']:
        #print(entry);
        if "expand member" in entry:
            adom_list.append(entry['name'])
            #print(entry)
    return adom_list

def get_vdom(fgt_device_name, adom_name):
    '''Get ADOMs
    Arguments:
    fgt_device_name - Device Name of the Fortigate(or cluster) listed in FortiManager under Device Manager
    adom_name - Pass the ADOM name

    Returns:
    vdom_list - returns vdom(s) from the ADOM and FortiGate Device
    '''
    vdom_list = []
    json_url = "dvmdb/adom/" + adom_name + "/device/" + fgt_device_name + "/vdom"
    body = {
        "id": 1,
        "method": "get",
        "params": [{
            "url": json_url
         }],
        "session": session
    }
    r = requests.post(url, json=body, verify=False)
    json_resp = json.loads(r.text)
    json_mesg = json_resp['result'][0]['status']['message']
    # print(json.dumps(json_resp, indent=2))
    print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
    print ('-->Searching for VDOM...')
    if json_resp['result'][0]['status']['code'] < 0:
        print(f'-->ERROR: Invalid or not found ADOM: {adom_name} for device: {fgt_device_name}\n')
    else:
        for entry in json_resp['result'][0]['data']:
            vdom_list.append(entry['name'])	
    return vdom_list

def list_filtered_adom_vdom(fgt_device_name):
    '''Get ADOMs
    Arguments:
    fgt_device_name - Device Name of the Fortigate(or cluster) listed in FortiManager under Device Manager

    Function calls:
    get_adom
    get_vdom

    Returns:
    root_vdom2adom_list - list of root VDOMs with their associated ADOMs
    vdom2adom_list - list of non-root VDOMs with their associated ADOMs
    '''
    vdom2adom_list = []
    root_vdom2adom_list = []
    adom_list = get_adom(fgt_device_name)    
    for adom  in adom_list:
        vdom_list = get_vdom(fgt_device_name, adom)
		##print(vdomLIST)
        for vdom in vdom_list:
            if vdom == 'root':
                root_vdom2adom_list.append(vdom + ":" + adom)
                print ('>>>>>>>>> Cluster Root VDOM to ADOM found: %s <<<<<<<' % adom )
                print ('\n')
				#print(rootvdom2adomLIST)    
            else:
                vdom2adom_list.append(vdom + ":" + adom)
                print ('>>>>>>>>> Match found VDOM: %s to ADOM: %s <<<<<<<' % (vdom, adom) )
                print ('\n')
    return root_vdom2adom_list, vdom2adom_list
		
def main():
    ''' The main function/program '''
    ## User Input Section ##
    # Prompt for IP Address of FortiManager
    print('Please Enter FortiManager IP Address:')
    host_ip = input()
    #Check User put in data
    while not host_ip:
        print('Error, Please Enter FortiManager IP Address:')
        host_ip = input()
    
    # Prompt for API User Name
    print('Please Enter FortiManager API User name:')
    host_apiuser = input()
    #Check User put in data
    while not host_apiuser:
        print('Error, Please Enter FortiManager API User name:')
        host_apiuser = input()
    
    # Prompt for API User password. use getpass() module to hide it being displayed
    host_passwd = getpass.getpass('Please Enter FortiManager API User password:')
    #Check User put in data
    while not host_passwd:
        host_passwd = getpass.getpass('Error, Please Enter FortiManager API User password:')
    
    # Prompt for FortiGate Device Name
    print('Please Enter the Device Name for the FortiGate listed in FortiManager:')
    fgt_device_name = input()
    while not fgt_device_name:
        print('Error, Please Enter the Device name for the FortiGate:')
        fgt_device_name = input()
    ## End User Input Section ##

    ## Call fmg_login Function
    fmg_login(host_apiuser, host_passwd, host_ip)

    ## Get ADOM from FortiGate Device
    adom_list = get_adom(fgt_device_name)
    print(f'ADOM List for device {fgt_device_name}: {adom_list}\n')
    
    ## Get VDOM to ADOM
    root_vdom2adom_list, vdom2adom_list = list_filtered_adom_vdom(fgt_device_name, )
    print(f'root VDOM:ADOM LIST for device {fgt_device_name}: {root_vdom2adom_list}')
    print(f'VDOM:ADOM LIST for device {fgt_device_name}: {vdom2adom_list}\n')

    ## Call fmg_logout Function
    fmg_logout(host_ip)

    ''' End main function/program '''

## Run the main function/program
if __name__ == '__main__':
    main()