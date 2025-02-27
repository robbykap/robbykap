def get_canvas_message(payload):
    if payload.get("deployed_content") and payload.get("content_to_review"):
        return "The following items have been deployed and the following items need to be reviewed..."
    elif payload.get("deployed_content"):
        return "The following items have been deployed..."
    elif payload.get("content_to_review"):
        return "The following items need to be reviewed..."
    else:
        return None


def get_gradescope_message(payload):
    if payload.get("updated_images") and payload.get("failed_images"):
        return "The following images have been updated and the following images failed to update..."
    elif payload.get("updated_images"):
        return "The following images have been updated..."
    elif payload.get("failed_images"):
        return "The following images failed to update..."
    else:
        return None


def get_message(dtype, payload) -> str:
    """Generates a message for the notification."""
    if dtype == "canvas":
        return get_canvas_message(payload)

    elif dtype == "gradescope":
        return get_gradescope_message(payload)