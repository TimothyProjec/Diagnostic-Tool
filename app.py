import streamlit as st
from datetime import datetime
from audio_processing.audio_handler import transcribe_audio, get_audio_info
from audio_processing.diagnosis_generation import generate_diagnosis_from_transcript, create_word_document
from ocr_handler.ocr_handler import batch_extract_from_images
from ocr_handler.source_manager import (
    initialize_source_manager,
    add_source,
    get_all_sources,
    get_confirmed_sources,
    all_sources_confirmed,
    get_source_summary,
    get_combined_text,
    bulk_confirm_all,
    open_review_modal,
    confirm_source,
    close_review_modal
)
from ocr_handler.review_modal import show_review_modal
from utils.chatbot_handler import initialize_chatbot, open_chat, close_chat, is_chat_open
from utils.chatbot_ui import render_chatbot_fullscreen

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide"
)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
initialize_source_manager()
initialize_chatbot()

if 'initial_diagnosis' not in st.session_state:
    st.session_state.initial_diagnosis = None
if 'final_diagnosis' not in st.session_state:
    st.session_state.final_diagnosis = None
if 'ready_for_download' not in st.session_state:
    st.session_state.ready_for_download = False

# ============================================================================
# CUSTOM CSS
# ============================================================================
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

# ============================================================================
# CHATBOT MODE - FULL SCREEN TAKEOVER
# ============================================================================
if st.session_state.initial_diagnosis and is_chat_open():
    # Get current diagnosis and source data
    current_diag = st.session_state.get('final_diagnosis', st.session_state.initial_diagnosis)
    source_data = get_combined_text()
    
    # Render full-screen chatbot (ChatGPT-style)
    render_chatbot_fullscreen(current_diag, source_data)
    
    # Stop here - chatbot takes over the entire screen
    st.stop()

# ============================================================================
# HEADER (Only shown when NOT in chatbot mode)
# ============================================================================
st.markdown('<div class="greeting">Hello, Doctor 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-greeting">Let\'s get started.</div>', unsafe_allow_html=True)

# ============================================================================
# STEP 1: AUDIO UPLOAD & TRANSCRIPTION
# ============================================================================
st.write("### 1. Consultation Audio")
st.caption("Upload audio recordings of patient consultations")

audio_files = st.file_uploader(
    "Upload Audio Files (Optional)", 
    type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg', 'mpga', 'webm'],
    accept_multiple_files=True,
    key="audio_uploader",
    help="You can upload multiple audio files"
)

if audio_files:
    st.success(f"✅ {len(audio_files)} audio file(s) loaded")
    
    for audio_file in audio_files:
        audio_info = get_audio_info(audio_file)
        st.caption(f"🎙️ {audio_file.name} - {audio_info['size_kb']} KB")
    
    # Check if already transcribed
    audio_filenames = [f.name for f in audio_files]
    existing_audio = [s for s in get_all_sources() if s['type'] == 'audio' and s['filename'] in audio_filenames]
    
    if existing_audio:
        st.info(f"ℹ️ {len(existing_audio)} audio file(s) already transcribed. See sources below.")
    
    # Transcription Button
    if st.button("🎙️ Transcribe Audio Files", key="audio_transcribe_btn", type="primary"):
        
        status_container = st.status("🎙️ Transcribing audio...", expanded=True)
        
        with status_container:
            st.write(f"🎤 Processing {len(audio_files)} audio file(s)...")
            
            for audio_file in audio_files:
                # Skip if already transcribed
                if any(s['filename'] == audio_file.name for s in get_all_sources()):
                    st.write(f"   ⏭️ Skipping {audio_file.name} (already transcribed)")
                    continue
                
                st.write(f"   Processing: {audio_file.name}")
                transcript_text = transcribe_audio(audio_file)
                
                if transcript_text:
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
            
            status_container.update(label="✅ Transcription Complete!", state="complete", expanded=False)
        
        st.success("🎉 Audio transcription complete! Review sources below.")
        st.rerun()

st.markdown("---")

# ============================================================================
# STEP 2: DOCUMENT UPLOAD & OCR
# ============================================================================
st.write("### 2. Patient History Documents")
st.caption("Upload medical records, lab reports, prescriptions, or handwritten notes")

add_medical_file = st.radio(
    "Do you want to add medical documents?", 
    ('No', 'Yes'),
    horizontal=True,
    key="add_docs_radio"
)

