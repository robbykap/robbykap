from argparse import ArgumentParser


def main(message: str) -> str | None:
    if not message:
        return None

    # Remove Items to deploy: from the message
    message = message.replace('Items to deploy:', '')

    new_message = ""
    items = message.split('-')[1:]
    for item in items:
        item = item.strip()
        item_type, item_name = item.split(' ', 1)
        new_message += f"- {item_type.upper()} {item_name}\n"

    return new_message


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('--message', type=str)
    args = argparse.parse_args()

    print(main(args.message))