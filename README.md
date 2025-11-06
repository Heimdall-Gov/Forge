# Forge 🛡️
AI Compliance Assessment Platform - Automated compliance analysis for EU AI Act and NIST AI RMF

## Overview

Forge is an automated compliance assessment tool that analyzes AI systems against the EU AI Act and NIST AI RMF. Using advanced LLM technology (Claude Sonnet 4), it provides:

- **Speed**: 90-second assessment vs. 40+ hours manual review
- **Accuracy**: LLM interprets complex legal frameworks with context awareness
- **Actionability**: Identifies specific gaps with detailed implementation guidance
- **Transparency**: Clear reasoning for all classifications and recommendations

## Key Features

- 📋 **Comprehensive Questionnaire**: 20 structured questions covering system characteristics, governance maturity, and risk impact
- 🤖 **4-Step LLM Analysis**:
  1. EU AI Act classification (PROHIBITED, HIGH_RISK, LIMITED_RISK, MINIMAL_RISK)
  2. EU AI Act requirements identification
  3. NIST AI RMF requirements identification
  4. Gap analysis with actionable recommendations
- 🔗 **Cross-Framework Mapping**: Shows relationships between EU AI Act and NIST requirements
- 📊 **Compliance Scoring**: 0-100 score based on gap severity distribution
- 📄 **Professional Reports**: Export detailed PDF reports
- 💾 **Assessment History**: SQLite/PostgreSQL database for storing results
- 🚀 **Background Processing**: Asynchronous assessment execution

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key (for Claude Sonnet 4)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Heimdall-Gov/Forge.git
cd Forge
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your Anthropic API key
```

Required environment variables:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LLM_MODEL=claude-sonnet-4-20250514
DATABASE_URL=sqlite:///./forge.db  # or PostgreSQL connection string
PORT=8000
```

4. **Run the application:**
```bash
python app.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Architecture

```
forge/
├── app.py                      # FastAPI backend with API endpoints
├── assessment_engine.py        # Core assessment logic (4 LLM calls)
├── questionnaire.py            # Question definitions and filtering
├── database.py                 # SQLAlchemy models and CRUD operations
├── cross_framework_mapping.py  # EU-NIST framework mapping
├── framework-docs/             # Framework reference documents
│   ├── eu-ai-act/
│   │   ├── classification.txt  # Articles 5, 6, Annex III
│   │   └── requirements.txt    # Articles 8-15, 26-27, 50
│   └── nist-ai-rmf/
│       ├── govern.txt          # GOVERN function
│       ├── map.txt             # MAP function
│       ├── measure.txt         # MEASURE function
│       └── manage.txt          # MANAGE function
└── requirements.txt
```

## How It Works

### Assessment Flow

1. **User submits questionnaire** → `POST /api/assessment`
   - 20 questions about AI system and organization
   - Assessment created in database with "pending" status
   - Background task starts processing

2. **4 Sequential LLM Calls** (runs in background):

   **Call #1: EU AI Act Classification**
   - Input: Full questionnaire + EU classification rules (Articles 5, 6, Annex III)
   - Output: Risk classification, rationale, confidence score
   - Model: Claude Sonnet 4, max_tokens: 2000, temperature: 0

   **Call #2: EU AI Act Requirements**
   - Input: System characteristics + classification result + EU requirements (Articles 8-15, 26-27, 50)
   - Output: Applicable articles and specific requirements
   - Model: Claude Sonnet 4, max_tokens: 4000, temperature: 0

   **Call #3: NIST AI RMF Requirements**
   - Input: System characteristics + pre-filtered NIST content based on stage/risk
   - Output: Applicable subcategories (GOVERN.x.x, MAP.x.x, etc.)
   - Model: Claude Sonnet 4, max_tokens: 6000, temperature: 0

   **Call #4: Gap Analysis**
   - Input: Governance maturity responses + EU requirements + NIST requirements
   - Output: Detailed gaps with implementation steps, examples, resources needed
   - Model: Claude Sonnet 4, max_tokens: 16000, temperature: 0.5

3. **Results saved to database**
   - Status updated to "completed"
   - Full result stored as JSON
   - Compliance score calculated

4. **User retrieves results** → `GET /api/assessment/{id}`
   - Complete assessment with all sections
   - Export to PDF available

### Key Technical Features

**Input Filtering**: Each LLM call receives only relevant questionnaire data to reduce token usage:
- Call #1: All responses (classification)
- Call #2: System characteristics only
- Call #3: System characteristics only
- Call #4: Governance maturity only

**NIST Pre-filtering**: NIST content is filtered based on system stage and risk level:
- Design/Development: GOVERN + MAP + MEASURE subset (~30K tokens)
- Deployment: GOVERN + MEASURE + MANAGE (~37K tokens)
- High-risk: All functions (~50K tokens)

**Structured Output**: Uses Anthropic's tool calling feature for guaranteed JSON schema compliance

**Error Handling**: Automatic retry with exponential backoff (3 attempts: 1s, 2s, 4s delays)

## API Endpoints

### Core Endpoints

**`GET /`**
- API information and available endpoints

**`GET /health`**
- Health check

**`GET /api/questions`**
- Get questionnaire questions
- Returns structured list with sections

**`POST /api/assessment`**
- Create new assessment
- Request body: `{ "questionnaire_responses": { ... } }`
- Returns: `202 Accepted` with `assessment_id` and status URL
- Assessment runs in background (~90 seconds)

**`GET /api/assessment/{id}/status`**
- Check assessment status
- Returns: `{ "status": "pending|processing|completed|failed", ... }`

**`GET /api/assessment/{id}`**
- Get complete assessment result
- Returns: Full result with EU AI Act, NIST, gaps, and cross-mapping
- Only available when status is "completed"

**`GET /api/assessment/{id}/pdf`**
- Export assessment as PDF
- Returns: PDF file download

## Example Usage

### Using cURL

```bash
# 1. Get questions
curl http://localhost:8000/api/questions

