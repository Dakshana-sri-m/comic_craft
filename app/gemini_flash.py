"""
Gemini Flash - Comic Panel Outline Generator.
Uses Google Gemini 1.5 Flash to generate structured 5-panel comic outlines.
"""
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini Flash model
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_outline(story_prompt: str, character_name: str = "Hero",
                     setting: str = "forest", tone: str = "dramatic",
                     art_style: str = "anime") -> list:
    """
    Generate a structured 5-panel comic outline based on the user's story prompt.

    Args:
        story_prompt: Main story idea from the user
        character_name: Name of the main character
        setting: Story setting (forest, school, city, space)
        tone: Story tone (dramatic, funny, poetic, light-hearted)
        art_style: Visual art style (anime, pixel art, comic book, realistic)

    Returns:
        List of dictionaries, each containing panel_number, title,
        scene_description, and image_prompt.
    """
    prompt = f"""You are a professional comic book writer and artist. Create a detailed 5-panel comic outline based on the following details:

Story Prompt: {story_prompt}
Main Character: {character_name}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

For each panel, provide:
1. panel_number (integer 1-5)
2. title (a short, catchy panel title)
3. scene_description (a vivid 2-3 sentence description of what happens in the scene)
4. image_prompt (a detailed art prompt for generating a {art_style} style illustration of this scene. Include the character name, action, environment details, lighting, mood, and art style. Make it very descriptive for image generation.)

IMPORTANT: Return ONLY a valid JSON array with exactly 5 panel objects. No extra text, no markdown formatting, no code blocks. Just the raw JSON array.

Example format:
[
  {{
    "panel_number": 1,
    "title": "The Beginning",
    "scene_description": "Description of what happens...",
    "image_prompt": "Detailed art prompt for image generation..."
  }}
]
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Clean up the response - remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()

        # Parse JSON
        panels = json.loads(response_text)

        # Validate structure
        if not isinstance(panels, list) or len(panels) == 0:
            raise ValueError("Invalid outline format: expected a non-empty list")

        validated_panels = []
        for i, panel in enumerate(panels[:5]):  # Limit to 5 panels
            validated_panel = {
                "panel_number": panel.get("panel_number", i + 1),
                "title": panel.get("title", f"Panel {i + 1}"),
                "scene_description": panel.get("scene_description", ""),
                "image_prompt": panel.get("image_prompt", "")
            }
            validated_panels.append(validated_panel)

        return validated_panels

    except json.JSONDecodeError as e:
        print(f"JSON parsing error in outline generation: {e}")
        print(f"Raw response: {response_text[:500]}")
        # Return a fallback outline
        return _generate_fallback_outline(story_prompt, character_name, setting, tone, art_style)
    except Exception as e:
        print(f"Error generating outline: {e}")
        return _generate_fallback_outline(story_prompt, character_name, setting, tone, art_style)


def _generate_fallback_outline(story_prompt: str, character_name: str,
                                setting: str, tone: str, art_style: str) -> list:
    """Generate a basic fallback outline if AI generation fails."""
    return [
        {
            "panel_number": 1,
            "title": "The Beginning",
            "scene_description": f"{character_name} stands at the entrance of the {setting}, ready for an adventure. {story_prompt}",
            "image_prompt": f"{art_style} style illustration of {character_name} standing at the entrance of a {setting}, {tone} atmosphere, detailed background, dramatic lighting"
        },
        {
            "panel_number": 2,
            "title": "The Discovery",
            "scene_description": f"{character_name} discovers something mysterious in the {setting}.",
            "image_prompt": f"{art_style} style illustration of {character_name} discovering a mysterious object in a {setting}, {tone} mood, detailed environment"
        },
        {
            "panel_number": 3,
            "title": "The Challenge",
            "scene_description": f"{character_name} faces a great challenge that tests their courage.",
            "image_prompt": f"{art_style} style illustration of {character_name} facing a dramatic challenge in {setting}, {tone} atmosphere, action pose, dynamic composition"
        },
        {
            "panel_number": 4,
            "title": "The Climax",
            "scene_description": f"{character_name} overcomes the challenge with bravery and determination.",
            "image_prompt": f"{art_style} style illustration of {character_name} triumphantly overcoming a challenge in {setting}, {tone} mood, heroic pose, epic lighting"
        },
        {
            "panel_number": 5,
            "title": "The Resolution",
            "scene_description": f"{character_name}'s adventure comes to a satisfying end in the {setting}.",
            "image_prompt": f"{art_style} style illustration of {character_name} at peace in {setting}, {tone} atmosphere, sunset lighting, satisfying conclusion"
        }
    ]
