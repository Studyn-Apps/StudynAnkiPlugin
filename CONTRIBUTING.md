# Contributing

Thank you for contributing to Studyn Anki Sync.

## Local development

The add-on runtime only uses the Python standard library. Validate a change
with:

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

The package is generated in `dist/`. To test the connection without using the
official API, run:

```powershell
python tools/mock_api.py
```

Then configure `http://127.0.0.1:8765/api/v1/anki` in **Tools > Studyn >
Configure server**.

## Pull requests

- Never include `user_files/credentials.json`, tokens, or real Anki data.
- Preserve the aggregate-only contract. Card, deck, and answer content must not
  be collected.
- Add or update tests when behavior changes.
- Run the complete test suite before opening a pull request.

## Releases

1. Update `ADDON_VERSION` in `studyn/version.py` and `version` in
   `manifest.json`.
2. Merge the change.
3. Create and push a matching tag, for example `v0.1.2`.

The release workflow verifies the version, runs the tests, builds the
`.ankiaddon`, and publishes it automatically to GitHub Releases.
