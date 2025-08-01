#!/usr/bin/env python3
"""
Test script for the Repository Monitor Email Agent

This script tests the agent functionality without sending actual emails.
"""

import os
import sys
from datetime import datetime, timedelta
from src import RepoMonitorState, Issue, PullRequest, GitHubClient, EmailService


def create_test_issues():
    """Create test issue data."""
    now = datetime.now()
    return [
        {
            "number": 1,
            "title": "Test Issue - Old",
            "state": "open",
            "created_at": now - timedelta(days=10),
            "updated_at": now - timedelta(days=2),
            "html_url": "https://github.com/test/repo/issues/1",
            "labels": [{"name": "bug", "color": "d73a4a"}],
            "assignees": [{"login": "testuser", "avatar_url": "https://example.com/avatar.png"}]
        },
        {
            "number": 2,
            "title": "Test Issue - Recent",
            "state": "open",
            "created_at": now - timedelta(days=3),
            "updated_at": now - timedelta(hours=1),
            "html_url": "https://github.com/test/repo/issues/2",
            "labels": [{"name": "enhancement", "color": "a2eeef"}],
            "assignees": []
        }
    ]


def create_test_prs():
    """Create test PR data."""
    now = datetime.now()
    return [
        {
            "number": 10,
            "title": "Test PR - Merged",
            "state": "closed",
            "merged_at": now - timedelta(hours=2),
            "closed_at": now - timedelta(hours=2),
            "html_url": "https://github.com/test/repo/pull/10",
            "labels": [{"name": "feature", "color": "a2eeef"}],
            "assignees": [{"login": "devuser", "avatar_url": "https://example.com/avatar2.png"}]
        },
        {
            "number": 11,
            "title": "Test PR - Closed",
            "state": "closed",
            "merged_at": None,
            "closed_at": now - timedelta(hours=1),
            "html_url": "https://github.com/test/repo/pull/11",
            "labels": [],
            "assignees": []
        }
    ]


def test_state_management():
    """Test the state management functionality."""
    print("Testing state management...")
    
    # Create test state
    state = RepoMonitorState(
        repo_owner="test-org",
        repo_name="test-repo",
        github_token="test-token",
        issue_threshold_days=7,
        email_recipients=["test@example.com"]
    )
    
    # Test issue age calculation
    test_issues = create_test_issues()
    for issue_data in test_issues:
        issue = Issue(**issue_data)
        print(f"Issue #{issue.number}: {issue.age_days} days old")
    
    # Test PR status
    test_prs = create_test_prs()
    for pr_data in test_prs:
        pr = PullRequest(**pr_data)
        status = "merged" if pr.is_merged else "closed" if pr.closed_at else "open"
        print(f"PR #{pr.number}: {status}")
    
    print("✅ State management tests passed\n")


def test_email_templates():
    """Test email template generation."""
    print("Testing email templates...")
    
    # Create test email service
    email_service = EmailService(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username="test@example.com",
        password="test-password"
    )
    
    # Test issue alert template
    test_issues = create_test_issues()
    issue_content = email_service._create_issue_alert_content(
        issues=test_issues,
        repo_name="test-repo",
        repo_url="https://github.com/test/repo",
        threshold_days=7
    )
    
    # Test PR notification template
    test_prs = create_test_prs()
    pr_content = email_service._create_pr_notification_content(
        prs=test_prs,
        repo_name="test-repo",
        repo_url="https://github.com/test/repo"
    )
    
    print(f"Issue alert template length: {len(issue_content)} characters")
    print(f"PR notification template length: {len(pr_content)} characters")
    print("✅ Email template tests passed\n")


def test_workflow_logic():
    """Test the workflow decision logic."""
    print("Testing workflow logic...")
    
    # Create test state
    state = RepoMonitorState(
        repo_owner="test-org",
        repo_name="test-repo",
        github_token="test-token",
        issue_threshold_days=7,
        email_recipients=["test@example.com"]
    )
    
    # Test with old issues (should trigger alert)
    test_issues = create_test_issues()
    alert_issues = []
    for issue_data in test_issues:
        issue = Issue(**issue_data)
        if issue.age_days >= state.issue_threshold_days:
            alert_issues.append(issue_data)
    
    print(f"Found {len(alert_issues)} issues exceeding {state.issue_threshold_days}-day threshold")
    
    # Test with recent PRs (should trigger notification)
    test_prs = create_test_prs()
    notification_prs = []
    for pr_data in test_prs:
        pr = PullRequest(**pr_data)
        if pr.is_merged or pr.closed_at:
            notification_prs.append(pr_data)
    
    print(f"Found {len(notification_prs)} PRs that were recently processed")
    print("✅ Workflow logic tests passed\n")


def main():
    """Run all tests."""
    print("🧪 Running Repository Monitor Email Agent Tests")
    print("=" * 50)
    
    try:
        test_state_management()
        test_email_templates()
        test_workflow_logic()
        
        print("🎉 All tests passed!")
        print("\nTo run the actual agent:")
        print("1. Set up your .env file with real credentials")
        print("2. Update config.yaml with your repository details")
        print("3. Run: python main.py --once")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 