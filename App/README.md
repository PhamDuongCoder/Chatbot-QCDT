# 🤖 QCĐT Chatbot — Streamlit App

A conversational chatbot powered by **Google Gemini** and **ChromaDB** to answer questions about Hanoi University of Science and Technology (QCĐT).

## ✨ Features

- 💬 **Interactive Chat Interface** — Beautiful Streamlit UI with chat history
- 🔍 **Semantic Search** — Retrieves relevant documents using ChromaDB embeddings
- 🤖 **Smart Responses** — Uses Google Gemini to generate contextual answers
- 📚 **Source Citation** — Shows where the answer came from
- 🎛️ **Configurable** — Adjust number of retrieved sources in settings
- 🗑️ **Chat Management** — Clear conversation history anytime

## 📋 Prerequisites

Before running the app, ensure you have:

1. **ChromaDB database created** with embedded chunks
   ```bash
   # Run the batch embedding script first
   python Script/Indexing/batch_embedding.py
   ```

2. **Google API Key** in `.env` file
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Required packages installed**
   ```bash
   pip install streamlit chromadb google-genai python-dotenv
   ```

## 🚀 How to Run

### **Option 1: Run from workspace root**
```bash
cd "c:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT"
streamlit run App/chatbot_app.py
```

### **Option 2: Run from terminal**
```bash
streamlit run "c:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\App\chatbot_app.py"
```

### **Option 3: Create a shortcut batch file** (Recommended)
Create `run_chatbot.bat` in workspace root:
```batch
@echo off
cd /d "c:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT"
streamlit run App/chatbot_app.py
pause
```

Then double-click `run_chatbot.bat` to start the app.

## 🎯 How to Use

1. **Open the app** — Browser opens to `http://localhost:8501`

2. **Ask questions** in Vietnamese or English:
   - "Điều kiện xét tuyển cao học?"
   - "Học phí năm 2025?"
   - "Quy trình đăng ký đồ án tốt nghiệp?"

3. **View sources** — Click "📚 Xem nguồn tham khảo" to see where the answer came from

4. **Adjust settings** — Use sidebar to control:
   - Number of retrieved documents (1-10)
   - Clear chat history

## 📂 File Structure

```
Chatbot QCĐT/
├── App/
│   └── chatbot_app.py          ← Main Streamlit app
├── Script/Indexing/
│   ├── batch_embedding.py      ← Embed chunks to ChromaDB
│   └── query_test.py           ← Test queries
├── VectorStore/
│   └── chroma.sqlite3          ← ChromaDB database
├── Chunked Data/               ← Your chunked files
└── .env                        ← API configuration
```

## 🔧 Configuration

Edit these settings in `chatbot_app.py`:

| Setting | Location | Default |
|---------|----------|---------|
| Database path | Line 13 | `VectorStore/` |
| Collection name | Line 14 | `qcdt_all` |
| Embedding model | Line 15 | `gemini-embedding-001` |
| LLM model | Line 147 | `gemini-1.5-flash` |

## 🐛 Troubleshooting

### ❌ "GOOGLE_API_KEY not found"
- Create `.env` file in workspace root
- Add: `GOOGLE_API_KEY=your_key_here`
- Save and restart app

### ❌ "Collection not found"
- Run batch embedding first: `python Script/Indexing/batch_embedding.py`
- Verify `VectorStore/chroma.sqlite3` exists

### ❌ "Embedding dimension mismatch"
- Ensure database was created with `gemini-embedding-001` model
- Don't use old embeddings with Sentence Transformers

### ⚠️ Slow responses
- First response may be slow (model download)
- Subsequent responses are faster
- Google API rate limits apply

## 📊 Database Stats

Check how many documents are embedded:
```bash
python Script/Indexing/batch_embedding.py --dry-run
```

## 🎨 Customization

### Change system prompt
Edit lines 136-138 to change chatbot behavior:
```python
system_prompt = """Bạn là một trợ lý thông minh..."""
```

### Change LLM model
Line 147:
```python
model="gemini-1.5-flash",  # or gemini-1.5-pro, gemini-2.0-flash, etc.
```

### Change UI colors
Edit CSS in lines 47-64

## 📝 Example Conversations

**User**: Điều kiện xét tuyển cao học?
**Bot**: [Retrieves relevant documents about admission conditions and generates response]

**User**: Học phí năm 2025 bao nhiêu?
**Bot**: [Searches tuition information and provides pricing]

**User**: Quy trình đăng ký đồ án?
**Bot**: [Explains the thesis registration process with sources]

---

**Created with ❤️ for QCĐT students**
