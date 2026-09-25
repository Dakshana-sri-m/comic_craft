"""
Image Generator - Comic-style Image Generation.
Uses Hugging Face Inference API with Stable Diffusion to generate comic-style illustrations.
"""
import os
import re
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Hugging Face API configuration
HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Directory for saving generated panels
BASE_DIR = Path(__file__).resolve().parent.parent
PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(text: str) -> str:
    """Convert text to a safe filename."""
    # Remove special characters and limit length
    safe = re.sub(r'[^\w\s-]', '', text.lower())
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe[:50]


def generate_image(image_prompt: str, panel_number: int = 1) -> str:
    """
    Generate a comic-style image using the Hugging Face Inference API.

    Args:
        image_prompt: Detailed prompt for image generation
        panel_number: Panel number for file naming

    Returns:
        Relative file path to the saved image (for use in HTML templates)
    """
    # Create filename
    filename = f"panel_{panel_number}_{sanitize_filename(image_prompt)}.png"
    filepath = PANELS_DIR / filename
    relative_path = f"/static/panels/{filename}"

    # Enhanced prompt for better comic-style results
    enhanced_prompt = f"{image_prompt}, high quality, detailed, vibrant colors, professional illustration"

    try:
        # Call Hugging Face Inference API
        headers = {}
        if HF_API_KEY:
            headers["Authorization"] = f"Bearer {HF_API_KEY}"

        response = httpx.post(
            HF_API_URL,
            headers=headers,
            json={
                "inputs": enhanced_prompt,
                "parameters": {
                    "width": 768,
                    "height": 512,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5
                }
            },
            timeout=120.0
        )

        if response.status_code == 200:
            # Save the image
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"Image saved: {filepath}")
            return relative_path
        else:
            print(f"HF API error (status {response.status_code}): {response.text[:200]}")
            return _generate_placeholder_image(panel_number, image_prompt)

    except Exception as e:
        print(f"Error generating image for panel {panel_number}: {e}")
        return _generate_placeholder_image(panel_number, image_prompt)


def _generate_placeholder_image(panel_number: int, prompt: str = "") -> str:
    """
    Generate a placeholder image when API is unavailable.
    Creates a styled SVG-based placeholder.
    """
    from PIL import Image, ImageDraw, ImageFont

    filename = f"panel_{panel_number}_placeholder.png"
    filepath = PANELS_DIR / filename
    relative_path = f"/static/panels/{filename}"

    # Create a visually appealing placeholder
    width, height = 768, 512
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient-like background with comic-themed colors
    colors = [
        (45, 27, 105),   # Deep purple
        (89, 50, 168),   # Purple
        (132, 76, 220),  # Light purple
        (175, 103, 255), # Lavender
        (220, 140, 255), # Pink lavender
    ]

    panel_colors = [
        [(45, 27, 105), (89, 50, 168)],
        [(168, 50, 50), (220, 103, 103)],
        [(50, 120, 168), (103, 180, 220)],
        [(50, 168, 80), (103, 220, 140)],
        [(168, 140, 50), (220, 200, 103)],
    ]

    idx = (panel_number - 1) % len(panel_colors)
    color1, color2 = panel_colors[idx]

    for y in range(height):
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Add panel number and text
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Panel number circle
    circle_x, circle_y = width // 2, height // 3
    draw.ellipse(
        [circle_x - 50, circle_y - 50, circle_x + 50, circle_y + 50],
        fill=(255, 255, 255, 180),
        outline=(255, 255, 255)
    )
    panel_text = str(panel_number)
    bbox = draw.textbbox((0, 0), panel_text, font=font_large)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        (circle_x - text_w // 2, circle_y - text_h // 2 - 5),
        panel_text, fill=(45, 27, 105), font=font_large
    )

    # Subtitle
    subtitle = f"Panel {panel_number} - AI Generated"
    bbox2 = draw.textbbox((0, 0), subtitle, font=font_small)
    sub_w = bbox2[2] - bbox2[0]
    draw.text(
        (width // 2 - sub_w // 2, height * 2 // 3),
        subtitle, fill=(255, 255, 255), font=font_small
    )

    # Truncated prompt text
    if prompt:
        short_prompt = prompt[:80] + "..." if len(prompt) > 80 else prompt
        bbox3 = draw.textbbox((0, 0), short_prompt, font=font_small)
        prompt_w = bbox3[2] - bbox3[0]
        draw.text(
            (width // 2 - prompt_w // 2, height * 2 // 3 + 35),
            short_prompt, fill=(200, 200, 255), font=font_small
        )

    img.save(filepath)
    print(f"Placeholder image saved: {filepath}")
    return relative_path
