#!/usr/bin/python
'''Project: FortiManager API Login 
   Date: 12-15-2020
   Python Version: 3.7.4
   FortiManager Version: v6.2.3 on Azure, compatible and tested with v6.0.9 GA
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
        print ('--> Logging out of FMG: %s' % hostIP)
        #HTTP & JSON code & message
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
    else:
        print ('<--Error Occured, check Hcode & Jmesg')
        #Exit Program, internal FortiManager error review Hcode & Jmesg
        print ('<-- HTTPcode: %d JSONmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print
        sys.exit(1)   


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
    ## End User Input Section ##

    ## Call fmg_login Function
    fmg_login(hostAPIUSER, hostPASSWD, hostIP)

    ## Call fmg_logout Function
    fmg_logout(hostIP)

    ''' End main function/program '''

## Run the main function/program
if __name__ == '__main__':
    main()