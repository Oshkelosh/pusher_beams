# Pusher Beams (`pusher_beams`)

Send push notifications via Pusher Beams batch publish API.

## Overview

| | |
|---|---|
| Addon ID | `pusher_beams` |
| Category | notification |
| Channels | push |
| Version | 1.0.0 |
| Category guide | [../README.md](../README.md) |

Only **one** notification provider per channel can be active at a time.

## Enable and configure

1. Install this package under `app/addons/notifications/pusher_beams/`
2. Open **Admin → Notifications → Pusher Beams** at `/admin/notifications/pusher_beams`
3. Enter instance ID and secret key
4. Enable the provider checkbox and save

## Configuration schema

| Field | Type | Description |
|-------|------|-------------|
| `instance_id` | string | Pusher Beams instance ID |
| `secret_key` | secret | Pusher Beams secret key |

Secrets are stored in `addon_configs`, not in `.env`.

## Routes

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/notifications/pusher_beams` | Config form |
| POST | `/admin/notifications/pusher_beams/save` | Save config |

### Public API

None — core calls `send_push()` with a Beams **interest** name as `to`.

## Provider setup

1. Create a Beams instance in the [Pusher dashboard](https://dashboard.pusher.com/beams).
2. Integrate the Beams SDK in your web or mobile client.
3. Subscribe devices to named **interests** (e.g. `user-123`).
4. Copy **Instance ID** and **Secret Key** from the Beams dashboard.
5. Pass the interest name as `to` when dispatching notifications.

Uses:

```
POST https://{instance_id}.pushnotifications.pusher.com/publish_api/v1/instances/{instance_id}/push/batch_publish
```

with Bearer authentication.

Email and SMS are not supported.

## Package layout

```
pusher_beams/
├── README.md
├── addon.py
├── routes.py
└── templates/
    └── pusher_beams_config.html
```

## See also

- [Notification addon development](../README.md)
- [Oshkelosh addon guide](../../README.md)
