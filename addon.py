"""Pusher Beams push notification integration."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field, SecretStr

from app.addons.notifications.base import NotificationAddon
from app.addons.notifications.helpers import post_json_webhook
from app.addons.log import info, warning
from app.addons.config_serialization import dump_addon_config


class PusherBeamsConfig(BaseModel):
    instance_id: str = Field(default=..., description="Pusher Beams instance ID")
    secret_key: SecretStr = Field(default=..., description="Pusher Beams secret key")

    @classmethod
    def config_model(cls):
        return cls


class PusherBeamsAddon(NotificationAddon):
    addon_id: str = "pusher_beams"
    addon_name: str = "Pusher Beams"
    addon_description: str = "Send push notifications via Pusher Beams."
    addon_category: str = "notification"
    version: str = "1.0.0"
    is_enabled: bool = False
    supported_channels: ClassVar[list[str]] = ["push"]

    _config: Dict[str, Any] | None = None
    _instance_id: str | None = None
    _secret_key: str | None = None

    @classmethod
    def config_schema(cls):
        return PusherBeamsConfig

    async def initialize(self, config: dict) -> None:
        validated = self.config_schema()(**config)
        self._config = dump_addon_config(validated)
        self._instance_id = validated.instance_id
        self._secret_key = validated.secret_key.get_secret_value()
        self.is_enabled = True
        info("Pusher Beams", "Initialized (instance={})", self._instance_id)

    async def validate_config(self, config: dict) -> None:
        from app.core.exceptions import ValidationError

        validated = self.config_schema()(**config)
        secret_key = validated.secret_key.get_secret_value()
        if not secret_key:
            return
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"https://{validated.instance_id}.pushnotifications.pusher.com/publish_api/v1/instances/{validated.instance_id}",
                headers={"Authorization": f"Bearer {secret_key}"},
            )
        if resp.status_code == 401:
            raise ValidationError(message="Invalid secret key — check your credentials")
        if resp.status_code == 403:
            raise ValidationError(
                message="Secret key is valid but missing required permissions: publish"
            )
        if resp.status_code >= 400 and resp.status_code != 404:
            raise ValidationError(message="Pusher Beams rejected the secret key")

    async def shutdown(self) -> None:
        self._instance_id = None
        self._secret_key = None
        self.is_enabled = False

    def _publish_url(self) -> str:
        iid = self._instance_id or ""
        return (
            f"https://{iid}.pushnotifications.pusher.com/publish_api/v1/"
            f"instances/{iid}/push/batch_publish"
        )

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("email", to)

    async def send_sms(self, to: str, body: str) -> Dict[str, Any]:
        return self.channel_not_supported("sms", to)

    async def send_push(
        self,
        to: str,
        title: str,
        body: str,
        data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if not self._instance_id or not self._secret_key:
            return {"success": False, "message_id": "", "error": "Not configured", "to": to}

        notification: dict[str, Any] = {
            "title": title,
            "body": body,
        }
        if data:
            notification["data"] = {k: str(v) for k, v in data.items()}

        payload = {
            "interests": [to],
            "web": {"notification": notification},
            "apns": {"aps": {"alert": {"title": title, "body": body}}},
            "fcm": {"notification": {"title": title, "body": body}},
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    self._publish_url(),
                    headers={
                        "Authorization": f"Bearer {self._secret_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                result = resp.json()
                publish_id = result.get("publishId", result.get("publish_id", ""))
                return {
                    "success": True,
                    "message_id": publish_id,
                    "to": to,
                }
        except Exception as exc:
            warning("Pusher Beams", "send_push to={} error: {}", to, exc)
            return {"success": False, "message_id": "", "error": str(exc), "to": to}

    async def send_webhook(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await post_json_webhook(url, payload)
        if not result.get("success"):
            warning("Pusher Beams", "send_webhook to={} error: {}", url, result.get("error"))
        return result

    def list_public_push_config(self) -> dict[str, Any] | None:
        if not self._instance_id:
            return None
        return {"provider": self.addon_id, "config": {"instanceId": self._instance_id}}

    def get_routers(self) -> List[APIRouter]:
        return []

    def get_admin_routes(self) -> List[APIRouter]:
        from app.addons.notifications.pusher_beams.routes import admin_router

        return [admin_router]

    def get_admin_templates(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "templates")

    def get_admin_static(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "static")
