# 📋 Streamlit Deployment Guide

## 🚀 Quick Deployment

### **For Streamlit Cloud (Easiest)**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit deployment files"
   git push
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**
   - Click "New app"
   - Select your GitHub repo
   - Choose branch: `main`
   - Set main file path: `App/chatbot_app.py`
   - Click "Deploy"

3. **Add API Key Secret**
   - After deployment, click app menu (⋮)
   - Click "Settings"
   - Click "Secrets"
   - Paste your API key:
     ```
     GOOGLE_API_KEY = "your_api_key_here"
     ```

4. **Upload VectorStore** (if using local SQLite)
   - Option A: Push VectorStore to GitHub (if not too large)
   - Option B: Use cloud storage (S3, GCS, etc.) - modify chatbot_app.py to download at startup

---

## 📦 Files I Created

### ✅ requirements.txt
Lists all Python dependencies needed. Streamlit automatically installs these.

**Includes:**
- `streamlit` - Web framework
- `chromadb` - Vector database
- `google-genai` - Google Gemini API
- `python-dotenv` - Load .env files
- `pydantic` - Data validation

### ✅ .streamlit/config.toml
Streamlit configuration for UI theme and logging.

### ✅ .streamlit/secrets.toml.example
Template for API key configuration (copy and rename to `secrets.toml` locally).

---

## ⚙️ Configuration

### **Local Development**
1. Create `.streamlit/secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml`:
   ```
   GOOGLE_API_KEY = "your_actual_key"
   ```

3. Run locally:
   ```bash
   streamlit run App/chatbot_app.py
   ```

### **Streamlit Cloud**
No `.env` needed! Configure in web interface:
- App menu → Settings → Secrets
- Paste your API key

---

## 🔑 API Key Security

✅ **What I Did:**
- API key is NEVER stored in git
- `.env` and `secrets.toml` are in `.gitignore`
- Code accepts both local (.env) and cloud (secrets) keys
- Better error messages for missing keys

✅ **What You Should Do:**
- Never commit API keys to GitHub
- Use Streamlit Secrets for cloud deployment
- Rotate keys periodically
- Don't share your `.env` file

---

## ❌ If Deployment Fails

### **Error: "ModuleNotFoundError: No module named chromadb"**
- ✅ I created `requirements.txt`
- ✅ Streamlit will auto-install from it
- If it still fails: Check if file is in repo root

### **Error: "GOOGLE_API_KEY not found"**
- Local: Create `.streamlit/secrets.toml` with your key
- Cloud: Add secret in Streamlit web interface
- Reload the app

### **Error: "VectorStore not found"**
- The database file must be in the repo
- Git-commit it: `git add VectorStore/chroma.sqlite3`
- Or use cloud storage integration

### **Error: "Collection not found"**
- Make sure you ran `batch_embedding.py` first
- Database path might be wrong in config
- Check `DB_PATH` in chatbot_app.py

---

## 📊 Checking Deployment

Visit: `https://share.streamlit.io` → Your Apps

You should see:
- ✅ App running (green dot)
- ✅ Chat interface loads
- ✅ Can send queries
- ✅ Responses appear with sources

---

## 🔗 Useful Links

- Streamlit Secrets: https://docs.streamlit.io/develop/concepts/connections/secrets-management
- Deploy Guide: https://docs.streamlit.io/deploy/streamlit-cloud
- ChromaDB Docs: https://docs.trychroma.com

---

## 🆘 Still Having Issues?

**Check these:**
1. ✅ `requirements.txt` exists in repo root
2. ✅ `App/chatbot_app.py` is the correct path
3. ✅ VectorStore folder is committed to git
4. ✅ API key is set in Secrets (not in code!)
5. ✅ No `.env` file in git (check `.gitignore`)

**Debug locally first:**
```bash
# Test if requirements install
pip install -r requirements.txt

# Test if app runs
streamlit run App/chatbot_app.py
```

If it works locally, it will work on Streamlit Cloud!
