#!/usr/bin/env python
# Python 3
# A wrapper around the amazing KNOXSS API (https://knoxss.me/?page_id=2729) by Brute Logic
# Inspired by "knoxssme" by @edoardottt2

import requests
import argparse
from signal import SIGINT, signal
import multiprocessing.dummy as mp
from termcolor import colored
import yaml
import json
import os

# Global variables
stopProgram = False
latestApiCalls = "Unknown"
urlPassed = True
rateLimitExceeded = False
successCount = 0
outFile = None
fileIsOpen = False

DEFAULT_API_URL = 'https://knoxss.me/api/v3'

# Yaml config values
API_URL = ''
API_KEY = ''

# Define colours
class tc:
    NORMAL = '\x1b[39m'
    RED = '\x1b[31m'
    GREEN = '\x1b[32m'
    YELLOW = '\x1b[33m'
    MAGENTA = '\x1b[35m'
    CYAN = '\x1b[36m'

# Object for an KNOXSS API response
class knoxss:
    Code = ''
    XSS = ''
    PoC = ''
    Calls = ''
    Error = ''
    POSTData = ''
    
def showBanner():
    print()
    print(tc.NORMAL+" _           "+tc.RED+"_ ___    "+tc.YELLOW+"__"+tc.CYAN+"      _")
    print(tc.NORMAL+"| | ___ __   "+tc.RED+"V"+tc.NORMAL+"_"+tc.RED+"V\ \  "+tc.YELLOW+"/ /"+tc.GREEN+"_ __"+tc.CYAN+" | | ")
    print(tc.NORMAL+"| |/ / '_ \ / _ \\"+tc.RED+"\ \\"+tc.YELLOW+"/ /"+tc.GREEN+"| '_ \\"+tc.CYAN+"| | ")
    print(tc.NORMAL+"|   <| | | | (_) "+tc.RED+"/ /"+tc.YELLOW+"\ \\"+tc.GREEN+"| | | |"+tc.CYAN+" | ")
    print(tc.NORMAL+"|_|\_\_| |_|\___"+tc.RED+"/_/  "+tc.YELLOW+"\_\\"+tc.GREEN+"_| |_|"+tc.CYAN+"_| ")
    print(tc.MAGENTA+"                 by @Xnl-h4ck3r "+tc.NORMAL)
    print()

# Functions used when printing messages dependant on verbose options
def verbose():
    return args.verbose

# Handle the user pressing Ctrl-C and programatic interupts
def handler(signal_received, frame):
    """
    This function is called if Ctrl-C is called by the user
    An attempt will be made to try and clean up properly
    """
    global stopProgram, rateLimitExceeded
    stopProgram = True
    if not rateLimitExceeded:
        print(colored('>>> "Oh my God, they killed Kenny... and knoXnl!" - Kyle','red'))
        quit()

# Show the chosen options and config settings
def showOptions():

    global urlPassed, fileIsOpen
            
    try:
        print(colored('Selected config and settings:', 'cyan'))
        
        print(colored('KNOXSS API Url: ', 'magenta'), API_URL)
        print(colored('KNOXSS API Key: ', 'magenta'), API_KEY)      
        
        if urlPassed:
            print(colored('-i: ' + args.input, 'magenta'), 'The URL to check with KNOXSS API.')
        else:
            print(colored('-i: ' + args.input, 'magenta'), 'All URLs will be passed to KNOXSS API.')

        if fileIsOpen:
            print(colored('-o: ' + args.output, 'magenta'), 'The output file where successful XSS payloads will be saved.')
            print(colored('-ow: ' + str(args.output_overwrite), 'magenta'), 'Whether the output will be overwritten if it already exists.')
        
        if not urlPassed:
            print(colored('-p: ' + str(args.processes), 'magenta'), 'The number of parallel requests made.')
        
        print(colored('-X: ' + args.http_method, 'magenta'), 'The HTTP method checked by KNOXSS API.')
        
        if args.headers != '':
            print(colored('-H: ' + args.headers, 'magenta'), 'HTTP Headers passed with requests.')
            
        print(colored('-afb: ' + str(args.advanced_filter_bypass), 'magenta'), 'Whether the Advanced Filter Bypass option is passed to KNOXSS API.')
        print()

    except Exception as e:
        print(colored('ERROR showOptions: ' + str(e), 'red'))