# 2. Submit assessment
curl -X POST http://localhost:8000/api/assessment \
  -H "Content-Type: application/json" \
  -d '{
    "questionnaire_responses": {
      "organization_type": "Startup",
      "industry": "Healthcare",
      "regions": ["EU", "US"],
      "organization_size": "50-200",
      "main_purpose": "Medical diagnosis support",
      "data_types": ["medical", "personal"],
      "stage": "development",
      "developer": "in-house",
      "criticality": "high",
      "policies": "No formal AI policies yet",
      "designated_team": "No",
      "approval_process": "Informal review by CTO",
      "record_keeping": "Version control for code only",
      "affects_rights": "Yes - healthcare decisions",
      "human_oversight": "Human-in-the-loop",
      "testing": "Basic accuracy testing",
      "complaint_mechanism": "No",
      "goal": "Compliance readiness",
      "preference": "Detailed framework",
      "standards": ["EU AI Act", "NIST AI RMF"]
    }
  }'

# Response: { "assessment_id": "550e8400-...", "status_url": "/api/assessment/550e8400-.../status" }

# 3. Check status (poll every 5-10 seconds)
curl http://localhost:8000/api/assessment/550e8400-.../status

# 4. Get results when completed
curl http://localhost:8000/api/assessment/550e8400-...

# 5. Download PDF
curl http://localhost:8000/api/assessment/550e8400-.../pdf -o report.pdf
```

### Using Python

```python
import requests
import time

# Submit assessment
response = requests.post("http://localhost:8000/api/assessment", json={
    "questionnaire_responses": {
        "organization_type": "Startup",
        "industry": "Healthcare",
        # ... other fields
    }
})

assessment_id = response.json()["assessment_id"]

# Poll for completion
while True:
    status_response = requests.get(f"http://localhost:8000/api/assessment/{assessment_id}/status")
    status = status_response.json()["status"]

    if status == "completed":
        break
    elif status == "failed":
        print(f"Assessment failed: {status_response.json()['error_message']}")
        exit(1)

    time.sleep(5)

# Get results
result = requests.get(f"http://localhost:8000/api/assessment/{assessment_id}").json()
print(f"Compliance Score: {result['gap_analysis']['compliance_score']}/100")
print(f"EU Classification: {result['eu_ai_act']['classification']}")

