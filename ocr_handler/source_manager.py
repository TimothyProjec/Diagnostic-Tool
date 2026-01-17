"""
Unified source management for all data inputs (OCR, Audio, etc.)
Handles review, editing, and confirmation workflow
"""

import streamlit as st
from datetime import datetime


def initialize_source_manager():
    """Initialize session state for source management"""
    if 'sources' not in st.session_state:
        st.session_state.sources = []
    if 'review_mode' not in st.session_state:
        st.session_state.review_mode = None  # Stores index of source being reviewed


def add_source(source_type, filename, raw_text, metadata=None):
    """
    Add a new source to the system
    
    Args:
        source_type: "ocr", "audio", "manual"
        filename: Name of the source file
        raw_text: Original extracted/transcribed text
        metadata: Additional info (word_count, file_size, etc.)
        
    Returns:
        int: Index of added source
    """
    initialize_source_manager()
    
    source = {
        "id": len(st.session_state.sources),
        "type": source_type,
        "filename": filename,
        "raw_text": raw_text,
        "edited_text": raw_text,  # Start with raw text
        "status": "pending",  # pending, confirmed, discarded
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confirmed_at": None,
        "metadata": metadata or {},
        "word_count": len(raw_text.split()) if raw_text else 0
    }
    
    st.session_state.sources.append(source)
    return source["id"]


def get_source_by_id(source_id):
    """Get source by ID"""
    initialize_source_manager()
    for source in st.session_state.sources:
        if source["id"] == source_id:
            return source
    return None


def update_source_text(source_id, new_text):
    """Update edited text for a source"""
    initialize_source_manager()
    for source in st.session_state.sources:
        if source["id"] == source_id:
            source["edited_text"] = new_text
            source["word_count"] = len(new_text.split())
            break


def confirm_source(source_id):
    """Mark source as confirmed"""
    initialize_source_manager()
    for source in st.session_state.sources:
        if source["id"] == source_id:
            source["status"] = "confirmed"
            source["confirmed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break


def discard_source(source_id):
    """Remove source from system"""
    initialize_source_manager()
    st.session_state.sources = [
        s for s in st.session_state.sources if s["id"] != source_id
    ]


def get_all_sources():
    """Get all sources"""
    initialize_source_manager()
    return st.session_state.sources


def get_pending_sources():
    """Get sources pending review"""
    initialize_source_manager()
    return [s for s in st.session_state.sources if s["status"] == "pending"]


def get_confirmed_sources():
    """Get confirmed sources"""
    initialize_source_manager()
    return [s for s in st.session_state.sources if s["status"] == "confirmed"]


def all_sources_confirmed():
    """Check if all sources are confirmed"""
    initialize_source_manager()
    if not st.session_state.sources:
        return False
    return all(s["status"] == "confirmed" for s in st.session_state.sources)


def get_combined_text():
    """Get all confirmed source texts combined"""
    confirmed = get_confirmed_sources()
    
    if not confirmed:
        return ""
    
    combined = []
    for source in confirmed:
        combined.append(f"\n{'='*60}")
        combined.append(f"SOURCE: {source['filename']} ({source['type'].upper()})")
        combined.append(f"{'='*60}\n")
        combined.append(source['edited_text'])
        combined.append("\n")
    
    return "\n".join(combined)


def get_source_summary():
    """Get summary statistics of all sources"""
    initialize_source_manager()
    
    sources = st.session_state.sources
    confirmed = get_confirmed_sources()
    pending = get_pending_sources()
    
    total_words = sum(s['word_count'] for s in confirmed)
    
    return {
        'total_sources': len(sources),
        'confirmed': len(confirmed),
        'pending': len(pending),
        'total_words': total_words,
        'by_type': {
            'ocr': len([s for s in confirmed if s['type'] == 'ocr']),
            'audio': len([s for s in confirmed if s['type'] == 'audio']),
            'manual': len([s for s in confirmed if s['type'] == 'manual'])
        }
    }


def bulk_confirm_all():
    """Confirm all pending sources at once"""
    initialize_source_manager()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for source in st.session_state.sources:
        if source["status"] == "pending":
            source["status"] = "confirmed"
            source["confirmed_at"] = timestamp


def clear_all_sources():
    """Remove all sources"""
    st.session_state.sources = []
    st.session_state.review_mode = None


def open_review_modal(source_id):
    """Open review modal for a source"""
    st.session_state.review_mode = source_id


def close_review_modal():
    """Close review modal"""
    st.session_state.review_mode = None
