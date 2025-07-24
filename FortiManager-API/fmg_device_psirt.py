#Quick & dirty python script to test API FortiManager 7.6.3 pull device psirt/vuln list that is displayed in the FortiManager -> Device for each FortiGate
# Change the Global VAR below for your environment.

import os
import os.path
import sys
import time
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json

requests.packages.urllib3.disable_warnings()

###Global VARs, change to match your local
hostADMIN = 'admin'
hostPASSWD = 'pwd'
hostIP = '192.168.1.1'
device = 'FGTFWNAME'
###END GLOBAL

url = 'https://' + hostIP + '/jsonrpc'
session = ''

def fmg_login():
        global session
        body = {
        "id": 1,
                "method": "exec",
                "params": [{
                        "url": "sys/login/user",
                        "data": [{
                                "user": hostADMIN,
                                "passwd": hostPASSWD
                        }]
                }],
                "session": 1
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        session = json_resp['session']
        print ('--> Logging into FMG: %s' % hostIP)
        print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))

def fmg_logout():
        body = {
        "id": 1,
                "method": "exec",
                "params": [{
                        "url": "sys/logout"
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        print ('--> Logging out of FMG: %s' % hostIP)
        print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        print

def workspace_lock(fmgADOM):
        json_url = "pm/config/adom/" + fmgADOM + "/_workspace/lock"
        body = {
                "id": 1,
                "method": "exec",
                "params": [{
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        #print ('--> Locking ADOM %s' % fmgADOM)
        #print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        #print

def workspace_unlock(fmgADOM):
        json_url = "pm/config/adom/" + fmgADOM + "/_workspace/unlock"
        body = {
                "id": 1,
                "method": "exec",
                "params": [{
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        #print ('--> Unlocking ADOM %s' % fmgADOM)
        #print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        #print

def workspace_commit(fmgADOM):
        json_url = "pm/config/adom/" + fmgADOM + "/_workspace/commit"
        body = {
                "id": 1,
                "method": "exec",
                "params": [{
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        print('--Saved All Changes in ADOM %s' % (fmgADOM))


def get_device(device):
        json_url = 'pm/config/'
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
        print(json.dumps(json_resp, indent=4))

def get_oid(device):
        json_url = 'dvmdb/device'
        body = {
                "method": "get",
                "params": [{
                        "fields": [
                                "name"
                        ],
                        "filter": [
                                "name",
                                "==",
                                device
                        ],
                        "option": [
                                "no loadsub"
                        ],
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        print(json.dumps(json_resp, indent=4))      
        return json_resp['result'][0]['data'][0]['oid']

def get_psirt( oid, adom='root'):
        json_url = 'pm/config/adom/' + adom + "/_psirt/data"
        body = {
                "method": "get",
                "params": [{
                        "scope member": [
                        {
                                "oid": oid
                        }],
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        print(json.dumps(json_resp, indent=4))      


#############MAIN


fmg_login()

device_oid = get_oid(device)
print(f'Device OID {device_oid}')
get_psirt(device_oid)

fmg_logout()
