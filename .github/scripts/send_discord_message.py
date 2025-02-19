import json

from datetime import datetime

import requests
from argparse import ArgumentParser

TO_REMOVE = ["Items to deploy:"]

def clean_message(message: str) -> list[str]:
    message = message.strip()
    message = message.replace("Items to deploy:", '')
    return message.split("The following quizzes need to be updated:")


def parse_message(to_deploy:str, update: str) -> tuple[list[str], list[str]]:
    deployed_files = []
    for line in to_deploy.strip().split('-'):
        if line:
            line = line.strip()
            rtype, title = line.split(' ', 1)
            deployed_files.append(f"- **{rtype.strip()}:** {title.strip()}")

    quizzes_to_update = []
    for line in update.strip().split('-'):
        if line:
            line = line.strip()
            title, link = line.split(':', 1)
            quizzes_to_update.append(f"- **{title.strip()}:** {link.strip()}")

    return deployed_files, quizzes_to_update


def get_info(message: str) -> tuple[list[str], list[str]]:
    to_deploy, update = clean_message(message)
    return parse_message(to_deploy, update)


def get_fields(author: str, branch: str, deployed_files: list[str], quizzes_to_update: list[str]) -> list[dict]:
    fields = [
        {"name": "\u200b", "value": "\u200b", "inline": False},
        {"name": "Author", "value": author, "inline": True},
        {"name": "\u200b", "value": "\u200b", "inline": True},
        {"name": "Branch", "value": branch, "inline": True},
        {"name": "\u200b", "value": "\u200b", "inline": False},
    ]

    if deployed_files:
        fields.append({"name": "Items to deploy", "value": '\n'.join(deployed_files), "inline": True})
        fields.append({"name": "\u200b", "value": "\u200b", "inline": True})

    if quizzes_to_update:
        fields.append({"name": "Updated Quiz(s)", "value": '\n'.join(quizzes_to_update), "inline": True})

    return fields


def send_request(description: str, author: str, branch: str, deployed_files: list[str] = None, quizzes_to_update: list[str] = None):
    fields = get_fields(author, branch, deployed_files, quizzes_to_update)
    payload = {
        "username": "MDXCanvas GitHub Action",
        "avatar_url": "https://digitallearning.utah.edu/_resources/images/logos/canvas/canvas-bug.png",
        "embeds": [{
            "title": "Canvas Updates",
            "description": description,
            "color": 16711764,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    print(json.dumps(payload, indent=4))
    response = requests.post("https://discord.com/api/webhooks/1339110649665425499/1ZXtpOKpCS1ExBVfcVwc3pF3Z4H_bj9LzKYW2s0Z7bsWMPwOnfOXSpVgNf-lfuaMxnng", json=payload)
    response.raise_for_status()


def main(message: str, description: str, author: str, branch: str):
    deployed_files, quizzes_to_update = get_info(message)
    send_request(description, author, branch, deployed_files, quizzes_to_update)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--message', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--author', required=True)
    parser.add_argument('--author-icon', required=True)
    parser.add_argument('--branch', required=True)
    args = parser.parse_args()

    main(args.message, args.description, args.authoricon, args.author, args.branch)
