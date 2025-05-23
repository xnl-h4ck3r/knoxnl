#!/usr/bin/env python
# Python 3
# A wrapper around the amazing KNOXSS API (https://knoxss.pro/?page_id=2729) by Brute Logic (@brutelogic)
# Inspired by "knoxssme" by @edoardottt2
# Full help here: https://github.com/xnl-h4ck3r/knoxnl#readme
# Good luck and good hunting! If you really love the tool (or any others), or they helped you find an awesome bounty, consider BUYING ME A COFFEE! (https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

import requests
import argparse
from signal import SIGINT, signal
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
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter, Retry
import re
import time
from urllib.parse import urlparse
from dateutil import tz
import subprocess
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import queue
import threading
import random

# Global variables
stopProgram = False
latestApiCalls = "Unknown"
urlPassed = True
rateLimitExceeded = False
needToStop = False
needToRetry = False
dontDisplay = False
successCountXSS = 0
successCountOR = 0
safeCount = 0
errorCount = 0
requestCount = 0
skipCount = 0
outFile = None
fileIsOpen = False
debugOutFile = None
debugFileIsOpen = False
todoFileName = ''
currentCount = {}
configPath = ''
inputValues = set()
blockedDomains = {}
HTTP_ADAPTER = None
HTTP_ADAPTER_DISCORD = None
retryAttempt = 0
apiResetPath = ''
timeAPIReset = None
forbiddenResponseCount = 0
latestVersion = ''
runtimeLog = ""

pauseEvent = Event()

DEFAULT_API_URL = 'https://api.knoxss.pro'
API_KEY_SECRET = "aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ=="

# The default timeout for KNOXSS API to respond in seconds
DEFAULT_TIMEOUT = 1200 # 20 minutes
DEFAULT_STALL_TIMEOUT = 300 # 5 minutes

# The default number of times to retry when having issues connecting to the KNOXSS API 
DEFAULT_RETRIES = 3

# The default number of seconds to wait when having issues connecting to the KNOXSS API before retrying
DEFAULT_RETRY_INTERVAL = 30

# The default backoff factor to use when retrying after having issues connecting to the KNOXSS API
DEFAULT_RETRY_BACKOFF_FACTOR = 1.5

# Yaml config values
API_URL = ''
API_KEY = ''
DISCORD_WEBHOOK = ''
DISCORD_WEBHOOK_COMPLETE = ''

# Object for an KNOXSS API response
class knoxss:
    Code = ''
    XSS = ''
    Redir = ''
    PoC = ''
    Calls = ''
    Error = ''
    POSTData = ''
    Timestamp = ''

# Shared map for readable IDs
thread_id_map = {}
thread_id_lock = threading.Lock()
thread_id_counter = [0]  # list so it's mutable in closure

# Use this to reset the number of retries every 24 hours
lastRetryResetTime = datetime.now()

def showVersion():
    global latestVersion
    try:
        if latestVersion == '':
            tprint('Current knoxnl version '+__version__+' (unable to check if latest)')
        elif __version__ == latestVersion:
            tprint('Current knoxnl version '+__version__+' ('+colored('latest','green')+')\n')
        else:
            tprint('Current knoxnl version '+__version__+' ('+colored('outdated','red')+')\n')
    except:
        pass
    
def showBanner():
    tprint()
    tprint(" _           "+colored("_ ___    ","red")+colored("__","yellow")+colored("      _","cyan"))
    tprint("| | ___ __   "+colored("V","red")+"_"+colored(r"V\ \  ","red")+colored("/ /","yellow")+colored("_ __","green")+colored(" | | ","cyan"))
    tprint(r"| |/ / '_ \ / _ \ "[:-1]+colored(r"\ \ "[:-1],"red")+colored("/ /","yellow")+colored(r"| '_ \ "[:-1],"green")+colored("| | ","cyan"))
    tprint("|   <| | | | (_) "+colored("/ /","red")+colored(r"\ \ "[:-1],"yellow")+colored("| | | |","green")+colored(" | ","cyan"))
    tprint(r"|_|\_\_| |_|\___"+colored("/_/  ","red")+colored(r"\_\ "[:-1],"yellow")+colored("_| |_|","green")+colored("_| ","cyan"))
    tprint(colored("                 by @Xnl-h4ck3r ","magenta"))
    tprint()
    try:
        currentDate = datetime.now().date()
        if currentDate.month == 12 and currentDate.day in (24,25):
            tprint(colored(" *** 🎅 HAPPY CHRISTMAS! 🎅 ***","green",attrs=["blink"]))
        elif currentDate.month == 10 and currentDate.day == 31:
            tprint(colored(" *** 🎃 HAPPY HALLOWEEN! 🎃 ***","red",attrs=["blink"]))
        elif currentDate.month == 1 and currentDate.day in  (1,2,3,4,5):
            tprint(colored(" *** 🥳 HAPPY NEW YEAR!! 🥳 ***","yellow",attrs=["blink"]))
        elif currentDate.month == 10 and currentDate.day == 10:
            tprint(colored(" *** 🧠 HAPPY WORLD MENTAL HEALTH DAY!! 💚 ***","yellow",attrs=["blink"]))
        tprint()
    except:
        pass
    tprint(colored('DISCLAIMER: We are not responsible for any use, and especially misuse, of this tool or the KNOXSS API','yellow'))
    tprint()
    showVersion()

# Functions used when printing messages dependant on verbose options
def verbose():
    return args.verbose

def showBlocked():
    global blockedDomains
    try:
        # Accumulate domains with a count more than the specified limit into a list
        domainsBlockedLimit = [domain for domain, count in blockedDomains.items() if count > args.skip_blocked-1]
        if domainsBlockedLimit:
            # Join the domains into a comma-separated string
            domainList = ', '.join(domainsBlockedLimit)
        
            tprint(colored('The following domains seem to be blocking KNOXSS and might be worth excluding for now:','yellow'),colored(domainList,'white'))
    except:
        pass
    
