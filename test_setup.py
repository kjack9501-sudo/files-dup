"""
Test script to verify the setup is correct.
Run this before starting the API server.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")
    try:
        from backend.config import GEMINI_API_KEY, GEMINI_MODEL
        print("[OK] Config module imported")
        
        from backend.rag_pipeline import RAGPipeline
        print("[OK] RAG Pipeline module imported")
        
        from backend.llm import LLMWrapper
        print("[OK] LLM Wrapper module imported")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_api_key():
    """Test if API key is configured."""
    print("\nTesting API key configuration...")
    try:
        from backend.config import GEMINI_API_KEY
        
        if not GEMINI_API_KEY:
            print("[ERROR] GEMINI_API_KEY is not set in .env file")
            return False
        elif GEMINI_API_KEY == "your_api_key_here":
            print("[WARNING] GEMINI_API_KEY is set to placeholder value")
            print("   Please update .env file with your actual Gemini API key")
            return False
        else:
            print(f"[OK] GEMINI_API_KEY is configured (length: {len(GEMINI_API_KEY)})")
            return True
    except Exception as e:
        print(f"[ERROR] Error checking API key: {e}")
        return False

def test_rag_pipeline():
    """Test if RAG pipeline can be initialized."""
    print("\nTesting RAG Pipeline initialization...")
    try:
        from backend.rag_pipeline import RAGPipeline
        
        pipeline = RAGPipeline(llm_provider=DEFAULT_LLM_PROVIDER)
        print("[OK] RAG Pipeline initialized successfully")
        return True
    except ValueError as e:
        if "API key" in str(e):
            print(f"[ERROR] {e}")
            print("   Please set GEMINI_API_KEY in .env file")
        else:
            print(f"[ERROR] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error initializing RAG Pipeline: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Document Knowledge Assistant - Setup Test")
    print("=" * 50)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test API key
    results.append(("API Key", test_api_key()))
    
    # Test RAG pipeline (only if API key is set)
    if results[1][1]:  # If API key test passed
        results.append(("RAG Pipeline", test_rag_pipeline()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("[SUCCESS] All tests passed! You can start the API server.")
        print("\nTo start the API:")
        print("  python backend\\api.py")
    else:
        print("[WARNING] Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Create .env file in Capstone_project/ folder")
        print("  2. Add: GEMINI_API_KEY=your_actual_api_key")
        print("  3. Get API key from: https://makersuite.google.com/app/apikey")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