if add_medical_file == 'Yes':
    st.info("📄 Upload images or PDF pages of medical documents")
    
    ocr_files = st.file_uploader(
        "Upload Patient Records", 
        type=['png', 'jpg', 'jpeg', 'pdf'], 
        accept_multiple_files=True,
        key="ocr_uploader",
        help="Supports images and PDF files"
    )
    
    if ocr_files:
        st.write(f"**{len(ocr_files)} file(s) ready for OCR**")
        
        for file in ocr_files:
            st.caption(f"📎 {file.name}")
        
        # Check if already processed
        ocr_filenames = [f.name for f in ocr_files]
        existing_ocr = [s for s in get_all_sources() if s['type'] == 'ocr' and s['filename'] in ocr_filenames]
        
        if existing_ocr:
            st.info(f"ℹ️ {len(existing_ocr)} document(s) already processed. See sources below.")
        
        # OCR Extract Button
        if st.button("🔍 Extract Text from Documents", key="ocr_extract_btn", type="primary"):
            
            try:
                OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
            except:
                st.error("❌ OpenRouter API key not found in secrets. Please add it in Streamlit Cloud settings.")
                st.stop()
            
            status_container = st.status("📄 Processing documents...", expanded=True)
            
            with status_container:
                st.write(f"🔍 Extracting text from {len(ocr_files)} document(s)...")
                
                # Filter out already processed files
                files_to_process = [f for f in ocr_files if not any(s['filename'] == f.name for s in get_all_sources())]
                
                if not files_to_process:
                    st.info("All files already processed!")
                else:
                    ocr_results = batch_extract_from_images(files_to_process, OPENROUTER_API_KEY, mode="full")
                    
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
                
                status_container.update(label="✅ OCR Complete!", state="complete", expanded=False)
            
            st.success("🎉 Document extraction complete! Review sources below.")
            st.rerun()

st.markdown("---")

# ============================================================================
# STEP 3: REVIEW & CONFIRM SOURCES
# ============================================================================
sources = get_all_sources()

if sources:
    st.write("### 3. Review Data Sources")
    st.caption("Review extracted text and make corrections before generating diagnosis")
    
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
            if st.button("✅ Confirm All Sources", key="bulk_confirm_btn", use_container_width=True):
                bulk_confirm_all()
                st.success("✅ All sources confirmed!")
                st.rerun()
        
        with col2:
            st.caption("Use this if all extractions are accurate and don't need review")
    
    st.markdown("---")
    
    # List all sources
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
            if st.button("👁️ Review", key=f"review_btn_{source['id']}", use_container_width=True):
                open_review_modal(source['id'])
                st.rerun()
        
        with col4:
            if source['status'] == 'pending':
                if st.button("✅", key=f"quick_confirm_{source['id']}", use_container_width=True, help="Quick confirm"):
                    confirm_source(source['id'])
                    st.rerun()
    
    st.markdown("---")

# Show review modal (ONLY if review_mode is set)
if st.session_state.get('review_mode') is not None:
    show_review_modal(st.session_state.review_mode)

# ============================================================================
# STEP 4: GENERATE INITIAL DIAGNOSIS
# ============================================================================
if sources and all_sources_confirmed():
    st.success("### 🎉 All Sources Confirmed!")
    
    # Summary preview
    with st.expander("📊 View Combined Data Summary", expanded=False):
        st.write("**Sources Ready for Diagnosis:**")
        for source in get_confirmed_sources():
            st.write(f"✅ **{source['filename']}** ({source['type'].upper()}) - {source['word_count']} words")
        
        st.markdown("---")
        st.write(f"**Total Input:** {summary['total_words']} words across {summary['confirmed']} source(s)")
        
        combined = get_combined_text()
        st.text_area("Combined Text Preview", combined, height=300, disabled=True, key="combined_preview")
    
    st.markdown("---")
    
    # Generate Initial Diagnosis Button
    if not st.session_state.initial_diagnosis:
        if st.button("🔬 Generate Initial Diagnosis", type="primary", key="gen_diagnosis_btn", use_container_width=False):
            
            status_container = st.status("🧠 Generating initial diagnosis...", expanded=True)
            
            with status_container:
                st.write("📝 Combining all confirmed sources...")
                combined_input = get_combined_text()
                
                st.write("🤖 Sending to AI for analysis...")
                initial_diagnosis = generate_diagnosis_from_transcript(combined_input)
                
                if initial_diagnosis:
                    st.write("✅ Initial diagnosis generated!")
                    st.session_state.initial_diagnosis = initial_diagnosis
                    st.session_state.final_diagnosis = initial_diagnosis  # Start with initial as final
                    status_container.update(label="✅ Diagnosis Ready!", state="complete", expanded=False)
                else:
                    st.error("❌ Diagnosis generation failed")
                    status_container.update(label="❌ Failed", state="error", expanded=False)
                    st.stop()
            
            st.rerun()

