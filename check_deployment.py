"""
Deployment Diagnostic Script
Checks if your project is properly configured for Streamlit Cloud deployment
"""

import sys
from pathlib import Path
import os

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_requirements():
    """Check if requirements.txt exists and has correct packages"""
    print_header("✓ Checking requirements.txt")
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt NOT FOUND!")
        return False
    
    print(f"✓ Found: {req_file}")
    
    required_packages = [
        "streamlit",
        "chromadb",
        "google-genai",
        "python-dotenv",
        "pydantic"
    ]
    
    content = req_file.read_text()
    missing = []
    
    for pkg in required_packages:
        if pkg.lower() in content.lower():
            print(f"  ✓ {pkg}")
        else:
            print(f"  ❌ {pkg} MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        return False
    
    return True

def check_vectorstore():
    """Check if VectorStore is properly set up"""
    print_header("✓ Checking VectorStore")
    
    db_path = Path("VectorStore")
    db_file = db_path / "chroma.sqlite3"
    
    if not db_path.exists():
        print(f"❌ VectorStore folder NOT FOUND at: {db_path}")
        print("\nYou need to:")
        print("  1. Run: python Script/Indexing/batch_embedding.py")
        print("  2. Commit: git add VectorStore/")
        print("  3. Push: git push")
        return False
    
    print(f"✓ VectorStore folder exists: {db_path}")
    
    if not db_file.exists():
        print(f"❌ Database file NOT FOUND: {db_file}")
        print("\nYou need to run embedding first:")
        print("  python Script/Indexing/batch_embedding.py")
        return False
    
    size_mb = db_file.stat().st_size / (1024 * 1024)
    print(f"✓ Database file exists: {db_file} ({size_mb:.2f} MB)")
    
    return True

def check_git_status():
    """Check if VectorStore is committed to git"""
    print_header("✓ Checking Git Status")
    
    try:
        import subprocess
        
        # Check if VectorStore is being tracked
        result = subprocess.run(
            ["git", "ls-files", "VectorStore/"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.stdout.strip():
            print(f"✓ VectorStore is tracked by git")
            
            # Show files
            files = result.stdout.strip().split("\n")
            for f in files[:5]:  # Show first 5
                print(f"    {f}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more files")
            
            return True
        else:
            print("❌ VectorStore is NOT tracked by git!")
            print("\nAdd it with:")
            print("  git add VectorStore/")
            print("  git commit -m 'Add embedded database'")
            print("  git push")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check git status: {e}")
        return False

def check_gitignore():
    """Check if .env is properly ignored"""
    print_header("✓ Checking .gitignore")
    
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        print("⚠️  .gitignore not found (might be okay)")
        return True
    
    content = gitignore.read_text()
    
    # Check for sensitive files
    sensitive = [
        (".env", "✓ .env is ignored"),
        ("secrets.toml", "✓ secrets.toml is ignored"),
        ("__pycache__", "✓ __pycache__ is ignored"),
    ]
    
    for pattern, msg in sensitive:
        if pattern in content:
            print(f"  {msg}")
        else:
            print(f"  ⚠️  {pattern} is NOT ignored")
    
    return ".env" in content

def check_streamlit_config():
    """Check if Streamlit configuration exists"""
    print_header("✓ Checking Streamlit Config")
    
    streamlit_dir = Path(".streamlit")
    config_file = streamlit_dir / "config.toml"
    
    if not streamlit_dir.exists():
        print(f"⚠️  .streamlit directory not found")
        return False
    
    if not config_file.exists():
        print(f"⚠️  .streamlit/config.toml not found")
        return False
    
    print(f"✓ Streamlit config found: {config_file}")
    return True

def check_app_file():
    """Check if chatbot app exists"""
    print_header("✓ Checking App File")
    
    app_file = Path("App/chatbot_app.py")
    if not app_file.exists():
        print(f"❌ App file NOT FOUND: {app_file}")
        return False
    
    print(f"✓ App file exists: {app_file}")
    
    # Check if it has the new path resolution
    content = app_file.read_text()
    if "get_db_path" in content:
        print(f"✓ App has new path resolution (good for Streamlit Cloud)")
    else:
        print(f"⚠️  App might not have optimal path resolution")
    
    return True

def main():
    print("\n" + "="*60)
    print("  STREAMLIT DEPLOYMENT DIAGNOSTIC")
    print("="*60)
    
    checks = [
        ("requirements.txt", check_requirements),
        ("VectorStore", check_vectorstore),
        ("Git Status", check_git_status),
        (".gitignore", check_gitignore),
        ("Streamlit Config", check_streamlit_config),
        ("App File", check_app_file),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ Everything looks good! Ready to deploy!")
        print("\nNext steps:")
        print("  1. Push to GitHub: git push")
        print("  2. Go to share.streamlit.io")
        print("  3. Create new app from your repo")
        print("  4. Set main file: App/chatbot_app.py")
        print("  5. Add GOOGLE_API_KEY in Secrets")
        return 0
    else:
        print(f"\n❌ {total - passed} issue(s) need to be fixed before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