# Handle the user pressing Ctrl-C and programatic interupts
def handler(signal_received, frame):
    """
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    """
    global stopProgram, needToStop, inputValues, blockedDomains, todoFileName, fileIsOpen, debugFileIsOpen
    stopProgram = True
    pauseEvent.clear()
    if not needToStop:
        tprint(colored('\n>>> "Oh my God, they killed Kenny... and knoXnl!" - Kyle','red'))
        # If there are any input values not checked, write them to a .todo file, unless the -nt/-no-todo arg was passed
        try:
            if len(inputValues) > 0 and not args.no_todo:
                try:
                    tprint(colored('\n>>> Just trying to save outstanding input to .todo file before ending...','yellow'))
                    with open(todoFileName, 'w') as file:
                        for inp in inputValues:
                            file.write(inp+'\n')
                    tprint(colored('All unchecked URLs have been written to','cyan'),colored(todoFileName+'\n', 'white'))
                except Exception as e:
                    tprint(colored('Error saving file ','cyan'),colored(todoFileName+'\n', 'white'),colored(':'+str(e),'red'))
        except:
            pass
        
        # If there were any domains that might be blocking KNOXSS, let the user know
        if args.skip_blocked > 0:
            showBlocked()
        
        # Try to close the output files before ending
        try:
            fileIsOpen = False
            outFile.close()
            debugFileIsOpen = False
            debugOutFile.close()
        except:
            pass
        sys.exit(0)
            
# Show the chosen options and config settings
def showOptions():

    global urlPassed, fileIsOpen, debugFileIsOpen, API_URL, timeAPIReset
            
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
                print(colored('Discord Webhook Complete:', 'magenta'), DISCORD_WEBHOOK_COMPLETE)  
                print(colored('-i: ' + args.input + ' (FILE)', 'magenta'), 'All URLs will be passed to KNOXSS API.')

        if fileIsOpen:
            print(colored('-o: ' + args.output, 'magenta'), 'The output file where successful XSS payloads will be saved.')
            print(colored('-ow: ' + str(args.output_overwrite), 'magenta'), 'Whether the output will be overwritten if it already exists.')
            print(colored('-oa: ' + str(args.output_all), 'magenta'), 'Whether the output all results to the output file, not just successful one\'s.')
            
        if debugFileIsOpen:
            print(colored('-do: ' + args.debug_output, 'magenta'), 'The output file where all debug information will be saved.')
            
        if not urlPassed:
            print(colored('-p: ' + str(args.processes), 'magenta'), 'The number of parallel requests made, i.e. number or processes/threads.')
        
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
            
        print(colored('-t: ' + str(args.timeout), 'magenta'), 'The number of seconds to wait for KNOXSS API to respond.')
        print(colored('-st: ' + str(args.stall_timeout), 'magenta'), 'The number of seconds to wait for the KNOXSS API scan to take between steps before aborting.')
        
        if args.retries == 0:
            print(colored('-r: ' + str(args.retries), 'magenta'), 'If having issues connecting to the KNOXSS API, the program will not sleep and not try to retry any URLs. ')
        else:
            print(colored('-r: ' + str(args.retries), 'magenta'), 'The number of times to retry when having issues connecting to the KNOXSS API. The number of retries will also be reset every 24 hours when running for a file.')
        if args.retries > 0:
            print(colored('-ri: ' + str(args.retry_interval), 'magenta'), 'How many seconds to wait before retrying when having issues connecting to the KNOXSS API.')
            print(colored('-rb: ' + str(args.retry_backoff), 'magenta'), 'The backoff factor used when retrying when having issues connecting to the KNOXSS API.')
        
        if args.skip_blocked > 0:
            print(colored('-sb: ' + str(args.skip_blocked), 'magenta'), 'The number of 403 Forbidden responses from a target (for a given HTTP method + scheme + (sub)domain) before skipping.')
        
        if args.force_new:
            print(colored('-fn: True', 'magenta'), 'Forces KNOXSS to do a new scan instead of getting cached results.')
             
        if args.runtime_log:
            print(colored('-rl: True', 'magenta'), 'Provides a live runtime log of the KNOXSS scan.')

        if args.no_todo and not urlPassed:
            print(colored('-nt: True', 'magenta'), 'If the input file is not completed because of issues with API, connection, etc. the .todo file will not be created.')
             
        if timeAPIReset is not None:
            print(colored('KNOXSS API Limit Reset Time:', 'magenta'), str(timeAPIReset.strftime("%Y-%m-%d %H:%M")))  
            if args.pause_until_reset:
                print(colored('-pur: True', 'magenta'), 'If the API limit is reached, the program will pause and then continue again when it has been reset.')
        else:
            if args.pause_until_reset:
                print(colored('-pur: True', 'magenta'), 'NOT POSSIBLE: Unfortunately the API reset time is currently unknown, so the program cannot be paused and continue when the API limit is reached.')
        print()

    except Exception as e:
        print(colored('ERROR showOptions: ' + str(e), 'red'))

# If an API key wasn't supplied, or was invalid, then point the user to https://knoxss.pro
def needApiKey():
    # If the console can't display 🤘 then an error will be raised to try without
    try:
        tprint(colored('Haven\'t got an API key? Why not head over to https://knoxss.pro and subscribe?\nDon\'t forget to generate and SAVE your API key before using it here! 🤘\n', 'green')) 
    except:
        tprint(colored('Haven\'t got an API key? Why not head over to https://knoxss.pro and subscribe?\nDon\'t forget to generate and SAVE your API key before using it here!\n', 'green')) 
              
