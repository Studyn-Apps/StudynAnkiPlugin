# Studyn - Anki Sync

- `api_base_url`: Studyn API address. It can also be changed through **Tools >
  Studyn > Configure server**. Plain HTTP is accepted only for `localhost` and
  `127.0.0.1`.
- `language`: interface language. Use `auto` to follow the computer locale, or
  set `pt-BR`, `en-US`, or `es-419` to override it manually. Restart Anki after
  changing this value. The same setting is available through **Tools > Studyn >
  Language**.
- `automatic_sync`: enables automatic synchronization.
- `check_for_updates`: checks the official GitHub repository for new releases
  and displays a notification when one is available.
- `day_starts_at_hour`: hour at which a new study day begins.
- `initial_sync_days`: number of days sent during the first sync.
- `max_sync_days`: maximum recovery range after an offline period.
- `request_timeout_seconds`: timeout for HTTPS requests.
- `sync_days`: range resent during regular syncs.
- `sync_debounce_seconds`: idle time after a review before syncing.
- `sync_every_reviews`: forces a sync after this number of reviews.
- `update_check_interval_hours`: minimum number of hours between GitHub release
  checks, from 1 to 168. The default is 24.

Access tokens are not stored in this file. They remain local in
`user_files/credentials.json` and must not be copied or shared.
