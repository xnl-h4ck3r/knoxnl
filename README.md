<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/title.png"></center>

## About

This is a python wrapper around the amazing [KNOXSS API](https://knoxss.me/?page_id=2729) by Brute Logic.
To use this tool (and the underlying API), you must have a valid KNOXSS API key. Don't have one? Go visit https://knoxss.me and subscribe!
This was inspired by the ["knoxssme" tool](https://github.com/edoardottt/lit-bb-hack-tools/tree/main/knoxssme) by @edoardottt2, but developed to allow for greater options.

## Installation

knoxnl supports **Python 3**.

```
$ git clone https://github.com/xnl-h4ck3r/knoxnl.git
$ cd knoxnl
$ python setup.py install
```

## Usage

| Arg  | Long Arg                 | Description                                                                                                                                                       |
| ---- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -i   | --input                  | Input to send to KNOXSS API: a single URL, or file of URLs.                                                                                                       |
| -o   | --output                 | The file to save the successful XSS and payloads to. If the file already exist it will just be appended to unless option `-ow` is passed.                         |
| -ow  | --output-overwrite       | If the output file already exists, it will be overwritten instead of being appended to.                                                                           |
| -X   | --http-method            | Which HTTP method to use, values `GET`, `POST` or `BOTH` (default: `GET`). If `BOTH` is chosen, then a `GET` call will be made, followed by a `POST`.             |
| -H   | --headers                | Add custom headers to pass with HTTP requests. Pass in the format `'Header1:value1;\|Header2:value2'` (e.g. separate different headers with a pipe \| character). |
| -A   | --api-key                | The KNOXSS API Key to use. This will be used instead of the value in `config.yml`                                                                                 |
| -afb | --advanced-filter-bypass | If the advanced filter bypass should be used on the KNOXSS API.                                                                                                   |
| -s   | --success-only           | Only show successful XSS payloads in the CLI output.                                                                                                              |
| -p   | --processes              | Basic multithreading is done when getting requests for a file of URLs. This argument determines the number of processes (threads) used (default: 3)               |
| -t   | --timeout                | How many seconds to wait for the KNOXSS API to respond before giving up (default: 180)                                                                            |
| -v   | --verbose                | Verbose output                                                                                                                                                    |
| -h   | --help                   | show the help message and exit                                                                                                                                    |

## config.yml

The `config.yml` file has the keys which can be updated to suit your needs:

- `API_URL` - This can be set to the KNOSS API endpoint, if and when the version number is increased
- `API_KEY` - Your KNOXSS API key that you will have generated on https://knoxss.me/

## Important Notes from KNOXSS API Guidelines

- Unlike other APIs that just retrieve data from a database, KNOXSS API returns the results like the web interface, actually performing a comprehensive vulnerability scan for XSS. Since scan results are not stored by our system, they need to be generated on the fly taking several JavaScript-evaluated live tests to return them. So it's natural the data returned takes much more time to get delivered since there's a long process involved at server side.
- The API standard rate limit is 3335 requests over a 24 hours period. That means an average of **2.3 requests per minute** so please try to keep this pace **to not overload the system**.
- **Generating or Regenerating your API Key** - The API key is in your profile. If you have never generated it you need to hit the button at least once to generate it and save. Any time you need a new API key for security reasons, you can simply hit the button and regenerate it.
- **Flash Mode Mark - [XSS]** - Provide the `[XSS]` mark in any place of the target's data values to enable Flash Mode which enables KNOXSS to perform a single quick XSS Polyglot based test.

## Examples

### Basic

Pass a single URL:

```
python3 knoxnl.py -i "https://brutelogic.com.br/xss.php"
```

Or a file of URLs:

```
python3 knoxnl.py -i ~/urls.txt
```

### Detailed

Test a single URL for both GET and POST. if it is successful, the payload will be output to `output.txt`. In this case, an API key is provided, overriding any in `config.yml` if it exists. Also, the parameter value has been passed as `[XSS]` which will request the KNOXSS API to enable Flash Mode which performs a single quick XSS Polyglot based test:

```
python3 knoxnl.py -i "https://brutelogic.com.br/xss.php?b3=[XSS]" -X BOTH -o output.txt -A 93c864f5-af3a-4f6a-8b25-8662bc8b5ab6
```

Pass cookies and an auth header for a single URL, and use the Advanced Filter Bypass option:

```
python3 knoxnl.py -i "https://bugbountytarget.com?a=one&b=2" -afb -H "Cookie: sessionId=9d7127ca-8966-4ae9-b20a-c2892a2f1167; lang=en;|Authorization: Basic eyJZb3UgZGlkbid0IHRoaW5rIHRoaXMgYSBnZW51aW5lIHRva2VuIGRpZCB5b3U/ISA7KSJ9"
```

## Issues

If you come across any problems at all, or have ideas for improvements, please feel free to raise an issue on Github. If there is a problem, it will be useful if you can provide the exact command you ran and a detailed description of the problem. If possible, run with `-v` to reproduce the problem and let me know about any error messages that are given, and the KNOXSS API request/response.

## Example output

Single URL:

<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/example1.png"></center>

File of URLs checked with GET and POST:

<center><img src="https://github.com/xnl-h4ck3r/knoxnl/blob/main/knoxnl/images/example2.png"></center>

Good luck and good hunting!
If you really love the tool (or any others), or they helped you find an awesome bounty, consider [BUYING ME A COFFEE!](https://ko-fi.com/xnlh4ck3r) ☕ (I could use the caffeine!)

🤘 /XNL-h4ck3r
