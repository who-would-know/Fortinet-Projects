###Example Code, change values in Global and Main to run in your environment
###Older code example not verified with latest FortiManager releases 

import os
import os.path
import sys
import time
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json

requests.packages.urllib3.disable_warnings()

###Put in file name below, example file test_cli_script.txt 
test_cli_script = open("test_cli_script.txt").read()

#Global VARs, change to match your local
hostADMIN = 'admin'
hostPASSWD = 'xxxx'
hostIP = '10.101.101.82'

url = 'https://' + hostIP + '/jsonrpc' 
session = ''
state = 0
adomRAW = ''
fgtLIST = []
adomLIST = []
taskID = ''

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


def list_adom():
        #global adomRAW
        #global adomLIST
        json_url = "dvmdb/adom"
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
        #print ('<-- Hcode: %d Jmesg: %s' % (r.status_code, json_resp['result'][0]['status']['message']))
        #print
        adomLISTraw = []
        for entry in json_resp['result'][0]['data']:
                adomLISTraw.append(entry['name'])
        #for adomRAW  in adomLISTraw:
        #        print ('--> Searching for ADOM %s' % (adomRAW))
	return adomLISTraw

def list_pkg(adom):
	json_url = "pm/pkg/adom/" + adom 
	#print ('url.... %s' % (json_url)) 
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
	#print ('------- %s' % (json_resp))
	pkgLIST = []
	for entry in json_resp['result'][0]['data']:
		pkgLIST.append(entry['name'])
	return pkgLIST

def create_cli(name, adom, cliscript):
        json_url = "dvmdb/adom/" + adom + "/script/"
        body = {
                "id": 1,
                "method": "add",
                "params": [{
                        "data": {
				"name": name,
                                "content": cliscript,
				"target": "adom_database",
				"type": "cli"
                        },
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
        print ('------111- %s' % (json_resp))

def exec_cli(name, adom, pkg):
	json_url = "dvmdb/adom/" + adom + "/script/execute"
        body = {
                "id": 1,
                "method": "exec",
                "params": [{
			"data": {
				"adom": adom,
				"package": pkg,
				"script": name
			},
                        "url": json_url
                }],
                "session": session
        }
        r = requests.post(url, json=body, verify=False)
        json_resp = json.loads(r.text)
	print ('------111- %s' % (json_resp))
						
	
	  

#############MAIN

fmg_login()
###(name of ADOM)
workspace_lock("BravoCorp")
##(name of CLI Script, Name of ADOM, name of Script file imported from file)
create_cli("testing", "BravoCorp", test_cli_script)
##(name of CLI Script, Name of ADOM, name of Policy Package)
exec_cli("testing", "BravoCorp", "default")
workspace_commit("BravoCorp")
workspace_unlock("BravoCorp")

fmg_logout()
