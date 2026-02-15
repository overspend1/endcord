import json
import os
import logging
from endcord import peripherals

logger = logging.getLogger(__name__)


class Locale:
    def __init__(self, locale_name="en"):
        self.locale_name = locale_name
        self.translations = {}
        self.load_locale(locale_name)

    def load_locale(self, locale_name):
        # Default English translations
        self.translations = {
            "connecting": "Connecting to {host}",
            "reconnecting": "Reconnecting",
            "network_error": "Network error.",
            "no_internet": "No internet connection.",
            "switch_channel_offline": "Can't switch channel when offline.",
            "sending_not_allowed_min": "Can't send a message: send at least {min} messages with the official client.",
            "thread_locked": "Can't send a message: this thread is locked.",
            "no_write_perms": "Can't send a message: No write permissions.",
            "upload_not_allowed": "Uploading is not allowed in this channel.",
            "attachments_uploading": "Attachments are still uploading.",
            "unknown_command": "Unknown command.",
            "invalid_command_args": "Invalid command arguments.",
            "restart_needed": "Restart needed for changes to take effect.",
            "unknown_settings_key": "Unknown settings key.",
            "account_standing": "Account standing: {standing}/100",
            "nothing_happens": "Nothing happens.",
            "teleport_point_set": "Teleportation point set.",
            "teleport_inside": "You're inside building. There is food here.",
            "no_media_support": "No media support.",
            "image_not_found_clipboard": "Image not found in clipboard.",
            "search_gifs": "Searching gifs",
            "cant_join_multiple_calls": "Cant join multiple calls",
            "no_members": "No members",
            "blocked_message": "Blocked message",
            "deleted_message": "Deleted message",
            "forwarded": "Forwarded",
            "poll_ended": "Poll has ended, results:",
            "winning_answer": "Winning answer",
            "votes_count": "Votes: {count} of total: {total}",
        }

        # Try to load from file
        locale_path = os.path.join("locales", f"{locale_name}.json")
        if os.path.exists(locale_path):
            try:
                with open(locale_path, "r", encoding="utf-8") as f:
                    file_translations = json.load(f)
                    self.translations.update(file_translations)
            except Exception as e:
                logger.error(f"Failed to load locale {locale_name}: {e}")

    def translate(self, key, **kwargs):
        text = self.translations.get(key, key)
        try:
            return text.format(**kwargs)
        except KeyError:
            return text


_locale = Locale()


def set_locale(locale_name):
    global _locale
    _locale = Locale(locale_name)


def _(key, **kwargs):
    return _locale.translate(key, **kwargs)
