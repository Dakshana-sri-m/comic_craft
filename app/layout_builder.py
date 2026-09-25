"""
Layout Builder - Organizes comic panels into a structured layout.
Matches generated images with their corresponding story text.
"""
import re


def build_comic_layout(outline: list, images: list, full_story: str) -> list:
    """
    Organize generated images and full comic story into a structured layout.

    Args:
        outline: List of panel outline dictionaries from generate_outline()
        images: List of image file paths from generate_image()
        full_story: Complete story text from generate_story()

    Returns:
        List of dictionaries containing panel_number, title, image_path,
        text, scene_description, and image_prompt.
    """
    # Split the full story into panel sections
    panel_texts = _split_story_by_panels(full_story, len(outline))

    layout = []
    for i, panel in enumerate(outline):
        panel_data = {
            "panel_number": panel.get("panel_number", i + 1),
            "title": panel.get("title", f"Panel {i + 1}"),
            "image_path": images[i] if i < len(images) else "",
            "text": panel_texts[i] if i < len(panel_texts) else panel.get("scene_description", ""),
            "scene_description": panel.get("scene_description", ""),
            "image_prompt": panel.get("image_prompt", "")
        }
        layout.append(panel_data)

    return layout


def _split_story_by_panels(full_story: str, num_panels: int) -> list:
    """
    Split the full story text into individual panel sections.

    Args:
        full_story: Complete story text
        num_panels: Expected number of panels

    Returns:
        List of text strings, one for each panel
    """
    if not full_story:
        return ["" for _ in range(num_panels)]

    # Try splitting by panel markers
    # Match patterns like "PANEL 1:", "Panel 1:", "**PANEL 1**:", etc.
    pattern = r'(?:(?:\*\*)?PANEL\s+\d+(?:\*\*)?[:\s])'
    parts = re.split(pattern, full_story, flags=re.IGNORECASE)

    # Remove empty first part if split created one
    parts = [p.strip() for p in parts if p.strip()]

    # If we got the right number of parts, return them
    if len(parts) >= num_panels:
        return parts[:num_panels]

    # If splitting by "PANEL" didn't work, try other markers
    alt_pattern = r'(?:Panel\s+\d+\s*[-–:]\s*)'
    parts = re.split(alt_pattern, full_story, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) >= num_panels:
        return parts[:num_panels]

    # Fallback: split the story evenly
    if len(parts) == 1 or len(parts) == 0:
        # Split by double newlines
        paragraphs = [p.strip() for p in full_story.split('\n\n') if p.strip()]

        if len(paragraphs) >= num_panels:
            # Distribute paragraphs among panels
            result = []
            per_panel = max(1, len(paragraphs) // num_panels)
            for i in range(num_panels):
                start = i * per_panel
                end = start + per_panel if i < num_panels - 1 else len(paragraphs)
                result.append('\n\n'.join(paragraphs[start:end]))
            return result
        else:
            # Just pad with empty strings
            return paragraphs + ["" for _ in range(num_panels - len(paragraphs))]

    # Pad if needed
    while len(parts) < num_panels:
        parts.append("")

    return parts[:num_panels]
