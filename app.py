"""
AI Compliance Assessment Platform - FastAPI Backend
Implements API endpoints as specified in PRD Section 4.2
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from datetime import datetime
from pathlib import Path
import markdown
import tempfile
import uuid

# Optional PDF export support
try:
    from weasyprint import HTML
    PDF_EXPORT_AVAILABLE = True
except (ImportError, OSError) as e:
    PDF_EXPORT_AVAILABLE = False
    print(f"⚠️  Warning: PDF export unavailable. WeasyPrint could not be loaded: {e}")
    print("   The API will work without PDF export. To enable PDF export on macOS:")
    print("   brew install pango gdk-pixbuf libffi")
    print("   pip install weasyprint")

from questionnaire import QuestionnaireResponse, get_questions
from assessment_engine import AssessmentEngine
from database import (
    init_db, get_db, create_assessment, get_assessment,
    update_assessment_status, save_assessment_results
)
from sqlalchemy.orm import Session

app = FastAPI(
    title="AI Compliance Assessment Platform",
    description="Automated compliance assessment tool for EU AI Act and NIST AI RMF",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    init_db()
    print("Database initialized successfully")

# Initialize assessment engine (singleton)
assessment_engine = AssessmentEngine()


# ===== Request/Response Models =====

class AssessmentRequest(BaseModel):
    """Request model for creating a new assessment"""
    questionnaire_responses: QuestionnaireResponse


class AssessmentStatusResponse(BaseModel):
    """Response model for assessment status"""
    assessment_id: str
    status: str
    created_at: str
    processing_time_seconds: Optional[int] = None
    error_message: Optional[str] = None


# ===== Background Task for Assessment =====

def run_assessment_task(assessment_id: str, responses: QuestionnaireResponse):
    """
    Background task to run the complete assessment.
    Updates the database with results or error.
    """
    from database import SessionLocal
    db = SessionLocal()

    try:
        # Update status to processing
        update_assessment_status(db, assessment_id, "processing")

        # Run the complete 4-step assessment
        result = assessment_engine.run_complete_assessment(responses)

        # Save results to database
        save_assessment_results(
            db,
            assessment_id,
            eu_classification=result['eu_ai_act']['classification'],
            eu_requirements=result['eu_ai_act'],
            nist_requirements=result['nist_ai_rmf'],
            gaps=result['gap_analysis'],
            compliance_score=result['gap_analysis']['compliance_score'],
            cross_framework_mapping=result['cross_framework_mapping'],
            full_result=result,
            processing_time_seconds=result['processing_time_seconds']
        )

        print(f"Assessment {assessment_id} completed successfully")

    except Exception as e:
        # Save error to database
        error_msg = str(e)
        update_assessment_status(db, assessment_id, "failed", error_msg)
        print(f"Assessment {assessment_id} failed: {error_msg}")

    finally:
        db.close()


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Compliance Assessment Platform API",
        "version": "1.0.0",
        "description": "Automated compliance assessment for EU AI Act and NIST AI RMF",
        "features": {
            "pdf_export_enabled": PDF_EXPORT_AVAILABLE
        },
        "endpoints": {
            "/api/questions": "GET - Get questionnaire questions",
            "/api/assessment": "POST - Create new assessment",
            "/api/assessment/{id}": "GET - Get assessment by ID",
            "/api/assessment/{id}/status": "GET - Get assessment status",
            "/api/assessment/{id}/pdf": "GET - Export assessment as PDF" + (" (unavailable)" if not PDF_EXPORT_AVAILABLE else ""),
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Compliance Assessment Platform"
    }


@app.get("/api/questions")
async def get_questionnaire():
    """
    Get the questionnaire questions.
    Returns structured list of questions for the UI.
    """
    questions = get_questions()
    return {
        "questions": questions,
        "total": len(questions),
        "sections": list(set(q.get("section", "General") for q in questions))
    }


@app.post("/api/assessment")
async def create_new_assessment(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new assessment.
    Accepts questionnaire responses and starts assessment process in background.

    Returns:
        202 Accepted with assessment_id and status URL
    """
    try:
        # Extract organization name from responses
        org_name = f"{request.questionnaire_responses.organization_type} - {request.questionnaire_responses.industry}"

        # Create assessment record in database
        assessment = create_assessment(
            db,
            questionnaire_responses=request.questionnaire_responses.model_dump(),
            organization_name=org_name
        )

        # Start assessment in background
        background_tasks.add_task(
            run_assessment_task,
            assessment.id,
            request.questionnaire_responses
        )

        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "assessment_id": assessment.id,
                "message": "Assessment started. Check status at /api/assessment/{id}/status",
                "status_url": f"/api/assessment/{assessment.id}/status",
                "estimated_time_seconds": 90
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create assessment: {str(e)}")


@app.get("/api/assessment/{assessment_id}/status")
async def get_assessment_status(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of an assessment.

    Returns:
        Current status: pending, processing, completed, or failed
    """
    assessment = get_assessment(db, assessment_id)

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "assessment_id": assessment.id,
        "status": assessment.status,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        "processing_time_seconds": assessment.processing_time_seconds,
        "error_message": assessment.error_message,
        "compliance_score": assessment.compliance_score if assessment.status == "completed" else None
    }


@app.get("/api/assessment/{assessment_id}")
async def get_assessment_result(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the complete assessment result.

    Returns:
        Full assessment result with all sections (EU AI Act, NIST, gaps, mapping)
    """
    assessment = get_assessment(db, assessment_id)

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Assessment not completed yet. Current status: {assessment.status}"
        )

    # Return the full result
    result = assessment.full_result
    result['assessment_id'] = assessment.id
    result['organization_name'] = assessment.organization_name

    return result


