import json
import os
import requests

from argparse import ArgumentParser

from datetime import datetime
from typing import Dict, List, Any

from process_info import get_info
from parse_fields import get_fields
from parse_message import get_message


def hex_to_decimal(hex_color: str) -> int:
    """Converts a hex color to a decimal color."""
    hex_color = hex_color.lstrip('#')
    return int(hex_color, 16)


def get_notification(
        username: str,
        avatar_url: str,
        author: str,
        author_icon: str,
        title: str,
        branch: str,
        message: str,
        color: int,
        fields: List[Dict[str, Any]],
        footer: Dict[str, str]
) -> Dict[str, Any]:
    """Builds the notification payload."""
    return {
        "username": username,
        "avatar_url": avatar_url,
        "embeds": [{
            "author": {"name": author, "icon_url": author_icon},
            "title": title,
            "description": f'**`{branch}`**\n\n{message}',
            "color": color,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": footer
        }]
    }


def main(dtype: str, notification_info_path: str, payload_path: str, author: str, author_icon: str, branch: str):
    """Main function for sending notifications."""

    # Load the payload
    with open(payload_path, "r") as f:
        payload = json.load(f)

    # Get notification information specific to the type of notification
    notification_info = get_info(dtype, notification_info_path)

    # Build notification fields
    fields = get_fields(dtype, payload)

    # Get the message
    message = get_message(dtype, payload)

    # If there is no message or the payload was not updated, do not send a notification
    if payload["updated"] is False or not message:
        return

    # Construct the notification
    notification = get_notification(
        username=notification_info["name"],
        avatar_url=notification_info["avatar_url"],
        author=author,
        author_icon=author_icon,
        title=notification_info["title"],
        branch=branch,
        message=message,
        color=hex_to_decimal(notification_info["color"]),
        fields=fields,
        footer=notification_info["footer"]
    )

    # Fetch the webhook URL from environment variables
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise EnvironmentError("DISCORD_WEBHOOK_URL environment variable is not set.")

    # Send the request
    response = requests.post(webhook_url, json=notification)
    response.raise_for_status()


if __name__ == "__main__":
    parser = ArgumentParser(description="Send Canvas or Gradescope notifications to Discord.")
    parser.add_argument("--type", required=True, choices=["canvas", "gradescope"], help="Type of notification")
    parser.add_argument("--notification-info", required=True, help="Path to the notification info JSON file")
    parser.add_argument("--payload", required=True, help="Path to the payload JSON file")
    parser.add_argument("--author", required=True, help="Name of the author")
    parser.add_argument("--author-icon", required=True, help="URL of the author's icon")
    parser.add_argument("--branch", required=True, help="Branch name")

    args = parser.parse_args()

    main(args.type, args.notification_info, args.payload, args.author, args.author_icon, args.branch)
