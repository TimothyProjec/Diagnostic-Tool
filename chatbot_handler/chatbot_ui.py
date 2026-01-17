"""
Simple inline chatbot UI
"""

import streamlit as st
from chatbot_handler.chatbot_handler import (
    initialize_chatbot,
    get_initial_greeting,
    add_message,
    get_chat_history,
    generate_chat_response,
    extract_diagnosis_update,
    apply_diagnosis_modification,
    close_chat,
    clear_chat
)


def render_chatbot_inline(current_diagnosis, source_data):
    """
    Render simple inline chatbot interface on same page
    
    Args:
        current_diagnosis: Current diagnosis text
        source_data: Combined source text for context
    """
    initialize_chatbot()
    
    st.markdown("---")
    st.write("### 💬 Chat with AI to Refine Diagnosis")
    
    # Initialize with greeting if first time
    chat_history = get_chat_history()
    if not chat_history:
        greeting = get_initial_greeting()
        add_message("assistant", greeting)
        chat_history = get_chat_history()
    
    # Display chat messages
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask a question or request changes...", key="chat_input_field"):
        
        # Add user message
        add_message("user", user_input)
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                
                ai_response = generate_chat_response(
                    user_input, 
                    current_diagnosis,
                    source_data
                )
                
                st.write(ai_response)
                
                # Check if this is a diagnosis modification
                updated_diagnosis = extract_diagnosis_update(ai_response, current_diagnosis)
                
                if updated_diagnosis:
                    st.success("✅ Diagnosis updated!")
                    apply_diagnosis_modification(updated_diagnosis)
                
                # Add AI response to history
                add_message("assistant", ai_response)
        
        st.rerun()
    
    # Action buttons below chat
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Clear Chat", key="clear_chat_btn", use_container_width=True):
            clear_chat()
            st.rerun()
    
    with col2:
        if st.button("✅ Done, Finalize Report", key="finalize_btn", type="primary", use_container_width=True):
            close_chat()
            st.session_state.ready_for_download = True
            st.success("✅ Diagnosis finalized! Scroll down to download.")
            st.rerun()
