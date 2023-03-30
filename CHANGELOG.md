## Changelog

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
