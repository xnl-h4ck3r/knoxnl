#!/usr/bin/env python
# Python 3
# A wrapper around the amazing KNOXSS API (https://knoxss.me/?page_id=2729) by Brute Logic (@brutelogic)
# Inspired by "knoxssme" by @edoardottt2
# Full help here: https://github.com/xnl-h4ck3r/knoxnl#readme
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

import requests
import argparse
from signal import SIGINT, signal
import multiprocessing.dummy as mp
import multiprocessing
import time
from termcolor import colored
import yaml
import json
import os
import sys
from pathlib import Path
try:
    from . import __version__
except:
    pass
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry
import re

# Global variables
stopProgram = False
latestApiCalls = "Unknown"
urlPassed = True
rateLimitExceeded = False
needToStop = False
dontDisplay = False
successCount = 0
outFile = None
fileIsOpen = False
todoFileName = ''
currentCount = {}
configPath = ''
inputValues = set()
blockedDomains = set()
HTTP_ADAPTER = None

DEFAULT_API_URL = 'https://api.knoxss.pro'

# The default timeout for KNOXSS API to respond in seconds
DEFAULT_TIMEOUT = 180

# Yaml config values
API_URL = ''
API_KEY = ''
DISCORD_WEBHOOK = ''

# Object for an KNOXSS API response
class knoxss:
    Code = ''
    XSS = ''
    PoC = ''
    Calls = ''
    Error = ''
    POSTData = ''

def showVersion():
    try:
        
        try:
            resp = requests.get('https://raw.githubusercontent.com/xnl-h4ck3r/knoxnl/main/knoxnl/__init__.py',timeout=3)
        except:
            print('Current knoxnl version '+__version__+' (unable to check if latest)')
        if __version__ == resp.text.split('=')[1].replace('"',''):
            print('Current knoxnl version '+__version__+' ('+colored('latest','green')+')\n')
        else:
            print('Current knoxnl version '+__version__+' ('+colored('outdated','red')+')\n')
    except:
        pass
    
def showBanner():
    print()
    print(" _           "+colored("_ ___    ","red")+colored("__","yellow")+colored("      _","cyan"))
    print("| | ___ __   "+colored("V","red")+"_"+colored(r"V\ \  ","red")+colored("/ /","yellow")+colored("_ __","green")+colored(" | | ","cyan"))
    print(r"| |/ / '_ \ / _ \ "[:-1]+colored(r"\ \ "[:-1],"red")+colored("/ /","yellow")+colored(r"| '_ \ "[:-1],"green")+colored("| | ","cyan"))
    print("|   <| | | | (_) "+colored("/ /","red")+colored(r"\ \ "[:-1],"yellow")+colored("| | | |","green")+colored(" | ","cyan"))
    print(r"|_|\_\_| |_|\___"+colored("/_/  ","red")+colored(r"\_\ "[:-1],"yellow")+colored("_| |_|","green")+colored("_| ","cyan"))
    print(colored("                 by @Xnl-h4ck3r ","magenta"))
    print()
    showVersion()

# Functions used when printing messages dependant on verbose options
def verbose():
    return args.verbose

def showBlocked():
    global blockedDomains
    try:
        # If there were any domains that might be blocking KNOXSS, let the user know
        if len(blockedDomains) > 0:
            print(colored('The following domains seem to be blocking KNOXSS and might be worth excluding for now:','yellow'),colored(', '.join(blockedDomains),'white'))
    except:
        pass
    
# Handle the user pressing Ctrl-C and programatic interupts
def handler(signal_received, frame):
    """
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    """
    global stopProgram, needToStop, inputValues, blockedDomains, todoFileName
    stopProgram = True
    if not needToStop:
        print(colored('\n>>> "Oh my God, they killed Kenny... and knoXnl!" - Kyle','red'))
        # If there are any input values not checked, write them to a .todo file
        try:
            if len(inputValues) > 0:
                try:
                    print(colored('\n>>> Just trying to save outstanding input to .todo file before ending...','yellow'))
                    with open(todoFileName, 'w') as file:
                        for inp in inputValues:
                            file.write(inp+'\n')
                    print(colored('All unchecked URLs have been written to','cyan'),colored(todoFileName+'\n', 'white'))
                except Exception as e:
                    print(colored('Error saving file ','cyan'),colored(todoFileName+'\n', 'white'),colored(':'+str(e),'red'))
        except:
            pass
        
        # If there were any domains that might be blocking KNOXSS, let the user know
        showBlocked()
        
        # Try to close the output file before ending
        try:
            outFile.close()
        except:
            pass
        quit()
            
