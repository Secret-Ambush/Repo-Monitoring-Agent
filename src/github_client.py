from datetime import datetime, timedelta
from typing import List, Dict
from github import Github
from .state import Issue, PullRequest


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: str):
        self.github = Github(token)
    
    def get_open_issues(self, owner: str, repo_name: str) -> List[Issue]:
        """Fetch all open issues from a repository."""
        repo = self.github.get_repo(f"{owner}/{repo_name}")
        issues = []
        
        for issue in repo.get_issues(state='open'):
            issue_data = Issue(
                number=issue.number,
                title=issue.title,
                state=issue.state,
                created_at=issue.created_at,
                updated_at=issue.updated_at,
                html_url=issue.html_url,
                labels=[{"name": label.name, "color": label.color} for label in issue.labels],
                assignees=[{"login": assignee.login, "avatar_url": assignee.avatar_url} for assignee in issue.assignees]
            )
            issues.append(issue_data)
        
        return issues
    
    def get_recent_prs(self, owner: str, repo_name: str, lookback_hours: int = 24) -> List[PullRequest]:
        """Fetch recently merged or closed pull requests."""
        repo = self.github.get_repo(f"{owner}/{repo_name}")
        prs = []
        
        # Calculate the lookback time
        lookback_time = datetime.now() - timedelta(hours=lookback_hours)
        
        for pr in repo.get_pulls(state='all'):
            # Only include PRs that were merged or closed within the lookback period
            if pr.merged_at and pr.merged_at >= lookback_time:
                pr_data = PullRequest(
                    number=pr.number,
                    title=pr.title,
                    state=pr.state,
                    merged_at=pr.merged_at,
                    closed_at=pr.closed_at,
                    html_url=pr.html_url,
                    labels=[{"name": label.name, "color": label.color} for label in pr.labels],
                    assignees=[{"login": assignee.login, "avatar_url": assignee.avatar_url} for assignee in pr.assignees]
                )
                prs.append(pr_data)
            elif pr.closed_at and pr.closed_at >= lookback_time and not pr.merged_at:
                # Include closed but not merged PRs
                pr_data = PullRequest(
                    number=pr.number,
                    title=pr.title,
                    state=pr.state,
                    merged_at=pr.merged_at,
                    closed_at=pr.closed_at,
                    html_url=pr.html_url,
                    labels=[{"name": label.name, "color": label.color} for label in pr.labels],
                    assignees=[{"login": assignee.login, "avatar_url": assignee.avatar_url} for assignee in pr.assignees]
                )
                prs.append(pr_data)
        
        return prs
    
    def get_repo_info(self, owner: str, repo_name: str) -> Dict:
        """Get basic repository information."""
        repo = self.github.get_repo(f"{owner}/{repo_name}")
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "html_url": repo.html_url,
            "open_issues_count": repo.open_issues_count,
            "stargazers_count": repo.stargazers_count,
            "forks_count": repo.forks_count
        } 