# If an API key wasn't supplied, or was invalid, then point the user to https://knoxss.me
def needApiKey():
    print(colored('Haven\'t got an API key? Why not head over to https://knoxss.me and subscribe? 🤘\n', 'green'))  
              
def getConfig():
    # Try to get the values from the config file, otherwise use the defaults
    global API_URL, API_KEY
    try:
        configPath = os.path.dirname(__file__)
        if configPath == '':
            configPath = 'config.yml'
        else:
            configPath = configPath + '/config.yml'
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
                print(colored('NOTE: Overriding "API_KEY" from config.yml with passed API Key ', 'cyan'), API_KEY + '\n')
            else:
                if API_KEY == 'YOUR_API_KEY':
                    print(colored('ERROR: You need to add your "API_KEY" to config.yml or pass it with the -A option.', 'red'))
                    needApiKey()
                    quit()
        except Exception as e:
            print(colored('Unable to read "API_KEY" from config.yml; We need an API key! - ' + str(e), 'red'))
            needApiKey()
            quit()
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
                
        except Exception as e:
            print(colored('ERROR getConfig: ' + str(e), 'red'))
            
# Call the KNOXSS API
def knoxssApi(targetUrl, headers, method, knoxssResponse):
    global latestApiCalls, rateLimitExceeded, stopProgram
    try:
        apiHeaders = {'X-API-KEY' : API_KEY, 
                     'Content-Type' : 'application/x-www-form-urlencoded',
                     'User-Agent' : 'knoXnl tool by @xnl-h4ck3r'
                     }
        
        # Replace any & in the URL with encoded value so we can add other data using &
        data = targetUrl.replace('&', '%26')
        data = 'target=' + data
        
        # Change data depending on method
        if method == 'POST':
            # If the target has parameters, i.e. ? then replace is with &post=, otherwise add &post= to the end
            if '?' in targetUrl:
                data = data.replace('?', '&post=', 1)
            else:
                data = data + '&post='
                
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
            resp = requests.post(
                url=API_URL,
                headers=apiHeaders,
                data=data
            )

            # Display the data sent to API and the response
            if verbose():
                print('KNOXSS API request:')
                print('     Data: ' + data)
                print('KNOXSS API response:')
                print(resp.text.strip())
                
            knoxssResponse.Code = str(resp.status_code)
            
            # Try to get the JSON response
            try:
                response = json.loads(resp.text)
                knoxssResponse.XSS = str(response['XSS'])
                knoxssResponse.PoC = str(response['PoC'])
                knoxssResponse.Calls = str(response['API Call'])
                if knoxssResponse.Calls == '0':
                    knoxssResponse.Calls = 'Unknown'
                knoxssResponse.Error = str(response['Error'])
                if knoxssResponse.Error == 'API rate limit exceeded.':
                    knoxssResponse.Calls = tc.RED+'API rate limit exceeded!'+tc.RED
                    rateLimitExceeded = True
                knoxssResponse.POSTData = str(response['POST Data'])
                
            except Exception as e:
                # The response probably wasn't JSON, so check the response message
                if resp.text.strip() == 'Incorrect API key.':
                    print(colored('The provided API Key is invalid!', 'red'))
                    rateLimitExceeded = True
                    knoxssResponse.Calls = tc.RED+'Incorrect API key: '+tc.NORMAL+API_KEY
                else:
                    print(colored('Something went wrong: ' + resp.text.strip(),'red'))
                        
            if knoxssResponse.Calls != 'Unknown':
                latestApiCalls = knoxssResponse.Calls
                 
        except Exception as e:
            knoxssResponse.Error = 'FAIL'
            print(colored(':( There was a problem calling KNOXSS API: ' + str(e), 'red'))
            
    except Exception as e:
        print(colored('ERROR knoxss 1:  ' + str(e), 'red'))

