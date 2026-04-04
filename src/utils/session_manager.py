import streamlit as st

def initialize_session_state():
    """تهيئة كل المتغيرات في session_state"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None
    if "pdf_last_data" not in st.session_state:
        st.session_state.pdf_last_data = None
    if "pdf_last_name" not in st.session_state:
        st.session_state.pdf_last_name = None
    if "full_pdf_data" not in st.session_state:
        st.session_state.full_pdf_data = None
    if "full_pdf_name" not in st.session_state:
        st.session_state.full_pdf_name = None
    if "full_txt_data" not in st.session_state:
        st.session_state.full_txt_data = None
    if "full_txt_name" not in st.session_state:
        st.session_state.full_txt_name = None


def reset_system():
    """إعادة ضبط النظام بالكامل"""
    keys = [
        "chat_history", "vector_store", "uploaded_files", "last_answer",
        "pdf_last_data", "pdf_last_name", "full_pdf_data", "full_pdf_name",
        "full_txt_data", "full_txt_name"
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
    