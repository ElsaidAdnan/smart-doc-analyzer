# 🤖 Smart Document Analyzer

**An intelligent multi-document RAG application** built with **LangGraph** and **LangChain**, featuring a modern and interactive **Streamlit** interface.

It enables users to upload multiple PDF files, intelligently extract information, compare content across documents, and generate insightful analysis using a **multi-agent system**.

---

## ✨ Key Features

- **Multi-PDF RAG**: Simultaneous analysis and comparison of multiple documents
- **Multi-Agent Architecture**: Powered by **LangGraph** (Extractor → Analyst → Critic)
- **Advanced PDF Parsing**: Excellent handling of complex tables and layouts using **LlamaParse**
- **Dual-Column UI**: Chat interface + Real-time Data Visualization Dashboard
- **Full Arabic Support**: Complete Arabic language support in UI and exported reports (PDF & TXT)
- **Professional Export**: Export last Q&A or full conversation as **PDF** and **TXT** with proper Arabic rendering
- **Interactive Charts**: Automatic extraction and visualization of numerical data using **Plotly**
- **Modular & Scalable Design**: Clean project structure following best practices

---

## 🏗️ System Architecture

The application follows an **agentic workflow** orchestrated by **LangGraph**:

1. **Extraction Node** — Retrieves relevant context from all uploaded documents using MMR search with source diversity.
2. **Analysis Node** — Performs deep analysis, extracts structured data (including JSON for charts).
3. **Critic Node** — Reviews, refines, and ensures the final response is accurate, concise, and well-formatted.

This three-stage pipeline significantly reduces hallucinations and improves answer quality.

---

## 🛠️ Tech Stack

| Technology                    | Purpose                                      |
|------------------------------|----------------------------------------------|
| **Streamlit**                | Web Interface                                |
| **LangGraph**                | Multi-agent workflow orchestration           |
| **LangChain**                | RAG pipelines, prompts & document handling   |
| **LlamaParse**               | High-quality PDF text & table extraction     |
| **Qdrant**                   | In-memory vector database                    |
| **Hugging Face Embeddings**  | `all-MiniLM-L6-v2`                           |
| **Groq**                     | Fast LLM inference (`llama-3.3-70b-versatile`) |
| **FPDF + arabic-reshaper**   | Arabic-compatible PDF generation             |
| **Plotly**                   | Interactive data visualizations              |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/ElsaidAdnan/smart-doc-analyzer.git
cd smart-doc-analyzer
```

### 2. Create and activate virtual environment (Recommended)

```Bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS
```

### 3. Install dependencies

```Bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Copy .env.example to .env and add your API keys:

```env
LLAMA_CLOUD_API_KEY=your_llama_cloud_key_here
GROQ_API_KEY=your_groq_key_here
```

### 5. Add Arabic Font
Download DejaVuSans.ttf (or Noto Sans Arabic)
Place it inside the fonts/ folder

### 6. Run the application

```Bash
python -m streamlit run src/main.py
```

------

## 📁 Project Structure

```Bash
smart-doc-analyzer/
├── src/
│   ├── main.py                    # Main Streamlit application
│   ├── config.py                  # Configuration settings
│   ├── core/
│   │   └── agent_state.py
│   ├── agents/                    # LangGraph nodes and graph
│   └── utils/                     # PDF/TXT generation, document processing, session
├── fonts/                         # Arabic fonts
├── archived_reports/              # Generated reports (auto-created)
├── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📸 Screenshots
(Add screenshots of the application here later)

---

## 🙋‍♂️ Contributing

Contributions, issues, and feature requests are welcome!
Feel free to:

Open an Issue
Submit a Pull Request
Suggest new features

---

## Developed with ❤️ by [Elsaid Adnan]
If you found this project useful, please give it a ⭐ on GitHub!
