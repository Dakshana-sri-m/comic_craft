"""
Pydantic schemas for ComicCraft request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional


class PromptRequest(BaseModel):
    """Schema for JSON-based comic generation requests."""
    story_prompt: str = Field(..., description="Main story idea or prompt for the comic")
    character_name: str = Field(default="Hero", description="Name of the main character")
    setting: str = Field(default="forest", description="Story setting (e.g., forest, school, city, space)")
    tone: str = Field(default="dramatic", description="Story tone (e.g., dramatic, funny, poetic, light-hearted)")
    art_style: str = Field(default="anime", description="Art style preference (e.g., anime, pixel art, comic book, realistic)")


class PanelOutline(BaseModel):
    """Schema for a single comic panel outline."""
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class ComicPanel(BaseModel):
    """Schema for a complete comic panel with image and text."""
    panel_number: int
    title: str
    image_path: str
    text: str
    scene_description: Optional[str] = None
    image_prompt: Optional[str] = None
