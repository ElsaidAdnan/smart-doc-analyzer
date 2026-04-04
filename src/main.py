import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from llama_parse import LlamaParse

from src.config import Config
from src.utils.session_manager import initialize_session_state, reset_system
from src.utils.document_processor import process_uploaded_files
from src.utils.pdf_generator import (
    create_pdf_with_last_question,
    create_pdf_with_full_chat,
    create_txt_with_last_question,
    create_txt_with_full_chat
)
from src.agents.graph import build_graph
from src.core.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
import datetime

# ====================== تهيئة Streamlit ======================
st.set_page_config(page_title="AI Document Analyzer", layout="wide", page_icon="🤖📄")

initialize_session_state()

# ====================== تهيئة الموارد ======================
@st.cache_resource
def init_resources():
    parser = LlamaParse(
        api_key=Config.LLAMA_CLOUD_API_KEY,
        result_type="markdown"
    )
    embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
    
    # استخدام Groq (يمكنك تغييره لاحقاً)
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=Config.GROQ_API_KEY
    )
    
    return parser, embeddings, llm

parser, embeddings, llm = init_resources()

# حفظ llm في session_state لاستخدامه في الـ nodes
if "llm" not in st.session_state:
    st.session_state.llm = llm

# بناء الـ Graph
app_graph = build_graph()

# ====================== الواجهة ======================
st.title("🤖📄 تحليل الوثائق الذكي")
st.markdown("!وابدأ المحادثة PDF تحليل ذكي ومقارنة بين الوثائق المرفوعة. قم برفع ملفات")

with st.sidebar:
    st.header("📁 إدارة المستندات")
    uploaded_files = st.file_uploader(
        "رفع الملفات (PDF)",
        type="pdf",
        accept_multiple_files=True
    )

    if st.button("🗑️ إعادة ضبط النظام"):
        reset_system()

    st.markdown("---")
    st.subheader("📄 تصدير التقارير")

    #if st.session_state.chat_history and len(st.session_state.chat_history) >= 2:
    if st.session_state.chat_history or len(st.session_state.chat_history) >= 2:
        last_question = st.session_state.chat_history[-2].content
        last_answer = st.session_state.chat_history[-1].content

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 PDF آخر سؤال", use_container_width=True):
                pdf_data, filename = create_pdf_with_last_question(last_question, last_answer)
                if pdf_data:
                    st.session_state.pdf_last_data = pdf_data
                    st.session_state.pdf_last_name = filename
                    st.success("✅ تم تجهيز PDF")

        with col2:
            if st.button("📥 TXT آخر سؤال", use_container_width=True):
                txt_data, txt_name = create_txt_with_last_question(last_question, last_answer)
                if txt_data:
                    st.session_state.txt_last_data = txt_data
                    st.session_state.txt_last_name = txt_name
                    st.success("✅ تم تجهيز TXT")

        # أزرار التحميل
        if st.session_state.get("pdf_last_data"):
            st.download_button(
                label="⬇️ تحميل PDF آخر سؤال",
                data=st.session_state.pdf_last_data,
                file_name=st.session_state.pdf_last_name,
                mime="application/pdf",
                use_container_width=True
            )

        if st.session_state.get("txt_last_data"):
            st.download_button(
                label="⬇️ تحميل TXT آخر سؤال",
                data=st.session_state.txt_last_data,
                file_name=st.session_state.txt_last_name,
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            if st.button("📑 PDF المحادثة كاملة", use_container_width=True):
                full_pdf, full_pdf_name = create_pdf_with_full_chat(st.session_state.chat_history)
                if full_pdf:
                    st.session_state.full_pdf_data = full_pdf
                    st.session_state.full_pdf_name = full_pdf_name
                    st.success("✅ تم تجهيز PDF كامل")

        with col4:
            if st.button("📑 TXT المحادثة كاملة", use_container_width=True):
                full_txt, full_txt_name = create_txt_with_full_chat(st.session_state.chat_history)
                if full_txt:
                    st.session_state.full_txt_data = full_txt
                    st.session_state.full_txt_name = full_txt_name
                    st.success("✅ تم تجهيز TXT كامل")

        if st.session_state.get("full_pdf_data"):
            st.download_button(
                label="⬇️ تحميل PDF كامل",
                data=st.session_state.full_pdf_data,
                file_name=st.session_state.full_pdf_name,
                mime="application/pdf",
                use_container_width=True
            )

        if st.session_state.get("full_txt_data"):
            st.download_button(
                label="⬇️ تحميل TXT كامل",
                data=st.session_state.full_txt_data,
                file_name=st.session_state.full_txt_name,
                mime="text/plain",
                use_container_width=True
            )

# ====================== معالجة الملفات ======================
if uploaded_files and st.session_state.vector_store is None:
    st.session_state.uploaded_files = uploaded_files
    st.session_state.vector_store = process_uploaded_files(uploaded_files, parser, embeddings)

# ====================== المحادثة ======================
col_chat, col_dash = st.columns([1, 1])

with col_chat:
    st.subheader("💬 المحادثة")
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
            st.markdown(msg.content)

if user_input := st.chat_input("اكتب سؤالك هنا..."):
    with col_chat:
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

    with col_chat:
        with st.chat_message("assistant"):
            with st.spinner("جاري التحليل..."):
                inputs = {
                    "input": user_input,
                    "chat_history": st.session_state.chat_history,
                    "context": "", 
                    "analysis": "",
                    "dashboard_data": {},
                    "final_answer": ""
                }
                output = app_graph.invoke(inputs)

                final_answer = output["final_answer"]
                st.markdown(final_answer)

                st.session_state.chat_history.append(AIMessage(content=final_answer))
                st.session_state.last_answer = final_answer

    with col_dash:
        st.subheader("📊 لوحة البيانات")
        if output.get("dashboard_data"):
            try:
                import pandas as pd
                import plotly.express as px
                
                df = pd.DataFrame(output["dashboard_data"])
                # يمكن تحسين هذا الجزء حسب شكل الـ JSON
                st.plotly_chart(px.bar(df), use_container_width=True)
            except:
                st.info("لا يمكن عرض البيانات في شكل جدول أو رسم بياني.")
        else:
            st.write("سيظهر الرسم البياني هنا عند وجود بيانات رقمية.")
            