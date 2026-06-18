"""Pusher Beams addon routes."""

from __future__ import annotations

from typing import Any

from app.addons.notifications.shared_routes import build_notification_routers


def _parse_pusher_beams_config_form(form: Any) -> tuple[dict[str, Any], bool]:
    return (
        {
            "instance_id": form.get("instance_id", ""),
            "secret_key": form.get("secret_key", ""),
        },
        form.get("is_enabled") == "on",
    )


admin_router, jinja_env = build_notification_routers(
    "pusher_beams",
    template_name="pusher_beams_config.html",
    page_title="Pusher Beams Settings",
    secret_keys=("secret_key",),
    parse_config_form=_parse_pusher_beams_config_form,
)
