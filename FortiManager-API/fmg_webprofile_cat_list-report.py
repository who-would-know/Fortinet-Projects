#!/usr/bin/python
'''Project: FortiManager Pull Web Filter Profiles per ADOM and list Local & FortiGuard Categories and their Action - Block, Warning, Auth, Allow, etc.
   Details: Customers or Security Engineers might need to display (on Screen & CSV) FortiManager ADOM(customer) Web Profile Local & FortiGuard Categories.
            There is multiple Section & Sub Level for FortiGuard Categories and hard to screenshot (expand sections, etc) then share.
            The get_webfiltercat function will use Prettytable Python Module to display via screen & output to CSV to share in a readable format.
            This could be done by changing the API and pointed to FortiGate directly.
            Biggest challenge was understanding first you grab the Web Profile, then grab the ID, then map the ID to FortiGuard Profile & Category names.
            This could probably be built out automatically but it is static per FortiOS version and if new Category is added in future FortiOS Releases
            easy to pull new ID then add it.
   Date: 12-26-2020
   Functions: def get_webfiltercat
   Python Version: 3.7.4
   FortiManager Version: v6.2.3 on Azure, compatible and tested with v6.0.9 GA
   Fortigate Version: FortiOS 6.2 & 6.0 compatible and tested.
   IDE: Visual Studio
   Instructions for Creating API User Account, for get_webfiltercat functions ReadOnly user Profile is the minimum: 
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
#Time - help to generate unique file
import time
#Pretty Tables to display in a readable format via screen & to help output to a CSV format.
from prettytable import PrettyTable

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

def get_webfiltercat(adom):
    '''FortiManager ADOM Web Profile Local & FortiGuard Category Display via Console & CSV file
    Arguments:
    ADOM - Name of the ADOM in FortiManager you would like pull & generate console & CSV report file for.
    '''
    #Global Vars for function
    #Actions - Webfilter Profile Action type Index to Text
    actionWF = {'0': 'Block',  '2': 'Monitor', '3': 'Warning', '4': 'Authenicate'}
    #Generate Timestamp for all output files
    timestr = time.strftime("%Y%m%d-%H%M%S")

    #Create and open file to write for Debug & console output of report
    try:
        fileNAMEOUTPUT = timestr + "_" + adom + "_" + "FMG_Web-Filter-Profile_Categories-DEBUG-CONSOLE-OUTPUT_LOG.txt"
        outputFILECONSOLE = open(fileNAMEOUTPUT, "w")
    except:
        #Output error & exit
        print("Unable to create DEBUG-OUTPUT file for Web Filter Profile Category, exiting...")
        sys.exit(1)

    #Get ADOM URL Profiles using the ADOM passed to Function. API URL
    json_url = "pm/config/adom/" + adom + "/obj/webfilter/profile"
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
    #Error Check then report if not found.
    if json_resp['result'][0]['status']['code'] == -6:
        print ('\nUnable to find ADOM: ' + adom + ". Please check ADOM exists. Debug file created.", file = outputFILECONSOLE )
        outputFILECONSOLE.close()
        sys.exit(1)

    if json_resp['result'][0]['data'] != None:
        #Print to file TXT & CSV
        try:
            fileNAME = timestr + "_ADOM_" + adom + "_Web-Filter-Profile_Categories.txt"
            fileNAMECSV = timestr + "_ADOM_" + adom + "_Web-Filter-Profile_Categories.csv"
            outputFILE = open(fileNAME, 'w')
            outputFILECSV = open(fileNAMECSV, 'w')
        except:
            #Output error & exit
            print("Unable to create Text & CSV output files for Web Filter Profile Category, exiting...")
            sys.exit(1)

        #Create using PrettyTable the Report Tables, Columns
        #Main loop to pull each Web Filter Profile Local & FortiGuard Categories
        for entry in json_resp['result'][0]['data']:
            table = PrettyTable()
            table.title = "Profile Name: " + entry['name']
            print ("Profile Name: " + entry['name'], file = outputFILECONSOLE)
            
            ###Get each Web Profile FortiGuard Categories
            json_url = "pm/config/adom/" + adom + "/obj/webfilter/profile/" + entry['name'] + "/ftgd-wf/filters"
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
            #Print to DEBUG-OUTPUT file raw JSON
            print (json.dumps(json_resp, indent=2), file = outputFILECONSOLE)

            
            ###Get each FortiGuard Category & it's associated action. Put it into a key pair CATEGORY-ID:ACTION
            cataction = {}
            for cats in json_resp['result'][0]['data']:
                cataction[str(cats['category']).strip('[\']')] = cats['action']
            #print(cataction)

            ###Create the Tables for Category to print
            table.field_names = ["Category", "Setting"]
            table.align["Category"] = "l"
            table.align["Setting"] = "l"

            ###Find Local Categories
            table.add_row(["Local Categories", ""])

            json_url = "pm/config/adom/" + adom + "/obj/webfilter/ftgd-local-cat"
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
            #Print to DEBUG-OUTPUT file raw JSON
            print (json.dumps(json_resp, indent=2), file = outputFILECONSOLE)
            if json_resp['result'][0]['data'] != None:
                for entry in json_resp['result'][0]['data']:
                    ##Enable below coments if you want to see the raw results, the ID & the Category Name
                    #print('---id: %s', entry['id'])
                    #print('---name: %s', actionWF[str(cataction[str(entry['id'])])])
                    if str(entry['id']) in cataction:
                        table.add_row(["    " + entry['desc'], actionWF[str(cataction[str(entry['id'])])]])
                    else:
                        table.add_row(["    " + entry['desc'], "Allow"])

            ##Here we start to take each cataction IP and Mapp it to the Human Readable Name. 
            ##We do not need a loop as cataction is a list with CATEGORY-ID:ACTION, so we can use Python 'in' that will search the List to find it.
            ##If that CATEGORY-ID does not exist, that means it is taking the default action "Allow". In FortiOS CLI (FortiGate) this is like when
            ##you do not see it in the default "show config".

            #Potentially Liable Section & all subsections
            table.add_row(["Potentially Liable", ""])
            if '83' in cataction:
                table.add_row(["    Child Abuse", actionWF[str(cataction['83'])]])
            else:
                table.add_row(["    Child Abuse", "Allow"])
            if '5' in cataction:
                table.add_row(["    Discrimination", actionWF[str(cataction['5'])]])
            else:
                table.add_row(["    Discrimination", "Allow"])
            if '1' in cataction:
                table.add_row(["    Drug Abuse", actionWF[str(cataction['1'])]])
            else:
                table.add_row(["    Drug Abuse", "Allow"])
            if '6' in cataction:
                table.add_row(["    Explicit Violence", actionWF[str(cataction['6'])]])
            else:
               table.add_row(["    Explicit Violence", "Allow"])   
            if '12' in cataction:
                table.add_row(["    Extremist Groups", actionWF[str(cataction['12'])]])
            else:
                table.add_row(["    Extremist Groups", "Allow"])   
            if '3' in cataction:
                table.add_row(["    Hacking", actionWF[str(cataction['3'])]])
            else:
                table.add_row(["    Hacking", "Allow"])   
            if '4' in cataction:
                table.add_row(["    Illegal or Unethical", actionWF[str(cataction['4'])]])
            else:
                table.add_row(["    Illegal or Unethical", "Allow"])   
            if '62' in cataction:
                table.add_row(["    Plagiarim", actionWF[str(cataction['62'])]])
            else:
                table.add_row(["    Plagiarim", "Allow"])   
            if '59' in cataction:
                table.add_row(["    Proxy Avoidance", actionWF[str(cataction['59'])]])
            else:
                table.add_row(["    Proxy Avoidance", "Allow"])
  
            #Adult/Mature Content Section & all the subsections
            table.add_row(["Adult/Mature Content", ""])
            if '7' in cataction:
                table.add_row(["    Abortion", actionWF[str(cataction['7'])]])
            else:
                table.add_row(["    Aboration", "Allow"])
            if '9' in cataction:
                table.add_row(["    Advocacy Organization", actionWF[str(cataction['9'])]])
            else:
                table.add_row(["    Advocacy Organization", "Allow"])
            if '64' in cataction:
                table.add_row(["    Alcohol", actionWF[str(cataction['64'])]])
            else:
                table.add_row(["    Alcohol", "Allow"])
            if '2' in cataction:
                table.add_row(["    Alternative Beliefs", actionWF[str(cataction['2'])]])
            else:
                table.add_row(["    Alternative Beliefs", "Allow"])
            if '15' in cataction:
                table.add_row(["    Dating",actionWF[str(cataction['15'])]])
            else:
                table.add_row(["    Dating", "Allow"])
            if '11' in cataction:
                table.add_row(["    Gambling", actionWF[str(cataction['11'])]])
            else:
                table.add_row(["    Gambling", "Allow"])
            if '66' in cataction:
                table.add_row(["    Lingerie and Swimsuit", actionWF[str(cataction['66'])]])
            else:
                table.add_row(["    Lingerie and Swimsuit", "Allow"])
            if '57' in cataction:
                table.add_row(["    Marijuana", actionWF[str(cataction['57'])]])
            else:
                table.add_row(["    Marijuana", "Allow"])
            if '13' in cataction:
                table.add_row(["    Nudity and Risque", actionWF[str(cataction['13'])]])
            else:
                table.add_row(["    Nudity and Risque", "Allow"])
            if '8' in cataction:
                table.add_row(["    Other Adult Materials", actionWF[str(cataction['8'])]])
            else:
                table.add_row(["    Other Adult Materials", "Allow"])
            if '14' in cataction:
                table.add_row(["    Pornography", actionWF[str(cataction['14'])]])
            else:
                table.add_row(["    Pornography", "Allow"])
            if '63' in cataction:
                table.add_row(["    Sex Education", actionWF[str(cataction['63'])]])
            else:
                table.add_row(["    Sex Education", "Allow"])
            if '67' in cataction:
                table.add_row(["    Sports Hunting and War Games", actionWF[str(cataction['67'])]])
            else:
                table.add_row(["    Sports Hunting and War Game", "Allow"])
            if '65' in cataction:
                table.add_row(["    Tobacco", actionWF[str(cataction['65'])]])
            else:
                table.add_row(["    Tobacco", "Allow"])
            if '16' in cataction:
                table.add_row(["    Weapons Sales", actionWF[str(cataction['16'])]])
            else:
                table.add_row(["    Weapons Sales", "Allow"])

            #Bandwidth Consuming Section & all the subsections
            table.add_row(["Bandwidth Consuming", ""])
            if '24' in cataction:
                table.add_row(["    File Sharing and Storage", actionWF[str(cataction['24'])]])
            else:
                table.add_row(["    File Sharing and Storage", "Allow"])
            if '19' in cataction:
                table.add_row(["    Freeware and Software Downloads", actionWF[str(cataction['19'])]])
            else:
                table.add_row(["    Freeware and Software Downloads", "Allow"])
            if '75' in cataction:
                table.add_row(["    Internet Radio and TV", actionWF[str(cataction['75'])]])
            else:
                table.add_row(["    Internet Radio and TV", "Allow"])
            if '76' in cataction:
                table.add_row(["    Internet Telephony", actionWF[str(cataction['76'])]])
            else:
                table.add_row(["    Internet Telephony", "Allow"])
            if '72' in cataction:
                table.add_row(["    Peer to Peer File Sharing",actionWF[str(cataction['72'])]])
            else:
                table.add_row(["    Peer to Peer File Sharing", "Allow"])
            if '25' in cataction:
                table.add_row(["    Streaming Media and Download", actionWF[str(cataction['25'])]])
            else:           
                table.add_row(["    Streaming Media and Download", "Allow"])

            #Security Risks Section & all the subsections
            table.add_row(["Security Risks", ""])
            if '88' in cataction:
                table.add_row(["    Dynamic DNS", actionWF[str(cataction['88'])]])
            else:
                table.add_row(["    Dynamic DNS", "Allow"])
            if '26' in cataction:
                table.add_row(["    Malicious Websites", actionWF[str(cataction['26'])]])
            else:
                table.add_row(["    Malicious Websites", "Allow"])
            if '90' in cataction:
                table.add_row(["    Newly Observed Domain", actionWF[str(cataction['90'])]])
            else:
                table.add_row(["    Newly Observed Domain", "Allow"])
            if '91' in cataction:
                table.add_row(["    Newly Registered Domain", actionWF[str(cataction['91'])]])
            else:
                table.add_row(["    Newly Registered Domain", "Allow"])
            if '61' in cataction:
                table.add_row(["    Phishing", actionWF[str(cataction['61'])]])
            else:
                table.add_row(["    Phishing", "Allow"])
            if '86' in cataction:
                table.add_row(["    Spam URLs", actionWF[str(cataction['86'])]])
            else:           
                table.add_row(["    Spam URLs", "Allow"])

            #General Interest - Personal Section & all the subsections
            table.add_row(["General Interest - Personal", ""])
            if '17' in cataction:
                table.add_row(["    Advertising", actionWF[str(cataction['17'])]])
            else:
                table.add_row(["    Advertising", "Allow"])
            if '29' in cataction:
                table.add_row(["    Arts and Culture", actionWF[str(cataction['29'])]])
            else:
                table.add_row(["    Arts and Culture", "Allow"])
            if '89' in cataction:
                table.add_row(["    Auction", actionWF[str(cataction['89'])]])
            else:
                table.add_row(["    Auction", "Allow"])
            if '18' in cataction:
                table.add_row(["    Brokerage and Trading", actionWF[str(cataction['18'])]])
            else:
                table.add_row(["    Brokerage and Trading", "Allow"])
            if '77' in cataction:
                table.add_row(["    Child Education",actionWF[str(cataction['77'])]])
            else:
                table.add_row(["    Child Education", "Allow"])
            if '82' in cataction:
                table.add_row(["    Content Servers", actionWF[str(cataction['82'])]])
            else:
                table.add_row(["    Content Servers", "Allow"])
            if '71' in cataction:
                table.add_row(["    Digital Post Cards", actionWF[str(cataction['71'])]])
            else:
                table.add_row(["    Digital Post Cards", "Allow"])
            if '85' in cataction:
                table.add_row(["    Domain Parking", actionWF[str(cataction['85'])]])
            else:
                table.add_row(["    Domain Parking", "Allow"])
            if '54' in cataction:
                table.add_row(["    Dynamic Content", actionWF[str(cataction['54'])]])
            else:
                table.add_row(["    Dynamic Content", "Allow"])
            if '30' in cataction:
                table.add_row(["    Education", actionWF[str(cataction['30'])]])
            else:
                table.add_row(["    Education", "Allow"])
            if '28' in cataction:
                table.add_row(["    Entertainment", actionWF[str(cataction['28'])]])
            else:
                table.add_row(["    Entertainment", "Allow"])
            if '58' in cataction:
                table.add_row(["    Folklore", actionWF[str(cataction['58'])]])
            else:
                table.add_row(["    Folklore", "Allow"])
            if '20' in cataction:
                table.add_row(["    Games", actionWF[str(cataction['20'])]])
            else:
                table.add_row(["    Games", "Allow"])
            if '40' in cataction:
                table.add_row(["    Global Religion", actionWF[str(cataction['40'])]])
            else:
                table.add_row(["    Global Religion", "Allow"])
            if '33' in cataction:
                table.add_row(["    Health and Wellness", actionWF[str(cataction['33'])]])
            else:
                table.add_row(["    Health and Wellness", "Allow"])
            if '69' in cataction:
                table.add_row(["    Instant Messaging", actionWF[str(cataction['69'])]])
            else:
                table.add_row(["    Instant Messaging", "Allow"])
            if '34' in cataction:
                table.add_row(["    Job Search", actionWF[str(cataction['34'])]])
            else:
                table.add_row(["    Job Search", "Allow"])
            if '55' in cataction:
                table.add_row(["    Meaningless Content", actionWF[str(cataction['55'])]])
            else:
                table.add_row(["    Meaningless Content", "Allow"])
            if '35' in cataction:
                table.add_row(["    Medicine", actionWF[str(cataction['35'])]])
            else:
                table.add_row(["    Medicine", "Allow"])
            if '36' in cataction:
                table.add_row(["    News and Media", actionWF[str(cataction['36'])]])
            else:
                table.add_row(["    News and Media", "Allow"])
            if '70' in cataction:
                table.add_row(["    Newsgroups and Message Boards", actionWF[str(cataction['70'])]])
            else:
                table.add_row(["    Newsgroups and Message Boards", "Allow"])
            if '87' in cataction:
                table.add_row(["    Personal Privacy", actionWF[str(cataction['87'])]])
            else:
                table.add_row(["    Personal Privacy", "Allow"])
            if '48' in cataction:
                table.add_row(["    Personal Vehicles", actionWF[str(cataction['48'])]])
            else:
                table.add_row(["    Personal Vehicles", "Allow"])
            if '80' in cataction:
                table.add_row(["    Personal Websites and Blogs", actionWF[str(cataction['80'])]])
            else:
                table.add_row(["    Personal Websites and Blogs", "Allow"])
            if '38' in cataction:
                table.add_row(["    Political Organizations", actionWF[str(cataction['38'])]])
            else:
                table.add_row(["    Political Organizations", "Allow"])
            if '78' in cataction:
                table.add_row(["    Real Estate", actionWF[str(cataction['78'])]])
            else:
                table.add_row(["    Real Estate", "Allow"])
            if '39' in cataction:
                table.add_row(["    Reference", actionWF[str(cataction['39'])]])
            else:
                table.add_row(["    Reference", "Allow"])
            if '79' in cataction:
                table.add_row(["    Restaurant and Dining", actionWF[str(cataction['79'])]])
            else:
                table.add_row(["    Restaurant and Dining", "Allow"])
            if '42' in cataction:
                table.add_row(["    Shopping", actionWF[str(cataction['42'])]])
            else:
                table.add_row(["    Shopping", "Allow"])
            if '37' in cataction:
                table.add_row(["    Social Networking", actionWF[str(cataction['37'])]])
            else:
                table.add_row(["    Social Networking", "Allow"])
            if '44' in cataction:
                table.add_row(["    Society and Lifestyles", actionWF[str(cataction['44'])]])
            else:
                table.add_row(["    Society and Lifestyles", "Allow"])
            if '46' in cataction:
                table.add_row(["    Sports", actionWF[str(cataction['46'])]])
            else:
                table.add_row(["    Sports", "Allow"])
            if '47' in cataction:
                table.add_row(["    Travel", actionWF[str(cataction['47'])]])
            else:
                table.add_row(["    Travel", "Allow"])
            if '68' in cataction:
                table.add_row(["    Web Chat", actionWF[str(cataction['68'])]])
            else:
                table.add_row(["    Web Chat", "Allow"])
            if '23' in cataction:
                table.add_row(["    Web-based Email", actionWF[str(cataction['23'])]])
            else:
                table.add_row(["    Web-based Email", "Allow"])

            #General Interest - Business Section & all the subsections
            table.add_row(["General Interest - Business", ""])
            if '53' in cataction:
                table.add_row(["    Armed Forces", actionWF[str(cataction['53'])]])
            else:
                table.add_row(["    Armed Forces", "Allow"])
            if '49' in cataction:
                table.add_row(["    Business", actionWF[str(cataction['49'])]])
            else:
                table.add_row(["    Business", "Allow"])
            if '92' in cataction:
                table.add_row(["    Charitable Organizations", actionWF[str(cataction['92'])]])
            else:
                table.add_row(["    Charitable Organizations", "Allow"])
            if '31' in cataction:
                table.add_row(["    Finance and Banking", actionWF[str(cataction['31'])]])
            else:
                table.add_row(["    Finance and Banking", "Allow"])
            if '43' in cataction:
                table.add_row(["    General Organizations",actionWF[str(cataction['43'])]])
            else:
                table.add_row(["    General Organizations", "Allow"])
            if '51' in cataction:
                table.add_row(["    Government and Legal Organizations", actionWF[str(cataction['51'])]])
            else:
                table.add_row(["    Government and Legal Organizations", "Allow"])
            if '52' in cataction:
                table.add_row(["    Information Technology", actionWF[str(cataction['52'])]])
            else:
                table.add_row(["    Information Technology", "Allow"])
            if '50' in cataction:
                table.add_row(["    Information and Computer Security", actionWF[str(cataction['50'])]])
            else:
                table.add_row(["    Information and Computer Security", "Allow"])
            if '95' in cataction:
                table.add_row(["    Online Meetings", actionWF[str(cataction['95'])]])
            else:
                table.add_row(["    Online Meetings", "Allow"])
            if '93' in cataction:
                table.add_row(["    Remote Access", actionWF[str(cataction['93'])]])
            else:
                table.add_row(["    Remote Access", "Allow"])
            if '41' in cataction:
                table.add_row(["    Search Engines and Portals", actionWF[str(cataction['41'])]])
            else:
                table.add_row(["    Search Engines and Portals", "Allow"])
            if '81' in cataction:
                table.add_row(["    Secure Websites", actionWF[str(cataction['81'])]])
            else:
                table.add_row(["    Secure Websites", "Allow"])
            if '94' in cataction:
                table.add_row(["    Web Analytics", actionWF[str(cataction['94'])]])
            else:
                table.add_row(["    Web Analytics", "Allow"])
            if '56' in cataction:
                table.add_row(["    Web Hosting", actionWF[str(cataction['56'])]])
            else:
                table.add_row(["    Web Hosting", "Allow"])
            if '84' in cataction:
                table.add_row(["    Web-based Applications", actionWF[str(cataction['84'])]])
            else:
                table.add_row(["    Web-based Applications", "Allow"])

            #Unrated Section & all the subsections
            table.add_row(["Unrated", ""])
            if '1' in cataction:
                table.add_row(["    Unrated", actionWF[str(cataction['1'])]])
            else:
                table.add_row(["    Unrated", "Allow"])

            print('\n')
            ###Print to Console
            print(table)

            ###Print to File
            print(table, file = outputFILE)
            print('\n')


            ###CSV Format
            table.vertical_char = ','
            table.junction_char = ','
            #table.hortizontal_char = ''
            print(table, file = outputFILECSV)
        
            #Print Profile Report Cats
            #Local Cats
            #FortiGuard Cats
    
    ##Close Text & CSV file
    outputFILE.close()
    outputFILECSV.close()

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

    # Prompt for ADOM Name
    print('Please Enter ADOM name as seen in FortiManager:')
    ADOMname = input()
    #Check User put in data
    while not ADOMname:
        print('Error, Please Enter ADOM name as seen in FortiManager:')
        ADOMname = input()   
    ## End User Input Section ##

    ## Call fmg_login Function
    fmg_login(hostAPIUSER, hostPASSWD, hostIP)

    ## Call & pass ADOM name to our get_webfiltercat function to output Text & CSV of Web Profiles
    get_webfiltercat(ADOMname)

    ## Call fmg_logout Function
    fmg_logout(hostIP)

    ''' End main function/program '''

## Run the main function/program
if __name__ == '__main__':
    main()