## Changelog

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
