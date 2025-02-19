import json
import os
import re
from datetime import datetime
import requests
from argparse import ArgumentParser


def extract_deployed_files(line: str) -> str:
    """
    Parses a deployment log line and formats it into a readable output.

    Examples:
        - "2025-02-19 20:30:01,805 - INFO - Deploying quiz Example Quiz"
          → "- **QUIZ:** Example Quiz"

    Ignores:
        - "2025-02-19 20:29:55,555 - INFO - Deploying to Canvas"
    """
    match = re.search(r"Deploying (?!to Canvas)(\w+) (.+)", line)
    return f"- **{match.group(1).upper().strip()}:** {match.group(2).strip()}" if match else ""


def extract_quizzes_to_update(line: str) -> str:
    """
    Extracts quiz name and link from a warning message.

    Examples:
        - "2025-02-19 20:17:37,227 - WARNING - Quiz Example Quiz has submissions.
           See https://byu.instructure.com/courses/20736/quizzes/511429 to save quiz."
          → "- **Example Quiz:** https://byu.instructure.com/courses/20736/quizzes/511429"
    """
    match = re.search(r"Quiz (.+?) has submissions\. See (https://\S+) to save quiz\.", line)
    return f"- **{match.group(1).strip()}:** {match.group(2).strip()}" if match else ""


def parse_message(message: str) -> tuple[list[str], list[str]]:
    """
    Parses a log message to extract deployed files and quizzes that need updating.
    """
    deployed_files = []
    quizzes_to_update = []

    for line in message.split('\n'):
        line = line.strip()

        if 'Deploying' in line:
            deploy_entry = extract_deployed_files(line)
            if deploy_entry:
                deployed_files.append(deploy_entry)

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