# Show the chosen options and config settings
def showOptions():

    global urlPassed, fileIsOpen, API_URL
            
    try:
        print(colored('Selected config and settings:', 'cyan'))
        
        print(colored('Config file path:', 'magenta'), configPath)
        print(colored('KNOXSS API Url:', 'magenta'), API_URL)
        print(colored('KNOXSS API Key:', 'magenta'), API_KEY)    
        print(colored('Discord Webhook:', 'magenta'), DISCORD_WEBHOOK)   
        
        if args.burp_piper:
            print(colored('-i: ' + args.input, 'magenta'), 'Request passed from Burp Piper Extension')
        else:
            if urlPassed:
                print(colored('-i: ' + args.input, 'magenta'), 'The URL to check with KNOXSS API.')
            else:
                print(colored('-i: ' + args.input + ' (FILE)', 'magenta'), 'All URLs will be passed to KNOXSS API.')

        if fileIsOpen:
            print(colored('-o: ' + args.output, 'magenta'), 'The output file where successful XSS payloads will be saved.')
            print(colored('-ow: ' + str(args.output_overwrite), 'magenta'), 'Whether the output will be overwritten if it already exists.')
            print(colored('-oa: ' + str(args.output_all), 'magenta'), 'Whether the output all results to the output file, not just successful one\'s.')
        
        if not urlPassed:
            print(colored('-p: ' + str(args.processes), 'magenta'), 'The number of parallel requests made.')
        
        print(colored('-X: ' + args.http_method, 'magenta'), 'The HTTP method checked by KNOXSS API.')
        
        if args.http_method in ('POST','BOTH'):
            if args.post_data != '':
                print(colored('-pd: ' + args.post_data, 'magenta'), 'Data passed with a POST request.')
            else:
                if urlPassed:
                    try:
                        postData = args.input.split('?')[1]
                    except:
                        postData = ''
                    print(colored('-pd: ' + postData, 'magenta'), 'Data passed with a POST request.')
                else:
                    print(colored('-pd: {the URL query string}', 'magenta'), 'Data passed with a POST request.')
            
        if args.headers != '':
            print(colored('-H: ' + args.headers, 'magenta'), 'HTTP Headers passed with requests.')
            
        print(colored('-afb: ' + str(args.advanced_filter_bypass), 'magenta'), 'Whether the Advanced Filter Bypass option is passed to KNOXSS API.')
        print(colored('-t: ' + str(args.timeout), 'magenta'), 'The number of seconds to wait for KNOXSS API to respond.')
        print()

    except Exception as e:
        print(colored('ERROR showOptions: ' + str(e), 'red'))

# If an API key wasn't supplied, or was invalid, then point the user to https://knoxss.me
def needApiKey():
    # If the console can't display 🤘 then an error will be raised to try without
    try:
        print(colored('Haven\'t got an API key? Why not head over to https://knoxss.me and subscribe?\nDon\'t forget to generate and SAVE your API key before using it here! 🤘\n', 'green')) 
    except:
        print(colored('Haven\'t got an API key? Why not head over to https://knoxss.me and subscribe?\nDon\'t forget to generate and SAVE your API key before using it here!\n', 'green')) 
              
