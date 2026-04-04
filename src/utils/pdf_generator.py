import datetime
import os
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from langchain_core.messages import HumanMessage, AIMessage

def create_pdf_with_last_question(question: str, answer: str):
    try:
        pdf = FPDF()
        pdf.add_page()

        # إضافة الخط العربي
        try:
            font_path = os.path.join("fonts", "DejaVuSans.ttf")
            pdf.add_font('DejaVu', '', font_path, uni=True)
            pdf.set_font('DejaVu', size=12)
        except Exception:
            pdf.set_font("Arial", size=12)

        clean_q = str(question).replace("**", "").replace("#", "")
        clean_a = str(answer).replace("**", "").replace("#", "").replace("- ", "• ")

        full_text = f"--- تقرير السؤال والإجابة ---\n"
        full_text += f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_text += "=" * 50 + "\n\n"
        full_text += f"❓ السؤال:\n{clean_q}\n\n"
        full_text += "=" * 50 + "\n\n"
        full_text += f"💡 الإجابة:\n{clean_a}"

        reshaped_text = reshape(full_text)
        bidi_text = get_display(reshaped_text)

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.multi_cell(w=0, h=10, txt=bidi_text, align='R')

        # حفظ الملف
        save_dir = "archived_reports"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_Last_QA_{timestamp}.pdf"
        server_path = os.path.join(save_dir, filename)

        pdf_bytes = bytes(pdf.output())
        with open(server_path, "wb") as f:
            f.write(pdf_bytes)

        return pdf_bytes, filename

    except Exception as e:
        print(f"Error in PDF Generation: {e}")
        return None, None


def create_pdf_with_full_chat(chat_history):
    try:
        if not chat_history:
            return None

        pdf = FPDF()
        pdf.add_page()

        try:
            font_path = os.path.join("fonts", "DejaVuSans.ttf")
            pdf.add_font('DejaVu', '', font_path, uni=True)
            pdf.set_font('DejaVu', size=12)
        except Exception:
            pdf.set_font("Arial", size=12)

        full_text = "--- سجل المحادثة الكامل ---\n\n"
        full_text += f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_text += "=" * 50 + "\n\n"

        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                full_text += f"❓ السؤال:\n{msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                content = msg.content.replace("**", "").replace("#", "").replace("- ", "• ")
                full_text += f"💡 الإجابة:\n{content}\n"
                full_text += "-" * 40 + "\n\n"

        reshaped_text = reshape(full_text)
        bidi_text = get_display(reshaped_text)

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.multi_cell(w=0, h=9, txt=bidi_text, align='R')

        save_dir = "archived_reports"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Full_Chat_Report_{timestamp}.pdf"
        server_path = os.path.join(save_dir, filename)

        pdf_bytes = bytes(pdf.output())
        with open(server_path, "wb") as f:
            f.write(pdf_bytes)

        return pdf_bytes, filename

    except Exception as e:
        print(f"Error in Full PDF Generation: {e}")
        return None, None


def create_txt_with_last_question(question: str, answer: str):
    try:
        save_dir = "archived_reports"
        os.makedirs(save_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Report_Last_QA_{timestamp}.txt"
        server_path = os.path.join(save_dir, filename)

        full_report = f"--- تقرير السؤال والإجابة ---\n"
        full_report += f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_report += "=" * 50 + "\n\n"
        full_report += f"❓ السؤال:\n{question}\n\n"
        full_report += "=" * 50 + "\n\n"
        full_report += f"💡 الإجابة:\n{answer}\n"

        with open(server_path, "w", encoding="utf-8") as f:
            f.write(full_report)

        return full_report, filename

    except Exception as e:
        print(f"Error in TXT Generation: {e}")
        return None, None


def create_txt_with_full_chat(chat_history):
    try:
        if not chat_history:
            return None, None

        full_report = "--- سجل المحادثة الكامل ---\n\n"
        full_report += f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_report += "=" * 50 + "\n\n"

        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                full_report += f"❓ السؤال:\n{msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                full_report += f"💡 الإجابة:\n{msg.content}\n"
                full_report += "-" * 40 + "\n\n"

        save_dir = "archived_reports"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Full_Chat_Report_{timestamp}.txt"
        server_path = os.path.join(save_dir, filename)

        with open(server_path, "w", encoding="utf-8") as f:
            f.write(full_report)

        return full_report, filename

    except Exception as e:
        print(f"Error in Full TXT Generation: {e}")
        return None, None
    