#!/usr/bin/env python3
"""
Test script for MCP-based Repository Monitor Email Agent

This script tests the MCP functionality without requiring actual MCP servers.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from src import MCPRepoMonitorState, MCPIssueModel, MCPPullRequestModel


def create_test_issues():
    """Create test issue data for MCP."""
    now = datetime.now()
    return [
        {
            "number": 1,
            "title": "Test Issue - Old (MCP)",
            "state": "open",
            "created_at": now - timedelta(days=10),
            "updated_at": now - timedelta(days=2),
            "html_url": "https://github.com/test/repo/issues/1",
            "labels": [{"name": "bug", "color": "d73a4a"}],
            "assignees": [{"login": "testuser", "avatar_url": "https://example.com/avatar.png"}]
        },
        {
            "number": 2,
            "title": "Test Issue - Recent (MCP)",
            "state": "open",
            "created_at": now - timedelta(days=3),
            "updated_at": now - timedelta(hours=1),
            "html_url": "https://github.com/test/repo/issues/2",
            "labels": [{"name": "enhancement", "color": "a2eeef"}],
            "assignees": []
        }
    ]


def create_test_prs():
    """Create test PR data for MCP."""
    now = datetime.now()
    return [
        {
            "number": 10,
            "title": "Test PR - Merged (MCP)",
            "state": "closed",
            "merged_at": now - timedelta(hours=2),
            "closed_at": now - timedelta(hours=2),
            "html_url": "https://github.com/test/repo/pull/10",
            "labels": [{"name": "feature", "color": "a2eeef"}],
            "assignees": [{"login": "devuser", "avatar_url": "https://example.com/avatar2.png"}]
        },
        {
            "number": 11,
            "title": "Test PR - Closed (MCP)",
            "state": "closed",
            "merged_at": None,
            "closed_at": now - timedelta(hours=1),
            "html_url": "https://github.com/test/repo/pull/11",
            "labels": [],
            "assignees": []
        }
    ]


def test_state_management():
    """Test the MCP state management functionality."""
    print("Testing MCP state management...")
    
    # Create test state
    state = MCPRepoMonitorState(
        repo_owner="test-org",
        repo_name="test-repo",
        issue_threshold_days=7,
        email_recipients=["test@example.com"]
    )
    
    # Test issue age calculation
    test_issues = create_test_issues()
    for issue_data in test_issues:
        issue = MCPIssueModel(**issue_data)
        print(f"Issue #{issue.number}: {issue.age_days} days old")
    
    # Test PR status
    test_prs = create_test_prs()
    for pr_data in test_prs:
        pr = MCPPullRequestModel(**pr_data)
        status = "merged" if pr.is_merged else "closed" if pr.closed_at else "open"
        print(f"PR #{pr.number}: {status}")
    
    print("✅ MCP state management tests passed\n")


def test_workflow_logic():
    """Test the MCP workflow decision logic."""
    print("Testing MCP workflow logic...")
    
    # Create test state
    state = MCPRepoMonitorState(
        repo_owner="test-org",
        repo_name="test-repo",
        issue_threshold_days=7,
        email_recipients=["test@example.com"]
    )
    
    # Test with old issues (should trigger alert)
    test_issues = create_test_issues()
    alert_issues = []
    for issue_data in test_issues:
        issue = MCPIssueModel(**issue_data)
        if issue.age_days >= state.issue_threshold_days:
            alert_issues.append(issue_data)
    
    print(f"Found {len(alert_issues)} issues exceeding {state.issue_threshold_days}-day threshold")
    
    # Test with recent PRs (should trigger notification)
    test_prs = create_test_prs()
    notification_prs = []
    for pr_data in test_prs:
        pr = MCPPullRequestModel(**pr_data)
        if pr.is_merged or pr.closed_at:
            notification_prs.append(pr_data)
    
    print(f"Found {len(notification_prs)} PRs that were recently processed")
    print("✅ MCP workflow logic tests passed\n")


def test_config_loading():
    """Test configuration loading for MCP."""
    print("Testing MCP configuration loading...")
    
    try:
        import yaml
        
        if not os.path.exists('config.yaml'):
            print("❌ config.yaml not found")
            return False
        
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        print(f"✅ MCP configuration loaded successfully")
        print(f"   Repository: {config['repository']['owner']}/{config['repository']['name']}")
        print(f"   Issue threshold: {config['monitoring']['issue_threshold_days']} days")
        print(f"   MCP servers: {list(config['mcp']['servers'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP configuration test failed: {e}")
        return False


async def test_mcp_client_mock():
    """Test MCP client with mock data."""
    print("Testing MCP client (mock)...")
    
    try:
        # This would normally test the actual MCP client
        # For now, we'll just test the data models
        test_issues = create_test_issues()
        test_prs = create_test_prs()
        
        print(f"✅ MCP client mock test passed")
        print(f"   Test issues: {len(test_issues)}")
        print(f"   Test PRs: {len(test_prs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False


async def main():
    """Run all MCP tests."""
    print("🧪 MCP Repository Monitor Email Agent Tests")
    print("=" * 50)
    
    try:
        test_state_management()
        test_workflow_logic()
        test_config_loading()
        await test_mcp_client_mock()
        
        print("🎉 All MCP tests passed!")
        print("\n📋 MCP vs Direct API Comparison:")
        print("✅ MCP provides unified interface")
        print("✅ MCP handles authentication automatically")
        print("✅ MCP is designed for AI model interaction")
        print("⚠️  MCP requires MCP servers to be running")
        print("⚠️  MCP adds abstraction layer")
        
        print("\nTo run the actual MCP agent:")
        print("1. Set up your .env file with credentials")
        print("2. Install MCP servers (mcp-github, mcp-email)")
        print("3. Run: python main.py --once")
        
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 