@app.get("/api/assessment/{assessment_id}/pdf")
async def export_assessment_pdf(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Export assessment as PDF file.

    Returns:
        PDF file download
    """
    # Check if PDF export is available
    if not PDF_EXPORT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PDF export is unavailable. WeasyPrint dependencies are not installed. "
                   "On macOS, install with: brew install pango gdk-pixbuf libffi"
        )

    assessment = get_assessment(db, assessment_id)

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if assessment.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Assessment not completed yet. Current status: {assessment.status}"
        )

    try:
        # Generate markdown report
        md_content = generate_markdown_report(assessment.full_result, assessment.organization_name)

        # Convert markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'toc', 'tables']
        )

        # Add CSS styling
        css = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
                border-left: 4px solid #3498db;
                padding-left: 10px;
            }
            h3 {
                color: #7f8c8d;
                margin-top: 20px;
            }
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.9em;
                font-weight: bold;
                margin-right: 8px;
            }
            .high-risk { background-color: #e74c3c; color: white; }
            .minimal-risk { background-color: #2ecc71; color: white; }
            .score {
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
            }
            ul, ol {
                margin-left: 20px;
            }
            li {
                margin-bottom: 8px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #3498db;
                color: white;
            }
            .gap-card {
                border: 1px solid #ddd;
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .critical { border-left: 4px solid #e74c3c; }
            .high { border-left: 4px solid #f39c12; }
            .medium { border-left: 4px solid #f1c40f; }
            .low { border-left: 4px solid #95a5a6; }
        </style>
        """

        # Create full HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>AI Compliance Assessment Report</title>
            {css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # Create temp file for PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            HTML(string=full_html).write_pdf(f.name)
            temp_path = f.name

        filename = f"ai_compliance_assessment_{assessment_id}_{datetime.now().strftime('%Y%m%d')}.pdf"

        return FileResponse(
            path=temp_path,
            filename=filename,
            media_type="application/pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


def generate_markdown_report(result: Dict[str, Any], org_name: str) -> str:
    """Generate a markdown report from assessment result"""

    md = f"""# AI Compliance Assessment Report

**Organization:** {org_name}
**Generated:** {result.get('timestamp', 'N/A')}
**Processing Time:** {result.get('processing_time_seconds', 'N/A')} seconds

---

## Executive Summary

### EU AI Act Classification
**Risk Level:** {result['eu_ai_act']['classification']}

**Confidence:** {result['eu_ai_act']['confidence'] * 100:.1f}%

**Rationale:** {result['eu_ai_act']['rationale']}

### Compliance Score
**Overall Score:** {result['gap_analysis']['compliance_score']}/100

**Gap Breakdown:**
- Critical Gaps: {result['gap_analysis']['score_breakdown']['critical_gaps']}
- High Gaps: {result['gap_analysis']['score_breakdown']['high_gaps']}
- Medium Gaps: {result['gap_analysis']['score_breakdown']['medium_gaps']}
- Low Gaps: {result['gap_analysis']['score_breakdown']['low_gaps']}
- Implemented: {result['gap_analysis']['score_breakdown']['implemented']}

---

## EU AI Act Analysis

### Applicable Articles
{', '.join([f"Article {a}" for a in result['eu_ai_act']['applicable_articles']])}

### Requirements
"""

    for req in result['eu_ai_act']['requirements']:
        md += f"""
**Article {req['article']}: {req['title']}**
- {req['description']}
- Applies to: {req['applies_to']}
- Mandatory: {'Yes' if req['mandatory'] else 'No'}
"""

    md += f"""
---

## NIST AI RMF Analysis

### Priority Functions
{', '.join(result['nist_ai_rmf']['priority_functions'])}

### Applicable Subcategories ({len(result['nist_ai_rmf']['applicable_subcategories'])})
{', '.join(result['nist_ai_rmf']['applicable_subcategories'])}

---

## Compliance Gaps and Recommendations

"""

    for gap in result['gap_analysis']['gaps']:
        md += f"""
### {gap['requirement_title']} ({gap['framework']})

**Status:** {gap['status'].upper()} | **Severity:** {gap['severity'].upper()}

**Current State:** {gap['current_state']}

**Implementation Steps:**
"""
        for i, step in enumerate(gap['recommendations']['implementation_steps'], 1):
            md += f"{i}. {step}\n"

        md += f"""
**Examples:**
"""
        for example in gap['recommendations']['examples']:
            md += f"- {example}\n"

        md += f"""
**Effort Estimate:** {gap['recommendations']['effort_estimate']}

**Resources Needed:**
"""
        for resource in gap['recommendations']['resources_needed']:
            md += f"- {resource}\n"

        if 'common_mistakes' in gap['recommendations']:
            md += f"""
**Common Mistakes to Avoid:**
"""
            for mistake in gap['recommendations']['common_mistakes']:
                md += f"- {mistake}\n"

        md += "\n---\n"

    return md


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
