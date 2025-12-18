import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (optional)
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🏥 Medical Diagnostic Assistant</h1>', unsafe_allow_html=True)

# Introduction
st.markdown("""
### Welcome to the AI-Powered Clinical Decision Support System

This application assists healthcare professionals in generating comprehensive diagnostic assessments 
by leveraging advanced AI technologies.
""")

# System Overview
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>🎤 Audio Transcription</h3>
        <p>Automatically transcribe doctor-patient consultations using OpenAI Whisper technology.</p>
        <ul>
            <li>Real-time transcription</li>
            <li>High accuracy</li>
            <li>Multiple audio formats</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>🔍 AI Diagnosis</h3>
        <p>Generate differential and provisional diagnoses using GPT-5 reasoning capabilities.</p>
        <ul>
            <li>Evidence-based reasoning</li>
            <li>Differential diagnosis</li>
            <li>Clinical recommendations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h3>📄 OCR Processing</h3>
        <p>Extract patient history from medical records using DeepSeek OCR technology.</p>
        <ul>
            <li>Structured data extraction</li>
            <li>Handwriting recognition</li>
            <li>Automated digitization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# How it works
st.markdown("---")
st.header("📋 How It Works")

steps_col1, steps_col2 = st.columns([1, 2])

with steps_col1:
    st.markdown("""
    ### Workflow Steps
    1. **Upload Audio** 📤
    2. **Transcribe Consultation** 🎙️
    3. **Extract Patient History** 📝
    4. **Generate Diagnosis** 🧠
    5. **Download Report** 📥
    """)

with steps_col2:
    st.info("""
    **System Features:**
    - Combines past medical history with current consultation data
    - Follows clinical reasoning methodology
    - Generates structured dashboard reports
    - Matches Fortis Hospital documentation format
    - HIPAA-compliant processing
    """)

# Getting Started
st.markdown("---")
st.header("🚀 Getting Started")

st.success("""
**To begin using the system:**

1. Navigate to **📝 Transcription** page from the sidebar to upload and transcribe audio
2. Go to **📄 OCR History** to extract patient medical history from documents (optional)
3. Visit **🔍 Diagnosis** page to generate comprehensive diagnostic assessment
4. Download the final report in your preferred format

**Note:** Ensure you have uploaded audio/documents before proceeding to diagnosis generation.
""")

# Sidebar information
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Hospital+Logo", use_container_width=True)
    
    st.markdown("### 📊 System Status")
    st.success("✅ All systems operational")
    
    st.markdown("### ℹ️ Information")
    st.info("""
    **Version:** 1.0.0  
    **Phase:** Beta Testing  
    **Developer:** Your Team
    """)
    
    st.markdown("### 📞 Support")
    st.markdown("""
    For technical support:  
    📧 support@hospital.com  
    📱 +91-XXXX-XXXX
    """)
    
    st.markdown("### ⚠️ Disclaimer")
    st.warning("""
    This tool is designed to assist healthcare professionals, 
    not replace clinical judgment. Always verify AI-generated 
    outputs with clinical expertise.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>© 2025 Medical Diagnostic Assistant | Powered by OpenAI, DeepSeek & Whisper AI</p>
    <p>🔒 HIPAA Compliant | 🔐 Secure Processing | 🌐 Cloud-Based</p>
</div>
""", unsafe_allow_html=True)
