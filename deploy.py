#!/usr/bin/env python3
"""
Deployment script for the Repository Monitor Email Agent

This script helps users set up the agent quickly by:
1. Creating the .env file from env.example
2. Validating the configuration
3. Running a test cycle
"""

import os
import sys
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import langgraph
        import langchain
        import github
        import yaml
        import jinja2
        import schedule
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def setup_env_file():
    """Set up the .env file from env.example."""
    print("Setting up environment file...")
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env setup")
            return True
    
    if not os.path.exists('env.example'):
        print("❌ env.example file not found")
        return False
    
    try:
        shutil.copy('env.example', '.env')
        print("✅ Created .env file from env.example")
        print("📝 Please edit .env with your actual credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def validate_config():
    """Validate the configuration files."""
    print("Validating configuration...")
    
    # Check if config.yaml exists
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml not found")
        return False
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Try to load configuration
    try:
        from src import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("✅ Configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def run_test():
    """Run a test cycle."""
    print("Running test cycle...")
    
    try:
        from src import RepoMonitorWorkflow, ConfigManager
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Create workflow and state
        workflow = RepoMonitorWorkflow(config)
        initial_state = config_manager.create_initial_state(config)
        
        print(f"Testing with repository: {config['repository']['owner']}/{config['repository']['name']}")
        print(f"Issue threshold: {config['monitoring']['issue_threshold_days']} days")
        print(f"Email recipients: {', '.join(config['email']['recipients'])}")
        
        # Run workflow
        final_state = workflow.run(initial_state)
        
        print(f"✅ Test completed successfully")
        print(f"Emails that would be sent: {len(final_state.sent_notifications)}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main deployment function."""
    print("🚀 Repository Monitor Email Agent - Deployment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment file
    if not setup_env_file():
        sys.exit(1)
    
    # Validate configuration
    if not validate_config():
        print("\n📋 Next steps:")
        print("1. Edit .env with your GitHub token and email credentials")
        print("2. Update config.yaml with your repository details")
        print("3. Run this script again to test the configuration")
        sys.exit(1)
    
    # Run test
    if not run_test():
        print("\n🔧 Troubleshooting:")
        print("1. Check your GitHub token has the correct permissions")
        print("2. Verify your email credentials are correct")
        print("3. Ensure the repository exists and is accessible")
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Usage:")
    print("- Run once: python main.py --once")
    print("- Run continuously: python main.py")
    print("- Run tests: python test_agent.py")


if __name__ == "__main__":
    main() 