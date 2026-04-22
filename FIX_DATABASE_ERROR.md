# 🔧 Fix: "Không thể kết nối database" Error

Your app is running but can't connect to the database on Streamlit Cloud. Here's how to fix it:

## 🚀 Quick Fix (3 Steps)

### **Step 1: Check if VectorStore is committed**
```bash
# Run diagnostic
python check_deployment.py
```

This will tell you exactly what's missing.

### **Step 2: If VectorStore is missing from git**
```bash
# Add it
git add VectorStore/

# Commit
git commit -m "Add embedded database"

# Push
git push
```

### **Step 3: Redeploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Find your app
- Click menu (⋮)
- Click "Reboot app"
- Or delete and redeploy with the new commit

---

## 🐛 Why This Happened

The issue: Your `VectorStore/chroma.sqlite3` database file was **not committed to GitHub**.

- ✅ Local: Works because VectorStore folder exists on your machine
- ❌ Cloud: Fails because Streamlit Cloud clones from GitHub, but VectorStore wasn't included

---

## ✅ What I Fixed in the App

1. **Better path resolution** — Works on both local and cloud
2. **Detailed error messages** — Shows exactly what's wrong and how to fix it
3. **File existence checks** — Verifies database before connecting

---

## 📋 Verification Checklist

Run this to verify everything:
```bash
python check_deployment.py
```

You should see:
```
✓ requirements.txt
✓ VectorStore
✓ Git Status (VectorStore is tracked)
✓ .gitignore
✓ Streamlit Config
✓ App File

Passed: 6/6
✅ Everything looks good!
```

---

## 🔗 If Still Not Working

**Check these URLs:**

1. **Is your git push successful?**
   ```bash
   git log -1  # Show latest commit
   ```

2. **Does Streamlit Cloud have the latest code?**
   - Go to your app on share.streamlit.io
   - Click menu (⋮) → Settings → Advanced settings
   - Check the commit hash matches your latest push

3. **Test locally first:**
   ```bash
   streamlit run App/chatbot_app.py
   ```
   If it works locally but not on Cloud, it's definitely a git/VectorStore issue.

---

## 🎯 The Exact Commands to Run

```bash
# 1. Make sure you're in the project root
cd "c:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT"

# 2. Check what's wrong
python check_deployment.py

# 3. Add and push VectorStore (if missing)
git add VectorStore/
git commit -m "Add embedded vector database"
git push origin main

# 4. Test locally (optional)
streamlit run App/chatbot_app.py

# 5. Go to Streamlit Cloud and reboot/redeploy
```

That's it! 🎉
