import streamlit as st
from datetime import datetime
from audio_processing.audio_handler import transcribe_audio, get_audio_info
from audio_processing.diagnosis_generation import generate_diagnosis_from_transcript, create_word_document
from utils.ocr_handler import batch_extract_from_images
from utils.source_manager import (
    initialize_source_manager,
    add_source,
    get_all_sources,
    get_confirmed_sources,
    all_sources_confirmed,
    get_source_summary,
    get_combined_text,
    bulk_confirm_all,
    open_review_modal,
    confirm_source
)
from utils.review_modal import show_review_modal

# Page configuration
st.set_page_config(
    page_title="Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
initialize_source_manager()

if 'diagnosis' not in st.session_state:
    st.session_state.diagnosis = None
if 'ready_for_diagnosis' not in st.session_state:
    st.session_state.ready_for_diagnosis = False

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

# --- Step 1: Consultation Audio Input ---
st.write("### 1. Consultation Audio")
audio_files = st.file_uploader(
    "Upload Audio Files (Optional if Patient History is provided)", 
    type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg', 'mpga', 'webm'],
    accept_multiple_files=True,
    key="audio_uploader"
)

if audio_files:
    st.success(f"✅ {len(audio_files)} audio file(s) loaded")
    for audio_file in audio_files:
        audio_info = get_audio_info(audio_file)
        st.caption(f"🎙️ {audio_file.name} - {audio_info['size_kb']} KB")

st.markdown("---")

# --- Step 2: Medical Files Input (OCR) ---
st.write("### 2. Patient History Documents")
add_medical_file = st.radio(
    "Do you want to add Medical documents for this patient?", 
    ('No', 'Yes'),
    horizontal=True
)

ocr_files = []

if add_medical_file == 'Yes':
    st.info("📄 Upload medical records, lab reports, prescriptions, or handwritten notes.")
    ocr_files = st.file_uploader(
        "Upload Patient Records (Images or PDF)", 
        type=['pdf', 'png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        key="ocr_uploader"
    )
    
    if ocr_files:
        st.write(f"**{len(ocr_files)} file(s) ready for OCR**")
        for file in ocr_files:
            st.caption(f"📎 {file.name}")

st.markdown("---")

# --- Step 3: Extract & Process All Sources ---
st.write("### 3. Extract & Process Data")

if st.button("🔍 Extract Text from All Sources", type="primary", use_container_width=False):
    
    has_audio = bool(audio_files)
    has_files = add_medical_file == 'Yes' and bool(ocr_files)
    
    if not has_audio and not has_files:
        st.error("⚠️ Please provide at least one input: Audio Recording OR Patient Files.")
    
    else:
        status_container = st.status("🔧 Processing all sources...", expanded=True)
        
        with status_container:
            # Process Audio Files
            if has_audio:
                st.write(f"🎙️ **Transcribing {len(audio_files)} audio file(s)...**")
                
                for idx, audio_file in enumerate(audio_files):
                    st.write(f"   Processing: {audio_file.name}")
                    transcript_text = transcribe_audio(audio_file)
                    
                    if transcript_text:
                        # Add to source manager
                        add_source(
                            source_type="audio",
                            filename=audio_file.name,
                            raw_text=transcript_text,
                            metadata={
                                'size_kb': get_audio_info(audio_file)['size_kb'],
                                'file_type': get_audio_info(audio_file)['type']
                            }
                        )
                        st.write(f"   ✅ Transcribed: {len(transcript_text.split())} words")
                    else:
                        st.error(f"   ❌ Transcription failed for {audio_file.name}")
            
            # Process OCR Files
            if has_files:
                st.write(f"📄 **Extracting text from {len(ocr_files)} document(s)...**")
                
                # Get API key
                try:
                    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
                except:
                    st.error("❌ OpenRouter API key not found in secrets")
                    st.stop()
                
                # Batch OCR extraction
                ocr_results = batch_extract_from_images(ocr_files, OPENROUTER_API_KEY, mode="full")
                
                for result in ocr_results:
                    if result['status'] == 'success':
                        add_source(
                            source_type="ocr",
                            filename=result['filename'],
                            raw_text=result['extracted_text'],
                            metadata={
                                'file_size_kb': result.get('file_size_kb', 0),
                                'word_count': result['word_count']
                            }
                        )
                        st.write(f"   ✅ {result['filename']}: {result['word_count']} words")
                    else:
                        st.error(f"   ❌ {result['filename']}: {result['error']}")
            
            status_container.update(label="✅ Extraction Complete!", state="complete", expanded=False)
        
        st.success("🎉 All sources extracted successfully!")
        st.info("👇 Please review and confirm all sources below before generating diagnosis")
        st.rerun()

# --- Step 4: Review & Confirm Sources ---
sources = get_all_sources()

if sources:
    st.markdown("---")
    st.write("### 📚 Review Data Sources")
    st.write("Review extracted text and make any necessary corrections before generating diagnosis.")
    
    # Summary metrics
    summary = get_source_summary()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sources", summary['total_sources'])
    col2.metric("✅ Confirmed", summary['confirmed'])
    col3.metric("⏳ Pending", summary['pending'])
    col4.metric("Total Words", summary['total_words'])
    
    # Bulk confirm option
    if summary['pending'] > 0:
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("✅ Confirm All Sources", use_container_width=True):
                bulk_confirm_all()
                st.success("All sources confirmed!")
                st.rerun()
        
        with col2:
            st.caption("Use this if all extractions are accurate and don't need review")
    
    st.markdown("---")
    
    # List all sources with review buttons
    for source in sources:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            if source['status'] == 'confirmed':
                icon = "✅"
                status_text = "Confirmed"
                status_color = "green"
            else:
                icon = "⏳"
                status_text = "Pending Review"
                status_color = "orange"
            
            st.markdown(f"{icon} **{source['filename']}** ({source['type'].upper()}) - :{status_color}[{status_text}]")
            st.caption(f"{source['word_count']} words | Added: {source['created_at']}")
        
        with col2:
            st.metric("Words", source['word_count'])
        
        with col3:
            if st.button("👁️ Review", key=f"review_{source['id']}", use_container_width=True):
                open_review_modal(source['id'])
        
        with col4:
            if source['status'] == 'pending':
                if st.button("✅", key=f"quick_confirm_{source['id']}", use_container_width=True, help="Quick confirm without review"):
                    confirm_source(source['id'])
                    st.rerun()

# Show review modal if triggered
if st.session_state.get('review_mode') is not None:
    show_review_modal(st.session_state.review_mode)

# --- Step 5: Generate Diagnosis (Only when all confirmed) ---
if sources and all_sources_confirmed():
    st.markdown("---")
    st.success("### 🎉 All Sources Confirmed and Ready!")
    
    # Summary preview
    with st.expander("📊 View Combined Data Summary", expanded=False):
        st.write("**Sources Ready for Diagnosis:**")
        for source in get_confirmed_sources():
            st.write(f"✅ **{source['filename']}** ({source['type'].upper()}) - {source['word_count']} words")
        
        st.markdown("---")
        st.write(f"**Total Input:** {summary['total_words']} words across {summary['confirmed']} source(s)")
        
        # Preview combined text
        combined = get_combined_text()
        st.text_area("Combined Text (Preview - This will be sent to AI)", combined, height=300, disabled=True)
    
    st.markdown("---")
    
    # Generate Diagnosis Button
    if st.button("🔬 Generate Diagnosis", type="primary", use_container_width=False):
        
        status_container = st.status("🧠 Generating diagnosis...", expanded=True)
        
        with status_container:
            st.write("📝 Combining all confirmed sources...")
            combined_input = get_combined_text()
            
            st.write("🤖 Sending to AI for analysis...")
            diagnosis_report = generate_diagnosis_from_transcript(combined_input)
            
            if diagnosis_report:
                st.write("✅ Diagnosis generated successfully!")
                st.session_state.diagnosis = diagnosis_report
                status_container.update(label="✅ Diagnosis Complete!", state="complete", expanded=False)
            else:
                st.error("❌ Diagnosis generation failed")
                status_container.update(label="❌ Failed", state="error", expanded=False)
                st.stop()
        
        st.rerun()

elif sources:
    st.markdown("---")
    pending_count = get_source_summary()['pending']
    st.warning(f"⚠️ Please review and confirm all sources before generating diagnosis ({pending_count} pending)")
    st.button("🔬 Generate Diagnosis", disabled=True, use_container_width=False)

# --- Display Diagnosis Results ---
if st.session_state.diagnosis:
    st.markdown("---")
    st.success("### 🎉 Diagnostic Assessment Generated!")
    
    # Show diagnosis report
    st.markdown("### 🩺 Diagnostic Report")
    st.text_area(
        "Medical Report", 
        st.session_state.diagnosis, 
        height=600,
        disabled=True,
        key="diagnosis_display"
    )
    
    # Download buttons
    st.markdown("### 📥 Download Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download combined source text
        combined_sources = get_combined_text()
        st.download_button(
            label="📄 Download Source Data",
            data=combined_sources,
            file_name=f"sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
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
            transcript=combined_sources
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
