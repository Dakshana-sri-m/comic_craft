"""
Gemini Pro - Comic Story Narration and Dialogue Generator.
Uses Google Gemini 1.5 Pro to create detailed comic narration and character dialogues.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini Pro model
model = genai.GenerativeModel("gemini-1.5-pro")


def generate_story(outline: list, character_name: str = "Hero",
                   tone: str = "dramatic") -> str:
    """
    Generate full comic story narration and dialogue from panel outlines.

    Args:
        outline: List of panel outline dictionaries from gemini_flash.generate_outline()
        character_name: Name of the main character
        tone: Story tone (dramatic, funny, poetic, light-hearted)

    Returns:
        Formatted string containing the complete comic story with narration
        and dialogues for all panels.
    """
    # Build outline text for the prompt
    outline_text = ""
    for panel in outline:
        outline_text += f"""
Panel {panel['panel_number']}: {panel['title']}
Scene: {panel['scene_description']}
---
"""

    prompt = f"""You are a professional comic book writer specializing in {tone} storytelling. 
Based on the following 5-panel comic outline, write a complete comic story with engaging narration and character dialogues.

Main Character: {character_name}
Tone: {tone}

OUTLINE:
{outline_text}

For EACH panel, write:
1. **Caption**: A brief atmospheric description (1-2 sentences) that sets the mood
2. **Narration**: A detailed narrative describing the action, emotions, and events (3-5 sentences)
3. **Dialogue** (if applicable): Character speech in quotes with character names

Format each panel clearly as:

PANEL [number]: [title]
Caption: [atmospheric caption]
Narration: [detailed narration]
Dialogue: [character dialogues if any]

Write in a vivid, engaging style appropriate for a {tone} comic book. Make the story flow naturally from panel to panel with a clear beginning, middle, and end.
"""

    try:
        response = model.generate_content(prompt)
        story_text = response.text.strip()
        return story_text

    except Exception as e:
        print(f"Error generating story: {e}")
        return _generate_fallback_story(outline, character_name, tone)


def _generate_fallback_story(outline: list, character_name: str, tone: str) -> str:
    """Generate a basic fallback story if AI generation fails."""
    story_parts = []
    for panel in outline:
        part = f"""PANEL {panel['panel_number']}: {panel['title']}
Caption: The story unfolds in a {tone} fashion...
Narration: {panel['scene_description']} {character_name} takes a moment to absorb the surroundings, feeling the weight of the adventure ahead.
Dialogue: "{character_name}: 'This is where my journey continues...'"
"""
        story_parts.append(part)

    return "\n\n".join(story_parts)
