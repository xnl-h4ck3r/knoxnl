## Changelog

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
