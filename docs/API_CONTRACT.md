# Studyn Anki Sync API contract — schema v1

Default base URL: `https://studyn.org/api/v1/anki`

All responses use JSON. Device tokens are opaque and must only be stored as
hashes by the server.

## Start device authorization

`POST /device-authorizations`

```json
{
  "deviceName": "DESKTOP-ABC",
  "addonVersion": "0.3.0",
  "ankiVersion": "25.09.4"
}
```

`201` response:

```json
{
  "deviceCode": "opaque-device-code",
  "userCode": "ABCD-EFGH",
  "verificationUri": "https://studyn.org/anki/connect",
  "verificationUriComplete": "https://studyn.org/anki/connect?code=ABCD-EFGH",
  "expiresIn": 600,
  "interval": 5
}
```

## Exchange the device code

`POST /token`

```json
{ "deviceCode": "opaque-device-code" }
```

While authorization is pending, return `400`:

```json
{ "error": "authorization_pending" }
```

After approval, return `200`:

```json
{
  "accessToken": "opaque-256-bit-token",
  "deviceId": "device-id",
  "displayName": "Studyn User"
}
```

The add-on also recognizes `slow_down`, `expired_token`, and `access_denied`.

## Synchronize

`POST /sync`

Header: `Authorization: Bearer <accessToken>`

```json
{
  "schemaVersion": 1,
  "syncId": "UUID",
  "collectedAt": "2026-08-10T22:00:00+00:00",
  "dayStartsAtHour": 4,
  "addonVersion": "0.3.0",
  "ankiVersion": "25.09.4",
  "range": {
    "start": "2026-07-11",
    "end": "2026-08-10"
  },
  "days": [
    {
      "date": "2026-08-10",
      "reviews": 214,
      "reviewTimeMs": 7340000,
      "againCount": 22,
      "hardCount": 31,
      "goodCount": 149,
      "easyCount": 12
    }
  ],
  "summary": {
    "currentStreak": 18,
    "lifetimeReviews": 48120,
    "lifetimeReviewTimeMs": 918200000
  }
}
```

The user is always derived from the token. `syncId` must have a unique index per
device or user. The range is authoritative: user records within the range that
are absent from `days` must be removed.

`200` response:

```json
{
  "acceptedDays": 24,
  "syncedAt": "2026-08-10T22:00:02+00:00"
}
```

## Revoke a device

`DELETE /devices/:deviceId`

Header: `Authorization: Bearer <accessToken>`

Return `200` or `204`. The token must stop working immediately.

## Recommended limits

- 730 days per sync;
- 10 syncs per minute per device;
- 2 MiB per payload;
- `dayStartsAtHour` between 0 and 23;
- non-negative integer counters;
- HTTPS required outside the local development environment.
