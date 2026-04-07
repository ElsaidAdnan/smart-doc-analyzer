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
from langchain_core.messages import HumanMessage, AIMessage
import pandas as pd
import plotly.express as px

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

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 PDF آخر سؤال", width="stretch"):
            if st.session_state.chat_history and len(st.session_state.chat_history) >= 2:
                last_question = st.session_state.chat_history[-2].content
                last_answer = st.session_state.chat_history[-1].content
                
                pdf_data, filename = create_pdf_with_last_question(last_question, last_answer)
                if pdf_data:
                    st.session_state.pdf_last_data = pdf_data
                    st.session_state.pdf_last_name = filename
                    st.success("✅ تم تجهيز PDF")
            else:
                st.warning("⚠️ لا توجد محادثة حالية لحفظها.")

    with col2:
        if st.button("📥 TXT آخر سؤال", width="stretch"):
            if st.session_state.chat_history and len(st.session_state.chat_history) >= 2:
                last_question = st.session_state.chat_history[-2].content
                last_answer = st.session_state.chat_history[-1].content
                
                txt_data, txt_name = create_txt_with_last_question(last_question, last_answer)
                if txt_data:
                    st.session_state.txt_last_data = txt_data
                    st.session_state.txt_last_name = txt_name
                    st.success("✅ تم تجهيز TXT")
            else:
                st.warning("⚠️ لا توجد محادثة حالية لحفظها.")

    # أزرار التحميل
    if st.session_state.get("pdf_last_data"):
        st.download_button(
            label="⬇️ تحميل PDF آخر سؤال",
            data=st.session_state.pdf_last_data,
            file_name=st.session_state.pdf_last_name,
            mime="application/pdf",
            width="stretch"
        )

    if st.session_state.get("txt_last_data"):
        st.download_button(
            label="⬇️ تحميل TXT آخر سؤال",
            data=st.session_state.txt_last_data,
            file_name=st.session_state.txt_last_name,
            mime="text/plain",
            width="stretch"
        )

    st.markdown("---")

    col3, col4 = st.columns(2)
        
    with col3:
        if st.button("📑 PDF المحادثة كاملة", width="stretch"):
            if st.session_state.chat_history:
                    
                full_pdf, full_pdf_name = create_pdf_with_full_chat(st.session_state.chat_history)
                if full_pdf:
                    st.session_state.full_pdf_data = full_pdf
                    st.session_state.full_pdf_name = full_pdf_name
                    st.success("✅ تم تجهيز PDF كامل")
            else:
                st.warning("⚠️ سجل المحادثة فارغ حالياً.")
        
    with col4:
        if st.button("📑 TXT المحادثة كاملة", width="stretch"):
            if st.session_state.chat_history:
            
                full_txt, full_txt_name = create_txt_with_full_chat(st.session_state.chat_history)
                if full_txt:
                    st.session_state.full_txt_data = full_txt
                    st.session_state.full_txt_name = full_txt_name
                    st.success("✅ تم تجهيز TXT كامل")
            else:
                st.warning("⚠️ سجل المحادثة فارغ حالياً.")    

    if st.session_state.get("full_pdf_data"):
        st.download_button(
            label="⬇️ تحميل PDF كامل",
            data=st.session_state.full_pdf_data,
            file_name=st.session_state.full_pdf_name,
            mime="application/pdf",
            width="stretch"
        )

    if st.session_state.get("full_txt_data"):
        st.download_button(
            label="⬇️ تحميل TXT كامل",
            data=st.session_state.full_txt_data,
            file_name=st.session_state.full_txt_name,
            mime="text/plain",
            width="stretch"
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
                st.session_state.last_output = output   #  مهم لحفظ الرسم البياني


    with col_dash:
        st.subheader("📊 لوحة البيانات التفاعلية")

        current_output = st.session_state.get("last_output", output)

        if current_output and current_output.get("dashboard_data"):
            try:
                raw_data = current_output["dashboard_data"]

                if not raw_data:
                    st.info("لا توجد بيانات رقمية للرسم")
                    st.stop()

                # ====================== تحويل البيانات بأمان ======================
                if isinstance(raw_data, dict):
                    if all(isinstance(v, (int, float)) for v in raw_data.values()):
                        df = pd.DataFrame([raw_data])
                        is_scalar = True
                    else:
                        df = pd.DataFrame(raw_data)
                        is_scalar = False
                else:
                    df = pd.DataFrame(raw_data)
                    is_scalar = False

                if df.empty:
                    st.info("البيانات فارغة")
                    st.json(raw_data)
                    st.stop()

                category_col = df.columns[0]

                # ====================== اختيار Tabs حسب نوع البيانات ======================
                if is_scalar:
                    tab_titles = ["📊 Bar Chart", "🥧 Pie Chart"]
                else:
                    tab_titles = ["📈 Line Chart", "📊 Bar Chart", "📉 Area Chart", "🥧 Pie Chart"]

                tabs = st.tabs(tab_titles)

                # تحضير البيانات المذابة
                if is_scalar:
                    df_melted = df.melt(var_name='البند', value_name='القيمة')
                else:
                    df_melted = df.melt(id_vars=[category_col], var_name='الفترة', value_name='القيمة')

                # ==================== حالة البيانات المفردة ====================
                if is_scalar:
                    with tabs[0]:   # Bar Chart
                        fig_bar = px.bar(df_melted, 
                                        x='البند', 
                                        y='القيمة', 
                                        text='القيمة',
                                        template="plotly_dark",
                                        title="📊 القيم المالية الرئيسية")
                        fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                        st.plotly_chart(fig_bar, use_container_width=True)

                    with tabs[1]:   # Pie Chart
                        fig_pie = px.pie(df_melted, 
                                        names='البند', 
                                        values='القيمة',
                                        template="plotly_dark",
                                        title="🥧 توزيع القيم")
                        st.plotly_chart(fig_pie, use_container_width=True)

                # ==================== حالة البيانات المتعددة ====================
                else:
                    with tabs[0]:   # Line Chart
                        fig = px.line(df_melted, x='الفترة', y='القيمة', color=category_col,
                                    markers=True, template="plotly_dark", 
                                    title="📈 الاتجاه الزمني")
                        st.plotly_chart(fig, use_container_width=True)

                    with tabs[1]:   # Bar Chart
                        fig = px.bar(df_melted, x='الفترة', y='القيمة', color=category_col,
                                    barmode='group', template="plotly_dark", 
                                    title="📊 مقارنة الفترات")
                        st.plotly_chart(fig, use_container_width=True)

                    with tabs[2]:   # Area Chart
                        fig = px.area(df_melted, x='الفترة', y='القيمة', color=category_col,
                                    template="plotly_dark", title="📉 الاتجاه التراكمي")
                        st.plotly_chart(fig, use_container_width=True)

                    with tabs[3]:   # Pie Chart
                        try:
                            value_col = df.columns[-1] if len(df.columns) > 1 else df.columns[0]
                            fig_pie = px.pie(df, names=category_col, values=value_col,
                                            template="plotly_dark", 
                                            title="🥧 توزيع النسب")
                            st.plotly_chart(fig_pie, use_container_width=True)
                        except:
                            st.info("Pie Chart غير مناسب لهذا النوع من البيانات")

                # ====================== عرض جدول الأرقام الدقيقة ======================
                st.markdown("### 📋 جدول البيانات الدقيقة")
                
                # تنسيق الأرقام الكبيرة (فواصل آلاف + تنسيق جميل)
                display_df = df.copy()
                
                # تنسيق الأعمدة الرقمية
                for col in display_df.columns:
                    if display_df[col].dtype in ['int64', 'float64']:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if x >= 1000 else x)
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # عرض البيانات الخام (JSON)
                with st.expander("🔍 عرض البيانات الخام (JSON)"):
                    st.json(raw_data)

            except Exception as e:
                st.error(f"⚠️ لرسم البيانات بشكل افضل : {str(e)}")
                st.write("البيانات المستلمة:", raw_data)

        else:
            st.info("💡 لا توجد بيانات رقمية قابلة للرسم.\n"
                    "جرب أسئلة تحتوي على أرقام أو مقارنات مثل:\n"
                    "«ما هي الإيرادات والأرباح والمصروفات للسنة الحالية؟»")
            