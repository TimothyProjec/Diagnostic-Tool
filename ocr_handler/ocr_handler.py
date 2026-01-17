"""
OCR text extraction using Qwen2.5-VL via API
"""

import streamlit as st
import requests
import base64
from PIL import Image
import io

def encode_image_to_base64(image_file):
    """
    Convert uploaded image to base64 string for API
    
    Args:
        image_file: Streamlit UploadedFile object
        
    Returns:
        str: Base64 encoded image
    """
    try:
        # Open and convert image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to bytes buffer
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=95)
        
        # Encode to base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return img_base64
        
    except Exception as e:
        st.error(f"Image encoding failed: {str(e)}")
        return None


def extract_text_from_image(image_file, api_key, prompt=None):
    """
    Extract text from medical document using Qwen2.5-VL API
    
    Args:
        image_file: Streamlit UploadedFile object
        api_key: OpenRouter API key
        prompt: Custom OCR instruction (optional)
        
    Returns:
        dict: Contains extracted text, status, and metadata
    """
    
    # Default medical OCR prompt
    if prompt is None:
        prompt = """Extract all text from this medical document while preserving structure and layout.
        
Pay special attention to:
- Patient demographics (name, age, DOB, ID numbers)
- Diagnoses and medical conditions
- Medications and dosages
- Lab results and vital signs
- Doctor's notes and observations
- Dates and timestamps

Preserve the original formatting and organization."""
    
    try:
        # Encode image to base64
        base64_image = encode_image_to_base64(image_file)
        
        if not base64_image:
            return {
                "filename": image_file.name,
                "extracted_text": None,
                "status": "failed",
                "error": "Image encoding failed",
                "word_count": 0
            }
        
        # API endpoint (OpenRouter)
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-app-url.streamlit.app",  # Optional
            "X-Title": "Medical Diagnostic Tool"  # Optional
        }
        
        payload = {
            "model": "qwen/qwen-2.5-vl-7b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 3000,
            "temperature": 0.1
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        extracted_text = result['choices'][0]['message']['content']
        
        return {
            "filename": image_file.name,
            "extracted_text": extracted_text,
            "status": "success",
            "error": None,
            "word_count": len(extracted_text.split()),
            "file_size_kb": round(image_file.size / 1024, 2)
        }
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"API Error: {e.response.status_code} - {e.response.text}"
        return {
            "filename": image_file.name,
            "extracted_text": None,
            "status": "failed",
            "error": error_msg,
            "word_count": 0
        }
        
    except requests.exceptions.Timeout:
        return {
            "filename": image_file.name,
            "extracted_text": None,
            "status": "failed",
            "error": "Request timeout - image might be too large",
            "word_count": 0
        }
        
    except Exception as e:
        return {
            "filename": image_file.name,
            "extracted_text": None,
            "status": "failed",
            "error": str(e),
            "word_count": 0
        }


def extract_structured_fields(image_file, api_key, fields):
    """
    Extract specific structured information from medical documents
    
    Args:
        image_file: Streamlit UploadedFile
        api_key: OpenRouter API key
        fields: List of field names to extract (e.g., ["Patient Name", "Date"])
        
    Returns:
        dict: Structured extraction result
    """
    
    fields_str = ", ".join(fields)
    
    prompt = f"""Extract ONLY the following specific information from this medical document:
{fields_str}

Format your response as:
Field Name: Value
Field Name: Value

If a field is not found in the document, write: Field Name: [Not found]
Be precise and extract exact values as they appear."""
    
    return extract_text_from_image(image_file, api_key, prompt)


def batch_extract_from_images(image_files, api_key, mode="full", fields=None):
    """
    Process multiple images for OCR
    
    Args:
        image_files: List of Streamlit UploadedFile objects
        api_key: OpenRouter API key
        mode: "full" or "structured"
        fields: List of fields (for structured mode)
        
    Returns:
        list: List of extraction results
    """
    results = []
    
    for image_file in image_files:
        if mode == "structured" and fields:
            result = extract_structured_fields(image_file, api_key, fields)
        else:
            result = extract_text_from_image(image_file, api_key)
        
        results.append(result)
    
    return results


def get_combined_text(ocr_results):
    """
    Combine all successful OCR results into single text
    
    Args:
        ocr_results: List of OCR result dicts
        
    Returns:
        str: Combined text from all documents
    """
    combined = []
    
    for result in ocr_results:
        if result['status'] == 'success' and result['extracted_text']:
            combined.append(f"\n{'='*60}\nFILE: {result['filename']}\n{'='*60}\n")
            combined.append(result['extracted_text'])
            combined.append("\n")
    
    return "\n".join(combined)
