from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import os
import json
from datetime import datetime
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
import tempfile

from questionnaire import QuestionnaireResponse, get_questions
from generator import FrameworkGenerator

app = FastAPI(
    title="AI Governance Framework Generator",
    description="Generate customized AI governance frameworks based on your organization's context",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generator
generator = FrameworkGenerator()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Governance Framework Generator API",
        "version": "1.0.0",
        "endpoints": {
            "/questions": "GET - Get questionnaire questions",
            "/generate": "POST - Generate framework based on responses",
            "/export/pdf": "POST - Export framework as PDF",
            "/export/markdown": "POST - Export framework as Markdown",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/questions")
async def get_questionnaire():
    """Get the questionnaire questions"""
    return {
        "questions": get_questions(),
        "total": len(get_questions())
    }


@app.post("/generate")
async def generate_framework(responses: QuestionnaireResponse):
    """Generate a customized AI governance framework"""
    try:
        # Generate the framework
        result = generator.generate_framework(responses)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "framework": result["framework"],
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ExportRequest(BaseModel):
    framework: str
    format: str = "markdown"  # markdown or pdf
    metadata: Dict[str, Any] = {}


@app.post("/export/markdown")
async def export_markdown(request: ExportRequest):
    """Export framework as Markdown file"""
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            # Add metadata header
            f.write(f"<!-- Generated on {datetime.now().isoformat()} -->\n")
            f.write(f"<!-- Metadata: {json.dumps(request.metadata)} -->\n\n")
            f.write(request.framework)
            temp_path = f.name
        
        return FileResponse(
            path=temp_path,
            filename=f"ai_governance_framework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            media_type="text/markdown"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/pdf")
async def export_pdf(request: ExportRequest):
    """Export framework as PDF file"""
    try:
        # Convert markdown to HTML
        html_content = markdown.markdown(
            request.framework,
            extensions=['extra', 'codehilite', 'toc']
        )
        
        # Add CSS styling
        css = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
            }
            h3 {
                color: #7f8c8d;
            }
            ul, ol {
                margin-left: 20px;
            }
            li {
                margin-bottom: 5px;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
            }
            blockquote {
                border-left: 4px solid #3498db;
                padding-left: 15px;
                color: #666;
                font-style: italic;
            }
        </style>
        """
        
        # Create full HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>AI Governance Framework</title>
            {css}
        </head>
        <body>
            <div class="header">
                <p style="text-align: right; color: #999;">
                    Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
            {html_content}
        </body>
        </html>
        """
        
        # Create temp file for PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            HTML(string=full_html).write_pdf(f.name)
            temp_path = f.name
        
        return FileResponse(
            path=temp_path,
            filename=f"ai_governance_framework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            media_type="application/pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/frameworks")
async def list_frameworks():
    """List available framework templates"""
    frameworks_dir = Path("frameworks")
    frameworks = []
    
    if frameworks_dir.exists():
        for file in frameworks_dir.iterdir():
            if file.suffix in ['.md', '.pdf']:
                frameworks.append({
                    "name": file.stem,
                    "type": file.suffix[1:],
                    "size": file.stat().st_size
                })
    
    return {
        "frameworks": frameworks,
        "total": len(frameworks)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)