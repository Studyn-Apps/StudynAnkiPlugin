# Security Policy

Studyn Anki Sync handles a device authorization token and aggregate study
statistics. Protecting those credentials and ensuring that card content never
leaves Anki are security requirements of this project.

## Supported versions

Security fixes are provided for the latest published version. Users should
install updates from the official
[GitHub Releases](https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/latest)
page. Older versions may no longer receive fixes.

## Report a vulnerability

Please do not disclose suspected vulnerabilities in a public issue, discussion,
pull request, or chat.

Use GitHub's private vulnerability reporting flow:

1. Open the repository's **Security** tab.
2. Select **Advisories**.
3. Choose **Report a vulnerability**.

You can also open the
[private report form](https://github.com/Studyn-Apps/StudynAnkiPlugin/security/advisories/new)
directly. If the form is unavailable, contact a repository maintainer privately
and ask for a secure reporting channel without including the vulnerability
details in the first message.

Include, when possible:

- the affected add-on and Anki versions;
- the operating system;
- clear reproduction steps;
- the expected and observed behavior;
- the potential impact;
- a minimal proof of concept with all real tokens and personal data removed.

Use **Tools > Studyn > Copy diagnostics** to collect technical environment
information. Review the text before sharing it. The report is designed to omit
tokens, device IDs, profile identities, and card content.

## Response process

Maintainers will aim to acknowledge a complete report within 7 days, validate
its impact, coordinate a fix, and agree on a responsible disclosure timeline.
Please allow time for supported users to update before publishing technical
details.

## Security boundaries

The add-on is expected to:

- send only aggregate review statistics defined in
  [docs/API_CONTRACT.md](docs/API_CONTRACT.md);
- require HTTPS except when connecting to `localhost` or `127.0.0.1`;
- keep authorization tokens inside `user_files/credentials.json`;
- exclude credential files from packages and source control;
- accept update links only from the official Studyn GitHub repository.

Requests for ordinary support, feature ideas, or non-sensitive bugs may be
opened as regular GitHub issues.
