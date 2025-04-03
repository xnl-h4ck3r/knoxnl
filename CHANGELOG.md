## Changelog

- 4.11

  - Changed

    - BUG FIX: When processing a file and it's complete, a discord message was only sent when finished but incomplete. It should also be sent when finished and the whole file was completed.
    - Make discord notifications prettier.

- 4.10

  - New

    - Allow the `-r`/`--retries` to be set to zero which will mean it will not try to sleep or retry any links if there are problems with the API.

  - Changed

    - BUG FIX: When the program sleeps for 10 seconds, the KNOXSS error wasn't shown for other thread completing before pausing.

- v4.9

  - New
    - Add `DISCORD_WEBHOOK_COMPLETE` to `config.yml` to specify Discord webhook URL for completion notifications (only if the input was a file). If a webhook has been given, details of a completion (whether finished completely or stopped in error) will be sent to Discord. This can obviously be the same value as `DISCORD_WEBHOOK` if required.
    - Add `-dwc`/`--discord-webhook-complete` argument. This can be passed in the command to specify a Discord webhook Completion webhook and will override the value in the `config.yml` file.
    - BUG FIX: Add the `-dw`/`--discord-webhook` argument to the `README`, which was missing.

- v4.8

  - New

    - Add argument `-fn`/`--force-new`. The Force New feature of the KNOXSS API is new in v4. Passing the argument forces KNOXSS to do a new scan instead of getting cached results.
    - Add argument `-rl`/`--runtime-log`. The Runtime Log feature of the KNOXSS API is new in v4. Passing the argument provides a live runtime log of the KNOXSS scan.
    - Add argument `-nt`/`--no-todo` to not create a `.todo` file if the input file is not completed because of errors.
    - If the "Error" in the KNOXSS response included the text "please retry" then it will be retried, and therefore added to the .todo file if stopped.

  - Changed

    - Change references of `https://brutelogic.com.br/xss.php` to `https://x55.is/brutelogic/xss.php` in the README.

- v4.7

  - Changed

    - Change all references of knoxss.me to knoxss.pro

- v4.6

  - Changed

    - Changed the response of `[ SAFE ]` to `[ NONE ]` because just because the service doesn't find XSS, it doesn't necessarily mean XSS is impossible on that URL.
    - Remove the `-afb` argument because this is no longer used in the API and is done automatically.

- v4.5

  - New

    - In the output `API calls made so far today`, also add the API limit reset time, if known.

  - Changed

    - Fix the bug that shows `:( There was a problem calling KNOXSS API: local variable 'resp' referenced before assignment` in certain situations where the KNOXSS API has initially timed out.
    - Remove `argparse` from `setup.py` because it is a Python standard module.

- v4.4

  - Changed

    - Fix a stupid bug I left in the last update while trying to test!

- v4.3

  - New

    - Add new argument `-up`/`--update` to easily update the program to the latest version.
    - Add new argument `-sb`/`--skip-blocked` to determine whether any URLs wil be skipped if they have resulted in that many 403 responses from the target. This was previously done all the time for more than 5 blocks for a scheme+(sub)domain, bit will only be done if this argument is passed with a value greater than zero. This is useful if you know there is a WAF in place.
    - If there is a problem with the `session` object before a call is even made to the KNOXSS API, catch the error, display to the user, and set the `knoxssResponse.Error` to `Some kind of network error occurred before calling KNOXSS`.
    - Save a new file `.apireset` to the default config directory (e.g. `~/.config/knoxnl/`) if a request is returned that has and `API Call` value starting with `1/`. The file will contain the `Timestamp` from the response, converted to the users timezone and increased by 24 hours and 5 minutes. This will be the rough time the API limit will be reset.
    - Add new argument `-pur`/`--pause-until-reset`. If passed, and the `.apireset` file exists, then when the API limit is reached, it will pause until 24 hours after the first request (when the limit is reset) and then continue again.
    - Display the API Limit Reset time from the `.apireset` file if it exists. The file will be deleted if the timestamp in the file is over 24 hours ago.
    - If the `-o`/`--output` value includes a directory, then caused error `[Errno 2] No such file or directory:`. The directory will now be created if it doesn't exist. The `.todo` file will also be created in that same directory.
    - Add Timestamp to the KNOXSS API response object and retrieve from the KNOXSS JSON response.
    - Add a Disclaimer to the README and the tool banner.
    - URL encode any `+` characters in the data for a POST request too.
    - Show stats when the program ends. This will show the number of requests made to the API, the number of successful, safe, error and skipped.

  - Changed

    - Only add the method+scheme+domain/domain to the blocked list and start skipping if there have been more than the number of occurrences specified by `-skip`/`--skip-blocked` (only if greater than zero).
    - Change the error message `Target is blocking KNOXSS IP` to `Target returned a "403 Forbidden". There could be WAF in place.`.
    - When getting the response, and there is no JSON, set the `knoxssResponse.Error` to `knoxssResponseError` instead of `none`. When the KNOXSS returns a response for a non-vulnerable URL, the default value of `knoxssResponse.Error` will be `none`. It needs to be different so isn't accidentally shown as `SAFE`.

