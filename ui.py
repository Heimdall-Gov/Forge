import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="AI Governance Framework Generator",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .framework-output {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🛡️ AI Governance Framework Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate customized AI governance frameworks tailored to your organization</p>', unsafe_allow_html=True)

# Initialize session state
if 'framework_generated' not in st.session_state:
    st.session_state.framework_generated = False
if 'framework_content' not in st.session_state:
    st.session_state.framework_content = ""
if 'responses' not in st.session_state:
    st.session_state.responses = {}

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["📋 Questionnaire", "📄 Generated Framework", "ℹ️ About"]
    )

# Main content
if page == "📋 Questionnaire":
    st.header("AI Governance Assessment Questionnaire")
    st.markdown("Please answer the following questions about your AI system and organization.")
    
    # Create form
    with st.form("questionnaire_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Company Size
            company_size = st.selectbox(
                "Organization Size",
                options=["startup", "sme", "enterprise"],
                format_func=lambda x: {
                    "startup": "Startup (1-50 employees)",
                    "sme": "SME (51-500 employees)",
                    "enterprise": "Enterprise (500+ employees)"
                }[x]
            )
            
            # Industry
            industry = st.selectbox(
                "Primary Industry",
                options=["healthcare", "finance", "retail", "education", "government", "technology", "other"],
                format_func=lambda x: x.title()
            )
            
            # AI Use Case
            ai_use_case = st.selectbox(
                "Primary AI Use Case",
                options=["customer_service", "decision_making", "content_generation", "prediction", "automation", "other"],
                format_func=lambda x: x.replace("_", " ").title()
            )
            
            # Geographic Location
            geographic_location = st.selectbox(
                "Primary Geographic Location/Market",
                options=["us", "eu", "uk", "canada", "asia", "other"],
                format_func=lambda x: {
                    "us": "United States",
                    "eu": "European Union",
                    "uk": "United Kingdom",
                    "canada": "Canada",
                    "asia": "Asia Pacific",
                    "other": "Other"
                }[x]
            )
        
        with col2:
            # Boolean fields
            user_facing = st.checkbox("Is your AI system directly user-facing?")
            handles_personal_data = st.checkbox("Does your system handle personal or sensitive data?")
            high_risk = st.checkbox("Is this a high-risk AI application? (e.g., healthcare decisions, financial lending)")
            
            # Compliance Level
            existing_compliance = st.selectbox(
                "Current Compliance/Governance Maturity",
                options=["none", "basic", "advanced"],
                format_func=lambda x: {
                    "none": "No formal governance",
                    "basic": "Basic policies in place",
                    "advanced": "Comprehensive governance framework"
                }[x]
            )
        
        # Additional Context
        additional_context = st.text_area(
            "Additional Context or Specific Requirements (Optional)",
            placeholder="Enter any specific requirements, constraints, or context about your AI system...",
            height=100
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate Framework", use_container_width=True)
        
        if submitted:
            # Prepare responses
            responses = {
                "company_size": company_size,
                "industry": industry,
                "ai_use_case": ai_use_case,
                "user_facing": user_facing,
                "handles_personal_data": handles_personal_data,
                "high_risk": high_risk,
                "geographic_location": geographic_location,
                "existing_compliance": existing_compliance,
                "additional_context": additional_context
            }
            
            # Store in session state
            st.session_state.responses = responses
            
            # Show loading spinner
            with st.spinner("🔄 Generating your customized AI governance framework..."):
                try:
                    # Make API request
                    response = requests.post(
                        f"{API_URL}/generate",
                        json=responses,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.framework_content = result["framework"]
                        st.session_state.framework_generated = True
                        st.success("✅ Framework generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error generating framework: {response.text}")
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Could not connect to the API. Make sure the backend is running.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

elif page == "📄 Generated Framework":
    st.header("Your AI Governance Framework")
    
    if st.session_state.framework_generated:
        # Display framework
        st.markdown(st.session_state.framework_content)
        
        # Export options
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Download as Markdown", use_container_width=True):
                # Create download
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="💾 Save Markdown",
                    data=st.session_state.framework_content,
                    file_name=f"ai_governance_framework_{timestamp}.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button("📄 Export as PDF", use_container_width=True):
                try:
                    response = requests.post(
                        f"{API_URL}/export/pdf",
                        json={
                            "framework": st.session_state.framework_content,
                            "format": "pdf",
                            "metadata": st.session_state.responses
                        }
                    )
                    if response.status_code == 200:
                        st.download_button(
                            label="💾 Save PDF",
                            data=response.content,
                            file_name=f"ai_governance_framework_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Error exporting PDF: {str(e)}")
        
        with col3:
            if st.button("🔄 Generate New Framework", use_container_width=True):
                st.session_state.framework_generated = False
                st.session_state.framework_content = ""
                st.rerun()
    
    else:
        st.info("📝 Please complete the questionnaire first to generate your framework.")
        if st.button("Go to Questionnaire"):
            st.rerun()

elif page == "ℹ️ About":
    st.header("About AI Governance Framework Generator")
    
    st.markdown("""
    ### 🎯 Purpose
    
    This tool helps organizations implement appropriate AI governance practices by generating 
    customized frameworks based on their specific context, use cases, and requirements.
    
    ### 🔧 How It Works
    
    1. **Assessment**: Answer questions about your organization and AI systems
    2. **Analysis**: The tool analyzes your responses and identifies relevant frameworks
    3. **Generation**: Using advanced AI, it generates a tailored governance framework
    4. **Export**: Download your framework in Markdown or PDF format
    
    ### 📚 Framework Sources
    
    Our recommendations are based on established frameworks including:
    - NIST AI Risk Management Framework
    - EU AI Act requirements
    - ISO/IEC standards for AI
    - Industry-specific best practices
    
    ### ⚠️ Disclaimer
    
    This tool provides guidance based on general best practices and should not be considered 
    as legal advice. Always consult with legal and compliance experts for your specific situation.
    
    ### 🔒 Privacy
    
    - Your responses are processed securely
    - No data is stored permanently
    - Frameworks are generated on-demand
    
    ### 📧 Contact
    
    For questions or feedback, please visit our [GitHub repository](https://github.com/Heimdall-Gov/Forge).
    """)
    
    # Show system status
    st.markdown("---")
    st.subheader("System Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ System is operational")
        else:
            st.warning("⚠️ System may be experiencing issues")
    except:
        st.error("❌ Cannot connect to backend API")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #95a5a6;'>
        <p>Built with ❤️ by Heimdall | Open Source AI Governance</p>
    </div>
    """,
    unsafe_allow_html=True
)