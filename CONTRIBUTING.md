# Contributing

Thank you for contributing to Studyn Anki Sync.

## Local development

The add-on runtime only uses the Python standard library. Validate a change
with:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q __init__.py studyn tests tools
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
- Ensure diagnostic changes never expose access tokens, device identifiers,
  profile identities, or card content.

Every push to `main` and every pull request runs the CI workflow on the Python
versions declared in `.github/workflows/ci.yml`.

## Releases

1. Update `ADDON_VERSION` in `studyn/version.py` and `version` in
   `manifest.json`.
2. Merge the change.
3. Move the relevant entries from `Unreleased` in `CHANGELOG.md` into the new
   version section.
4. Create and push a matching tag, for example `v0.3.0`.

The release workflow verifies the version, runs the tests, builds the
`.ankiaddon`, generates `SHA256SUMS.txt`, and publishes both files automatically
to GitHub Releases. Verify the checksum after publishing with:

```powershell
Get-FileHash .\studyn-anki-sync-0.3.0.ankiaddon -Algorithm SHA256
```
