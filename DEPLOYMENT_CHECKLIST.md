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

## 🚀 Deployment Steps

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Go to share.streamlit.io**
   - Click "New app"
   - Select your repo
   - Main file: `App/chatbot_app.py`
   - Click "Deploy"

3. **Add Secret (After Deployment)**
   - App menu (⋮) → Settings → Secrets
   - Add: `GOOGLE_API_KEY = "your_key_here"`

4. **Test the App**
   - Try a sample query
   - Verify responses appear
   - Check source citations

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
