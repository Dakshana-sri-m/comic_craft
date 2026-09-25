"""
Routes - FastAPI Route Handlers for ComicCraft.
Manages all routing, user input processing, AI workflow integration,
and template rendering.
"""
import json
import traceback

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path

from app.main import templates, EXPORTS_DIR, BASE_DIR
from app.schemas import PromptRequest
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    Render the homepage with the comic creation form.
    Users can input story prompt, character name, setting, tone, and art style.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(default="Hero"),
    setting: str = Form(default="forest"),
    tone: str = Form(default="dramatic"),
    art_style: str = Form(default="anime")
):
    """
    Handle form-based comic generation.
    Processes user input, generates comic outline, story, images,
    builds layout, and exports PDF.
    """
    try:
        # Step 1: Generate comic outline using Gemini Flash
        print(f"[ComicCraft] Generating outline for: {story_prompt[:50]}...")
        outline = generate_outline(story_prompt, character_name, setting, tone, art_style)
        print(f"[ComicCraft] Outline generated with {len(outline)} panels")

        # Step 2: Generate full story using Gemini Pro
        print("[ComicCraft] Generating story narration...")
        full_story = generate_story(outline, character_name, tone)
        print(f"[ComicCraft] Story generated ({len(full_story)} chars)")

        # Step 3: Generate images for each panel
        print("[ComicCraft] Generating panel images...")
        images = []
        for panel in outline:
            img_path = generate_image(
                panel.get("image_prompt", ""),
                panel.get("panel_number", 1)
            )
            images.append(img_path)
            print(f"[ComicCraft] Image generated for panel {panel.get('panel_number')}")

        # Step 4: Build comic layout
        print("[ComicCraft] Building comic layout...")
        layout = build_comic_layout(outline, images, full_story)

        # Step 5: Generate PDF
        print("[ComicCraft] Generating PDF...")
        pdf_title = f"{character_name}'s Adventure"
        pdf_path = save_pdf(layout, pdf_title)
        print(f"[ComicCraft] PDF saved at: {pdf_path}")

        # Render comic preview
        return templates.TemplateResponse("comic_preview.html", {
            "request": request,
            "layout": layout,
            "pdf_path": pdf_path,
            "story_prompt": story_prompt,
            "character_name": character_name
        })

    except Exception as e:
        print(f"[ComicCraft] Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {str(e)}")


@router.post("/generate-comic/json", response_class=JSONResponse)
async def generate_comic_json(prompt_request: PromptRequest):
    """
    Handle JSON-based comic generation via API.
    Returns JSON response with layout data and PDF path.
    """
    try:
        # Step 1: Generate comic outline
        outline = generate_outline(
            prompt_request.story_prompt,
            prompt_request.character_name,
            prompt_request.setting,
            prompt_request.tone,
            prompt_request.art_style
        )

        # Step 2: Generate full story
        full_story = generate_story(
            outline,
            prompt_request.character_name,
            prompt_request.tone
        )

        # Step 3: Generate images
        images = []
        for panel in outline:
            img_path = generate_image(
                panel.get("image_prompt", ""),
                panel.get("panel_number", 1)
            )
            images.append(img_path)

        # Step 4: Build layout
        layout = build_comic_layout(outline, images, full_story)

        # Step 5: Generate PDF
        pdf_title = f"{prompt_request.character_name}'s Adventure"
        pdf_path = save_pdf(layout, pdf_title)

        return JSONResponse(content={
            "status": "success",
            "layout": layout,
            "pdf_path": pdf_path,
            "message": "Comic generated successfully!"
        })

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON input: {str(e)}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {str(e)}")


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    """
    Display the export success confirmation page.
    """
    return templates.TemplateResponse("export_success.html", {"request": request})


@router.get("/download-pdf")
async def download_pdf(path: str):
    """
    Download a generated PDF file.
    """
    try:
        # Security: ensure the path is within our exports directory
        pdf_path = BASE_DIR / path.lstrip('/')
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        if EXPORTS_DIR not in pdf_path.parents and pdf_path.parent != EXPORTS_DIR:
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(
            str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/test-image", response_class=HTMLResponse)
async def test_image(request: Request, prompt: str = "A brave hero standing on a mountain top at sunset, anime style, dramatic lighting"):
    """
    Developer utility route to test image generation.
    """
    try:
        image_path = generate_image(prompt, panel_number=0)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "test_image": image_path,
            "test_prompt": prompt
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image test failed: {str(e)}")
