#!/usr/bin/env python3
"""
Simple dashboard for the Repository Monitor Email Agent

This script provides a basic dashboard to view:
- Current repository status
- Recent monitoring activity
- Configuration summary
"""

import os
import json
from datetime import datetime, timedelta
from src import ConfigManager, GitHubClient


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def get_repo_status(config):
    """Get current repository status."""
    print_header("Repository Status")
    
    try:
        github_client = GitHubClient(config['repository']['token'])
        repo_info = github_client.get_repo_info(
            config['repository']['owner'],
            config['repository']['name']
        )
        
        print(f"Repository: {repo_info['full_name']}")
        print(f"Description: {repo_info['description'] or 'No description'}")
        print(f"Open Issues: {repo_info['open_issues_count']}")
        print(f"Stars: {repo_info['stargazers_count']}")
        print(f"Forks: {repo_info['forks_count']}")
        print(f"URL: {repo_info['html_url']}")
        
        return repo_info
        
    except Exception as e:
        print(f"❌ Failed to fetch repository status: {e}")
        return None


def get_current_issues(config):
    """Get current open issues."""
    print_header("Current Open Issues")
    
    try:
        github_client = GitHubClient(config['repository']['token'])
        issues = github_client.get_open_issues(
            config['repository']['owner'],
            config['repository']['name']
        )
        
        if not issues:
            print("✅ No open issues found")
            return []
        
        threshold_days = config['monitoring']['issue_threshold_days']
        old_issues = []
        
        for issue in issues:
            age_days = issue.age_days
            status = "⚠️  OLD" if age_days >= threshold_days else "✅ Recent"
            print(f"#{issue.number}: {issue.title}")
            print(f"  Age: {age_days} days | Status: {status}")
            print(f"  Labels: {', '.join([label['name'] for label in issue.labels])}")
            print(f"  Assignees: {', '.join([assignee['login'] for assignee in issue.assignees])}")
            print()
            
            if age_days >= threshold_days:
                old_issues.append(issue)
        
        if old_issues:
            print(f"⚠️  {len(old_issues)} issues exceed the {threshold_days}-day threshold")
        
        return issues
        
    except Exception as e:
        print(f"❌ Failed to fetch issues: {e}")
        return []


def get_recent_prs(config):
    """Get recent pull request activity."""
    print_header("Recent Pull Request Activity")
    
    try:
        github_client = GitHubClient(config['repository']['token'])
        prs = github_client.get_recent_prs(
            config['repository']['owner'],
            config['repository']['name'],
            config['monitoring']['pr_lookback_hours']
        )
        
        if not prs:
            print("📭 No recent PR activity found")
            return []
        
        for pr in prs:
            status = "✅ Merged" if pr.is_merged else "❌ Closed" if pr.closed_at else "⏳ Open"
            print(f"#{pr.number}: {pr.title}")
            print(f"  Status: {status}")
            if pr.merged_at:
                print(f"  Merged: {pr.merged_at.strftime('%Y-%m-%d %H:%M')}")
            elif pr.closed_at:
                print(f"  Closed: {pr.closed_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Labels: {', '.join([label['name'] for label in pr.labels])}")
            print()
        
        return prs
        
    except Exception as e:
        print(f"❌ Failed to fetch PRs: {e}")
        return []


def show_config_summary(config):
    """Show configuration summary."""
    print_header("Configuration Summary")
    
    print(f"Repository: {config['repository']['owner']}/{config['repository']['name']}")
    print(f"Issue Threshold: {config['monitoring']['issue_threshold_days']} days")
    print(f"Check Interval: Every {config['monitoring']['check_interval_hours']} hours")
    print(f"PR Lookback: {config['monitoring']['pr_lookback_hours']} hours")
    print(f"Email Recipients: {', '.join(config['email']['recipients'])}")
    print(f"SMTP Server: {config['email']['smtp_host']}:{config['email']['smtp_port']}")


def show_next_actions(issues, threshold_days):
    """Show recommended next actions."""
    print_header("Recommended Actions")
    
    old_issues = [issue for issue in issues if issue.age_days >= threshold_days]
    
    if old_issues:
        print(f"🚨 {len(old_issues)} issues need attention:")
        for issue in old_issues:
            print(f"  - #{issue.number}: {issue.title} ({issue.age_days} days old)")
        print("\n💡 Consider:")
        print("  - Assigning issues to team members")
        print("  - Adding priority labels")
        print("  - Scheduling review meetings")
    else:
        print("✅ All issues are within acceptable age limits")
    
    print("\n📧 Email notifications will be sent for:")
    print(f"  - Issues open for {threshold_days}+ days")
    print("  - Recently merged/closed pull requests")


def main():
    """Main dashboard function."""
    print("📊 Repository Monitor Email Agent - Dashboard")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Show configuration summary
        show_config_summary(config)
        
        # Get repository status
        repo_info = get_repo_status(config)
        
        # Get current issues
        issues = get_current_issues(config)
        
        # Get recent PRs
        prs = get_recent_prs(config)
        
        # Show recommended actions
        show_next_actions(issues, config['monitoring']['issue_threshold_days'])
        
        print_header("Dashboard Complete")
        print("💡 Run 'python main.py --once' to execute a monitoring cycle")
        print("💡 Run 'python main.py' to start continuous monitoring")
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 