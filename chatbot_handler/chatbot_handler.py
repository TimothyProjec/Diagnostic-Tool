"""
Chatbot handler for diagnosis refinement
Uses GPT-4o-mini to interact with doctor and modify diagnosis
"""

import streamlit as st
from openai import OpenAI

@st.cache_resource
def get_openai_client():
    """Initialize OpenAI client"""
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def initialize_chatbot():
    """Initialize chatbot session state"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'chat_modifications' not in st.session_state:
        st.session_state.chat_modifications = []


def get_initial_greeting():
    """Returns the chatbot's initial greeting message"""
    return """The initial diagnosis is ready for your review. I'm here to collaborate with you on refining it. What aspects would you like to explore or adjust?

I can help you:
• Modify specific sections of the diagnosis
• Explain reasoning behind conclusions
• Add or remove diagnoses
• Adjust medications or recommendations
• Answer medical knowledge questions
• Clarify any contradictions or uncertainties

What would you like to discuss?"""


def add_message(role, content):
    """
    Add a message to chat history
    
    Args:
        role: "user" or "assistant"
        content: Message text
    """
    initialize_chatbot()
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": st.session_state.get('timestamp', None)
    })


def get_chat_history():
    """Get all chat messages"""
    initialize_chatbot()
    return st.session_state.chat_history


def clear_chat():
    """Clear chat history"""
    st.session_state.chat_history = []
    st.session_state.chat_modifications = []


def generate_chat_response(user_message, current_diagnosis, source_data):
    """
    Generate AI response to user message
    
    Args:
        user_message: User's input
        current_diagnosis: Current diagnosis text
        source_data: Combined source text for context
        
    Returns:
        str: AI response
    """
    try:
        client = get_openai_client()
        
        # Build system prompt
        system_prompt = """You are an expert medical AI assistant helping a doctor refine a diagnostic assessment.

Your role:
- Collaborate with the doctor to improve the diagnosis
- Answer medical knowledge questions accurately
- Modify diagnosis sections when requested
- Ask clarifying questions when needed
- Admit when you don't have information from sources
- Never fabricate data not in the sources

When modifying the diagnosis:
- Make surgical, precise changes
- Preserve the original format/structure
- Highlight what you changed
- Explain your reasoning

When information is missing:
- Ask the doctor for clarification
- Suggest what information would help
- Don't speculate without data

Be professional, collaborative, and concise."""

        # Build context for this conversation
        conversation_context = f"""CURRENT DIAGNOSIS:
{current_diagnosis}

SOURCE DATA AVAILABLE:
{source_data[:3000]}  # Truncate if too long

Previous conversation:
"""
        
        # Add recent chat history (last 5 messages for context)
        recent_history = st.session_state.chat_history[-5:] if len(st.session_state.chat_history) > 5 else st.session_state.chat_history
        for msg in recent_history:
            conversation_context += f"\n{msg['role'].upper()}: {msg['content']}"
        
        conversation_context += f"\n\nDOCTOR'S NEW REQUEST: {user_message}"
        
        # Call GPT-4o-mini
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation_context}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        ai_response = response.choices[0].message.content
        
        return ai_response
        
    except Exception as e:
        return f"❌ Error generating response: {str(e)}\n\nPlease try rephrasing your question."


def extract_diagnosis_update(ai_response, current_diagnosis):
    """
    Extract updated diagnosis from AI response if modification was requested
    
    Args:
        ai_response: AI's response text
        current_diagnosis: Current diagnosis text
        
    Returns:
        str: Updated diagnosis or None if no update
    """
    # Simple heuristic: if response contains diagnosis-like structure, it's an update
    # More sophisticated: use another LLM call to extract structured updates
    
    # Check if AI response contains key diagnosis markers
    markers = ["DIAGNOSIS:", "MEDICATIONS:", "Name:", "Age:", "SPECIAL RISKS"]
    
    if any(marker in ai_response for marker in markers):
        # Likely contains updated diagnosis
        return ai_response
    
    return None


def apply_diagnosis_modification(modification_text):
    """
    Apply a diagnosis modification from chatbot
    
    Args:
        modification_text: New diagnosis text
    """
    st.session_state.final_diagnosis = modification_text
    st.session_state.chat_modifications.append({
        "timestamp": st.session_state.get('timestamp', None),
        "modification": modification_text
    })


def get_chat_summary():
    """
    Generate summary of chat conversation for report
    
    Returns:
        str: Summary text
    """
    if not st.session_state.chat_history:
        return ""
    
    summary_lines = ["CLINICAL DISCUSSION SUMMARY:", ""]
    
    modifications = st.session_state.get('chat_modifications', [])
    
    if modifications:
        summary_lines.append("Modifications made through AI consultation:")
        for idx, mod in enumerate(modifications, 1):
            summary_lines.append(f"{idx}. [Modification applied via chat]")
        summary_lines.append("")
    
    summary_lines.append(f"Total chat interactions: {len(st.session_state.chat_history)} messages")
    
    return "\n".join(summary_lines)


def open_chat():
    """Open chatbot interface"""
    st.session_state.show_chat = True


def close_chat():
    """Close chatbot interface"""
    st.session_state.show_chat = False


def is_chat_open():
    """Check if chat is currently open"""
    return st.session_state.get('show_chat', False)
