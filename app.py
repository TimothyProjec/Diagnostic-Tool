import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to center text and style the header
st.markdown("""
    <style>
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 5rem;
    }
    .greeting {
        font-size: 4rem;
        color: #1f77b4;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-greeting {
        font-size: 2rem;
        color: #4a4a4a;
        text-align: center;
        font-weight: 300;
    }
    </style>
""", unsafe_allow_html=True)

# Main Content
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<p class="greeting">Hello, Doctor 👋</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-greeting">Let\'s get started.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Minimal Sidebar (Optional: specific to navigation or disclaimer only)
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=Hospital+Logo", use_container_width=True)
    st.markdown("---")
    st.caption("Select a tool from the navigation menu above to begin.")
    
    # Keeping the disclaimer is usually recommended for medical apps, 
    # but you can remove this block if you want it strictly minimal.
    st.markdown("### ⚠️ Disclaimer")
    st.caption("""
    AI-assisted tool. Verify all outputs with clinical judgment.
    """)