def getConfig():
    # Try to get the values from the config file, otherwise use the defaults
    global API_URL, API_KEY, DISCORD_WEBHOOK, DISCORD_WEBHOOK_COMPLETE, configPath, HTTP_ADAPTER, HTTP_ADAPTER_DISCORD, apiResetPath
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
            tprint(colored('ERROR getConfig 2: ' + str(e), 'red'))
        
        # Set up an HTTPAdaptor for retry strategy when sending Discord notifications
        try:
            retry= Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                raise_on_status=False,
                respect_retry_after_header=True
            )
            HTTP_ADAPTER_DISCORD = HTTPAdapter(max_retries=retry)
        except Exception as e:
            tprint(colored('ERROR getConfig 2: ' + str(e), 'red'))
        
        
        configPath.absolute
        # Set config file path and apireset file path
        if configPath == '':
            apiResetPath = '.apireset'
            configPath = 'config.yml'
        else:
            apiResetPath = Path(configPath / '.apireset')
            configPath = Path(configPath / 'config.yml')
        config = yaml.safe_load(open(configPath))
        
        try:
            API_URL = config.get('API_URL')
        except Exception as e:
            tprint(colored('Unable to read "API_URL" from config.yml; defaults set', 'red'))
            API_KEY = DEFAULT_API_URL
        try:
            API_KEY = config.get('API_KEY')
            if args.api_key != '':
                API_KEY = args.api_key
                tprint(colored('NOTE: Overriding "API_KEY" from config.yml with passed API Key', 'cyan'), API_KEY + '\n')
            else:
                if API_KEY is None or API_KEY == 'YOUR_API_KEY':
                    tprint(colored('ERROR: You need to add your "API_KEY" to config.yml or pass it with the -A option.', 'red'))
                    needApiKey()
                    sys.exit(0)
        except Exception as e:
            tprint(colored('Unable to read "API_KEY" from config.yml; We need an API key! - ' + str(e), 'red'))
            needApiKey()
            sys.exit(0)
        
        # Set the Discord webhook. If passed with argument -dw / --discord-webhook then this will override the config value
        if args.discord_webhook != '':
            DISCORD_WEBHOOK = args.discord_webhook
        else:
            try:
                DISCORD_WEBHOOK = config.get('DISCORD_WEBHOOK').replace('YOUR_WEBHOOK','')
            except Exception as e:
                DISCORD_WEBHOOK = ''
        
        # Set the Discord webhook Complete. If passed with argument -dwc / --discord-webhook-complete then this will override the config value
        if args.discord_webhook_complete != '':
            DISCORD_WEBHOOK_COMPLETE = args.discord_webhook_complete
        else:
            try:
                DISCORD_WEBHOOK_COMPLETE = config.get('DISCORD_WEBHOOK_COMPLETE').replace('YOUR_WEBHOOK','')
            except Exception as e:
                DISCORD_WEBHOOK_COMPLETE = ''
        
    except Exception as e:
        try:
            if args.api_key == '':
                tprint(colored('Unable to read config.yml and API Key not passed with -A; Unable to use KNOXSS API! - ' + str(e), 'red'))
                needApiKey()
                sys.exit(0)
            else:
                API_URL = DEFAULT_API_URL
                API_KEY = args.api_key
                tprint(colored('Unable to read config.yml; using default API URL and passed API Key', 'cyan'))
            DISCORD_WEBHOOK = args.discord_webhook    
            DISCORD_WEBHOOK_COMPLETE = args.discord_webhook_complete    
        except Exception as e:
            tprint(colored('ERROR getConfig 1: ' + str(e), 'red'))

# Get a short ID for the thread
def short_thread_id():
    ident = threading.get_ident()
    with thread_id_lock:
        if ident not in thread_id_map:
            thread_id_map[ident] = thread_id_counter[0]
            thread_id_counter[0] += 1
        return thread_id_map[ident]
    
# Prefix CLI output with a Thread number so the runtime logs and responses can be tracked effectively.
# Only prefix if the number of threads is more than 1 and a file was passed as input
def tprint(*arguments, sep=' ', end='\n'):
    global urlPassed, debugOutFile, debugFileIsOpen
    try:
        message = sep.join(str(arg) for arg in arguments)
        tid = colored('[T'+str(short_thread_id()+1)+']','magenta')
        if (verbose() or args.runtime_log) and (args.processes > 1 and not urlPassed):
            print(f"{tid} {message}", end=end)
        else:
            if not re.match(r'^\[\d{2}:\d{2}:\d{2}\]: ', message) or (verbose() or args.runtime_log):
                print(message, end=end)
            
        # If there is a debug file then write it all to the file
        if debugFileIsOpen:
            if (args.processes > 1 and not urlPassed):
                debugOutFile.write(f"{tid} {message}{end}")
            else:
                debugOutFile.write(message + end)
    except Exception as e:
        print(colored('ERROR tprint 1: ' + str(e), 'red'))
    
# Call the knoxss API       
def knoxssApi(targetUrl, headers, method, knoxssResponse):
    global latestApiCalls, rateLimitExceeded, needToStop, dontDisplay, stopProgram
    global HTTP_ADAPTER, inputValues, needToRetry, requestCount, runtimeLog, debugFileIsOpen

    try:
        if stopProgram: return
        try:
            apiHeaders = {
                'X-API-KEY': API_KEY,
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'knoXnl tool by @xnl-h4ck3r'
            }

            targetData = targetUrl.replace('&', '%26').replace('+', '%2B')
            postData = ''
            if method == 'POST' and args.http_method in ('POST', 'BOTH'):
                if args.post_data != '':
                    postData = args.post_data.replace('&', '%26').replace('+', '%2B')
                    if '?' in targetUrl:
                        targetData = targetData.split('?')[0]
                else:
                    if '?' in targetUrl:
                        postData = targetData.split('?')[1]
                        targetData = targetData.split('?')[0]

            data = f'target={targetData}'
            if method == 'POST':
                data += f'&post={postData}'
            if args.force_new:
                data += '&new=1'
            if args.runtime_log or verbose() or debugFileIsOpen:
                data += '&log=1'
            if headers != '':
                encHeaders = headers.replace(' ', '%20').replace('|', '%0D%0A')
                data += f'&auth={encHeaders}'
        except Exception as e:
            tprint(colored('ERROR knoxssApi 2:  ' + str(e), 'red'))

        tryAgain = True
        while tryAgain:
            tryAgain = False
            session = requests.Session()
            session.mount('https://', HTTP_ADAPTER)
            requestCount += 1

            fullResponse = ""
            runtimeLog = ""
            q = queue.Queue()
            shared = {'status_code': None}
            reader_finished = threading.Event()

            def reader():
                global stopProgram
                try:
                    if stopProgram:
                        return
                    with session.post(
                        url=API_URL,
                        headers=apiHeaders,
                        data=data.encode('utf-8'),
                        timeout=None,
                        stream=True
                    ) as r:
                        shared['status_code'] = r.status_code
                        for line in r.iter_lines(decode_unicode=True):
                            if line:
                                q.put(line)
                except Exception as e:
                    nonlocal connectionError
                    connectionError = True
                    q.put(f"[Reader error] {e}")
                finally:
                    reader_finished.set()
                    q.put(None)

            connectionError = False
            thread = threading.Thread(target=reader, daemon=True)
            thread.start()

            start_time = time.time()
            last_line_time = start_time
            stalled = False
            timed_out = False

            if stopProgram: return
            try:
                while True:
                    if stopProgram: break
                    if time.time() - start_time > args.timeout:
                        timed_out = True
                        break

                    try:
                        line = q.get(timeout=0.5)
                        if line is None:
                            break  # End of stream
                        if not line.startswith("["):
                            fullResponse += line + "\n"

                        if (args.runtime_log or verbose() or debugFileIsOpen) and line.startswith("["):
                            tprint(line)

                        last_line_time = time.time()

                    except queue.Empty:
                        if time.time() - last_line_time > args.stall_timeout:
                            stalled = True
                            break
            except Exception as e:
                tprint(colored('ERROR knoxssApi 3:  ' + str(e), 'red'))
            
            if stopProgram: return
            try:
                knoxssResponse.Code = str(shared['status_code']) if shared['status_code'] else "Unknown"
                if connectionError:
                    knoxssResponse.Error = 'There was a problem connecting to the KNOXSS API. Check your internet connection.'
                    knoxssResponse.PoC = 'none'
                    knoxssResponse.Calls = 'Unknown'
                    if args.retries > 0:
                        needToRetry = True
                elif stalled:
                    knoxssResponse.Error = f"The scan stalled for more than {args.stall_timeout} seconds, so aborting."
                    knoxssResponse.PoC = 'none'
                    knoxssResponse.Calls = 'Unknown'
                elif timed_out:
                    knoxssResponse.Error = f"The scan exceeded the timeout of {args.timeout} seconds."
                    knoxssResponse.PoC = 'none'
                    knoxssResponse.Calls = 'Unknown'
                else:
                    if verbose() or debugFileIsOpen:
                        tprint('KNOXSS API request:')
                        tprint('     Data: ' + data)
                        tprint('KNOXSS API response:')
                        tprint(fullResponse.strip())

                    jsonPart = fullResponse.strip()
                    if not jsonPart:
                        raise ValueError("Empty response received from KNOXSS API")
                    jsonResponse = json.loads(jsonPart)
                    knoxssResponse.XSS = str(jsonResponse.get('XSS'))
                    knoxssResponse.Redir = str(jsonResponse.get('Redir'))
                    knoxssResponse.PoC = str(jsonResponse.get('PoC'))
                    knoxssResponse.Calls = str(jsonResponse.get('API Call', 'Unknown'))
                    if knoxssResponse.Calls == '0':
                        knoxssResponse.Calls = 'Unknown'
                    knoxssResponse.Error = str(jsonResponse.get('Error'))
                    knoxssResponse.POSTData = str(jsonResponse.get('POST Data'))
                    knoxssResponse.Timestamp = str(jsonResponse.get('Timestamp'))

                    if knoxssResponse.PoC != 'none':
                        if 'service unavailable' in knoxssResponse.Error.lower() or "please retry" in knoxssResponse.Error.lower():
                            if args.retries > 0:
                                needToRetry = True
                        elif knoxssResponse.Error == 'API rate limit exceeded.':
                            rateLimitExceeded = True
                            knoxssResponse.Calls = 'API rate limit exceeded!'
                            if not (timeAPIReset is not None and args.pause_until_reset):
                                needToStop = True
                        else:
                            inputValues.discard(targetUrl)
                    else:
                        inputValues.discard(targetUrl)

                    if knoxssResponse.Calls not in ('Unknown', ''):
                        latestApiCalls = knoxssResponse.Calls
            except Exception as e:
                knoxssResponse.Error = str(e)
                knoxssResponse.PoC = 'none'
                knoxssResponse.Calls = 'Unknown'
                tprint(colored('ERROR knoxssApi 4:  ' + str(e), 'red'))
            
    except Exception as e:
        tprint(colored('ERROR knoxssApi 1:  ' + str(e), 'red'))

