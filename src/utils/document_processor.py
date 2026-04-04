import streamlit as st
import os
from langchain_core.documents import Document as LC_Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from src.config import Config

def process_uploaded_files(uploaded_files, parser, embeddings):
    """معالجة الملفات المرفوعة وإنشاء Vector Store"""
    if not uploaded_files:
        return None

    all_docs = []
    
    with st.spinner("🔍 جاري تحليل المستندات باستخدام LlamaParse..."):
        for f in uploaded_files:
            temp_path = f"temp_{f.name}"
            try:
                with open(temp_path, "wb") as tmp:
                    tmp.write(f.getbuffer())

                # تحليل الملف بـ LlamaParse
                parsed_data = parser.load_data(temp_path, extra_info={"source": f.name})

                for doc in parsed_data:
                    metadata = doc.metadata.copy()
                    metadata["source"] = f.name
                    all_docs.append(LC_Document(
                        page_content=doc.text,
                        metadata=metadata
                    ))
            finally:
                # تنظيف الملف المؤقت
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # تقسيم النصوص
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        final_chunks = splitter.split_documents(all_docs)

        # إنشاء Vector Store
        vector_store = QdrantVectorStore.from_documents(
            final_chunks,
            embeddings,
            location=":memory:",
            collection_name=Config.COLLECTION_NAME
        )

        st.success(f"✅ تم معالجة {len(uploaded_files)} ملف بنجاح!")
        return vector_store
    