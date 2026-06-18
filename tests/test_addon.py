"""Minimal unit tests for the pusher_beams addon."""

from app.addons.notifications.pusher_beams.addon import PusherBeamsAddon


def test_addon_identity():
    assert PusherBeamsAddon.addon_id == "pusher_beams"
    assert PusherBeamsAddon.addon_category == "notification"