def checkForAlteredParams(url):
    # Show a warning if it looks like the user has tampered with the parameter values before sending to knoxnl. Some indications of this are using FUZZ and also Gxss.
    # Show a warning if any XSS payloads appear to be included in the URL already
    try:
        if '=FUZZ' in url or '=Gxss' in url:
            tprint(colored('WARNING: It appears the URL may have been manually changed by yourself (or another tool) first. KNOXSS might not work as expected without the default values of parameters (some parameters might be value sensitive). Just pass original URLs to knoxnl.', 'yellow'))
        regexCheck = r'<[A-Z]+|alert([^\}]*)|javascript:'
        regexCheckCompiled = re.compile(regexCheck, re.IGNORECASE)
        if regexCheckCompiled.search(url):
            tprint(colored('WARNING: It appears the URL may already include some XSS payload. If that\'s correct, KNOXSS won\'t work as expected since it\'s not meant to receive XSS payloads, but to provide them.', 'yellow'))
    except Exception as e:
        tprint(colored('ERROR checkForAlteredParams 1:  ' + str(e), 'red'))
        
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
            # Check for non default values of parameters
            checkForAlteredParams(inputArg)

            processUrl(inputArg)
        else: # It's a file of URLs
            try:
                # Open file and put all values in input set, but in random order
                with open(inputArg, 'r') as inputFile:
                    lines = [line.strip() for line in inputFile if line.strip() != '']

                # Randomize the order before adding to the set. This is to help "fly under the radar" of WAFs on the target systems
                random.shuffle(lines)
                inputValues = set(lines)

                print(colored('Calling KNOXSS API for '+str(len(inputValues))+' targets (with '+str(args.processes)+' processes/threads)...\n', 'cyan'))
                if not stopProgram:
                    with ThreadPoolExecutor(max_workers=args.processes) as executor:
                        executor.map(processUrl, inputValues)

            except Exception as e:
                print(colored('ERROR processInput 3: ' + str(e), 'red'))
                
    except Exception as e:
        print(colored('ERROR processInput 1: ' + str(e), 'red'))

def discordNotify(target, poc, vulnType):
    global DISCORD_WEBHOOK, HTTP_ADAPTER_DISCORD
    try:
        embed = {
            "description": "```\n" + poc + "\n```",
            "title": "KNOXSS POC for " + target,
            "color": 42320,
            "fields": [
                {
                    "name": "",
                    "value": "[☕ Buy me a coffee, Thanks!](https://ko-fi.com/xnlh4ck3r)",
                    "inline": False
                }
            ]
        }
        data = {
            "content": vulnType + " found by knoxnl! 🤘",
            "username": "knoxnl",
            "embeds": [embed],
            "avatar_url": "https://avatars.githubusercontent.com/u/84544946"
        }

        session = requests.Session()
        session.mount('https://', HTTP_ADAPTER_DISCORD)

        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            result = session.post(DISCORD_WEBHOOK, json=data)

            if result.status_code == 429:
                try:
                    retry_after = result.json().get("retry_after", 1)
                    time.sleep(retry_after)
                    continue
                except Exception as e:
                    time.sleep(1)
                    continue
            elif result.status_code >= 300:
                tprint(colored('ERROR: Failed to send notification to Discord - ' + result.text, 'yellow'))
                break  

            break
        
        # If we used all attempts and it never broke out early, print final warning:
        if attempt == max_attempts and (result.status_code < 200 or result.status_code >= 300):
            tprint(colored('ERROR: Failed to send notification to Discord after '+str(max_attempts)+' attempts.', 'red'))
          
    except Exception as e:
        tprint(colored('ERROR discordNotify: ' + str(e), 'red'))

