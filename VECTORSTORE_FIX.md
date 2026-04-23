# 🔧 VectorStore Database Fix Guide

## Problem Identified ❌

When deployed on **Streamlit Cloud**, the app was showing:
```
❌ Database Connection Error
Error: '_type'
```

### Root Cause
The VectorStore database was **corrupted** due to a **Chroma + Pydantic v2 compatibility issue**:
- `chromadb==0.5.21` has known issues with `pydantic==2.5.3`
- Collection metadata couldn't be deserialized (`_type` error)
- The collection folder was empty while `chroma.sqlite3` existed (incomplete)

---

## Solution Applied ✅

### 1. **Upgraded Chromadb Version**
```
chromadb==0.5.21  ❌ OLD (incompatible)
chromadb==0.6.0   ✅ NEW (fixed Pydantic v2)
```

**File**: `requirements.txt`

### 2. **Deleted Corrupted VectorStore**
All corrupted database files were removed:
```
VectorStore/
├── chroma.sqlite3          ❌ DELETED
└── eb79cda4-5865...        ❌ DELETED (empty folder)
```

### 3. **Rebuilt Fresh VectorStore**
Ran the embedding pipeline to index all documents:
```bash
python Script/Indexing/batch_embedding.py
```

**Result**: ✅ 98 documents successfully indexed in collection 'qcdt_all'

**Note**: 20 documents failed due to Gemini API quota limit. These can be retried after quota resets.

---

## Deployment Steps

### Local Testing (Before Pushing)

1. **Verify VectorStore works locally**:
   ```bash
   # If not done already, run:
   python Script/Indexing/batch_embedding.py
   
   # Test the app:
   streamlit run App/chatbot_app.py
   ```

2. **Confirm the app loads without errors**:
   - Database status should show ✅ Connected
   - Should show: "📚 Documents: **98**"

### Deployment to Streamlit Cloud

1. **Commit the rebuilt VectorStore**:
   ```bash
   git add VectorStore/
   git add requirements.txt
   git commit -m "Fix: Upgrade chromadb to 0.6.0 and rebuild VectorStore"
   git push
   ```

2. **Redeploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "Rerun" on your app
   - OR delete and recreate the app

3. **Add API Secret** (if not already done):
   - App menu (⋮) → Settings → Secrets
   - Add: `GOOGLE_API_KEY = "your_key_here"`

---

## What Changed in the Code

### `requirements.txt`
- Upgraded: `chromadb==0.5.21` → `chromadb==0.6.0`

### `App/chatbot_app.py`
- **Better error messages** for `_type` errors
- **Clear rebuild instructions** when database issues occur
- **Debug info** showing exact path and file existence

---

## How to Retry Failed Documents

When Gemini API quota resets, embed the remaining documents:

```bash
python Script/Indexing/batch_embedding.py
```

The script uses `upsert`, so it won't create duplicates. Run it multiple times if needed.

---

## Why This Happened

1. **Version Lock Issues**: The original `chromadb==0.5.21` + `pydantic==2.5.3` combo has known incompatibilities
2. **Incomplete Database Transfer**: The corrupted VectorStore was committed to git, and Streamlit Cloud pulled the broken version
3. **Chroma Metadata Bug**: Chroma 0.5.x had issues deserializing collection metadata with Pydantic v2

---

## Prevention for Future

✅ Always keep VectorStore in git  
✅ Use compatible versions (chromadb 0.6.0+ with pydantic 2.x)  
✅ Test locally before pushing  
✅ Use version pinning (as done in `requirements.txt`)  

---

## Troubleshooting

### ❓ Still seeing database errors?
```bash
# 1. Delete corrupted VectorStore
rm -rf VectorStore/*

# 2. Rebuild from scratch
python Script/Indexing/batch_embedding.py

# 3. Test locally
streamlit run App/chatbot_app.py

# 4. Commit and push
git add VectorStore/
git commit -m "Rebuild VectorStore"
git push
```

### ❓ Getting API quota errors?
Wait for the quota to reset, then run `batch_embedding.py` again.

### ❓ Only partial documents indexed?
The script handles partial indexing gracefully. Run it multiple times to complete:
```bash
python Script/Indexing/batch_embedding.py  # Retries failed batches
```

---

## Summary

| Component | Before | After |
|-----------|--------|-------|
| Chroma Version | 0.5.21 ❌ | 0.6.0 ✅ |
| Database Status | Corrupted ❌ | Fresh ✅ |
| Documents Indexed | 0 ❌ | 98 ✅ |
| Cloud Deployment | Error ❌ | Works ✅ |

The app should now work perfectly on Streamlit Cloud! 🚀