elif sources:
    st.warning(f"⚠️ Please review and confirm all sources ({get_source_summary()['pending']} pending)")
    st.button("🔬 Generate Initial Diagnosis", disabled=True, key="gen_diagnosis_disabled")

# ============================================================================
# STEP 5: INITIAL DIAGNOSIS DISPLAY (Before entering chat)
# ============================================================================
if st.session_state.initial_diagnosis and not is_chat_open() and not st.session_state.ready_for_download:
    st.markdown("---")
    st.success("### ✅ Initial Diagnosis Generated!")
    
    st.info("👉 Click the button below to refine your diagnosis with AI assistance")
    
    # Show diagnosis preview (collapsed)
    with st.expander("📋 View Initial Diagnosis", expanded=False):
        st.text_area(
            "Initial Diagnosis", 
            st.session_state.initial_diagnosis, 
            height=500,
            disabled=True,
            key="initial_diag_preview"
        )
    
    st.markdown("---")
    
    # Single prominent button to enter chatbot
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "💬 Refine with AI Assistant", 
            key="enter_chat_btn", 
            type="primary", 
            use_container_width=True,
            help="Open AI chat to review and improve the diagnosis"
        ):
            open_chat()
            st.rerun()
    
    st.markdown("---")
    st.caption("💡 Tip: Use AI chat to modify, explain, or add to the diagnosis before finalizing")

# ============================================================================
# STEP 6: DOWNLOAD (Only shown after exiting chat)
# ============================================================================
if st.session_state.get('ready_for_download') and st.session_state.final_diagnosis:
    st.markdown("---")
    st.success("### 🎉 Diagnosis Finalized!")
    
    # Show final diagnosis
    with st.expander("📋 Final Diagnosis", expanded=True):
        
        # If modifications were made, show comparison
        if st.session_state.get('chat_modifications'):
            st.info(f"✏️ {len(st.session_state.chat_modifications)} modification(s) made via AI chat")
            
            tab1, tab2 = st.tabs(["Final Version", "Original Version"])
            
            with tab1:
                st.text_area(
                    "Final Diagnosis",
                    st.session_state.final_diagnosis,
                    height=500,
                    disabled=True,
                    key="final_diag_display"
                )
            
            with tab2:
                st.text_area(
                    "Original Diagnosis",
                    st.session_state.initial_diagnosis,
                    height=500,
                    disabled=True,
                    key="original_diag_display"
                )
        else:
            # No modifications
            st.text_area(
                "Final Diagnosis",
                st.session_state.final_diagnosis,
                height=500,
                disabled=True,
                key="final_diag_only"
            )
    
    st.markdown("---")
    st.write("### 📥 Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        combined_sources = get_combined_text()
        st.download_button(
            label="📄 Download Source Data",
            data=combined_sources,
            file_name=f"sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_sources"
        )
    
    with col2:
        st.download_button(
            label="📋 Download Report (TXT)",
            data=st.session_state.final_diagnosis,
            file_name=f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_txt"
        )
    
    with col3:
        word_doc = create_word_document(
            st.session_state.final_diagnosis,
            transcript=combined_sources
        )
        
        if word_doc:
            st.download_button(
                label="📄 Download Report (WORD)",
                data=word_doc,
                file_name=f"Medical_Diagnosis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="download_word"
            )
    
    st.markdown("---")
    
    # Option to go back to chat
    if st.button("↩️ Back to Chat (Make More Changes)", key="back_to_chat"):
        st.session_state.ready_for_download = False
        open_chat()
        st.rerun()

# ============================================================================
# DISCLAIMER
# ============================================================================
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ DISCLAIMER: AI-Assisted Diagnosis</strong><br>
    This diagnosis is generated by Artificial Intelligence and is subject to potential inaccuracies. 
    It is designed to function <strong>solely as a decision support tool</strong>. 
    It does not replace professional medical judgment. 
</div>
""", unsafe_allow_html=True)