def discordNotifyComplete(input, description, incomplete):
    global DISCORD_WEBHOOK_COMPLETE, HTTP_ADAPTER_DISCORD
    try:
        if incomplete:
            title = "INCOMPLETE FOR FILE `"+input+"`"
            embed_color = 16711722  # Red
        else:
            title = "COMPLETE FOR FILE `"+input+"`"
            embed_color = 42320  # Green

        embed = {
            "description": description,
            "title": title,
            "color": embed_color,
            "fields": [
                {
                    "name": "",
                    "value": "[☕ Buy me a coffee, Thanks!](https://ko-fi.com/xnlh4ck3r)", 
                    "inline": False
                }
            ]
        }

        data = {
            "content": "knoxnl finished!",
            "username": "knoxnl",
            "avatar_url": "https://avatars.githubusercontent.com/u/84544946",
            "embeds": [embed],
        }

        session = requests.Session()
        session.mount('https://', HTTP_ADAPTER_DISCORD)

        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            result = session.post(DISCORD_WEBHOOK_COMPLETE, json=data)

            if result.status_code == 429:
                try:
                    retry_after = result.json().get("retry_after", 1)
                    time.sleep(retry_after)
                    continue
                except Exception as e:
                    time.sleep(1)
                    continue
            elif result.status_code >= 300:
                tprint(colored('ERROR: Failed to send Complete notification to Discord - ' + result.text, 'yellow'))
                break  
            
            break
        
        # If we used all attempts and it never broke out early, print final warning:
        if attempt == max_attempts and (result.status_code < 200 or result.status_code >= 300):
            tprint(colored('ERROR: Failed to send Complete notification to Discord after '+str(max_attempts)+' attempts.', 'red'))

    except Exception as e:
        tprint(colored('ERROR discordNotifyComplete 1: ' + str(e), 'red'))
        
def getAPILimitReset():
    global apiResetPath, timeAPIReset
    try:
        # If the .apireset file exists then get the API reset time
        if os.path.exists(apiResetPath):
            # Read the timestamp from the file
            with open(apiResetPath, 'r') as file:
                timeAPIReset = datetime.strptime(file.read().strip(), '%Y-%m-%d %H:%M')
    
        # If the timestamp is more than 24 hours ago, then delete the file and set the timeAPIReset back to None
        if timeAPIReset is not None and (datetime.now() - timeAPIReset) > timedelta(hours=24):
            timeAPIReset = None
            # If the .apireset file already exists then delete it
            if os.path.exists(apiResetPath):
                os.remove(apiResetPath)

    except Exception as e:
        tprint(colored('ERROR getAPILimitReset 1: ' + str(e), 'red'))
        
def setAPILimitReset(timestamp):
    global apiResetPath, latestApiCalls, timeAPIReset
    try:
        # Convert the timestamp to the local timezone and add 24 hours and 5 minutes
        timestamp = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')
        localTimezone = tz.tzlocal()
        localTimestamp = timestamp.astimezone(localTimezone)
        timeAPIReset = localTimestamp + timedelta(hours=24, minutes=5)

        # If the .apireset file already exists then delete it
        if os.path.exists(apiResetPath):
            os.remove(apiResetPath)
            
        # Write the new API limit reset time to the .apireset file, and set the global variable
        with open(apiResetPath, 'w') as file:
            file.write(timeAPIReset.strftime('%Y-%m-%d %H:%M'))
        
    except Exception as e:
        tprint(colored('ERROR setAPILimitReset 1: ' + str(e), 'red'))
        
def processOutput(target, method, knoxssResponse):
    global latestApiCalls, successCountXSS, successCountOR, outFile, debugOutFile, debugFileIsOpen, currentCount, rateLimitExceeded, urlPassed, needToStop, dontDisplay, blockedDomains, needToRetry, forbiddenResponseCount, errorCount, safeCount, requestCount, skipCount, runtimeLog, stopProgram
    try:
        if stopProgram: return
        knoxssResponseError = knoxssResponse.Error
        
        if knoxssResponse.Calls == 'Unknown' and all(s not in knoxssResponseError.lower() for s in ["content type", "can't test it (forbidden)"]):
            if not args.success_only:
                
                # If there is a 403, it maybe because the users IP is blocked on the KNOXSS firewall
                if knoxssResponse.Code == "403":
                    knoxssResponseError = '403 Forbidden - Check http://knoxss.pro manually and if you are blocked, contact Twitter/X @KN0X55 or brutelogic@null.net'
                    needToStop = True
                # If there is "InvalidChunkLength" in the error returned, it means the KNOXSS API returned an empty response
                elif 'InvalidChunkLength' in knoxssResponseError:
                    knoxssResponseError = 'The API Timed Out'
                    if args.retries > 0:
                        needToRetry = True
                    
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
                    xssText = '[ ERR! ] - (' + method + ') ' + target + '  KNOXSS ERR: ' + knoxssResponseError
                    errorCount = errorCount + 1
                    if urlPassed:
                        tprint(colored(xssText, 'red'))
                    else:
                        tprint(colored(xssText, 'red'), colored('['+latestApiCalls+']','white'))
                    if args.output_all and fileIsOpen:
                        outFile.write(xssText + '\n')
        else:
            # If it is a new reset time then replace the .apireset file
            if knoxssResponse.Timestamp != '' and latestApiCalls.startswith('1/'):
                setAPILimitReset(knoxssResponse.Timestamp)
            
            # If the error has "got another 403" it means the a 403 was returned by the target
            if "got another 403" in knoxssResponseError.lower():
                knoxssResponseError = 'Target returned a "403 Forbidden". There could be WAF in place.'
                # If requested to skip blocked domains after a limit, then save them
                if args.skip_blocked > 0:
                    try:
                        parsedTarget = urlparse(target)
                        domain = '(' + method + ') ' + str(parsedTarget.scheme + '://' + parsedTarget.netloc)
                        pauseEvent.set()
                        blockedDomains[domain] = blockedDomains.get(domain, 0) + 1
                        pauseEvent.clear()
                    except:
                        pass
            
            # If it is the generic error "KNOXSS engine is failing at some point" then we will not display that because it will be reported as NONE
            if 'failing at some point' in knoxssResponseError:
                knoxssResponseError = 'none'
                    
            # If for any reason neither of the XSS and Redir flags are "true" (not intended) then assume it the PoC is XSS
            if knoxssResponse.PoC != 'none' and knoxssResponse.XSS != 'true' and knoxssResponse.Redir != 'true':
                knoxssResponse.XSS = 'true'
            
            # If no PoC then report as [ NONE ]
            if knoxssResponse.PoC == 'none':
                if not args.success_only:
                    xssText = '[ NONE ] - (' + method + ') ' + target
                    if knoxssResponseError != 'none':
                        errorText = ' KNOXSS ERR: ' + knoxssResponseError
                    else:
                        errorText = ''
                    safeCount = safeCount + 1
                    if urlPassed:
                        tprint(colored(xssText, 'yellow'), colored(errorText,'red'))
                    else:
                        tprint(colored(xssText, 'yellow'), colored(errorText,'red'), colored('['+latestApiCalls+']','white'))
                    if args.output_all and fileIsOpen:
                        outFile.write(xssText + '\n') 
            else:            
                if knoxssResponse.XSS == 'true':
                    xssText = '[ XSS! ] - (' + method + ') ' + knoxssResponse.PoC
                    if urlPassed:
                        tprint(colored(xssText, 'green'))
                    else:
                        tprint(colored(xssText, 'green'), colored('['+latestApiCalls+']','white'))
                    successCountXSS = successCountXSS + 1
                    
                    # If there was an Open Redirect too, then increment that count
                    if knoxssResponse.Redir == 'true':
                        vulnType = 'XSS (and OR)'
                    else:
                        vulnType = 'XSS'
                        
                    # Send a notification to discord if a webhook was provided
                    if DISCORD_WEBHOOK != '':
                        discordNotify(target,knoxssResponse.PoC,vulnType)
                        
                    # Write the successful XSS details to file
                    if fileIsOpen:
                        outFile.write(xssText + '\n')
                        
                elif knoxssResponse.Redir == 'true':
                    orText = '[ OR ! ] - (' + method + ') ' + knoxssResponse.PoC
                    if urlPassed:
                        tprint(colored(orText, 'green'))
                    else:
                        tprint(colored(orText, 'green'), colored('['+latestApiCalls+']','white'))
                    successCountOR = successCountOR + 1
                    
                    # Send a notification to discord if a webhook was provided
                    if DISCORD_WEBHOOK != '':
                        discordNotify(target,knoxssResponse.PoC, 'Open Redirect')
                        
                    # Write the successful OR details to file
                    if fileIsOpen:
                        outFile.write(orText + '\n')
                        
                # This shouldn't happen, but just in case, output an error if verbose was chosen
                else: 
                    if verbose() or debugFileIsOpen:
                        tprint(colored('ERROR: There was a PoC, but didn\'t seem to be an XSS or OR. Check the response for details:', 'red'))
                        tprint(knoxssResponse)
                        
    except Exception as e:
        tprint(colored('ERROR showOutput 1: ' + str(e), 'red'))

