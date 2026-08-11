<div align="center">
  <img src="static/logo.png" width="128" alt="Studyn logo">
  <h1>Studyn Anki Sync</h1>
  <p>Turn your Anki study activity into progress on the global Studyn leaderboard.</p>

  <p>
    <a href="https://github.com/Studyn-Apps/StudynAnkiPlugin/releases"><img src="https://img.shields.io/github/v/release/Studyn-Apps/StudynAnkiPlugin?style=flat-square" alt="Latest release"></a>
    <a href="https://github.com/Studyn-Apps/StudynAnkiPlugin/actions/workflows/release.yml"><img src="https://img.shields.io/github/actions/workflow/status/Studyn-Apps/StudynAnkiPlugin/release.yml?style=flat-square&label=release" alt="Release workflow"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/Studyn-Apps/StudynAnkiPlugin?style=flat-square" alt="MIT License"></a>
  </p>

  <p>
    <strong>English</strong> ·
    <a href="README.pt-BR.md">Português (Brasil)</a> ·
    <a href="README.es-419.md">Español (Latinoamérica)</a>
  </p>
</div>

Studyn Anki Sync is the official open-source add-on that connects Anki Desktop
to [Studyn](https://studyn.org/anki). It securely sends aggregate review
statistics so you can follow your consistency, compare progress, and join the
global ranking without exposing the content of your cards.

## Highlights

- **Global leaderboard:** your Anki activity contributes to your Studyn profile.
- **Automatic sync:** reviews are sent in the background after you study.
- **Reliable totals:** authoritative snapshots prevent duplicate statistics and
  correctly reflect undone reviews.
- **Useful metrics:** reviews, study time, Again/Hard/Good/Easy counts, lifetime
  totals, and current streak.
- **Profile-aware:** each Anki profile can be connected to its own Studyn account.
- **Localized:** automatic support for `en-US`, `pt-BR`, and `es-419`.
- **Easy support:** copy a sanitized diagnostic report directly from Anki.
- **Update alerts:** receive a notification when a new official release is available.
- **Lightweight:** no third-party Python dependencies in the add-on runtime.

## Privacy by design

Only aggregate study statistics are sent to Studyn. The add-on **never sends**:

- card text, questions, or answers;
- deck names, tags, card IDs, or note IDs;
- your AnkiWeb username or password;
- your collection database or media files.

The authorization token is stored locally in `user_files/credentials.json` and
is separated by Anki profile. You can revoke it at any time with **Tools >
Studyn > Disconnect**.

Please report security concerns privately according to [SECURITY.md](SECURITY.md).

## Requirements

- Anki Desktop 2.1.50 or newer;
- a Studyn account;
- an internet connection for account linking and synchronization.

The add-on runs on Anki Desktop. Reviews completed on AnkiMobile, AnkiDroid, or
another client are included after that review history reaches Anki Desktop and
the add-on synchronizes.

## Install

1. Download the newest `.ankiaddon` from
   [GitHub Releases](https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/latest)
   or from the [Studyn Anki page](https://studyn.org/anki).
2. Open the downloaded file with Anki Desktop and confirm the installation.
3. Restart Anki.
4. Open **Tools > Studyn > Connect account**.
5. Approve the connection in the browser window that opens.

Studyn performs the first synchronization immediately after the account is
connected. To update the add-on later, install the newer `.ankiaddon` over the
existing version; your local authorization is preserved.

## Use

The **Tools > Studyn** menu provides all add-on actions:

| Action | Purpose |
| --- | --- |
| **Connect account** | Link the current Anki profile to Studyn. |
| **Sync now** | Send the latest aggregate statistics immediately. |
| **View status** | View the account, server, last sync, and last error. |
| **Copy diagnostics** | Copy sanitized technical information for support requests. |
| **Configure server** | Change the API address, primarily for local development. |
| **Language** | Select automatic detection or a supported language. |
| **Disconnect** | Revoke the device and remove its local authorization. |

### Languages

The interface follows the computer locale by default:

- Brazilian Portuguese locales use `pt-BR`;
- Spanish locales use `es-419`;
- English and unsupported locales use `en-US`.

To override detection, open **Tools > Studyn > Language**, enter `auto`,
`en-US`, `pt-BR`, or `es-419`, then restart Anki so every menu label is updated.

## How synchronization works

The first connection uploads the previous 365 study days. Regular syncs resend
the latest 31 days and automatically extend the recovery window after a longer
offline period. Each payload contains absolute totals for a date range, making
repeated requests idempotent instead of adding the same reviews twice.

These ranges and synchronization thresholds can be adjusted in `config.json`.
See [config.md](config.md) for every available option and
[docs/API_CONTRACT.md](docs/API_CONTRACT.md) for the backend protocol.

By default, the add-on checks the official GitHub Releases API at most once
every 24 hours. It sends no Studyn credentials during this request and displays
each new-version notification only once. Set `check_for_updates` to `false` to
disable it or change `update_check_interval_hours` to adjust the interval.

## Troubleshooting

**The browser displays `Not Found` while connecting.**

Open **Tools > Studyn > Configure server** and confirm that the address points
to the API base, including `/api/v1/anki`. For local development, use
`http://127.0.0.1:3000/api/v1/anki` when the site runs on port 3000.

**The ranking has not updated yet.**

Open **Tools > Studyn > View status** to inspect the last synchronization and then
choose **Sync now**. If reviews came from another Anki client, first synchronize
that client with Anki Desktop.

**The interface is using the wrong language.**

Choose the desired locale under **Tools > Studyn > Language** and restart Anki.

For a support request, use **Tools > Studyn > Copy diagnostics** and review the
copied text before sharing it. Tokens, device IDs, profile identities, card
content, and URL credentials are excluded or redacted.

## Development

The project uses only the Python standard library at runtime. With Python 3
installed, run the test suite and build the package with:

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

The installable file is generated in `dist/`. To test without the production
API, start the included mock server:

```powershell
python tools/mock_api.py
```

Then set **Tools > Studyn > Configure server** to:

```text
http://127.0.0.1:8765/api/v1/anki
```

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before
opening a pull request, see [CHANGELOG.md](CHANGELOG.md) for version history,
and follow [SECURITY.md](SECURITY.md) for private vulnerability reports.

## Releases

Tags matching the add-on version trigger the release workflow. For example,
pushing `v0.3.1` runs the tests, builds the `.ankiaddon`, generates its SHA-256
checksum, and publishes both files to GitHub Releases. The complete maintainer checklist is in
[CONTRIBUTING.md](CONTRIBUTING.md#releases).

## License

Released under the [MIT License](LICENSE).