- v4.2

  - Changed

    - BUG FIX: `&` were not being encoded since the version 4.1

- v4.1

  - New

    - Add arg `-r`/`--retries` for the number of times to retry when having issues connecting to the KNOXSS API (default: 3)
    - Add arg `ri`/`--retry-interval` for how many seconds to wait before retrying when having issues connecting to the KNOXSS API (default: 30 seconds)
    - Add arg `rb`/`--rety-backoff` for the backoff factor used when retrying when having issues connecting to the KNOXSS API (default: 1.5). For example, with defaults, first time will wait for 30 seconds, 2nd time will be 45 (30 x 1.5) seconds, etc.
    - Check for the runtime error `Response ended prematurely` when sending to the API. This can happen if the user is using a VPN, which the KNOXSS servers don't seem to like.
    - If a scheme and domain have been flagged as blocked already, skip other URLs with the same. Include `from urllib.parse import urlparse` and add `urlparse3` to `setup.py` to achieve this.
    - URL encode any `+` characters in the target URL so they don't get changed to spaces.

  - Changed

    - Change the error `The target website timed out` to `The KNOXSS API timed out getting the response (consider changing -t value)`
    - Change the error `The target dropped the connection.` to `The KNOXSS API dropped the connection.`
    - Set the default timeout limit for requests to the KNOXSS API to 600 seconds. The previous default was 180, but this has been resulting in many timeouts as the server response can take a lot longer for some URLs.
    - If you set `-t`/`--timeout` to 0, it will not request a timeout at all when calling the KNOXSS API.
    - When adding a blocked domain to the set, include the scheme too because there have been examples where a target blocks KNOXSS for `https://target.com`, but not `http://target.com`.

- v4.0

  - New

    - Add `long_description_content_type` to `setup.py` to upload to PyPi
    - Add `knxonl` to `PyPi` so can be installed with `pip install knoxnl`
    - Include a NOTE in the `README` to put a URL in quotes when passing as input because the shell can interpret the `&` character as an instruction to run a background task.
    - If a `Read timed out` error happens then the target timed out, but could work again later. The target URL will be added back to the end of the list to try again later (or be written to the `.todo` file).

  - Changed

    - If the input file ends with `.YYYYMMDD_HHMMSS.todo` then remove that part before adding it for the new `.todo` file.
    - When an input URL contains unicode characters, it can cause an error from the API like `'latin-1' codec can't encode characters in position 41-41: Body ('�') is not valid Latin-1`. When posting to the API, use `data.encode('utf-8')` to send it encoded in UTF-8.
    - Ensure that the current URL is removed from the list written to the `.todo` file if it is an error with the target.

- v3.4

  - Changed

    - Fix a bug that causes the error `ERROR showOutput 1: '_io.TextIOWrapper' object has no attribute 'print'` when writing to the output file.

- v3.3

  - Changed

    - If input from a file is a blank line, just ignore instead of raising an error.
    - Fix a bug when using `knoxnl` from Burps Piper. Only try writing the `.todo` file if a file was passed.

- v3.2

  - Fix bug that was stopping `--version` argument working

- v3.1

  - New

    - When installing knoxnl, if the config.yml already exists then it will keep that one and create `config.yml.NEW` in case you need to replace the old config.

- v3.0

  - New

    - The `.todo` file will also be written if `Ctrl-C` is used to exit.
    - Show the current version of the tool in the banner, and whether it is the latest, or outdated.
    - Check for `urllib3` error mentioning `Temporary failure in name resolution`. This implies the users internet connection has been lost so we will stop processing.
    - Check for `urllib3` error mentioning `Failed to establish a new connection`. This implies the machine is running low on memory.
    - Add `Config file path` to data shown when `-v` is passed.
    - Sometimes when you call KNOXSS API, you will get the error `Expiration time reset, please try again.`. f this happens, the same request will be made again one more time.
    - Add a HTTPAdapter to retry if the request to the API returns status code 429, 500, 502, 503 or 504
    - Add `TOOO` section to README.md
    - If a file is passed as input, show how many targets knoxnl is running for.
    - If a message from the KNOXSS API indicated that the target is blocking KNOXSS, then a list of domains that are blocking will be displayed at the end.

  - Changed

    - If the `API_KEY` value is blank in `config.yml`, make sure the error is displayed correctly. Also add the following message to the error message displayed: `Don't forget to generate and SAVE your API key before using it here!`
    - Check for `Invalid or expired API key.` as-well as `Incorrect API key.` and add the following text to the error message displayed: `Check if your subscription is still active, or if you forgot to save your current API key.`