def getConfig():
    # Try to get the values from the config file, otherwise use the defaults
    global API_URL, API_KEY, DISCORD_WEBHOOK, configPath, HTTP_ADAPTER
    try:
        
        # Put config in global location based on the OS.
        configPath = (
            Path(os.path.join(os.getenv('APPDATA', ''), 'knoxnl')) if os.name == 'nt'
            else Path(os.path.join(os.path.expanduser("~"), ".config", "knoxnl")) if os.name == 'posix'
            else Path(os.path.join(os.path.expanduser("~"), "Library", "Application Support", "knoxnl")) if os.name == 'darwin'
            else None
        )

        # Set up an HTTPAdaptor for retry strategy when making requests
        try:
            retry= Retry(
                total=2,
                backoff_factor=0.1,
                status_forcelist=[429, 500, 502, 503, 504],
                raise_on_status=False,
                respect_retry_after_header=False
            )
            HTTP_ADAPTER = HTTPAdapter(max_retries=retry)
        except Exception as e:
            print(colored('ERROR getConfig 2: ' + str(e), 'red'))
        
        configPath.absolute
        if configPath == '':
            configPath = 'config.yml'
        else:
            configPath = Path(configPath / 'config.yml')
        config = yaml.safe_load(open(configPath))
        try:
            API_URL = config.get('API_URL')
        except Exception as e:
            print(colored('Unable to read "API_URL" from config.yml; defaults set', 'red'))
            API_KEY = DEFAULT_API_URL
        try:
            API_KEY = config.get('API_KEY')
            if args.api_key != '':
                API_KEY = args.api_key
                print(colored('NOTE: Overriding "API_KEY" from config.yml with passed API Key', 'cyan'), API_KEY + '\n')
            else:
                if API_KEY is None or API_KEY == 'YOUR_API_KEY':
                    print(colored('ERROR: You need to add your "API_KEY" to config.yml or pass it with the -A option.', 'red'))
                    needApiKey()
                    quit()
        except Exception as e:
            print(colored('Unable to read "API_KEY" from config.yml; We need an API key! - ' + str(e), 'red'))
            needApiKey()
            quit()
        
        # Set the Discord webhook. If passed with argument -dw / --discord-webhook then this will override the config value
        if args.discord_webhook != '':
            DISCORD_WEBHOOK = args.discord_webhook
        else:
            try:
                DISCORD_WEBHOOK = config.get('DISCORD_WEBHOOK').replace('YOUR_WEBHOOK','')
            except Exception as e:
                DISCORD_WEBHOOK = ''
        
    except Exception as e:
        try:
            if args.api_key == '':
                print(colored('Unable to read config.yml and API Key not passed with -A; Unable to use KNOXSS API! - ' + str(e), 'red'))
                needApiKey()
                quit()
            else:
                API_URL = DEFAULT_API_URL
                API_KEY = args.api_key
                print(colored('Unable to read config.yml; using default API URL and passed API Key', 'cyan'))
            DISCORD_WEBHOOK = args.discord_webhook    
        except Exception as e:
            print(colored('ERROR getConfig 1: ' + str(e), 'red'))
            
