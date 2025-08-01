from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel


@dataclass
class RepoMonitorState:
    """State for the repository monitoring workflow."""
    
    # Repository configuration
    repo_owner: str
    repo_name: str
    github_token: str
    
    # Monitoring configuration
    issue_threshold_days: int = 7
    email_recipients: List[str] = field(default_factory=list)
    
    # Current repository state
    open_issues: List[Dict] = field(default_factory=list)
    recent_prs: List[Dict] = field(default_factory=list)
    
    # Email tracking
    last_email_sent: Optional[datetime] = None
    sent_notifications: List[str] = field(default_factory=list)
    
    # Email configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    
    # Workflow state
    should_send_issue_alert: bool = False
    should_send_pr_notification: bool = False
    alert_issues: List[Dict] = field(default_factory=list)
    notification_prs: List[Dict] = field(default_factory=list)


class Issue(BaseModel):
    """GitHub issue model."""
    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    html_url: str
    labels: List[Dict] = []
    assignees: List[Dict] = []
    
    @property
    def age_days(self) -> int:
        """Calculate how many days the issue has been open."""
        return (datetime.now() - self.created_at).days


class PullRequest(BaseModel):
    """GitHub pull request model."""
    number: int
    title: str
    state: str
    merged_at: Optional[datetime]
    closed_at: Optional[datetime]
    html_url: str
    labels: List[Dict] = []
    assignees: List[Dict] = []
    
    @property
    def is_merged(self) -> bool:
        """Check if the PR was merged."""
        return self.merged_at is not None 