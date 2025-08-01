"""
MCP Client for Repository Monitor Email Agent

This module provides a unified interface for GitHub and email operations
using the Model Context Protocol (MCP).
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class MCPIssue:
    """GitHub issue model for MCP."""
    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    html_url: str
    labels: List[Dict] = None
    assignees: List[Dict] = None
    
    @property
    def age_days(self) -> int:
        """Calculate how many days the issue has been open."""
        return (datetime.now() - self.created_at).days


@dataclass
class MCPPullRequest:
    """GitHub pull request model for MCP."""
    number: int
    title: str
    state: str
    merged_at: Optional[datetime]
    closed_at: Optional[datetime]
    html_url: str
    labels: List[Dict] = None
    assignees: List[Dict] = None
    
    @property
    def is_merged(self) -> bool:
        """Check if the PR was merged."""
        return self.merged_at is not None


class MCPClient:
    """Unified MCP client for GitHub and email operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.github_session: Optional[ClientSession] = None
        self.email_session: Optional[ClientSession] = None
        
    async def connect(self):
        """Connect to MCP servers."""
        await self._connect_github()
        await self._connect_email()
    
    async def _connect_github(self):
        """Connect to GitHub MCP server."""
        try:
            github_config = self.config['mcp']['servers']['github']
            params = StdioServerParameters(
                command=github_config['command'],
                args=github_config['args']
            )
            
            self.github_session = await stdio_client(params)
            print("✅ Connected to GitHub MCP server")
            
        except Exception as e:
            print(f"❌ Failed to connect to GitHub MCP server: {e}")
            raise
    
    async def _connect_email(self):
        """Connect to Email MCP server."""
        try:
            email_config = self.config['mcp']['servers']['email']
            params = StdioServerParameters(
                command=email_config['command'],
                args=email_config['args']
            )
            
            self.email_session = await stdio_client(params)
            print("✅ Connected to Email MCP server")
            
        except Exception as e:
            print(f"❌ Failed to connect to Email MCP server: {e}")
            raise
    
    async def get_open_issues(self, owner: str, repo: str) -> List[MCPIssue]:
        """Get open issues using MCP GitHub server."""
        if not self.github_session:
            raise RuntimeError("GitHub MCP session not connected")
        
        try:
            # MCP call to get issues
            result = await self.github_session.call_tool(
                "github_get_issues",
                {
                    "owner": owner,
                    "repo": repo,
                    "state": "open"
                }
            )
            
            issues = []
            for issue_data in result.content:
                issue = MCPIssue(
                    number=issue_data['number'],
                    title=issue_data['title'],
                    state=issue_data['state'],
                    created_at=datetime.fromisoformat(issue_data['created_at']),
                    updated_at=datetime.fromisoformat(issue_data['updated_at']),
                    html_url=issue_data['html_url'],
                    labels=issue_data.get('labels', []),
                    assignees=issue_data.get('assignees', [])
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            print(f"❌ Failed to get issues via MCP: {e}")
            return []
    
    async def get_recent_prs(self, owner: str, repo: str, lookback_hours: int = 24) -> List[MCPPullRequest]:
        """Get recent pull requests using MCP GitHub server."""
        if not self.github_session:
            raise RuntimeError("GitHub MCP session not connected")
        
        try:
            # MCP call to get pull requests
            result = await self.github_session.call_tool(
                "github_get_pull_requests",
                {
                    "owner": owner,
                    "repo": repo,
                    "state": "all",
                    "lookback_hours": lookback_hours
                }
            )
            
            prs = []
            for pr_data in result.content:
                pr = MCPPullRequest(
                    number=pr_data['number'],
                    title=pr_data['title'],
                    state=pr_data['state'],
                    merged_at=datetime.fromisoformat(pr_data['merged_at']) if pr_data.get('merged_at') else None,
                    closed_at=datetime.fromisoformat(pr_data['closed_at']) if pr_data.get('closed_at') else None,
                    html_url=pr_data['html_url'],
                    labels=pr_data.get('labels', []),
                    assignees=pr_data.get('assignees', [])
                )
                prs.append(pr)
            
            return prs
            
        except Exception as e:
            print(f"❌ Failed to get PRs via MCP: {e}")
            return []
    
    async def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information using MCP GitHub server."""
        if not self.github_session:
            raise RuntimeError("GitHub MCP session not connected")
        
        try:
            result = await self.github_session.call_tool(
                "github_get_repository",
                {
                    "owner": owner,
                    "repo": repo
                }
            )
            
            return result.content[0]
            
        except Exception as e:
            print(f"❌ Failed to get repo info via MCP: {e}")
            return {}
    
    async def send_email(self, to: List[str], subject: str, body: str, html_body: str = None) -> bool:
        """Send email using MCP email server."""
        if not self.email_session:
            raise RuntimeError("Email MCP session not connected")
        
        try:
            result = await self.email_session.call_tool(
                "email_send",
                {
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "html_body": html_body
                }
            )
            
            return result.content.get('success', False)
            
        except Exception as e:
            print(f"❌ Failed to send email via MCP: {e}")
            return False
    
    async def close(self):
        """Close MCP sessions."""
        if self.github_session:
            await self.github_session.aclose()
        if self.email_session:
            await self.email_session.aclose()
        print("✅ Closed MCP sessions")


# Convenience functions for synchronous usage
def create_mcp_client(config: Dict[str, Any]) -> MCPClient:
    """Create and connect MCP client."""
    client = MCPClient(config)
    return client


async def get_issues_mcp(client: MCPClient, owner: str, repo: str) -> List[MCPIssue]:
    """Get issues using MCP."""
    return await client.get_open_issues(owner, repo)


async def get_prs_mcp(client: MCPClient, owner: str, repo: str, lookback_hours: int = 24) -> List[MCPPullRequest]:
    """Get PRs using MCP."""
    return await client.get_recent_prs(owner, repo, lookback_hours)


async def send_email_mcp(client: MCPClient, to: List[str], subject: str, body: str, html_body: str = None) -> bool:
    """Send email using MCP."""
    return await client.send_email(to, subject, body, html_body) 