import json
import os
import re

from datetime import datetime

import requests
from argparse import ArgumentParser


import re
from typing import List, Tuple

def extract_deployed_files(line: str) -> str:
    """
    Parses a deployed line and formats it.
    """
    rtype, title = line.strip('-').strip().split(' ', 1)
    return f"- **{rtype.strip()}:** {title.strip()}"


def extract_quizzes_to_update(line: str) -> str:
    """
    Extracts quiz name and link from a warning message.
    """
    match = re.search(r"Quiz (.+?) has submissions\. See (https://\S+) to save quiz\.", line)
    if match:
        title, link = match.groups()
        return f"- **{title}:** {link}"
    return ""

def parse_message(message: str) -> Tuple[List[str], List[str]]:
    """
    Parses a log message to extract deployed files and quizzes that need updating.
    """
    deployed_files = []
    quizzes_to_update = []
    to_deploy = False

    for line in message.split('\n'):
        line = line.strip()

        if 'INFO' in line:  # Skip INFO log lines
            continue

        if line == 'Items to deploy:':  # Start of deployed files section
            to_deploy = True
            continue

        if 'WARNING' in line:  # Start of quizzes to update section
            to_deploy = False

        if to_deploy and line.startswith('-'):
            deployed_files.append(extract_deployed_files(line))

        elif 'WARNING' in line:
            quiz_entry = extract_quizzes_to_update(line)
            if quiz_entry:
                quizzes_to_update.append(quiz_entry)

    return deployed_files, quizzes_to_update



def get_fields(deployed_files: list[str], quizzes_to_update: list[str]) -> list[dict]:
    fields = [{"name": "\u200b", "value": "\u200b", "inline": False}]

    if deployed_files:
        fields.append({"name": "Item(s) deployed", "value": '\n'.join(deployed_files), "inline": True})

    if quizzes_to_update:
        if deployed_files:  # Add spacing only if both sections exist
            fields.append({"name": "\u200b", "value": "\u200b", "inline": True})
        fields.append({"name": "Updated Quiz(s)", "value": '\n'.join(quizzes_to_update), "inline": True})

    fields.append({"name": "\u200b", "value": "\u200b", "inline": False})
    return fields


def send_request(
        author: str,
        author_icon: str,
        branch: str,
        deployed_files: list[str] = None,
        quizzes_to_update: list[str] = None
):
    fields = get_fields(deployed_files, quizzes_to_update)
    payload = {
        "username": "Canvas Notifications",
        "avatar_url": "https://digitallearning.utah.edu/_resources/images/logos/canvas/canvas-bug.png",
        "embeds": [{
            "author": {
                "name": author,
                "icon_url": author_icon
            },
            "title": "CS 110 - Course Updates",
            "description": f'**`{branch}`**'
                           f'\n'
                           f'\n'
                           f'The following branch has been merged and subsequent changes have been made or need saving...',
            "color": 16711764,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "MDXCanvas GitHub Action",
                "icon_url": "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png"
            }
        }]
    }
    print(json.dumps(payload, indent=4))
    response = requests.post(WEBOOK_URL, json=payload)
    response.raise_for_status()


def main(message: str, author: str, author_icon:str, branch: str):
    deployed_files, quizzes_to_update = parse_message(message)
    if not deployed_files and not quizzes_to_update:
        return
    send_request(author, author_icon, branch, deployed_files, quizzes_to_update)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--message', required=True)
    parser.add_argument('--author', required=True)
    parser.add_argument('--author-icon', required=True)
    parser.add_argument('--branch', required=True)
    args = parser.parse_args()

    WEBOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    main(args.message, args.author, args.author_icon, args.branch)