def processInput():
    global urlPassed, latestApiCalls, stopProgram, rateLimitExceeded
    try:
        latestApiCalls = 'Unknown'
        
        # If the -i (--input) can be a standard file (text file with URLs per line),
        # if the value passed is not a valid file, then assume it is an individual URL
        inputArg = args.input
        urlPassed = False
        try:
            inputFile = open(inputArg, 'r')
            firstLine = inputFile.readline()
        except IOError:
            urlPassed = True
        except Exception as e:
            print(colored('ERROR processInput 2: ' + str(e), 'red'))
        
        if verbose():
            showOptions()
        
        print(colored('Calling KNOXSS API...\n', 'cyan'))
        if urlPassed:
            processUrl(inputArg)
        else: # It's a file of URLs
            try:
                inputFile = open(inputArg, 'r')
                with inputFile as f:
                    if not stopProgram:
                        p = mp.Pool(args.processes)
                        p.map(processUrl, f)
                        p.close()
                        p.join()
                inputFile.close()
            except Exception as e:
                print(colored('ERROR processInput 3: ' + str(e), 'red'))
                
    except Exception as e:
        print(colored('ERROR processInput 1: ' + str(e), 'red'))

def processOutput(target, method, knoxssResponse):
    global latestApiCalls, successCount, outFile
    try:
        if knoxssResponse.Error != 'FAIL':
            if knoxssResponse.Calls != 'Unknown':
                latestApiCalls =  knoxssResponse.Calls
                
            if knoxssResponse.Error != 'none':
                if not args.success_only:
                    print(colored('[ ERR! ] - (' + method + ')  ' + target + '  {' + knoxssResponse.Error + '}', 'red'))
            else:
                if knoxssResponse.XSS == 'true':
                    xssText = '[ XSS! ] - (' + method + ')  ' + knoxssResponse.PoC
                    print(colored(xssText, 'green'))
                    successCount = successCount + 1
                    if fileIsOpen:
                        outFile.write(xssText + '\n')
                else:
                    if not args.success_only:
                        print(colored('[ SAFE ] - (' + method + ')  ' + target, 'yellow'))
                    
    except Exception as e:
        print(colored('ERROR showOutput 1: ' + str(e), 'red'))

# Process one URL        
def processUrl(target):
    
    global stopProgram, rateLimitExceeded
    
    try:
        if not stopProgram and not rateLimitExceeded:
            target = target.strip()
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
        else:
            os.kill(os.getpid(),SIGINT)
                   
    except Exception as e:
        print(colored('ERROR processUrl 1: ' + str(e), 'red'))

# Validate the -p argument 
def processes_type(x):
    x = int(x) 
    if x < 1 or x > 5:
        raise argparse.ArgumentTypeError('The number of processes must be between 1 and 5')     
    return x
                                
# Run knoXnl
if __name__ == '__main__':

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
        required=True,
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
        '-X',
        '--http-method',
        action='store',
        help='Which HTTP method to use, values GET, POST or BOTH (default: GET). If BOTH is chosen, then a GET call will be made, followed by a POST.',
        default='GET',
        choices=['GET','POST','BOTH']
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
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
    args = parser.parse_args()

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
        print(colored('\nAPI calls made so far today - ' + latestApiCalls + '\n', 'cyan'))
        
        # Report if any successful XSS was found this time
        if successCount > 0:
            print(colored('🤘 '+str(successCount)+' successful XSS found! 🤘\n','green'))
        else:
            print(colored('No successful XSS found... better luck next time! 🤘\n','cyan'))

        # If the output was sent to a file, close the file
        if fileIsOpen:
            try:
                outFile.close()
            except Exception as e:
                print(colored("ERROR: Unable to close output file: " + str(e), "red"))

    except Exception as e:
        print(colored('ERROR main 1: ' + str(e), 'red'))