# Process one URL        
def processUrl(target):
    
    global stopProgram, latestApiCalls, urlPassed, needToStop, needToRetry, retryAttempt, rateLimitExceeded, timeAPIReset, skipCount, apiResetPath, lastRetryResetTime
    try:    
        # If the event is set, pause for a while until its unset again
        while pauseEvent.is_set() and not stopProgram and not needToStop:
            time.sleep(1)
        
        if not stopProgram and not needToStop:
            
            # Reset retryAttempt every 24 hours
            if (datetime.now() - lastRetryResetTime).total_seconds() >= 86400:
                retryAttempt = 0
                lastRetryResetTime = datetime.now()
            
            # If the API Limit was exceeded, and we want to wait until the limit is reset pause all processes until that time
            if rateLimitExceeded and timeAPIReset is not None and args.pause_until_reset:
                # Set the event to pause all processes
                pauseEvent.set()
                tprint(colored(f'WAITING UNTIL {str(timeAPIReset.strftime("%Y-%m-%d %H:%M"))} WHEN THEN API LIMIT HAS BEEN RESET...','yellow'))
                time_difference = (timeAPIReset - datetime.now()).total_seconds()
                timeAPIReset = None
                os.remove(apiResetPath)
                time.sleep(time_difference)
                tprint(colored('API LIMIT HAS BEEN RESET. RESUMING...','yellow'))
                # Reset the event for to unpause all processes
                pauseEvent.clear()
                    
            # If we need to try again because of an KNOXSS error, then delay
            if needToRetry and args.retries > 0:
                if retryAttempt < args.retries:
                    # Set the event to pause all processes
                    pauseEvent.set()
                    needToRetry = False
                    if retryAttempt == 0:
                        delay = args.retry_interval * 1.0
                    else:
                        delay = args.retry_interval * (retryAttempt * args.retry_backoff)
                    if retryAttempt == args.retries:
                        tprint(colored('WARNING: There are issues with KNOXSS API. Sleeping for ' + str(delay) + ' seconds before trying again. Last retry.', 'yellow'))
                    else:
                        tprint(colored('WARNING: There are issues with KNOXSS API. Sleeping for ' + str(delay) + ' seconds before trying again.', 'yellow'))
                    retryAttempt += 1
                    time.sleep(delay)
                    # Reset the event for the next iteration
                    pauseEvent.clear()
                else:
                    needToStop = True
                   
            target = target.strip()
            # Check if target has scheme. If not, then add https://
            if '://' not in target:
                tprint(colored('WARNING: Input "'+target+'" should include a scheme. Using https by default...', 'yellow'))
                target = 'https://'+target
            
            # If the domain has already been flagged as blocked, then skip it and remove from the input values so not written to the .todo file
            parsedTarget = urlparse(target)
 
            headers = args.headers.strip()
            knoxssResponse=knoxss()        

            if args.http_method in ('GET','BOTH'): 
                method = 'GET'
                domain = '(' + method + ') ' + str(parsedTarget.scheme + '://' + parsedTarget.netloc)
                
                # If skipping blocked domains was requested, check if the domain is in blockedDomains, if not, add it with count 0
                if args.skip_blocked > 0:
                    while pauseEvent.is_set():
                        time.sleep(1)
                    pauseEvent.set()
                    if domain not in blockedDomains:
                        blockedDomains[domain] = 0
                    pauseEvent.clear()
                
                # If skipping blocked domains was requested and the domain has been blocked more than the requested number of times, then skip, otherwise process  
                if args.skip_blocked > 0 and blockedDomains[domain] > args.skip_blocked-1:
                    tprint(colored('[ SKIP ] - ' + domain + ' has already been flagged as blocked, so skipping ' + target, 'yellow', attrs=['dark']))
                    skipCount = skipCount + 1
                    inputValues.discard(target)
                else:
                    knoxssApi(target, headers, method, knoxssResponse)
                    processOutput(target, method, knoxssResponse)
        
            if args.http_method in ('POST','BOTH'): 
                method = 'POST'
                domain = '(' + method + ') ' + str(parsedTarget.scheme + '://' + parsedTarget.netloc)
                
                # If skipping blocked domains was requested, check if the domain is in blockedDomains, if not, add it with count 0
                if args.skip_blocked > 0:
                    while pauseEvent.is_set():
                        time.sleep(1)
                    pauseEvent.set()
                    if domain not in blockedDomains:
                        blockedDomains[domain] = 0
                    pauseEvent.clear()
                
                # If skipping blocked domains was requested and the domain has been blocked more than the requested number of times, then skip, otherwise process  
                if args.skip_blocked > 0 and blockedDomains[domain] > args.skip_blocked-1:
                    tprint(colored('[ SKIP ] - ' + domain + ' has already been flagged as blocked, so skipping ' + target, 'yellow', attrs=['dark']))
                    skipCount = skipCount + 1
                    inputValues.discard(target)
                else:
                    knoxssApi(target, headers, method, knoxssResponse)
                    processOutput(target, method, knoxssResponse)

    except Exception as e:
        pauseEvent.clear()
        tprint(colored('ERROR processUrl 1: ' + str(e), 'red'))   

