#!/usr/bin/python3

#This is a Git Merge Test LIne. Thanks!

import os
import sys
import socket
import json
import requests
import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getCreds():
    bigip = input('BIG-IP Management IP address:')
    bigipUser = input('Username:')
    bigipPassword = getpass.getpass('BIG-IP Password:')
    return [bigip, bigipUser, bigipPassword]

def getToken(bigip, bigipUser, bigipPassword):
    tokenHeaders = {'Content-type': 'application/json'}
    authUrl = 'https://' + bigip + '/mgmt/shared/authn/login'
    tokenData = '{"username": "' + bigipUser + '", "password": "' + bigipPassword + '","loginProviderName": "tmos"}'
    tokenResponse = requests.post(authUrl, data=tokenData, headers=tokenHeaders, verify=False)
    tokenText = tokenResponse.text
    tokenStatusCode = tokenResponse.status_code
    if tokenStatusCode == 200: 
        tokenJson = json.loads(tokenText)
        tokenDetail = tokenJson['token']
        tokenValue = ''
        for key, value in tokenDetail.items():
            if key == 'token':
                tokenValue = value
        return tokenValue
    else:
        print(f'HTTP Response Code {str(tokenStatusCode)} getting Auth Token - exiting Script')
        sys.exit()

def getPools(bigip, authToken):
    authHeader = {'X-F5-Auth-Token': authToken}
    response = requests.get('https://' + bigip + '/mgmt/tm/ltm/pool', headers=authHeader, verify=False).text
    pool_list = json.loads(response)
    pool_details = pool_list["items"]
    print(f'Pool list for {bigip} Common Partition:')
    for objList in pool_details:
        for key, value in objList.items():
            if key == 'name':
                print(f'{key} : {value}')

def isOpen(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
                s.connect((ip, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()

def main():
    os.system('clear')
    userCreds = getCreds()
    bigip = userCreds[0]
    bigipUser = userCreds[1]
    bigipPassword = userCreds[2]
    connectAttempt = isOpen(bigip, '443')
    if connectAttempt:
        userToken = getToken(bigip, bigipUser, bigipPassword)
        getPools(bigip,userToken)
    else:
         print(f'Could not connect to {bigip} on port 443. Please verify the IP address and device availability.')

if __name__ == "__main__":
   main()
