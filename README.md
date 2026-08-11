# Studyn - Anki Sync

Official add-on for sending aggregated Anki Desktop review statistics to the
global Studyn leaderboard.

Requires Anki 2.1.50 or newer.

## Languages

The interface automatically follows the computer locale and supports Brazilian
Portuguese (`pt-BR`), English (`en-US`), and Latin American Spanish (`es-419`).
Unsupported locales fall back to English.

To override automatic detection, open **Tools > Studyn > Language**, select
`pt-BR`, `en-US`, or `es-419`, and restart Anki. The same value can be changed
directly through the `language` setting in the add-on configuration.

## What it does

- aggregates local reviews by study day;
- tracks review time, Again/Hard/Good/Easy counts, and streaks;
- connects each Anki profile to a Studyn account through the browser;
- syncs absolute snapshots without duplicating values;
- runs without blocking the interface and retries after failures;
- preserves authorization when the add-on is updated.

The add-on **does not send** card text, deck names, tags, card IDs, questions,
answers, or AnkiWeb credentials.

## Installation

1. Download the latest version from
   [GitHub Releases](https://github.com/Studyn-Apps/StudynAnkiPlugin/releases).
2. Open the downloaded file with Anki Desktop.
3. Restart Anki.
4. Open **Tools > Studyn > Connect account**.

The add-on is designed for Anki Desktop. Reviews completed in another client
will appear on the leaderboard after that history is synced with Desktop and
the add-on runs.

## Development

The add-on runtime has no external dependencies. Run the tests with:

```powershell
python -m unittest discover -s tests -v
```

Start the local mock API with:

```powershell
python tools/mock_api.py
```

In Anki, open **Tools > Studyn > Configure server** and enter:

```text
http://127.0.0.1:8765/api/v1/anki
```

If the Next.js site is running on port 80, use
`http://127.0.0.1/api/v1/anki`. For port 3000, use
`http://127.0.0.1:3000/api/v1/anki`.

Build the installable package with:

```powershell
python tools/build.py
```

## Publishing

The repository includes a GitHub Actions workflow. Pushing a tag such as
`v0.2.0` verifies the version, runs the tests, builds the `.ankiaddon`, and
publishes it automatically to GitHub Releases. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the complete release process.

## Synchronization

The add-on sends an authoritative range of days. The server must replace the
user's data within that range, including removing omitted days. This makes sync
idempotent and handles reviews that were undone in Anki.

The first connection uploads 365 days. Later syncs resend 31 days and expand
automatically after an offline period. These limits can be adjusted in
`config.json`.

## Credentials

The device token is stored in `user_files/credentials.json`, isolated by a hash
of the Anki profile name. This file must remain local and must never be included
in commits, public backups, or error reports.

See [docs/API_CONTRACT.md](docs/API_CONTRACT.md) for the backend contract.
