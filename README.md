# Forge 🛡️
Open-source AI Governance Framework Generator. A lean, LLM-powered tool that generates tailored governance frameworks and compliance checklists based on your AI project's context.

## Features

- 📋 **Smart Questionnaire**: Context-aware questions about your AI system
- 🤖 **LLM-Powered Generation**: Uses GPT-4/Claude to create customized frameworks
- 📚 **Framework Library**: Incorporates NIST AI RMF, EU AI Act, and more
- 📄 **Multiple Export Formats**: Download as Markdown or PDF
- 🚀 **Lean Architecture**: No vector DB needed - leverages large context windows
- 🔒 **Privacy-First**: No data storage, frameworks generated on-demand

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key or Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Heimdall-Gov/Forge.git
cd Forge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

1. Start the FastAPI backend:
```bash
python app.py
```

2. In a new terminal, start the Streamlit UI:
```bash
streamlit run ui.py
```

3. Open your browser to `http://localhost:8501`

## Configuration

Edit `.env` file to configure:

```env
# Choose your LLM provider
LLM_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Model selection
LLM_MODEL=gpt-4-turbo-preview  # or claude-3-opus-20240229
```

## Adding Custom Frameworks

Add framework documents to the `frameworks/` directory:
- Markdown files (`.md`) are loaded directly
- PDF files (`.pdf`) are extracted automatically
- Framework naming convention: `framework_name.md` or `framework_name.pdf`

## API Endpoints

- `GET /` - API information
- `GET /questions` - Get questionnaire structure
- `POST /generate` - Generate framework from responses
- `POST /export/markdown` - Export as Markdown
- `POST /export/pdf` - Export as PDF
- `GET /frameworks` - List available frameworks

## Deployment

### Using Docker

```bash
docker build -t forge .
docker run -p 8000:8000 -p 8501:8501 --env-file .env forge
```

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Deploy to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy!

## Architecture

```
Forge/
├── app.py              # FastAPI backend
├── ui.py               # Streamlit frontend
├── questionnaire.py    # Question logic
├── generator.py        # LLM integration
├── frameworks/         # Framework documents
│   ├── nist_ai_rmf.md
│   └── eu_ai_act.md
└── requirements.txt
```

## How It Works

1. **User Input**: Complete questionnaire about your AI system
2. **Context Analysis**: System determines relevant frameworks based on responses
3. **Framework Loading**: Relevant frameworks loaded into LLM context
4. **Generation**: LLM generates customized governance framework
5. **Export**: Download in your preferred format

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Disclaimer

This tool provides guidance based on general best practices and should not be considered as legal advice. Always consult with legal and compliance experts for your specific situation.

## Support

- 🐛 [Report Issues](https://github.com/Heimdall-Gov/Forge/issues)
- 💬 [Discussions](https://github.com/Heimdall-Gov/Forge/discussions)
- 📧 Contact: forge@heimdall.gov