# Call the KNOXSS API
def knoxssApi(targetUrl, headers, method, knoxssResponse):
    global latestApiCalls, rateLimitExceeded, needToStop, dontDisplay, HTTP_ADAPTER, inputValues
    try:
        apiHeaders = {'X-API-KEY' : API_KEY, 
                     'Content-Type' : 'application/x-www-form-urlencoded',
                     'User-Agent' : 'knoXnl tool by @xnl-h4ck3r'
                     }
        
        # Replace any & in the URL with encoded value so we can add other data using &
        targetData = targetUrl.replace('&', '%26')
    
        # If processing a POST
        if method == 'POST' and args.http_method in ('POST','BOTH'):
            postData = ''
            
            # If the --post-data argument was passed, use those values
            if args.post_data != '':
                postData = args.post_data.replace('&', '%26')
                # If the target has query string parameters, remove them
                if '?' in targetUrl:
                    targetData = targetData.split('?')[0]
                    
            else: # post-data not passed
                # If the target has parameters, i.e. ? then replace it with &post=, otherwise add &post= to the end
                if '?' in targetUrl:
                    postData = targetData.split('?')[1]
                    targetData = targetData.split('?')[0]
    
        data = 'target=' + targetData
        
        # Add the post data if necessary
        if method == 'POST':
            data = data + '&post=' + postData

        # Add the Advanced Filter Bypass option if required
        if args.advanced_filter_bypass:
            data = data + '&afb=1'

        # Add Headers if required
        if headers != '':
            # Headers must be in format header1:value%0D%0Aheader2:value
            encHeaders = headers.replace(' ','%20')
            encHeaders = encHeaders.replace('|','%0D%0A')
            data = data + '&auth=' + encHeaders

        # Make a request to the KNOXSS API
        try:
            tryAgain = True
            while tryAgain:
                tryAgain = False
                try:
                    session = requests.Session()
                    session.mount('https://', HTTP_ADAPTER)
                    resp = session.post(
                        url=API_URL,
                        headers=apiHeaders,
                        data=data.encode('utf-8'),
                        timeout=args.timeout
                    )
                    fullResponse = resp.text.strip()
                except Exception as e:
                    if 'failure in name resolution' in str(e).lower():
                        needToStop = True
                        knoxssResponse.Error = 'It appears the internet connection was lost. Please try again later.'
                    elif 'failed to establish a new connection' in str(e).lower():
                        needToStop = True
                        knoxssResponse.Error = 'Failing to establish a new connection to KNOXSS. This can happen if there is an issue with the KNOXSS API or can happen if your machine is running low on memory.'
                    elif 'remote end closed connection' in str(e).lower() or 'connection aborted' in str(e).lower():
                        knoxssResponse.Error = 'The target dropped the connection.'
                        # Remove the URL from the input set
                        inputValues.discard(targetUrl)
                        return
                    else:
                        knoxssResponse.Error = str(e)
                        # remove the URL from the input set
                        inputValues.discard(targetUrl)
                        return
                
                if not needToStop:
                    
                    # Display the data sent to API and the response
                    if verbose():
                        print('KNOXSS API request:')
                        print('     Data: ' + data)
                        print('KNOXSS API response:')
                        print(fullResponse)
                        
                    knoxssResponse.Code = str(resp.status_code)
                    
                    # Try to get the JSON response
                    try:
                        jsonResponse = json.loads(fullResponse)
                        if jsonResponse == '':
                            knoxssResponse.Error = fullResponse
                            
                        # If the error has "try again", and we haven't already tried before, set to True to try one more time
                        if 'expiration time reset' in fullResponse.lower():
                            if tryAgain:
                                tryAgain = False
                            else:
                                tryAgain = True
                        else:        
                            knoxssResponse.XSS = str(jsonResponse['XSS'])
                            knoxssResponse.PoC = str(jsonResponse['PoC'])
                            knoxssResponse.Calls = str(jsonResponse['API Call'])
                            if knoxssResponse.Calls == '0':
                                knoxssResponse.Calls = 'Unknown'
                            knoxssResponse.Error = str(jsonResponse['Error'])
                            
                            # If service unavailable flag to stop
                            if knoxssResponse.Error == 'service unavailable':
                                needToStop = True
                            # If the API rate limit is exceeded, flag to stop
                            elif knoxssResponse.Error == 'API rate limit exceeded.':
                                rateLimitExceeded = True
                                needToStop = True
                                knoxssResponse.Calls = 'API rate limit exceeded!'
                            else: # remove the URL from the int input set
                                inputValues.discard(targetUrl)
                                # If the target timed out, add it back to the end of the input values because it could be tried again
                                if 'Read timed out' in knoxssResponse.Error: 
                                    inputValues.add(targetUrl)
                                
                            knoxssResponse.POSTData = str(jsonResponse['POST Data'])
                        
                    except Exception as e:
                        knoxssResponse.Calls = 'Unknown'
                        if fullResponse is None:
                            fullResponse = ''

                        # The response probably wasn't JSON, so check the response message
                        if fullResponse.lower() == 'incorrect apy key.' or fullResponse.lower() == 'invalid or expired api key.':
                            print(colored('The provided API Key is invalid! Check if your subscription is still active, or if you forgot to save your current API key.', 'red'))
                            needToStop = True
                            dontDisplay = True
                            
                        elif fullResponse.lower() == 'no api key provided.':
                            print(colored('No API Key was provided! Check config.yml', 'red'))
                            needToStop = True
                            dontDisplay = True

                        elif 'hosting server read timeout' in fullResponse.lower():
                            knoxssResponse.Error = 'Hosting Server Read Timeout'
                        
                        elif 'type of target page can\'t lead to xss' in fullResponse.lower(): 
                            knoxssResponse.Error = 'XSS is not possible with the requested URL'
                            inputValues.discard(targetUrl)
                        else:
                            print(colored('Something went wrong: '+str(e),'red'))
                            # remove the URL from the int input set
                            inputValues.discard(targetUrl)
                                
                    if knoxssResponse.Calls != 'Unknown':
                        latestApiCalls = knoxssResponse.Calls
                        
        except Exception as e:
            knoxssResponse.Error = 'FAIL'
            print(colored(':( There was a problem calling KNOXSS API: ' + str(e), 'red'))
            
    except Exception as e:
        print(colored('ERROR knoxss 1:  ' + str(e), 'red'))

