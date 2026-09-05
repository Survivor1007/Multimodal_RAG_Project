import os
import sys
import shutil

def setup_environment():
    """
    Automated environment setup script for reproducing the project setup.
    Creates .env from template, initializes data directories, and verifies dependencies.
    """
    print("🚀 Initializing Multimodal Hybrid RAG Environment Setup...")

    # 1. Verify Python Version
    python_ver = sys.version_info
    print(f"🐍 Python Version: {python_ver.major}.{python_ver.minor}.{python_ver.micro}")
    if python_ver.major < 3 or (python_ver.major == 3 and python_ver.minor < 10):
        print("⚠️ Warning: Python 3.10+ is recommended for this project.")

    # 2. Setup .env file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_example = os.path.join(project_root, ".env.example")
    env_target = os.path.join(project_root, ".env")
    backend_env = os.path.join(project_root, "backend", ".env")

    if not os.path.exists(env_target) and os.path.exists(env_example):
        shutil.copyfile(env_example, env_target)
        print(f"✅ Created root '.env' from template '{env_example}'")

    if not os.path.exists(backend_env) and os.path.exists(env_example):
        shutil.copyfile(env_example, backend_env)
        print(f"✅ Created backend '.env' from template '{env_example}'")

    # 3. Create necessary index & data directories
    data_dirs = [
        os.path.join(project_root, "backend", "data", "indexes"),
        os.path.join(project_root, "backend", "data", "uploads"),
        os.path.join(project_root, "backend", "logs"),
        os.path.join(project_root, "backend", "models"),
    ]

    for d in data_dirs:
        os.makedirs(d, exist_ok=True)
        print(f"📁 Verified directory: '{d}'")

    # 4. Check core package imports
    required_modules = ["fastapi", "sqlalchemy", "faiss", "sentence_transformers", "torch", "pydantic"]
    missing = []
    for mod in required_modules:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)

    if missing:
        print(f"❌ Missing Python dependencies: {missing}")
        print("👉 Run: pip install -r backend/requirements.txt")
    else:
        print("✅ All core ML & FastAPI dependencies are installed!")

    print("\n🎉 Setup verification complete! Run server with: uvicorn backend.app.main:app --reload")

if __name__ == "__main__":
    setup_environment()
