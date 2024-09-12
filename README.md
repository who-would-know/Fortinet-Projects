# Fortinet-Projects
Fortinet API Example Code Repo

## FortiManager API Login Functions Example
### Date: 12-15-2020
Code Filename: FortiManager/fmg_api_login.py  
Summary: Basic functions to Login & Logoff in FortiManager  

## FortiManager API Import Policy from Device Example
### Date: 12-16-2020
Code Filename: FortiManager/fmg_policy_import.py  
Summary: Imports in Policy package of Device/VDOM into an ADOM  

## FortiManager API Proxy commands to FortiGate - Threat Feed Example
### Date: 12-16-2020
Code Filename: FortiManager/fmg_proxy_to_Threat-Feed-pull.py  
Summary: If features are not available on FortiManager, in this example Threat Feed  
         then you can Proxy FortiGate API calls via FortiManager without having to setup  
         and go directly to the FortiGate. This is also useful for install CERTS for SSL Inspection  
         which exist locally on the FortiGate Device.  

## FortiManager Pull Web Filter Profiles per ADOM and List Local & FortiGuard Categories with their Actions Example
### Date: 12-26-2020
Code Filename: fmg_webprofile_cat_list-report.py  
Summary: Customers or Security Engineers might need to display and send (via Text,CSV) FortiManager ADOM(customer) 
         Web Filter Profile Local & FortiGuard Categories with their Actions - Block, Monitor, Warning, Allow, Authenication, etc.
         This example shows how to pull all Web Profiles in a ADOM, pull Local & FortiGuard Category Name+ID+Action, then
         display them via Terminal, Text & CSV files.	 

## FortiManager With FortiGate Device Name, returns VDOM to ADOM mappings
### Date: 09-12-2024
Code Filename: FMG_GET_ADOM-to-VDOM_Mapping.py  
Summary: If you have a FortiGate with VDOMs and they are in different ADOMs, you might need to pull all the ADOM:VDOM mappings for example, 
         you upgraded a FortiGate with VDOMs and now need to upgrade their ADOMs, you can run this to grab that list and then upgrade those ADOMs.  
