"""
Groq Pro - Comic Story Narration and Dialogue Generator.
Uses Groq API with Llama 70B model to create detailed comic narration and character dialogues.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use a more capable model for story generation
MODEL = "llama-3.1-70b-versatile"


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
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"You are a professional comic book writer specializing in {tone} storytelling. Write vivid, engaging narratives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4096,
        )
        story_text = response.choices[0].message.content.strip()
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