# Download PDF
pdf_response = requests.get(f"http://localhost:8000/api/assessment/{assessment_id}/pdf")
with open("report.pdf", "wb") as f:
    f.write(pdf_response.content)
```

## Database

### SQLite (Default)
No setup required. Database file created automatically at `./forge.db`

### PostgreSQL (Production)
1. Create database:
```sql
CREATE DATABASE forge_db;
```

2. Update `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/forge_db
```

### Schema
```sql
CREATE TABLE assessments (
    id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP,
    organization_name VARCHAR(255),
    questionnaire_responses JSON,
    status VARCHAR(50),  -- pending, processing, completed, failed
    eu_classification VARCHAR(50),
    eu_requirements JSON,
    nist_requirements JSON,
    gaps JSON,
    compliance_score INTEGER,
    cross_framework_mapping JSON,
    full_result JSON,
    processing_time_seconds INTEGER,
    error_message TEXT
);
```

## Framework Documents

Framework documents in `framework-docs/` can be updated with full official text:

### EU AI Act
- `eu-ai-act/classification.txt`: Articles 5, 6, Annex III (~15K tokens recommended)
- `eu-ai-act/requirements.txt`: Articles 8-15, 26-27, 50 (~25K tokens recommended)
- Source: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689

### NIST AI RMF
- `nist-ai-rmf/govern.txt`: GOVERN function (~15K tokens)
- `nist-ai-rmf/map.txt`: MAP function (~10K tokens)
- `nist-ai-rmf/measure.txt`: MEASURE function (~12K tokens)
- `nist-ai-rmf/manage.txt`: MANAGE function (~10K tokens)
- Source: https://doi.org/10.6028/NIST.AI.100-1

**Note**: Current files contain placeholder/summary content. Replace with full official text for production use.

## Cost Analysis

### Per Assessment Costs (using Claude Sonnet 4)

| Call | Input Tokens | Output Tokens | Cost |
|------|--------------|---------------|------|
| #1 EU Classification | 17K | 0.8K | $0.06 |
| #2 EU Requirements | 27K | 2K | $0.11 |
| #3 NIST Requirements | 35K | 2.5K | $0.14 |
| #4 Gap Analysis | 5.5K | 7K | $0.12 |
| **Total** | **84.5K** | **12.3K** | **$0.43** |

Pricing: $3.00/1M input tokens, $15.00/1M output tokens

## Deployment

### Docker

```bash
docker build -t forge .
docker run -p 8000:8000 --env-file .env forge
```

### Production Considerations

1. **Use PostgreSQL** for better performance and concurrency
2. **Request Anthropic Tier 2 API access** for higher rate limits (200K tokens/min)
3. **Add queue system** (Redis/RabbitMQ) for handling concurrent assessments
4. **Enable logging** and monitoring
5. **Set up backup** for database
6. **Use environment-based configuration** for different environments

## Limitations

- Requires Anthropic API key (Claude Sonnet 4)
- Assessment takes ~90 seconds to complete
- Framework documents contain placeholder content (need official full text)
- No user authentication system (single-tenant)
- No queue system for concurrent assessments (process in-memory)

## Roadmap

- [ ] Add complete EU AI Act and NIST AI RMF full text
- [ ] Implement queue system (Redis/Celery) for scalability
- [ ] Add user authentication and multi-tenancy
- [ ] Create React frontend for better UX
- [ ] Add additional frameworks (ISO/IEC 42001, OECD, etc.)
- [ ] Implement document upload and analysis
- [ ] Add continuous monitoring and tracking features

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

This tool provides guidance based on AI Act and NIST framework interpretation and should not be considered as legal advice. Always consult with legal and compliance experts for your specific situation. Classifications and recommendations are generated by AI and may contain errors or omissions.

## Support

- 🐛 [Report Issues](https://github.com/Heimdall-Gov/Forge/issues)
- 💬 [Discussions](https://github.com/Heimdall-Gov/Forge/discussions)
- 📧 Contact: forge@heimdall.gov

## Acknowledgments

- EU AI Act: European Commission
- NIST AI RMF: National Institute of Standards and Technology
- Claude Sonnet 4: Anthropic
