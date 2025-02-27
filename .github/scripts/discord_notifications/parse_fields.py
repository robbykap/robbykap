from typing import Dict, List, Any


def parse_canvas_content(content: Dict[str, List[str]]) -> str:
    """Parses Canvas content into a formatted string."""
    return "\n".join(f'- **{rtype}:** {name}' for rtype in content for name in content[rtype])


def generate_fields(payload: Dict[str, Any], key: str, title: str) -> List[Dict[str, Any]]:
    """Generates formatted fields for notifications."""
    fields = []
    if payload.get(key):
        fields.append({
            "name": title,
            "value": "\n".join(f'- {item}' for item in payload[key]),
            "inline": True
        })
    return fields


def canvas_fields(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates fields specific to Canvas notifications."""
    fields = [{"name": "\u200b", "value": "\u200b", "inline": False}]

    if payload.get("deployed_content"):
        fields.append({
            "name": "Item(s) deployed",
            "value": parse_canvas_content(payload["deployed_content"]),
            "inline": True
        })

    if payload.get("content_to_review"):
        if "deployed_content" in payload:  # Add spacing only if both sections exist
            fields.append({"name": "\u200b", "value": "\u200b", "inline": True})
        fields.append({
            "name": "Updated Quiz(s)",
            "value": "\n".join(f'- **{name}:** {link}' for name, link in payload["content_to_review"]),
            "inline": True
        })

    fields.append({"name": "\u200b", "value": "\u200b", "inline": False})
    return fields


def gradescope_fields(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates fields specific to Gradescope notifications."""
    fields = [{"name": "\u200b", "value": "\u200b", "inline": False}]

    fields.extend(generate_fields(payload, "updated_images", "Updated Images"))

    if len(payload["updated_images"]) > 0:
        fields.append({"name": "\u200b", "value": "\u200b", "inline": True})

    fields.extend(generate_fields(payload, "failed_images", "Failed Images"))

    fields.append({"name": "\u200b", "value": "\u200b", "inline": False})
    return fields


def get_fields(dtype: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Returns the appropriate fields based on the notification type."""
    if dtype == "canvas":
        return canvas_fields(payload)
    elif dtype == "gradescope":
        return gradescope_fields(payload)