def processInput():
    global urlPassed, latestApiCalls, stopProgram, inputValues, todoFileName
    try:
        latestApiCalls = 'Unknown'

        # if the Burp Piper Extension argument was passed, assume the input is passed by stdin 
        if args.burp_piper:
            try:
                # Get URL and 
                firstLine = sys.stdin.readline()
                # Get HOST header
                secondLine = sys.stdin.readline()
                args.input = 'https://'+secondLine.split(' ')[1].strip()+firstLine.split(' ')[1].strip()
                # Get first header after HOST
                headers = ''
                header = sys.stdin.readline()
                # Get all headers
                while header.strip() != '':
                    if header.lower().find('cookie') >= 0 or header.lower().find('api') >= 0 or header.lower().find('auth') >= 0:
                        headers = headers + header.strip()+'|'
                    header = sys.stdin.readline()
                args.headers = headers.rstrip('|')
                # Get the POST body
                postBody = ''
                postBodyLine = sys.stdin.readline()
                while postBodyLine.strip() != '':
                    postBody = postBody + postBodyLine.strip()
                    postBodyLine = sys.stdin.readline()
                postBody = postBody.replace('&', '%26')
                args.post_data = postBody
                
            except Exception as e:
                print(colored('ERROR: Burp Piper Extension input expected: ' + str(e), 'red'))
                exit()
        else:
            # Check that the -i argument was passed
            if not args.input:
                print(colored('ERROR: The -i / --input argument must be passed (unless calling from Burp Piper extension with -bp / --burp-piper). The input can be a single URL or a file or URLs.', 'red'))
                exit()
            
            # Set .todo file name in case we need later
            # If the existing filename already has ".YYYYMMDD_HHMMSS.todo" at the end, then remove it before creating the new name
            originalFileName = args.input
            pattern = r'\.\d{8}_\d{6}\.todo$'
            if re.search(pattern, originalFileName):
                originalFileName = re.sub(pattern, '', originalFileName)
            todoFileName = originalFileName+'.'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.todo'
                     
            # If the -i (--input) can be a standard file (text file with URLs per line),
            # if the value passed is not a valid file, then assume it is an individual URL
            urlPassed = False
            try:
                inputFile = open(args.input, 'r')
                firstLine = inputFile.readline()
            except IOError:
                urlPassed = True
            except Exception as e:
                print(colored('ERROR processInput 2: ' + str(e), 'red'))
        
        if verbose():
            showOptions()
        
        inputArg = args.input
        if urlPassed:
            print(colored('Calling KNOXSS API...\n', 'cyan'))
            # Check if input has scheme. If not, then add https://
            if '://' not in inputArg:
                print(colored('WARNING: Input "'+inputArg+'" should include a scheme. Using https by default...', 'yellow'))
                inputArg = 'https://'+inputArg
            processUrl(inputArg)
        else: # It's a file of URLs
            try:
                # Open file and put all values in input set
                with open(inputArg, 'r') as inputFile:
                    lines = inputFile.readlines()          
                for line in lines:
                    if line.strip() != '':
                        inputValues.add(line.strip())

                print(colored('Calling KNOXSS API for '+str(len(inputValues))+' targets...\n', 'cyan'))
                if not stopProgram:
                    p = mp.Pool(args.processes)
                    p.map(processUrl, inputValues)
                    p.close()
                    p.join()

            except Exception as e:
                print(colored('ERROR processInput 3: ' + str(e), 'red'))
                
    except Exception as e:
        print(colored('ERROR processInput 1: ' + str(e), 'red'))

