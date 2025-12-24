"""
Audio transcription using OpenAI Whisper API
"""

from openai import OpenAI
import tempfile
import os
import streamlit as st

@st.cache_resource
def get_openai_client():
    """Initialize OpenAI client with API key from secrets"""
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def transcribe_audio(audio_file):
    """
    Transcribe audio file using Whisper API
    
    Args:
        audio_file: Streamlit UploadedFile object
        
    Returns:
        str: Transcribed text or None if error
    """
    try:
        client = get_openai_client()
        
        # Create temporary file (Whisper API needs file path)
        file_extension = os.path.splitext(audio_file.name)[1]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            # Write uploaded file to temp location
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Transcribe using Whisper
        with open(tmp_file_path, 'rb') as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        
        # Clean up temp file
        os.remove(tmp_file_path)
        
        return transcript
        
    except Exception as e:
        st.error(f"❌ Transcription failed: {str(e)}")
        return None

def get_audio_info(audio_file):
    """
    Get metadata about uploaded audio file
    
    Args:
        audio_file: Streamlit UploadedFile object
        
    Returns:
        dict: File metadata
    """
    return {
        "filename": audio_file.name,
        "size_kb": round(audio_file.size / 1024, 2),
        "type": audio_file.type
    }
