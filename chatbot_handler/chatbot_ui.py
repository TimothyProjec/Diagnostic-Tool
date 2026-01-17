"""
Modern chatbot UI with ChatGPT-style interface
"""

import streamlit as st
from utils.chatbot_handler import (
    initialize_chatbot,
    get_initial_greeting,
    add_message,
    get_chat_history,
    generate_chat_response,
    extract_diagnosis_update,
    apply_diagnosis_modification,
    close_chat
)


def render_chatbot_fullscreen(current_diagnosis, source_data):
    """
    Render full-screen ChatGPT-style chatbot interface
    
    Args:
        current_diagnosis: Current diagnosis text
        source_data: Combined source text for context
    """
    initialize_chatbot()
    
    # Custom CSS for ChatGPT-style UI
    st.markdown("""
        <style>
        /* Chat container styling */
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header styling */
        .chat-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .chat-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .chat-subtitle {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* Diagnosis preview styling */
        .diagnosis-preview {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }
        
        /* Chat message styling enhancements */
        .stChatMessage {
            margin-bottom: 15px;
        }
        
        /* Input field styling */
        .stChatInput {
            border-radius: 25px;
        }
        
        /* Button container */
        .action-buttons {
            position: sticky;
            bottom: 0;
            background: white;
            padding: 20px 0;
            border-top: 2px solid #e0e0e0;
            margin-top: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="chat-header">
            <div class="chat-title">🤖 AI Diagnostic Assistant</div>
            <div class="chat-subtitle">Collaborate to refine your diagnosis</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Diagnosis preview (collapsible)
    with st.expander("📋 Current Diagnosis (Click to view)", expanded=False):
        st.text_area(
            "Current Diagnosis",
            current_diagnosis,
            height=300,
            disabled=True,
            key="chat_diag_preview",
            label_visibility="collapsed"
        )
        st.caption("💡 Ask the AI to modify any part of this diagnosis")
    
    st.markdown("---")
    
    # Initialize with greeting if first time
    chat_history = get_chat_history()
    if not chat_history:
        greeting = get_initial_greeting()
        add_message("assistant", greeting)
        chat_history = get_chat_history()
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        for idx, message in enumerate(chat_history):
            with st.chat_message(
                message["role"],
                avatar="🤖" if message["role"] == "assistant" else "👨‍⚕️"
            ):
                st.markdown(message["content"])
    
    # Suggested prompts (only show if chat just started)
    if len(chat_history) <= 1:
        st.markdown("### 💡 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Explain reasoning", key="suggest_explain", use_container_width=True):
                st.session_state.suggested_prompt = "Explain the reasoning behind the provisional diagnosis"
                st.rerun()
        
        with col2:
            if st.button("✏️ Modify diagnosis", key="suggest_modify", use_container_width=True):
                st.session_state.suggested_prompt = "I'd like to change the provisional diagnosis"
                st.rerun()
        
        with col3:
            if st.button("📊 Add tests", key="suggest_tests", use_container_width=True):
                st.session_state.suggested_prompt = "What additional tests should I recommend?"
                st.rerun()
    
    # Chat input
    default_prompt = st.session_state.pop('suggested_prompt', None)
    
    if user_input := st.chat_input(
        "Ask a question or request changes...", 
        key="chat_input_field"
    ):
        
        # Add user message
        add_message("user", user_input)
        
        # Display user message
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(user_input)
        
        # Generate AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Analyzing..."):
                
                ai_response = generate_chat_response(
                    user_input, 
                    current_diagnosis,
                    source_data
                )
                
                st.markdown(ai_response)
                
                # Check if this is a diagnosis modification
                updated_diagnosis = extract_diagnosis_update(ai_response, current_diagnosis)
                
                if updated_diagnosis:
                    st.success("✅ Diagnosis updated based on your request!")
                    apply_diagnosis_modification(updated_diagnosis)
                
                # Add AI response to history
                add_message("assistant", ai_response)
        
        st.rerun()
    
    # Handle suggested prompt
    if default_prompt:
        # Trigger the prompt as if user typed it
        add_message("user", default_prompt)
        
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(default_prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Analyzing..."):
                ai_response = generate_chat_response(
                    default_prompt, 
                    current_diagnosis,
                    source_data
                )
                
                st.markdown(ai_response)
                
                updated_diagnosis = extract_diagnosis_update(ai_response, current_diagnosis)
                
                if updated_diagnosis:
                    st.success("✅ Diagnosis updated!")
                    apply_diagnosis_modification(updated_diagnosis)
                
                add_message("assistant", ai_response)
        
        st.rerun()
    
    # Sticky action buttons at bottom
    st.markdown("---")
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Clear Chat", key="clear_chat_btn", use_container_width=True, help="Start over"):
            from utils.chatbot_handler import clear_chat
            clear_chat()
            st.rerun()
    
    with col2:
        if st.button("👁️ View Diagnosis", key="view_diag_btn", use_container_width=True):
            # Toggle expander open
            st.info("👆 Check the 'Current Diagnosis' section above")
    
    with col3:
        if st.button(
            "📄 Generate Final Report", 
            key="generate_final_report_btn", 
            type="primary", 
            use_container_width=True,
            help="Finalize and download the diagnosis report"
        ):
            close_chat()
            st.session_state.ready_for_download = True
            st.success("✅ Report ready! Scroll down to download.")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat statistics
    st.markdown("---")
    st.caption(f"💬 {len(chat_history)} messages | 🤖 AI-powered refinement | ✅ Changes auto-saved")


def show_chatbot_transition():
    """
    Show transition screen when entering chatbot mode
    """
    st.balloons()
    
    st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <h1 style="color: #667eea;">🤖 Entering AI Collaboration Mode</h1>
            <p style="font-size: 1.2rem; color: #666;">
                Work with AI to refine your diagnosis to perfection
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