def process_batch(urls):
    with multiprocessing.Pool(processes=args.processes) as pool:
        pool.map(processUrl, urls)

def discordNotify(target,poc):
    global DISCORD_WEBHOOK
    try:
        embed = {
            "description": "```\n"+poc+"\n```",
            "title": "KNOXSS POC for "+target
        }
        data = {
            "content": "XSS found by knoxnl! 🤘",
            "username": "knoxnl",
            "embeds": [embed],
        }
        try:
            result = requests.post(DISCORD_WEBHOOK, json=data)
            if 300 <= result.status_code < 200:
                print(colored('WARNING: Failed to send notification to Discord - ' + result.json(), 'yellow'))
        except Exception as e:
            print(colored('WARNING: Failed to send notification to Discord - ' + str(e), 'yellow'))
    except Exception as e:
        print(colored('ERROR discordNotify 1: ' + str(e), 'red'))
        
def processOutput(target, method, knoxssResponse):
    global latestApiCalls, successCount, outFile, currentCount, rateLimitExceeded, urlPassed, needToStop, dontDisplay, blockedDomains
    try:
        if knoxssResponse.Error != 'FAIL':
                
            if knoxssResponse.Error != 'none':
                if not args.success_only:
                    knoxssResponseError = knoxssResponse.Error
                    # If there is a 403, it maybe because the users IP is blocked on the KNOXSS firewall
                    if knoxssResponse.Code == "403":
                       knoxssResponseError = '403 Forbidden - Check http://knoxss.me manually and if you are blocked, contact Twitter/X @KN0X55 or brutelogic@null.net'
                    # If there is "InvalidChunkLength" in the error returned, it means the KNOXSS API returned an empty response
                    if 'InvalidChunkLength' in knoxssResponseError:
                        knoxssResponseError = 'The API Timed Out'
                    # If there is "Read timed out" in the error returned, it means the target website itself timed out
                    if 'Read timed out' in knoxssResponseError:
                        knoxssResponseError = 'The target website timed out'  
                    # If the error has "can\'t test it (forbidden)" it means the target is blocking KNOXSS IP address
                    if 'can\'t test it (forbidden)' in knoxssResponseError:
                        knoxssResponseError = 'Target is blocking KNOXSS IP'
                        try:
                            domain = target.split('://')[1].split('#')[0].split('?')[0].split('/')[0]
                            blockedDomains.add(domain)
                        except:
                            pass
                        
                    # If service is unavailable then we need to stop
                    if knoxssResponseError == 'service unavailable':
                        needToStop = True
                        print(colored('The KNOXSS service is currently unavailable. Please try again later.', 'red'))
                        return
                    
                    # If method is POST, remove the query string from the target and show the post data in [ ] 
                    if method == 'POST':
                        try:
                            querystring = target.split('?')[1]
                        except:
                            querystring = ''
                        target = target.split('?')[0]
                        if args.post_data:
                            target = target + ' ['+args.post_data+']'
                        else:
                            if querystring != '':
                                target = target + ' [' + querystring + ']'                            
                    
                    if not dontDisplay:        
                        xssText = '[ ERR! ] - (' + method + ')  ' + target + '  KNOXSS ERR: ' + knoxssResponseError
                        if urlPassed or rateLimitExceeded:
                            print(colored(xssText, 'red'))
                        else:
                            print(colored(xssText, 'red'), colored('['+latestApiCalls+']','white'))
                        if args.output_all and fileIsOpen:
                            outFile.write(xssText + '\n')
            else:
                if knoxssResponse.XSS == 'true':
                    xssText = '[ XSS! ] - (' + method + ')  ' + knoxssResponse.PoC
                    if urlPassed:
                        print(colored(xssText, 'green'))
                    else:
                        print(colored(xssText, 'green'), colored('['+latestApiCalls+']','white'))
                    successCount = successCount + 1
                    # Send a notification to discord if a webook was provided
                    if DISCORD_WEBHOOK != '':
                        discordNotify(target,knoxssResponse.PoC)
                    # Write the successful XSS details to file
                    if fileIsOpen:
                        outFile.write(xssText + '\n')
                else:
                    if not args.success_only:
                        xssText = '[ SAFE ] - (' + method + ')  ' + target
                        if urlPassed:
                            print(colored(xssText, 'yellow'))
                        else:
                            print(colored(xssText, 'yellow'), colored('['+latestApiCalls+']','white'))
                        if args.output_all and fileIsOpen:
                            outFile.write(xssText + '\n')
                
                # Determine whether to wait for a minute
                try:
                    currentMinute=str(datetime.now().hour)+':'+str(datetime.now().minute)
                    if currentMinute in currentCount.keys():
                        currentCount[currentMinute] += 1
                    else:
                        currentCount = {currentMinute : 1}
                    # If the current count is > 3 then wait a minute
                    if currentCount[currentMinute] > args.processes:
                        time.sleep(60)
                except Exception as e:
                    print(colored('ERROR showOutput 2:  ' + str(e), 'red'))    
                    
    except Exception as e:
        print(colored('ERROR showOutput 1: ' + str(e), 'red'))

