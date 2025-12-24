import streamlit as st
from datetime import datetime
from utils.audio_handler import transcribe_audio, get_audio_info
from utils.diagnosis_generator import generate_diagnosis_from_transcript, create_word_document

# Page configuration
st.set_page_config(
    page_title="Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'diagnosis' not in st.session_state:
    st.session_state.diagnosis = None

# Custom CSS for styling
st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem !important; 
        padding-bottom: 2rem !important;
    }
    .greeting {
        font-size: 4rem !important;
        color: #1f77b4;
        font-weight: 800;
        margin-bottom: 0px;
        line-height: 1.2;
    }
    .sub-greeting {
        font-size: 1.8rem !important;
        color: #4a4a4a;
        font-weight: 300;
        margin-top: 0px;
        margin-bottom: 3rem;
    }
    .disclaimer-box {
        margin-top: 3rem;
        padding: 1rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        border-radius: 0.25rem;
        font-size: 0.9rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown('<div class="greeting">Hello, Doctor 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-greeting">Let\'s get started.</div>', unsafe_allow_html=True)

# --- Step 1: Ambient AI Audio Input ---
st.write("### 1. Consultation Audio")
audio_file = st.file_uploader(
    "Upload Audio (Optional if Patient History is provided)", 
    type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg', 'mpga', 'webm']
)

if audio_file:
    st.success(f"✅ Audio loaded: {audio_file.name}")
    audio_info = get_audio_info(audio_file)
    st.caption(f"📊 Size: {audio_info['size_kb']} KB | Type: {audio_info['type']}")

st.markdown("---")

# --- Step 2: Medical Files Input ---
st.write("### 2. Patient History")
add_medical_file = st.radio(
    "Do you want to add a Medical file for this patient?", 
    ('No', 'Yes'),
    horizontal=True
)

uploaded_files = []

if add_medical_file == 'Yes':
    st.info("📄 You can upload a single PDF or multiple image pages.")
    uploaded_files = st.file_uploader(
        "Upload Patient Records (PDF or Images)", 
        type=['pdf', 'png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) attached.**")
        for file in uploaded_files:
            st.caption(f"📎 {file.name}")

st.markdown("---")

# --- Step 3: Submission Logic ---
if st.button("🚀 Submit & Generate Diagnosis", type="primary", use_container_width=False):
    
    # Check what inputs we have
    has_audio = audio_file is not None
    has_files = add_medical_file == 'Yes' and bool(uploaded_files)

    # LOGIC: If NEITHER is present, stop.
    if not has_audio and not has_files:
        st.error("⚠️ Please provide at least one input: Audio Recording OR Patient Files.")
    
    else:
        # Create status container
        status_container = st.status("🔧 Initializing AI System...", expanded=True)
        
        transcript_text = ""
        patient_history = ""
        
        with status_container:
            # 1. Process Audio (Only if present)
            if has_audio:
                st.write("🎙️ **Transcribing Audio with Whisper API...**")
                transcript_text = transcribe_audio(audio_file)
                
                if transcript_text:
                    st.write("✅ Transcription Complete.")
                    st.session_state.transcript = transcript_text
                else:
                    st.error("❌ Transcription failed. Check your API key.")
                    st.stop()
            else:
                st.write("ℹ️ No audio provided. Skipping transcription.")

            # 2. Process Files (Only if present)
            if has_files:
                st.write("📂 **Reading Patient Files...**")
                # TODO: Add OCR/PDF extraction logic here
                patient_history = f"[Patient records from {len(uploaded_files)} file(s) - OCR integration pending]"
                st.write("✅ Medical History Extracted.")
            else:
                st.write("ℹ️ No files provided. Skipping record analysis.")

            # 3. Combine inputs
            combined_input = ""
            if transcript_text:
                combined_input += f"CONSULTATION TRANSCRIPT:\n{transcript_text}\n\n"
            if patient_history:
                combined_input += f"PATIENT HISTORY:\n{patient_history}\n\n"

            # 4. Generate Diagnosis
            st.write("🧠 **Synthesizing Data & Creating Diagnosis...**")
            diagnosis_report = generate_diagnosis_from_transcript(combined_input)
            
            if diagnosis_report:
                st.write("✅ Diagnosis Generated.")
                st.session_state.diagnosis = diagnosis_report
                status_container.update(label="✅ Analysis Complete!", state="complete", expanded=False)
            else:
                st.error("❌ Diagnosis generation failed.")
                status_container.update(label="❌ Analysis Failed", state="error", expanded=False)
                st.stop()

        # --- Display Results ---
        st.success("🎉 Diagnostic Assessment Generated Successfully!")
        
        # Assessment summary
        st.markdown("### 📋 Assessment Summary")
        if has_audio and not has_files:
            st.info("📝 Generated based on Consultation Audio only.")
        elif has_files and not has_audio:
            st.info("📝 Generated based on Patient Records only.")
        else:
            st.info("📝 Generated by combining Audio insights + Patient Records.")

        # Show transcript if available
        if st.session_state.transcript:
            with st.expander("📄 View Transcript", expanded=False):
                st.text_area("Transcribed Text", st.session_state.transcript, height=200, disabled=True)
        
        # Show diagnosis report
        st.markdown("### 🩺 Diagnostic Report")
        st.text_area(
            "Medical Report", 
            st.session_state.diagnosis, 
            height=600,
            disabled=True,
            help="Formatted medical report following hospital template"
        )
        
        # Download buttons
        st.markdown("### 📥 Download Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.transcript:
                st.download_button(
                    label="📄 Download Transcript",
                    data=st.session_state.transcript,
                    file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            st.download_button(
                label="📋 Download Report (TXT)",
                data=st.session_state.diagnosis,
                file_name=f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col3:
            # Generate Word document
            word_doc = create_word_document(
                st.session_state.diagnosis,
                transcript=st.session_state.transcript
            )
            
            if word_doc:
                st.download_button(
                    label="📄 Download Report (WORD)",
                    data=word_doc,
                    file_name=f"Medical_Diagnosis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

# --- Disclaimer ---
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ DISCLAIMER: AI-Assisted Diagnosis</strong><br>
    This diagnosis is generated by Artificial Intelligence and is subject to potential inaccuracies. 
    It is designed to function <strong>solely as a decision support tool</strong>. 
    It does not replace professional medical judgment. 
</div>
""", unsafe_allow_html=True)