- v2.10

  - New

    - If a URL is provided without a scheme, then add `https://` as default and warn the user.
    - Add `*.todo` to `.gitignore` file.

  - Changed

    - The `.todo` file will not just be written if the `-o` option is used. If an input file is passed then when the APi Rate Limit is hit, or the Service Unavailable message is given, the remaining URLs will be written to a `.todo` file.
    - The `.todo` file will be named with the name of the input file plus a timestamp, e.g. `inputfile.YYYMMDD_HHMMSS.todo`. It was previously the same as the output file name plus `.todo`.
    - Limit the number of successful API calls made per minute (requested by @KN0X55).
    - Fix a bug that sometimes prevented the `API calls made so far today` being displayed.
    - If the message `service unavailable` is returned from the API, the process will stop, and the `.todo` file will be written.
    - Show more specific error messages.

- v2.9

  - New

    - Add `DISCORD_WEBHOOK` to `config.yml` to specify Discord webhook URL for alerts. If a webhook has been given, details of a successful XSS will be sent to Discord.
    - Add `-dw`/`--discord-webhook` argument. This can be passed in the command to specify a Discord webhook and will override the value in the `config.yml` file.

- v2.8

  - New

    - Add `--version` argument to see the current version of knoxnl.

- v2.7

  - Changed

    - Back out changes from v2.3 that changed the processing of a file of URLs by running a batch of 1-5 (determines by the `-p` argument) at a time per minute. This has caused the messages to be incorrect when running for a file or URLs.

- v2.6

  - Changed

    - Changes to prevent `SyntaxWarning: invalid escape sequence` errors when Python 3.12 is used.

- v2.5

  - Changed

    - Fix a bug from [Issue #5](https://github.com/xnl-h4ck3r/knoxnl/issues/5) that prevented output being written.

- v2.4

  - Changed

    - Change the default KNOXSS API URL to the new version after the upgrade.

- v2.3

  - Changes

    - Change the processing of a file of URLs by running a batch of 1-5 (determines by the `-p` argument) at a time per minute. This is required by the KNOXSS API, and will result is getting blocked by their WAF if not followed.
    - Change the number of the daily limit of KNOXSS API calls from 3335 to 5000 in README. This changed after a KNOXSS server upgrade.
    - Show a specific error if the API rate limit is reached, and also if the user gets 403 from the API

- v2.2

  - Changed

    - Sometimes the console can't display unicode characters. When displaying strings with the emoji 🤘, if an error occurs, try writing without.
    - Change description for setting up with Piper to clarify the Linux way is also for Windows if NOT using WSL.

- v2.1

  - Changed

    - Remove code that encodes the whole URL as this prevents successful XSS being found in some cases.

- v2.0

  - New

    - Improve installation method to allow `pip` and `pipx`.

  - Changed

    - Only output HTML with `Something went wrong:` message if the error is from `knoxss``. Don't output messages like when there is no internet connection.

- v1.5

  - New

    - Added argument `-bp`/`--burp-piper` which can be used if calling from the Burp Piper extension.

- v1.4

  - New

    - Add argument `-pd`/`--post-data`. If a POST request is made, this is the POST data passed. It must be in the format `'param1=value&param2=value&param3=value'`. If this isn't passed and query string parameters are used, then these will be used as POST data if POST Method is requested.

  - Changed

    - Fix a bug that was incorrectly formatting POST requests when using the URL query string as Post data.
    - When showing Error results, remove the query string from the URL and show post data in `[]` after.
    - When `-v` is used and settings are displayed, clarify when a file is used for input, e.g. add ` (FILE)` to the name.

- v1.3

  - New

    - If a file is passed as input and the `-o` \ `--output` argument is passed then if the KNOXSS API rate limit is reached before checking all URLs, all unchecked URLs will be written to a file with the same location and name as the output file, but with a `.todo` suffix. This file can then be renamed and used as input when you are allowed to make API requests again.

- v1.2

  - New

    - Add argument `-oa`/`--output-all`. If passed, all results will be output to the file, not just successful one's.
    - Show the current API calls and limit in the CLI at the end of each line, e.g. `[1337/3335]`.
    - Try to close the output file before ending when someone presses Ctrl-C.

  - Changed

    - Include `pyaml` in the `setup.py` file as this is required.

- v1.1

  - Changed

    - Small improvements to display some errors in a better way

- v1.0

  - Changed

    - When URL is passed to the API in POST data, after encoding & to %26 characters, URL encode the whole URL. This still works as before, but also resolves some issues with URLs that caused an InvalidChunkLength error.

- v0.1

  - Initial release