# Process one URL        
def processUrl(target):
    
    global stopProgram, latestApiCalls, urlPassed, needToStop
    try:
        if not stopProgram and not needToStop:
            target = target.strip()
            # Check if target has scheme. If not, then add https://
            if '://' not in target:
                print(colored('WARNING: Input "'+target+'" should include a scheme. Using https by default...', 'yellow'))
                target = 'https://'+target
                
            headers = args.headers.strip()
            knoxssResponse=knoxss()        

            if args.http_method in ('GET','BOTH'): 
                method = 'GET'
                knoxssApi(target, headers, method, knoxssResponse)
                processOutput(target, method, knoxssResponse)
        
            if args.http_method in ('POST','BOTH'): 
                method = 'POST'
                knoxssApi(target, headers, method, knoxssResponse)
                processOutput(target, method, knoxssResponse)

    except Exception as e:
        print(colored('ERROR processUrl 1: ' + str(e), 'red'))   

# Validate the -p argument 
def processes_type(x):
    x = int(x) 
    if x < 1 or x > 5:
        raise argparse.ArgumentTypeError('The number of processes must be between 1 and 5')     
    return x
                                
# Run knoXnl
def main():
    global args, latestApiCalls, urlPassed, successCount, fileIsOpen, outFile, needToStop, todoFileName, blockedDomains
    
    # Tell Python to run the handler() function when SIGINT is received
    signal(SIGINT, handler)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='knoXnl - by @Xnl-h4ck3r: A wrapper around the KNOXSS API by Brute Logic (requires an API key)'    
    )
    parser.add_argument(
        '-i',
        '--input',
        action='store',
        help='Input to send to KNOXSS API: a single URL, or file of URLs.',
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        help='The file to save the successful XSS and payloads to. If the file already exist it will just be appended to unless option -ow is passed.',
        default='',
    )
    parser.add_argument(
        '-ow',
        '--output-overwrite',
        action='store_true',
        help='If the output file already exists, it will be overwritten instead of being appended to.',
    )
    parser.add_argument(
        '-oa',
        '--output-all',
        action='store_true',
        help='Output all results to file, not just successful one\'s.',
    )
    parser.add_argument(
        '-X',
        '--http-method',
        action='store',
        help='Which HTTP method to use, values GET, POST or BOTH (default: GET). If BOTH is chosen, then a GET call will be made, followed by a POST.',
        default='GET',
        choices=['GET','POST','BOTH']
    )
    parser.add_argument(
        '-pd',
        '--post-data',
        help='If a POST request is made, this is the POST data passed. It must be in the format \'param1=value&param2=value&param3=value\'. If this isn\'t passed and query string parameters are used, then these will be used as POST data if POST Method is requested.',
        action='store',
        default='',
    )
    parser.add_argument(
        '-H',
        '--headers',
        help='Add custom headers to pass with HTTP requests. Pass in the format \'Header1:value1|Header2:value2\' (e.g. separate different headers with a pipe | character).',
        action='store',
        default='',
    )
    parser.add_argument(
        '-A',
        '--api-key',
        help='The KNOXSS API Key to use. This will be used instead of the value in config.yml',
        action='store',
        default='',
    )
    parser.add_argument(
        '-afb',
        '--advanced-filter-bypass',
        action='store_true',
        help='If the advanced filter bypass should be used on the KNOXSS API.',
    )
    parser.add_argument(
        '-s',
        '--success-only',
        action='store_true',
        help='Only show successful XSS payloads in the CLI output.',
    )
    parser.add_argument(
        '-p',
        '--processes',
        help='Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes (threads) used (default: 3)',
        action='store',
        type=processes_type,
        default=3,
        metavar="<integer>",
    )
    parser.add_argument(
        '-t',
        '--timeout',
        help='How many seconds to wait for the KNOXSS API to respond before giving up (default: '+str(DEFAULT_TIMEOUT)+' seconds)',
        default=DEFAULT_TIMEOUT,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        '-bp',
        '--burp-piper',
        action='store_true',
        help='Set if called from the Burp Piper extension.',
    )
    parser.add_argument(
        '-dw',
        '--discord-webhook',
        help='The Discord Webhook to send successful XSS notifications to. This will be used instead of the value in config.yml',
        action='store',
        default='',
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    parser.add_argument('--version', action='store_true', help="Show version number")
    args = parser.parse_args()

    # If --version was passed, display version and exit
    if args.version:
        print(colored('knoxnl - v' + __version__,'cyan'))
        sys.exit()
        
    # If no input was given, raise an error
    if sys.stdin.isatty():
        if args.input is None:
            print(colored('You need to provide an input with -i argument or through <stdin>.', 'red'))
            sys.exit()
            
    showBanner()

    # Get the config settings from the config.yml file
    getConfig()

    # If -o (--output) argument was passed then open the output file
    if args.output != "":
        try:
            # If argument -ow was passed and the file exists, overwrite it, otherwise append to it
            if args.output_overwrite:
                outFile = open(os.path.expanduser(args.output), "w")
            else:
                outFile = open(os.path.expanduser(args.output), "a")
            fileIsOpen = True
        except Exception as e:
            print(colored('WARNING: Output won\'t be saved to file - ' + str(e) + '\n', 'red'))
                                
    try:

        processInput()
        
        # Show the user the latest API quota       
        if latestApiCalls is None:
            latestApiCalls = 'Unknown'
        print(colored('\nAPI calls made so far today - ' + latestApiCalls + '\n', 'cyan'))
           
        # If a file was passed, there is a reason to stop, write the .todo file and let the user know about it
        if needToStop and not urlPassed and not args.burp_piper:
            try:
                with open(todoFileName, 'w') as file:
                    for inp in inputValues:
                        file.write(inp+'\n')
                print(colored('Had to stop due to errors. All unchecked URLs have been written to','cyan'),colored(todoFileName+'\n', 'white'))
            except Exception as e:
                print(colored('Was unable to write .todo file: '+str(e),'red'))
        
        showBlocked()
            
        # Report if any successful XSS was found this time
        # If the console can't display 🤘 then an error will be raised to try without
        try:
            if successCount > 0:
                print(colored('🤘 '+str(successCount)+' successful XSS found! 🤘\n','green'))
            else:
                print(colored('No successful XSS found... better luck next time! 🤘\n','cyan'))
        except:
            if successCount > 0:
                print(colored(str(successCount)+' successful XSS found!\n','green'))
            else:
                print(colored('No successful XSS found... better luck next time!\n','cyan'))
                
        # If the output was sent to a file, close the file
        if fileIsOpen:
            try:
                outFile.close()
            except Exception as e:
                print(colored("ERROR: Unable to close output file: " + str(e), "red"))
        
    except Exception as e:
        print(colored('ERROR main 1: ' + str(e), 'red'))
        
if __name__ == '__main__':
    main()
