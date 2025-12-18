import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS for left alignment and styling
st.markdown("""
    <style>
    .greeting {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-greeting {
        font-size: 1.2rem;
        color: #4a4a4a;
        font-weight: 300;
        margin-bottom: 2rem;
    }
    /* Force left alignment of the main block if needed */
    .block-container {
        padding-top: 2rem;
        padding-left: 2rem; 
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Section (Top Left) ---
st.markdown('<p class="greeting">Hello, Doctor 👋</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-greeting">Let\'s get started.</p>', unsafe_allow_html=True)

# --- Step 1: Ambient AI Audio Input ---
st.write("### 1. Consultation Audio")
audio_file = st.file_uploader(
    "Upload Audio for Ambient AI (MP3, WAV, M4A)", 
    type=['mp3', 'wav', 'm4a'],
    help="This module is currently in beta."
)

if audio_file:
    st.success(f"Audio loaded: {audio_file.name}")

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
    st.info("You can upload a single PDF or multiple image pages.")
    
    # This single uploader handles multiple files (acting as "Add Pages")
    uploaded_files = st.file_uploader(
        "Upload Patient Records (PDF or Images)", 
        type=['pdf', 'png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) attached.**")

st.markdown("---")

# --- Step 3: Submission & Processing Simulation ---
if st.button("🚀 Submit & Generate Diagnosis", type="primary"):
    
    # 1. Validation: Ensure at least audio is uploaded (optional logic)
    if not audio_file:
        st.warning("⚠️ Please upload an audio file to proceed.")
    else:
        # Create a container to hold the status updates
        status_container = st.status("Initializing AI System...", expanded=True)
        
        with status_container:
            # Simulate Audio Transcription
            st.write("🎙️ **Transcribing Audio...**")
            time.sleep(2) # Simulate processing time
            st.write("✅ Transcription Complete.")
            
            # Simulate File Reading (if files exist)
            if add_medical_file == 'Yes' and uploaded_files:
                st.write("📂 **Reading Patient Files...**")
                for f in uploaded_files:
                    st.write(f"   - Scanning {f.name}...")
                    time.sleep(1) # Simulate OCR per file
                st.write("✅ Medical History Extracted.")
            elif add_medical_file == 'Yes' and not uploaded_files:
                st.warning("⚠️ No medical files found, skipping history...")
            else:
                st.write("ℹ️ No medical files selected. Proceeding with audio only.")

            # Simulate Diagnosis Generation
            st.write("🧠 **Creating Diagnosis...**")
            time.sleep(2)
            
            status_container.update(label="Analysis Complete!", state="complete", expanded=False)

        # Show Final Success Message
        st.success("🎉 Diagnosis Generated Successfully!")
        
        # Placeholder for where the actual report would go
        st.markdown("""
        ### Assessment Summary
        * **Chief Complaint:** Derived from audio...
        * **History:** Derived from uploaded pages...
        * **Differential Diagnosis:** [AI Output Placeholder]
        """)
