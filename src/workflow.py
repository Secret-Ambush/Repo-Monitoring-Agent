from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .state import RepoMonitorState, Issue, PullRequest
from .github_client import GitHubClient
from .email_service import EmailService
from datetime import datetime


class RepoMonitorWorkflow:
    """LangGraph workflow for repository monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.github_client = GitHubClient(config['repository']['token'])
        self.email_service = EmailService(
            config['email']['smtp_host'],
            config['email']['smtp_port'],
            config['email']['username'],
            config['email']['password']
        )
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(RepoMonitorState)
        
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
    
    def _fetch_data_node(self, state: RepoMonitorState) -> RepoMonitorState:
        """Fetch current repository data."""
        print(f"Fetching data for {state.repo_owner}/{state.repo_name}...")
        
        # Fetch open issues
        issues = self.github_client.get_open_issues(state.repo_owner, state.repo_name)
        state.open_issues = [issue.dict() for issue in issues]
        
        # Fetch recent PRs
        prs = self.github_client.get_recent_prs(
            state.repo_owner, 
            state.repo_name, 
            self.config['monitoring']['pr_lookback_hours']
        )
        state.recent_prs = [pr.dict() for pr in prs]
        
        print(f"Found {len(state.open_issues)} open issues and {len(state.recent_prs)} recent PRs")
        return state
    
    def _analyze_issues_node(self, state: RepoMonitorState) -> RepoMonitorState:
        """Analyze issues to determine if alerts should be sent."""
        print("Analyzing issues for alerts...")
        
        # Find issues that exceed the threshold
        alert_issues = []
        for issue_data in state.open_issues:
            issue = Issue(**issue_data)
            if issue.age_days >= state.issue_threshold_days:
                alert_issues.append(issue_data)
        
        state.alert_issues = alert_issues
        state.should_send_issue_alert = len(alert_issues) > 0
        
        print(f"Found {len(alert_issues)} issues that exceed the {state.issue_threshold_days}-day threshold")
        return state
    
    def _analyze_prs_node(self, state: RepoMonitorState) -> RepoMonitorState:
        """Analyze PRs to determine if notifications should be sent."""
        print("Analyzing PRs for notifications...")
        
        # Find PRs that were recently merged or closed
        notification_prs = []
        for pr_data in state.recent_prs:
            pr = PullRequest(**pr_data)
            if pr.is_merged or pr.closed_at:
                notification_prs.append(pr_data)
        
        state.notification_prs = notification_prs
        state.should_send_pr_notification = len(notification_prs) > 0
        
        print(f"Found {len(notification_prs)} PRs that were recently processed")
        return state
    
    def _should_send_issue_alert(self, state: RepoMonitorState) -> str:
        """Determine if issue alert should be sent."""
        return "send_alert" if state.should_send_issue_alert else "skip"
    
    def _should_send_pr_notification(self, state: RepoMonitorState) -> str:
        """Determine if PR notification should be sent."""
        return "send_notification" if state.should_send_pr_notification else "skip"
    
    def _send_issue_alert_node(self, state: RepoMonitorState) -> RepoMonitorState:
        """Send issue alert email."""
        print("Sending issue alert email...")
        
        repo_url = f"https://github.com/{state.repo_owner}/{state.repo_name}"
        
        success = self.email_service.send_issue_alert(
            recipients=state.email_recipients,
            issues=state.alert_issues,
            repo_name=state.repo_name,
            repo_url=repo_url,
            threshold_days=state.issue_threshold_days
        )
        
        if success:
            print("Issue alert email sent successfully")
            state.sent_notifications.append(f"issue_alert_{datetime.now().isoformat()}")
        else:
            print("Failed to send issue alert email")
        
        return state
    
    def _send_pr_notification_node(self, state: RepoMonitorState) -> RepoMonitorState:
        """Send PR notification email."""
        print("Sending PR notification email...")
        
        repo_url = f"https://github.com/{state.repo_owner}/{state.repo_name}"
        
        success = self.email_service.send_pr_notification(
            recipients=state.email_recipients,
            prs=state.notification_prs,
            repo_name=state.repo_name,
            repo_url=repo_url
        )
        
        if success:
            print("PR notification email sent successfully")
            state.sent_notifications.append(f"pr_notification_{datetime.now().isoformat()}")
        else:
            print("Failed to send PR notification email")
        
        return state
    
    def _update_state_node(self, state: RepoMonitorState) -> RepoMonitorState:
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
        
        print("Workflow completed successfully")
        return state
    
    def run(self, initial_state: RepoMonitorState) -> RepoMonitorState:
        """Run the workflow with the given initial state."""
        return self.workflow.invoke(initial_state) 