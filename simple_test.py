#!/usr/bin/env python3
"""
Simple test script that doesn't require LangGraph
Tests basic GitHub API and email functionality
"""

import os
import sys
from datetime import datetime, timedelta

def test_basic_imports():
    """Test if basic dependencies can be imported."""
    print("Testing basic imports...")
    
    try:
        import yaml
        print("✅ PyYAML imported successfully")
    except ImportError:
        print("❌ PyYAML not available")
        return False
    
    try:
        import github
        print("✅ PyGithub imported successfully")
    except ImportError:
        print("❌ PyGithub not available")
        return False
    
    try:
        import jinja2
        print("✅ Jinja2 imported successfully")
    except ImportError:
        print("❌ Jinja2 not available")
        return False
    
    try:
        import schedule
        print("✅ Schedule imported successfully")
    except ImportError:
        print("❌ Schedule not available")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError:
        print("❌ python-dotenv not available")
        return False
    
    return True

def test_github_api():
    """Test GitHub API access."""
    print("\nTesting GitHub API...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment")
        return False
    
    try:
        from github import Github
        g = Github(github_token)
        
        # Test repository access
        repo = g.get_repo("Secret-Ambush/testingIssues")
        print(f"✅ Successfully accessed repository: {repo.full_name}")
        print(f"   Open issues: {repo.open_issues_count}")
        print(f"   Description: {repo.description or 'No description'}")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

def test_email_templates():
    """Test email template generation."""
    print("\nTesting email templates...")
    
    try:
        from jinja2 import Template
        
        # Simple test template
        template = Template("Hello {{ name }}! Today is {{ date }}.")
        result = template.render(name="Test User", date=datetime.now().strftime("%Y-%m-%d"))
        
        print(f"✅ Template rendering successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Email template test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        import yaml
        
        if not os.path.exists('config.yaml'):
            print("❌ config.yaml not found")
            return False
        
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Repository: {config['repository']['owner']}/{config['repository']['name']}")
        print(f"   Issue threshold: {config['monitoring']['issue_threshold_days']} days")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🧪 Simple Dependency Test")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_config_loading,
        test_github_api,
        test_email_templates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! You can now install LangGraph if needed.")
        print("\nTo install LangGraph:")
        print("pip install langgraph langchain langchain-openai")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 