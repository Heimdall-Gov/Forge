import os
import json
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
from dotenv import load_dotenv
from questionnaire import QuestionnaireResponse, determine_relevant_frameworks

load_dotenv()


class FrameworkGenerator:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.frameworks_dir = Path("frameworks")
        self.templates_dir = Path("templates")
        
        if self.llm_provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
        elif self.llm_provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = os.getenv("LLM_MODEL", "claude-3-opus-20240229")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def load_framework(self, framework_name: str) -> str:
        """Load a framework document from the frameworks directory"""
        framework_path = self.frameworks_dir / f"{framework_name}.md"
        pdf_path = self.frameworks_dir / f"{framework_name}.pdf"
        
        if framework_path.exists():
            with open(framework_path, 'r') as f:
                return f.read()
        elif pdf_path.exists():
            return self.extract_pdf_text(pdf_path)
        else:
            return f"Framework {framework_name} not found. Using general best practices."
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                return text[:50000]  # Limit to first 50k chars for context window
        except Exception as e:
            return f"Error loading PDF: {str(e)}"
    
    def generate_framework(self, responses: QuestionnaireResponse) -> Dict[str, str]:
        """Generate a customized AI governance framework based on responses"""
        
        # Determine relevant frameworks
        relevant_frameworks = determine_relevant_frameworks(responses)
        
        # Load framework content
        framework_content = []
        for framework_name in relevant_frameworks:
            content = self.load_framework(framework_name)
            if content:
                framework_content.append(f"=== {framework_name.upper()} ===\n{content}\n")
        
        # Create the prompt
        prompt = self.create_prompt(responses, framework_content)
        
        # Generate the framework
        if self.llm_provider == "openai":
            return self.generate_with_openai(prompt)
        else:
            return self.generate_with_anthropic(prompt)
    
    def create_prompt(self, responses: QuestionnaireResponse, framework_content: List[str]) -> str:
        """Create the prompt for the LLM"""
        context = {
            "company_size": responses.company_size,
            "industry": responses.industry,
            "ai_use_case": responses.ai_use_case,
            "user_facing": responses.user_facing,
            "handles_personal_data": responses.handles_personal_data,
            "high_risk": responses.high_risk,
            "geographic_location": responses.geographic_location,
            "existing_compliance": responses.existing_compliance,
            "additional_context": responses.additional_context
        }
        
        prompt = f"""You are an AI governance expert. Generate a customized AI governance framework based on the following context and reference frameworks.

USER CONTEXT:
{json.dumps(context, indent=2)}

REFERENCE FRAMEWORKS:
{' '.join(framework_content) if framework_content else 'Using general AI governance best practices.'}

Generate a comprehensive but practical AI governance framework that includes:

1. EXECUTIVE SUMMARY
   - Brief overview of the framework
   - Key compliance requirements
   - Risk level assessment

2. GOVERNANCE STRUCTURE
   - Roles and responsibilities
   - Decision-making processes
   - Oversight mechanisms

3. RISK ASSESSMENT
   - Risk identification methodology
   - Risk categorization
   - Mitigation strategies

4. DATA GOVERNANCE
   - Data collection guidelines
   - Privacy requirements
   - Data quality standards

5. MODEL DEVELOPMENT & VALIDATION
   - Development standards
   - Testing requirements
   - Validation procedures

6. DEPLOYMENT & MONITORING
   - Deployment checklist
   - Performance monitoring
   - Incident response

7. DOCUMENTATION REQUIREMENTS
   - Required documentation
   - Audit trails
   - Reporting standards

8. COMPLIANCE CHECKLIST
   - Immediate actions (Priority 1)
   - Short-term actions (Priority 2)
   - Long-term actions (Priority 3)

Make the framework specific to their context, practical, and actionable. Use clear, concise language and provide specific examples where relevant.

Format the output in Markdown with clear headers and bullet points."""
        
        return prompt
    
    def generate_with_openai(self, prompt: str) -> Dict[str, str]:
        """Generate framework using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in AI governance and compliance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            framework_content = response.choices[0].message.content
            
            return {
                "status": "success",
                "framework": framework_content,
                "metadata": {
                    "model": self.model,
                    "provider": "openai"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "framework": "Error generating framework. Please check your API key and try again."
            }
    
    def generate_with_anthropic(self, prompt: str) -> Dict[str, str]:
        """Generate framework using Anthropic"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system="You are an expert in AI governance and compliance.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            framework_content = response.content[0].text
            
            return {
                "status": "success",
                "framework": framework_content,
                "metadata": {
                    "model": self.model,
                    "provider": "anthropic"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "framework": "Error generating framework. Please check your API key and try again."
            }