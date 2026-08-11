# Changelog

All notable changes to Studyn Anki Sync are documented in this file. The
project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0] - 2026-08-11

### Added

- Safe diagnostic reports that can be copied from Anki without account tokens,
  device identifiers, profile names, card content, or URL credentials.
- Automatic checks for new GitHub releases, limited to once every 24 hours by
  default, with one notification per version.
- Continuous integration for pushes and pull requests across supported Python
  runtimes.
- SHA-256 checksum file attached to every GitHub release.
- Security reporting policy and multilingual project documentation.

### Changed

- Expanded the **Tools > Studyn** menu with **Copy diagnostics**.
- Added configurable update checks and check intervals.

## [0.2.0] - 2026-08-11

### Added

- Automatic interface language detection.
- Brazilian Portuguese (`pt-BR`), English (`en-US`), and Latin American Spanish
  (`es-419`) translations.
- Manual language override under **Tools > Studyn > Language**.

## [0.1.2] - 2026-08-10

### Added

- Initial public release.
- Browser-based Studyn account connection.
- Aggregate Anki review synchronization and global leaderboard support.
- Background synchronization, retry handling, status display, and local server
  configuration.
- Per-profile credential isolation and revocation.

[Unreleased]: https://github.com/Studyn-Apps/StudynAnkiPlugin/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Studyn-Apps/StudynAnkiPlugin/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Studyn-Apps/StudynAnkiPlugin/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/tag/v0.1.2
