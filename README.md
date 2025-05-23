<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/title.png"></center>

## About - v5.2

This is a python wrapper around the amazing [KNOXSS API](https://knoxss.pro/?page_id=2729) by Brute Logic.
To use this tool (and the underlying API), you must have a valid KNOXSS API key. Don't have one? Go visit https://knoxss.pro and subscribe!
This was inspired by the ["knoxssme" tool](https://github.com/edoardottt/lit-bb-hack-tools/tree/main/knoxssme) by @edoardottt2, but developed to allow for greater options.

**DISCLAIMER: We are not responsible for any use, and especially misuse, of this tool or the KNOXSS API**

## Installation

**NOTE: If you already have a `config.yml` file, it will not be overwritten. The file `config.yml.NEW` will be created in the same directory. If you need the new config, remove `config.yml` and rename `config.yml.NEW` back to `config.yml`.**

`knoxnl` supports **Python 3**.

Install `knoxnl` in default (global) python environment.

```bash
pip install knoxnl
```

OR

```bash
pip install git+https://github.com/xnl-h4ck3r/knoxnl.git -v
```

You can upgrade with

```bash
knoxnl -up
```

OR

```bash
pip install --upgrade knoxnl
```

### pipx

Quick setup in isolated python environment using [pipx](https://pypa.github.io/pipx/)

```bash
pipx install git+https://github.com/xnl-h4ck3r/knoxnl.git
```

## Usage

| Arg  | Long Arg                   | Description                                                                                                                                                                                                                                                                  |
| ---- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -i   | --input                    | Input to send to KNOXSS API: a single URL, or file of URLs. **NOTE: If you pass a URL, put it in quotes otherwise the shell can interpret `&` characters as instruction to run a background task.**                                                                          |
| -o   | --output                   | The file to save the successful XSS and payloads to. If the file already exist it will just be appended to unless option `-ow` is passed. If the full path doesn't exist, then any necessary directories will be created.                                                    |
| -ow  | --output-overwrite         | If the output file already exists, it will be overwritten instead of being appended to.                                                                                                                                                                                      |
| -oa  | --output-all               | Write all results to the output file, not just successful one's.                                                                                                                                                                                                             |
| -X   | --http-method              | Which HTTP method to use, values `GET`, `POST` or `BOTH` (default: `GET`). If `BOTH` is chosen, then a `GET` call will be made, followed by a `POST`.                                                                                                                        |
| -pd  | --post-data                | If a POST request is made, this is the POST data passed. It must be in the format `'param1=value&param2=value&param3=value'`. If this isn't passed and query string parameters are used, then these will be used as POST data if POST Method is requested.                   |
| -H   | --headers                  | Add custom headers to pass with HTTP requests. Pass in the format `'Header1:value1;\|Header2:value2'` (e.g. separate different headers with a pipe \| character).                                                                                                            |
| -A   | --api-key                  | The KNOXSS API Key to use. This will be used instead of the value in `config.yml`                                                                                                                                                                                            |
| -s   | --success-only             | Only show successful XSS and Open Redirect payloads in the CLI output.                                                                                                                                                                                                       |
| -p   | --processes                | Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes/threads (one per URL to check) are run per minute (default: 3). This is due to the rate limit of the KNOXSS API.                                     |
| -t   | --timeout                  | How many seconds to wait for the KNOXSS API to respond before giving up (default: 600). If set to 0, then timeout will be used.                                                                                                                                              |
| -st  | --stall-timeout            | How many seconds to wait for the KNOXSS API scan to take between steps before aborting (default: 1200 seconds).                                                                                                                                                              |
| -bp  | --burp-piper               | Use if **knoxnl** is called from the Burp Piper extension, so that a request in **Burp Suite** proxy can be tested. See the [Using in Burp Suite Proxy](#using-in-burp-suite-proxy) section below.                                                                           |
| -dw  | --discord-webhook          | The Discord Webhook to send successful XSS and Open Redirect notifications to. This will be used instead of the value in `config.yml`.                                                                                                                                       |
| -dwc | --discord-webhook-complete | The Discord Webhook to send completion notifications to when a file has been used as input (whether finished completely or stopped in error). This will be used instead of the value in `config.yml`.                                                                        |
| -r   | --retries                  | The number of times to retry when having issues connecting to the KNOXSS API (default: 3). If set to 0 then then it will not sleep or try to retry any URLs. The number of retries will also be reset every 24 hours when running for a file.                                |
| -ri  | --retry-interval           | How many seconds to wait before retrying when having issues connecting to the KNOXSS API (default: 30)                                                                                                                                                                       |
| -rb  | --retry-backoff            | The backoff factor used when retrying when having issues connecting to the KNOXSS API (default: 1.5). For example, with defaults, first time will wait for 30 seconds, 2nd time will be 45 (30 x 1.5) seconds, etc.                                                          |
| -pur | --pause-until-reset        | If the API Limit reset time is known and the API limit is reached, wait the required time until the limit is reset and continue again. The reset time is only known if knoxnl has run for request number 1 previously. The API rate limit is reset 24 hours after request 1. |
| -sb  | --skip-blocked             | The number of 403 Forbidden responses from a target (for a given HTTP method + scheme + (sub)domain) before skipping. This is useful if you know the target has a WAF. The default is zero, which means no blocking is done.                                                 |
| -fn  | --force-new                | Forces KNOXSS to do a new scan instead of getting cached results. **NOTE: Using this option will make checks SLOWER because it won't check the cache. Using the option all the time will defeat the purpose of the cache system.**                                           |
| -rl  | --runtime-log              | Provides a live runtime log of the KNOXSS scan that will be streamed. This will be prefixed with the number of the thread running, e.g. `[T2]` so the output can be tracked easier (if `-p`/`--processes` > 1).                                                              |
| -nt  | --no-todo                  | Do not create the .todo file if the input file is not completed because of issues with API, connection, etc.                                                                                                                                                                 |
| -up  | --update                   | Update knoxnl to the latest version.                                                                                                                                                                                                                                         |
| -v   | --verbose                  | Verbose output                                                                                                                                                                                                                                                               |
| -do  | --debug-output             | VerThe file to save all terminal output to a file, used for debugging. Using this option will also show the JSON response.                                                                                                                                                   |
|      | --version                  | Show current version number.                                                                                                                                                                                                                                                 |
| -h   | --help                     | show the help message and exit                                                                                                                                                                                                                                               |

## config.yml

The `config.yml` file (in the global location based on the OS, e.g. `~/.config/knoxnl/config.yml`) has the keys which can be updated to suit your needs:

- `API_URL` - This can be set to the KNOXSS API endpoint, if and when it is changed
- `API_KEY` - Your KNOXSS API key that you will have generated on https://knoxss.pro/
- `DISCORD_WEBHOOK` - Your discord webhook URL if you want to be notified of successful XSS and Open Redirect
- `DISCORD_WEBHOOK_COMPLETE` - Your discord webhook URL if you want to be notified of completion when a file has been used as input (whether finished completely or stopped in error).

## Important Notes from KNOXSS API Guidelines

- Unlike other APIs that just retrieve data from a database, KNOXSS API returns the results like the web interface, actually performing a comprehensive vulnerability scan for XSS and Open Redirects. Since scan results are not stored on our system, they need to be generated on the fly taking several JavaScript-evaluated live tests to return them. So it's natural the data returned takes much more time to get delivered since there's a long process involved at server side. To have a better idea of what the APi is actually doing, you can stream the KNOXSS runtime logs with the `-rl`/`--runtime-log` argument (this also shows using the `-v`/`--verbose` argument).
- The API standard rate limit is 5000 requests over a 24 hours period. That means an average of **2.3 requests per minute** so please try to keep this pace **to not overload the system**. Due to this rate limit, if the input is a file or URLs, then only a batch (determined by argument `-p`/`--processes`) will be run per minute.
- **Generating or Regenerating your API Key** - The API key is in your profile. If you have never generated it you need to hit the button at least once to generate it and save. Any time you need a new API key for security reasons, you can simply hit the button and regenerate it.
- **Flash Mode Mark - [XSS]** - Provide the `[XSS]` mark in any place of the target's data values to enable Flash Mode which enables KNOXSS to perform a single quick XSS Polyglot based test.

## Important Notes for knoxnl

- At the time of writing this, the daily limit of KNOXSS API calls is **5000**. If you are testing a large file of URLs, it is advisable that you use the `-o` / `--output` option to specify a file where output will be written. If you do reach the API limit, it resets 24 hours after the first API call was made. If you are processing a file of URLs, you can use the `-pur`/`--pause-until-reset` to wait until the reset happens and then continue (this is only possible if the first request was run by `knoxnl` so it could save the response timestamp).
- If you pass an input file and the API limit is reached, or the Service is Unavailable, part way through the input, all unchecked URLs will be output to an file in the same location, and with the same name as the input file, but with a `.YYYYMMDD_HHMMSS.todo` suffix. You can then rename this file and use this as input at another time. The `.todo` file will be created in the current directory unless a path is specified in the `-o`/`--output` directory, and then the `.todo` file will be created in the same directory.
- By default, only successful results are written to the output file.
- Passing argument `-oa` / `--output-all` will write **ALL** results to the output file, not just successful one's.
- The KNOXSS API has a rate limit of no more than 5 URLs processed per minute. If the rate limit is exceeded then you might end up getting blocked by their WAF, and you will not get the results you want. This rate limit is taken into account when passing a file of URLs as input. However, if you keep running for a single URL more than this per minute you wil run into problems. Please respect the rules of their API.
- When creating a file of URLs to pass as input, bear in mind that KNOXSS only looks for mainly is XSS in HTML and XML responses. However, JS, JSON and Text are not blocked from scanning due to header injection auxiliary vulnerabilities, so it can be worth passing URLs with these response types too. KNOXSS also can't search for XSS on responses that give a 403 response. When curating a file of URLs, a tool such as [urless](https://github.com/xnl-h4ck3r/urless) can also help.
- The KNOXSS only deals with POST requests with basic post data in the format `'param1=value&param2=value&param3=value'`, e.g. `Content-Type: application/x-www-form-urlencoded`.
- If the `-pd`/`--post-data` argument is not passed and a POST request is made, it will use the query string from the URL as post data if it has one.
- If a file is passed as input and POST method is required, then the post data parameters need to be provided as a query string for the URL in the file, e.g. `https://example.com?postParam1=value&postParam2-value`. If you use the `-pd`/`--post-data` with an input file then ALL URLs will use that post data.
- These are required based on the way the KNOXSS API works.

## Examples

### Basic

Pass a single URL:

**NOTE: If you pass a URL, put it in quotes otherwise the shell can interpret `&` characters as instruction to run a background task.**

```
knoxnl -i "https://x55.is/brutelogic/xss.php"
```

Or a file of URLs:

```
knoxnl -i ~/urls.txt
```

### Detailed

Test a single URL for both GET and POST. if it is successful, the payload will be output to `output.txt`. In this case, an API key is provided, overriding any in `config.yml` if it exists. Also, the parameter value has been passed as `[XSS]` which will request the KNOXSS API to enable Flash Mode which performs a single quick XSS Polyglot based test:

```
knoxnl -i "https://x55.is/brutelogic/xss.php?b3=[XSS]" -X BOTH -o output.txt -A 93c864f5-af3a-4f6a-8b25-8662bc8b5ab6
```

Test a single URL for POST and pass post body data:

```
knoxnl -i "https://x55.is/brutelogic/xss.php" -X POST -pd user=xnl -o output.txt
```

Pass cookies and an auth header for a single URL:

```
knoxnl -i "https://bugbountytarget.com?a=one&b=2" -H "Cookie: sessionId=9d7127ca-8966-4ae9-b20a-c2892a2f1167; lang=en;|Authorization: Basic eyJZb3UgZGlkbid0IHRoaW5rIHRoaXMgYSBnZW51aW5lIHRva2VuIGRpZCB5b3U/ISA7KSJ9"
```

## Using in Burp Suite Proxy

To be able to use **knoxnl** to test a request in Burp Suite Proxy, we can use it in conjunction with the amazing `Piper` extension by András Veres-Szentkirályi. Follow the steps below to set it up:

1. Go to the **BApp Store** in Burp and install the **Piper** extension.
2. Go to the **Piper** tab and click the **Context menu items** sub tab, then click the **Add** button.
3. In the **Add menu item** dialog box, enter the **Name** as `knoxnl` and change the **Can handle...** drop down to `HTTP requests only`.
4. Change both the **Minimum required number of selected items** and **Maximum allowed number of selected items** values to `1`.
5. Click the **Edit...** button for **Command** and the **Command invocation editor** dialog box should be displayed.
6. Check the **Pass HTTP headers to command** check-box.
7. If you are on a Linux machine, or Windows without WSL, do the following:
   - In the **Command line parameters** box you enter the command and arguments one line at a time.
   - You want to enter a command of `/my/path/to/python3 /my/path/to/knoxnl.py --burp-piper -X BOTH` for example, providing the full path of the `knoxnl` binary file.
   - So in the **Command line parameters** input field it would look like this:
     ```
     /my/path/to/knoxnl
     --burp-piper
     -X
     BOTH
     ```
   - You may want to add other **knoxnl** arguments too, such as `-A your_knoxss_api_key`, `-t 60`, etc. Remember to put the argument and the value on separate lines.
8. If you are on a Windows machine using WSL, do the following:
   - In the **Command line parameters** box you enter the command and arguments one line at a time.
   - You want to enter a command of `wsl -e /my/path/to/knoxnl --burp-piper -X BOTH` for example, providing the full path of the `knoxnl.py` binary file.
   - So in the **Command line parameters** input field it would look like this:
     ```
     wsl
     -e
     /my/path/to/knoxnl
     --burp-piper
     -X
     BOTH
     ```
   - You may want to add other **knoxnl** arguments too, such as `-A your_knoxss_api_key`, `-t 60`, etc. Remember to put the argument and the value on separate lines.
9. Click the **OK** button on the **Command invocation editor** dialog box.
10. Click the **OK** button on the **Edit menu item** dialog box.

Piper is now set up to be able to call **knoxnl**.

To call **knoxnl** for a particular request, follow these steps:

1. Right click on a Request and select **Extensions -> Piper -> Process 1 request -> knoxnl**.
2. A window should open with the title **Piper - knoxnl**.
3. **IMPORTANT NOTE:** This **Piper** window stays blank until the command is complete (which could be up to 180 seconds - the default value of `-t`/`--timeout`).
4. When complete, it should show the **knoxnl** output in the same way as on the command line version. Just close the window when you have finished.

With **Piper** you can also send the **knoxnl** request to a queue by selecting **Extensions -> Piper -> Add to queue**. You can then go to the **Queue** sub tab under **Piper** and see the request. Right click the request to send to **knoxnl**.

## Issues

If you come across any problems at all, or have ideas for improvements, please feel free to raise an issue on Github. If there is a problem, it will be useful if you can provide the exact command you ran and a detailed description of the problem. If possible, run with `-v` to reproduce the problem and let me know about any error messages that are given, and the KNOXSS API request/response.

## TODO

- Allow input to be piped into `knoxnl`.
- Allow a large file to be passed, and if the API limit is reached, wait until the API limit is refreshed and continue.
- Deal with downgrading HTTPS to HTTP if required.
- If a target is blocking KNOXSS, then try a few times, and if no success then skip all links for that domain, and write to a `.blocked` file.

## Example output

Single URL:

<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/example1.png"></center>

File of URLs checked with GET and POST:

<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/example2.png"></center>

Example Discord notification:

<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/discord.png"></center>

Good luck and good hunting!
If you really love the tool (or any others), or they helped you find an awesome bounty, consider [BUYING ME A COFFEE!](https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

🤘 /XNL-h4ck3r
