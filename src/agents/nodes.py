import re
import json
import streamlit as st
from src.config import Config
from langchain_core.messages import HumanMessage, AIMessage

def extraction_node(state):
    """الوكيل الأول: استخراج السياق من الوثائق"""
    if not st.session_state.vector_store:
        return {"context": "لا توجد وثائق مرفوعة."}

    retriever = st.session_state.vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 10,
            "fetch_k": 25,
            "lambda_mult": 0.6
        }
    )

    docs = retriever.invoke(state['input'])
    context_parts = []
    sources_found = set()

    for d in docs:
        source_name = d.metadata.get('source', 'مصدر مجهول')
        sources_found.add(source_name)
        context_parts.append(f"--- من وثيقة: {source_name} ---\n{d.page_content}\n")

    context = "\n\n".join(context_parts)

    if len(sources_found) < len(st.session_state.get('uploaded_files', [])):
        context += "\n\n⚠️ ملاحظة: تم العثور على بيانات من بعض الملفات فقط. حاول المقارنة بين كل الملفات."

    return {"context": context}


def analysis_node(state):
    """الوكيل الثاني: تحليل المحتوى"""
    prompt = f"""أنت خبير استخراج معلومات دقيق.
أجب على السؤال باختصار شديد بناءً على السياق فقط.

السياق:
{state['context']}

السؤال: {state['input']}

التعليمات:
- ابدأ الإجابة مباشرة بدون مقدمات.
- استخدم نقاط مركزة.
- إذا وجدت أرقام تاريخية أو مقارنات، استخرجها داخل <CHART_DATA>...</CHART_DATA> بصيغة JSON.
- إذا لم تجد إجابة، قل "المعلومة غير متوفرة في الوثائق".

الإجابة:"""

    res = st.session_state.llm.invoke(prompt)   # سنمرر llm من main
    content = res.content

    dashboard_data = {}
    json_match = re.search(r'<CHART_DATA>(.*?)</CHART_DATA>', content, re.DOTALL)
    if json_match:
        try:
            dashboard_data = json.loads(json_match.group(1).strip())
            content = content.replace(json_match.group(0), "\n*(تم استخراج بيانات بيانية)*\n")
        except:
            dashboard_data = {}

    return {"analysis": content, "dashboard_data": dashboard_data}


def critic_node(state):
    """الوكيل الثالث: تنقيح الإجابة النهائية"""
    prompt = f"""حوّل التقرير التالي إلى إجابة نهائية مختصرة واحترافية.

التقرير:
{state['analysis']}

السؤال: {state['input']}

المهام:
- احذف الحشو والتكرار.
- اجعل الإجابة في 3-6 نقاط فقط.
- اذكر المصادر في النهاية إن أمكن.
- اكتب بلغة عربية فصحى واضحة.

الإجابة النهائية:"""

    res = st.session_state.llm.invoke(prompt)
    return {"final_answer": res.content}
