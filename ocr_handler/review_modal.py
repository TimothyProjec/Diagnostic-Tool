"""
Modal component for reviewing and editing source text
"""

import streamlit as st
from ocr_handler.source_manager import (  # ← Fixed path
    get_source_by_id, 
    update_source_text, 
    confirm_source,
    discard_source,
    close_review_modal
)

@st.dialog("📝 Review & Edit Source", width="large")
def show_review_modal(source_id):
    """
    Display modal for reviewing and editing source text
    
    Args:
        source_id: ID of source to review
    """
    source = get_source_by_id(source_id)
    
    if not source:
        st.error("Source not found")
        return
    
    # Header info
    st.markdown(f"### 📄 {source['filename']}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Type", source['type'].upper())
    col2.metric("Words", source['word_count'])
    col3.metric("Status", source['status'].upper())
    
    st.markdown("---")
    
    # Instructions
    st.info("""
    **Instructions:**
    - Review the extracted text below
    - Make any necessary corrections
    - Click **Confirm & Save** when ready
    - Or **Discard** to remove this source entirely
    """)
    
    # Editable text area
    edited_text = st.text_area(
        "Extracted Text (Editable)",
        value=source['edited_text'],
        height=400,
        help="Edit the text to correct any OCR errors or add missing information",
        key=f"edit_text_{source_id}"
    )
    
    # Show if text was modified
    if edited_text != source['raw_text']:
        st.warning("⚠️ You have made changes to the original text")
    
    # Character/word count
    st.caption(f"Characters: {len(edited_text)} | Words: {len(edited_text.split())}")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("✅ Confirm & Save", type="primary", use_container_width=True):
            # Update text if changed
            if edited_text != source['edited_text']:
                update_source_text(source_id, edited_text)
            
            # Confirm source
            confirm_source(source_id)
            
            st.success(f"✅ {source['filename']} confirmed!")
            st.balloons()
            
            # Close modal
            close_review_modal()
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            close_review_modal()
            st.rerun()
    
    with col3:
        if st.button("🗑️ Discard", use_container_width=True):
            discard_source(source_id)
            st.warning(f"🗑️ {source['filename']} discarded")
            close_review_modal()
            st.rerun()