# Validate the -p argument 
def processes_type(x):
    x = int(x) 
    if x < 1 or x > 5:
        raise argparse.ArgumentTypeError('The number of processes must be between 1 and 5')     
    return x

def updateProgram():
    try:
        # Execute pip install --upgrade knoxnl
        subprocess.run(['pip', 'install', '--upgrade', 'knoxnl'], check=True)
        print(colored(f'knoxnl successfully updated {__version__} -> {latestVersion} (latest) 🤘', 'green'))
    except subprocess.CalledProcessError as e:
        print(colored(f'Unable to update knoxnl to version {latestVersion}: {str(e)}', 'red'))

def argcheckStallTimeout(value):
    ivalue = int(value)
    if ivalue < 60:
        raise argparse.ArgumentTypeError("stall-timeout must be at least 60 seconds.")
    return ivalue
                                      
# Run knoXnl
def main():
    global args, latestApiCalls, urlPassed, successCountXSS, successCountOR, fileIsOpen, outFile, debugOutFile, debugFileIsOpen, needToStop, todoFileName, blockedDomains, latestVersion, safeCount, errorCount, requestCount, skipCount, DISCORD_WEBHOOK_COMPLETE

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
        '-s',
        '--success-only',
        action='store_true',
        help='Only show successful XSS payloads in the CLI output.',
    )
    parser.add_argument(
        '-p',
        '--processes',
        help='Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes/threads used (default: 3). ',
        action='store',
        type=processes_type,
        default=3,
        metavar="<integer>",
    )
    parser.add_argument(
        '-t',
        '--timeout',
        help='How many seconds to wait for the KNOXSS API to respond before giving up (default: '+str(DEFAULT_TIMEOUT)+' seconds). If set to 0, then timeout will be used.',
        default=DEFAULT_TIMEOUT,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        '-st',
        '--stall-timeout',
        help='How many seconds to wait for the KNOXSS API scan to take between steps before aborting (default: '+str(DEFAULT_STALL_TIMEOUT)+' seconds). If set to 0, then timeout will be used.',
        default=DEFAULT_STALL_TIMEOUT,
        type=argcheckStallTimeout,
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
    parser.add_argument(
        '-dwc',
        '--discord-webhook-complete',
        help='The Discord Webhook to send completion notifications to when a file has been used as input  (whether finished completely or stopped in error). This will be used instead of the value in config.yml.',
        action='store',
        default='',
    )
    parser.add_argument(
        '-r',
        '--retries',
        help='The number of times to retry when having issues connecting to the KNOXSS API (default: '+str(DEFAULT_RETRIES)+'). If set to 0 then then it will not sleep or try to retry any URLs.',
        default=DEFAULT_RETRIES,
        type=int,
    )
    parser.add_argument(
        '-ri',
        '--retry-interval',
        help='How many seconds to wait before retrying when having issues connecting to the KNOXSS API (default: '+str(DEFAULT_RETRY_INTERVAL)+' seconds)',
        default=DEFAULT_RETRY_INTERVAL,
        type=int,
        metavar="<seconds>",
    )
    parser.add_argument(
        '-rb',
        '--retry-backoff',
        help='The backoff factor used when retrying when having issues connecting to the KNOXSS API (default: '+str(DEFAULT_RETRY_BACKOFF_FACTOR)+')',
        default=DEFAULT_RETRY_BACKOFF_FACTOR,
        type=float,
    )
    parser.add_argument(
        '-pur',
        '--pause-until-reset',
        action='store_true',
        help='If the API Limit reset time is known and the API limit is reached, wait the required time until the limit is reset and continue again. The reset time is only known if knoxnl has run for request number 1 previously. The API rate limit is reset 24 hours after request 1.',
    )
    parser.add_argument(
        '-sb',
        '--skip-blocked',
        help='The number of 403 Forbidden responses from a target (for a given HTTP method + scheme + (sub)domain) before skipping. This is useful if you know the target has a WAF. The default is zero, which means no blocking is done.',
        default=0,
        type=int,
    )
    parser.add_argument(
        '-fn',
        '--force-new',
        action='store_true',
        help='Forces KNOXSS to run a new scan instead of getting cached results. NOTE: Using this option will make checks SLOWER because it won\'t check the cache. Using the option all the time will defeat the purpose of the cache system.',
    )
    parser.add_argument(
        '-rl',
        '--runtime-log',
        action='store_true',
        help='Provides a live runtime log of the KNOXSS scan that will be streamed. This will be prefixed with the number of the thread running, e.g. `[T2]` so the output can be tracked easier (if -p/--processes > 1).',
    )
    parser.add_argument(
        '-nt',
        '--no-todo',
        action='store_true',
        help='Do not create the .todo file if the input file is not completed because of issues with API, connection, etc.',
    )
    parser.add_argument(
        '-up',
        '--update',
        action='store_true',
        help='Update knoxnl to the latest version.',
    )
    parser.add_argument(
        '-do',
        '--debug-output',
        action='store',
        help='The file to save all terminal output to a file, used for debugging. Using this option will also show the JSON response.',
        default='',
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    parser.add_argument('--version', action='store_true', help="Show version number")
    args = parser.parse_args()

    # If --version was passed, display version and exit
    if args.version:
        print(colored('knoxnl - v' + __version__,'cyan'))
        sys.exit()

    # Get the latest version
    try:
        resp = requests.get('https://raw.githubusercontent.com/xnl-h4ck3r/knoxnl/main/knoxnl/__init__.py',timeout=3)
        latestVersion = resp.text.split('=')[1].replace('"','')
    except:
        pass
                        
    showBanner()

    # If --update was passed, update to the latest version
    if args.update:
        try:
            if latestVersion == '':
                print(colored('Unable to check the latest version. Check your internet connection.', 'red'))
            elif __version__ != latestVersion:
                updateProgram()
            else:
                print(colored('You are already running the latest version of knoxnl.Thanks for using!', 'green'))
            print()
            print(colored('✅ Want to buy me a coffee? ☕ https://ko-fi.com/xnlh4ck3r 🤘', 'green'))
            sys.exit()
        except Exception as e:
            print(colored(f'ERROR: Unable to update - {str(e)}','red'))
             
    # If no input was given, raise an error
    if sys.stdin.isatty():
        if args.input is None:
            print(colored('You need to provide an input with -i argument or through <stdin>.', 'red'))
            sys.exit()
            
    # Get the config settings from the config.yml file
    getConfig()
    
    # Get the API reset time from the .apireset file
    getAPILimitReset()

    # If -o (--output) argument was passed then open the output file
    if args.output != "":
        try:
            # If the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
            try:
                output_path = os.path.abspath(os.path.expanduser(args.output))
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            except Exception as e:
                pass
            # If argument -ow was passed and the file exists, overwrite it, otherwise append to it
            if args.output_overwrite:
                outFile = open(os.path.expanduser(args.output), "w")
            else:
                outFile = open(os.path.expanduser(args.output), "a")
            fileIsOpen = True
        except Exception as e:
            print(colored('WARNING: Output won\'t be saved to file - ' + str(e) + '\n', 'red'))
    
    # If -do (--debug-output) argument was passed then open the debug output file
    if args.debug_output != "":
        try:
            # If the filename has any "/" in it, remove the contents after the last one to just get the path and create the directories if necessary
            try:
                output_path = os.path.abspath(os.path.expanduser(args.debug_output))
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            except Exception as e:
                pass
            # Append to the debug file if it exists already
            debugOutFile = open(os.path.expanduser(args.debug_output), "a")
            debugFileIsOpen = True
        except Exception as e:
            print(colored('WARNING: Debug output won\'t be saved to file - ' + str(e) + '\n', 'red'))
                                
    try:

        processInput()
        
        completeDescription = ""
        
        # Show the user the latest API quota       
        if latestApiCalls is None or latestApiCalls == '':
            latestApiCalls = 'Unknown'
        if timeAPIReset is not None:
            message = '\nAPI calls made so far today - ' + latestApiCalls + ' (API Limit Reset Time: ' +str(timeAPIReset.strftime("%Y-%m-%d %H:%M")) + ')\n'
            print(colored(message, 'cyan'))
            completeDescription = message
        else:
            message = '\nAPI calls made so far today - ' + latestApiCalls + '\n'
            print(colored(message, 'cyan'))
            completeDescription = message
           
        # If a file was passed, there is a reason to stop, write the .todo file and let the user know about it (unless -nt/--no-todo was passed)
        if needToStop and not urlPassed and not args.burp_piper and not args.no_todo:
            try:
                with open(todoFileName, 'w') as file:
                    for inp in inputValues:
                        file.write(inp+'\n')
                print(colored('Had to stop due to errors. All unchecked URLs have been written to','cyan'),colored(todoFileName+'\n', 'white'))
                completeDescription = completeDescription + 'Had to stop due to errors. All unchecked URLs have been written to `'+todoFileName+'`\n'
            except Exception as e:
                message = 'Was unable to write .todo file: '+str(e)+'\n'
                print(colored(message,'red'))
                completeDescription = completeDescription + message
        
        if args.skip_blocked > 0:
            showBlocked()
        
        # Report number of None, Error and Skipped results
        if args.skip_blocked > 0:
            message = f'Requests made to KNOXSS API: {str(requestCount)} (XSS!: {str(successCountXSS)}, OR!: {str(successCountOR)}, NONE: {str(safeCount)}, ERR!: {str(errorCount)}, SKIP: {str(skipCount)})'
            print(colored(message,'cyan'))
        else:
            message = f'Requests made to KNOXSS API: {str(requestCount)} (XSS!: {str(successCountXSS)}, OR!: {str(successCountOR)}, NONE: {str(safeCount)}, ERR!: {str(errorCount)})'
            print(colored(message,'cyan'))
        completeDescription = completeDescription + message + '\n'
             
        # Report if any successful XSS or Open Redirect was found this time. 
        # If the console can't display 🤘 then an error will be raised to try without
        try:
            message = ""
            if successCountOR == 1:
                openRedirectTerm = 'Open Redirect'
            else: 
                openRedirectTerm = 'Open Redirects'
            if successCountXSS > 0 and successCountOR > 0:
                message = '🤘 '+str(successCountXSS)+' successful XSS found and '+str(successCountOR)+' successful '+openRedirectTerm+' found! 🤘\n'
                print(colored(message,'green'))
            else:
                if successCountXSS > 0:
                    message = '🤘 '+str(successCountXSS)+' successful XSS found! 🤘\n'
                    print(colored(message,'green'))
                elif successCountOR > 0:
                    message = '🤘 No successful XSS, but '+str(successCountOR)+' successful '+openRedirectTerm+' found! 🤘\n'
                    print(colored(message,'green'))
                else:
                    message = 'No successful XSS or '+openRedirectTerm+' found... better luck next time! 🤘\n'
                    print(colored(message,'cyan'))
        except:
            print(colored('ERROR: ' + str(e), 'red'))   
        completeDescription = completeDescription + message
        
        # If the output was sent to a file, close the file
        if fileIsOpen:
            try:
                fileIsOpen = False
                outFile.close()
            except Exception as e:
                print(colored("ERROR: Unable to close output file: " + str(e), "red"))
        
        # If the debug output was sent to a file, close the file
        if debugFileIsOpen:
            try:
                debugFileIsOpen = False
                debugOutFile.close()
            except Exception as e:
                print(colored("ERROR: Unable to close debug output file: " + str(e), "red"))
                
        # If a file was passed as input and the Discord webhook for Completion was given, then send an appropriate notification
        if not urlPassed and not args.burp_piper and DISCORD_WEBHOOK_COMPLETE != '':
            discordNotifyComplete(args.input,completeDescription,needToStop)
                        
    except Exception as e:
        print(colored('ERROR main 1: ' + str(e), 'red'))
        
if __name__ == '__main__':
    main()
