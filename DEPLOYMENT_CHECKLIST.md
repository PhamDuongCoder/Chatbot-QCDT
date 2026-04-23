# ✅ Deployment Checklist

Complete these steps before deploying to Streamlit Cloud:

## 📋 Pre-Deployment Checklist

- [ ] **requirements.txt exists** in repo root with all dependencies
- [ ] **App runs locally** without errors:
  ```bash
  streamlit run App/chatbot_app.py
  ```
- [ ] **All code is committed** to GitHub:
  ```bash
  git add .
  git commit -m "Prepare for deployment"
  git push
  ```
- [ ] **.env is NOT committed** (check .gitignore):
  ```bash
  git status  # Should NOT show .env
  ```
- [ ] **VectorStore exists** with embedded data
- [ ] **API key is secure** (not in code or git)

---

## � Recent Fixes Applied (April 2026)

**Issue**: Database connection error (`_type`) on Streamlit Cloud

**Root Cause**: 
- `chromadb==0.5.21` incompatible with `pydantic==2.5.3`
- VectorStore database was corrupted

**What Was Fixed**:
- ✅ Upgraded `chromadb` to `0.6.0` (Pydantic v2 compatible)
- ✅ Deleted and rebuilt VectorStore from scratch
- ✅ Re-indexed all documents (98/118 successfully)
- ✅ Improved error messages in app

**Status**: Ready to deploy ✅

---

## 🚀 Deployment Steps

1. **Verify Local Setup**
   ```bash
   # Test app locally
   streamlit run App/chatbot_app.py
   # Should show: ✅ Connected with 98 documents
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Fix: Upgrade chromadb 0.6.0 and rebuild VectorStore"
   git push origin main
   ```

3. **Redeploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Find your app
   - Click menu (⋮) → "Rerun app" 
   - OR delete and create new deployment

4. **Add Secret (If Not Already Done)**
   - App menu (⋮) → Settings → Secrets
   - Add: `GOOGLE_API_KEY = "your_key_here"`

5. **Test the App**
   - Verify database shows ✅ Connected
   - Try a sample query in Vietnamese
   - Check sources are displayed

---

## ⚠️ Important Notes

- **VectorStore is now in Git**: It's tracked and required for deployment
- **20 Documents Pending**: API quota limited - will retry after quota resets
- **No .env needed on Cloud**: Use Streamlit Secrets instead
- **Chromadb Version**: Now 0.6.0 (locked to prevent future issues)

---

## 🔒 Security Check

- [ ] No `.env` in git
- [ ] No API keys in Python code
- [ ] `.streamlit/secrets.toml` in `.gitignore`
- [ ] Secrets configured in Streamlit Cloud web UI
- [ ] `.gitignore` includes `__pycache__/` and `*.pyc`

---

## 📊 After Deployment

- [ ] App is live and running
- [ ] Check Streamlit Logs for errors
- [ ] Test with multiple queries
- [ ] Verify database connections work
- [ ] Share your app URL!

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | Check `requirements.txt` is in repo root |
| API key error | Add secret in Streamlit web interface |
| Slow first load | First request downloads models (normal) |
| Database error | Commit `VectorStore/` to git |
| Chrome warning | Update theme in `.streamlit/config.toml` |

---

**Status:** Ready for deployment! ✅
