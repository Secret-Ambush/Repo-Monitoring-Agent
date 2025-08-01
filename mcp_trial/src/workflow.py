"""
MCP-based LangGraph workflow for repository monitoring
"""

import asyncio
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import MCPRepoMonitorState, MCPIssueModel, MCPPullRequestModel
from .mcp_client import MCPClient
from datetime import datetime


class MCPRepoMonitorWorkflow:
    """LangGraph workflow for MCP-based repository monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mcp_client = None
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    async def initialize(self):
        """Initialize MCP client."""
        self.mcp_client = MCPClient(self.config)
        await self.mcp_client.connect()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(MCPRepoMonitorState)
        
        # Add nodes
        workflow.add_node("fetch_data", self._fetch_data_node)
        workflow.add_node("analyze_issues", self._analyze_issues_node)
        workflow.add_node("analyze_prs", self._analyze_prs_node)
        workflow.add_node("send_issue_alert", self._send_issue_alert_node)
        workflow.add_node("send_pr_notification", self._send_pr_notification_node)
        workflow.add_node("update_state", self._update_state_node)
        
        # Define the workflow edges
        workflow.set_entry_point("fetch_data")
        
        # After fetching data, analyze both issues and PRs
        workflow.add_edge("fetch_data", "analyze_issues")
        workflow.add_edge("fetch_data", "analyze_prs")
        
        # Conditional edges based on analysis results
        workflow.add_conditional_edges(
            "analyze_issues",
            self._should_send_issue_alert,
            {
                "send_alert": "send_issue_alert",
                "skip": "update_state"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_prs",
            self._should_send_pr_notification,
            {
                "send_notification": "send_pr_notification",
                "skip": "update_state"
            }
        )
        
        # After sending emails, update state
        workflow.add_edge("send_issue_alert", "update_state")
        workflow.add_edge("send_pr_notification", "update_state")
        
        # End the workflow
        workflow.add_edge("update_state", END)
        
        return workflow.compile()
    
    async def _fetch_data_node(self, state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Fetch current repository data using MCP."""
        print(f"Fetching data for {state.repo_owner}/{state.repo_name} via MCP...")
        
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        
        # Fetch open issues via MCP
        issues = await self.mcp_client.get_open_issues(state.repo_owner, state.repo_name)
        state.open_issues = [issue.__dict__ for issue in issues]
        
        # Fetch recent PRs via MCP
        prs = await self.mcp_client.get_recent_prs(
            state.repo_owner, 
            state.repo_name, 
            self.config['monitoring']['pr_lookback_hours']
        )
        state.recent_prs = [pr.__dict__ for pr in prs]
        
        print(f"Found {len(state.open_issues)} open issues and {len(state.recent_prs)} recent PRs via MCP")
        return state
    
    def _analyze_issues_node(self, state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Analyze issues to determine if alerts should be sent."""
        print("Analyzing issues for alerts...")
        
        # Find issues that exceed the threshold
        alert_issues = []
        for issue_data in state.open_issues:
            issue = MCPIssueModel(**issue_data)
            if issue.age_days >= state.issue_threshold_days:
                alert_issues.append(issue_data)
        
        state.alert_issues = alert_issues
        state.should_send_issue_alert = len(alert_issues) > 0
        
        print(f"Found {len(alert_issues)} issues that exceed the {state.issue_threshold_days}-day threshold")
        return state
    
    def _analyze_prs_node(self, state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Analyze PRs to determine if notifications should be sent."""
        print("Analyzing PRs for notifications...")
        
        # Find PRs that were recently merged or closed
        notification_prs = []
        for pr_data in state.recent_prs:
            pr = MCPPullRequestModel(**pr_data)
            if pr.is_merged or pr.closed_at:
                notification_prs.append(pr_data)
        
        state.notification_prs = notification_prs
        state.should_send_pr_notification = len(notification_prs) > 0
        
        print(f"Found {len(notification_prs)} PRs that were recently processed")
        return state
    
    def _should_send_issue_alert(self, state: MCPRepoMonitorState) -> str:
        """Determine if issue alert should be sent."""
        return "send_alert" if state.should_send_issue_alert else "skip"
    
    def _should_send_pr_notification(self, state: MCPRepoMonitorState) -> str:
        """Determine if PR notification should be sent."""
        return "send_notification" if state.should_send_pr_notification else "skip"
    
    async def _send_issue_alert_node(self, state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Send issue alert email via MCP."""
        print("Sending issue alert email via MCP...")
        
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        
        # Create email content
        subject = f"[ALERT] Issues Open Beyond {state.issue_threshold_days} Days - {state.repo_name}"
        
        # Simple text body for MCP
        body_lines = [f"Repository: {state.repo_owner}/{state.repo_name}"]
        body_lines.append(f"Threshold: {state.issue_threshold_days} days")
        body_lines.append("")
        
        for issue_data in state.alert_issues:
            issue = MCPIssueModel(**issue_data)
            body_lines.append(f"#{issue.number}: {issue.title}")
            body_lines.append(f"  Age: {issue.age_days} days")
            body_lines.append(f"  URL: {issue.html_url}")
            body_lines.append("")
        
        body = "\n".join(body_lines)
        
        # Send email via MCP
        success = await self.mcp_client.send_email(
            recipients=state.email_recipients,
            subject=subject,
            body=body
        )
        
        if success:
            print("Issue alert email sent successfully via MCP")
            state.sent_notifications.append(f"issue_alert_{datetime.now().isoformat()}")
        else:
            print("Failed to send issue alert email via MCP")
        
        return state
    
    async def _send_pr_notification_node(self, state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Send PR notification email via MCP."""
        print("Sending PR notification email via MCP...")
        
        if not self.mcp_client:
            raise RuntimeError("MCP client not initialized")
        
        # Create email content
        subject = f"[UPDATE] Pull Requests Processed - {state.repo_name}"
        
        # Simple text body for MCP
        body_lines = [f"Repository: {state.repo_owner}/{state.repo_name}"]
        body_lines.append("")
        
        for pr_data in state.notification_prs:
            pr = MCPPullRequestModel(**pr_data)
            status = "merged" if pr.is_merged else "closed"
            body_lines.append(f"#{pr.number}: {pr.title}")
            body_lines.append(f"  Status: {status}")
            body_lines.append(f"  URL: {pr.html_url}")
            body_lines.append("")
        
        body = "\n".join(body_lines)
        
        # Send email via MCP
        success = await self.mcp_client.send_email(
            recipients=state.email_recipients,
            subject=subject,
            body=body
        )
        
        if success:
            print("PR notification email sent successfully via MCP")
            state.sent_notifications.append(f"pr_notification_{datetime.now().isoformat()}")
        else:
            print("Failed to send PR notification email via MCP")
        
        return state
    
    def _update_state_node(self, state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Update workflow state after processing."""
        print("Updating workflow state...")
        
        # Update last email sent time if any emails were sent
        if state.sent_notifications:
            state.last_email_sent = datetime.now()
        
        # Reset workflow flags
        state.should_send_issue_alert = False
        state.should_send_pr_notification = False
        state.alert_issues = []
        state.notification_prs = []
        
        print("MCP workflow completed successfully")
        return state
    
    async def run(self, initial_state: MCPRepoMonitorState) -> MCPRepoMonitorState:
        """Run the workflow with the given initial state."""
        # Initialize MCP client if not already done
        if not self.mcp_client:
            await self.initialize()
        
        # Set MCP client in state
        initial_state.mcp_client = self.mcp_client
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state
    
    async def cleanup(self):
        """Clean up MCP connections."""
        if self.mcp_client:
            await self.mcp_client.close() 