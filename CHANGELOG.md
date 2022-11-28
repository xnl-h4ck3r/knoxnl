## Changelog

- v1.0

  - Changed

    - When URL is passed to the API in POST data, after encoding & to %26 characters, URL encode the whole URL. This still works as before, but also resolves some issues with URLs that caused an InvalidChunkLength error.

- v0.1

  - Initial release
