import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from jinja2 import Template


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_issue_alert(self, recipients: List[str], issues: List[Dict], 
                        repo_name: str, repo_url: str, threshold_days: int) -> bool:
        """Send email alert for issues that have been open beyond the threshold."""
        
        subject = f"[ALERT] Issues Open Beyond {threshold_days} Days - {repo_name}"
        
        # Create email content
        content = self._create_issue_alert_content(issues, repo_name, repo_url, threshold_days)
        
        return self._send_email(recipients, subject, content)
    
    def send_pr_notification(self, recipients: List[str], prs: List[Dict], 
                           repo_name: str, repo_url: str) -> bool:
        """Send email notification for recently merged pull requests."""
        
        subject = f"[UPDATE] Pull Requests Merged - {repo_name}"
        
        # Create email content
        content = self._create_pr_notification_content(prs, repo_name, repo_url)
        
        return self._send_email(recipients, subject, content)
    
    def _create_issue_alert_content(self, issues: List[Dict], repo_name: str, 
                                  repo_url: str, threshold_days: int) -> str:
        """Create HTML content for issue alert email."""
        
        template = Template("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f44336; color: white; padding: 15px; border-radius: 5px; }
                .issue { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .issue-title { font-weight: bold; color: #333; }
                .issue-meta { color: #666; font-size: 14px; margin-top: 5px; }
                .issue-link { color: #0366d6; text-decoration: none; }
                .repo-link { margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 Issues Open Beyond {{ threshold_days }} Days</h2>
                <p>Repository: {{ repo_name }}</p>
            </div>
            
            <p>The following issues have been open for more than <strong>{{ threshold_days }} days</strong> and may require attention:</p>
            
            {% for issue in issues %}
            <div class="issue">
                <div class="issue-title">
                    <a href="{{ issue.html_url }}" class="issue-link">#{{ issue.number }} - {{ issue.title }}</a>
                </div>
                <div class="issue-meta">
                    <strong>Age:</strong> {{ issue.age_days }} days<br>
                    <strong>Created:</strong> {{ issue.created_at.strftime('%Y-%m-%d %H:%M') }}<br>
                    <strong>Last Updated:</strong> {{ issue.updated_at.strftime('%Y-%m-%d %H:%M') }}<br>
                    {% if issue.labels %}
                    <strong>Labels:</strong> 
                    {% for label in issue.labels %}
                    <span style="background-color: #{{ label.color }}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">{{ label.name }}</span>
                    {% endfor %}<br>
                    {% endif %}
                    {% if issue.assignees %}
                    <strong>Assignees:</strong> 
                    {% for assignee in issue.assignees %}
                    {{ assignee.login }}{% if not loop.last %}, {% endif %}
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            <div class="repo-link">
                <a href="{{ repo_url }}" class="issue-link">View Repository on GitHub</a>
            </div>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                This email was sent by the Repository Monitor Agent on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}
            </p>
        </body>
        </html>
        """)
        
        return template.render(
            issues=issues,
            repo_name=repo_name,
            repo_url=repo_url,
            threshold_days=threshold_days,
            datetime=datetime
        )
    
    def _create_pr_notification_content(self, prs: List[Dict], repo_name: str, repo_url: str) -> str:
        """Create HTML content for PR notification email."""
        
        template = Template("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #28a745; color: white; padding: 15px; border-radius: 5px; }
                .pr { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .pr-title { font-weight: bold; color: #333; }
                .pr-meta { color: #666; font-size: 14px; margin-top: 5px; }
                .pr-link { color: #0366d6; text-decoration: none; }
                .repo-link { margin-top: 20px; }
                .merged { border-left: 4px solid #28a745; }
                .closed { border-left: 4px solid #dc3545; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔄 Recent Pull Request Activity</h2>
                <p>Repository: {{ repo_name }}</p>
            </div>
            
            <p>The following pull requests were recently processed:</p>
            
            {% for pr in prs %}
            <div class="pr {% if pr.merged_at %}merged{% elif pr.closed_at %}closed{% endif %}">
                <div class="pr-title">
                    <a href="{{ pr.html_url }}" class="pr-link">#{{ pr.number }} - {{ pr.title }}</a>
                </div>
                <div class="pr-meta">
                    <strong>Status:</strong> 
                    {% if pr.merged_at %}
                    <span style="color: #28a745;">✅ Merged</span>
                    {% elif pr.closed_at %}
                    <span style="color: #dc3545;">❌ Closed</span>
                    {% else %}
                    <span style="color: #ffc107;">⏳ Open</span>
                    {% endif %}<br>
                    {% if pr.merged_at %}
                    <strong>Merged:</strong> {{ pr.merged_at.strftime('%Y-%m-%d %H:%M') }}<br>
                    {% elif pr.closed_at %}
                    <strong>Closed:</strong> {{ pr.closed_at.strftime('%Y-%m-%d %H:%M') }}<br>
                    {% endif %}
                    {% if pr.labels %}
                    <strong>Labels:</strong> 
                    {% for label in pr.labels %}
                    <span style="background-color: #{{ label.color }}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">{{ label.name }}</span>
                    {% endfor %}<br>
                    {% endif %}
                    {% if pr.assignees %}
                    <strong>Assignees:</strong> 
                    {% for assignee in pr.assignees %}
                    {{ assignee.login }}{% if not loop.last %}, {% endif %}
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            <div class="repo-link">
                <a href="{{ repo_url }}" class="pr-link">View Repository on GitHub</a>
            </div>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                This email was sent by the Repository Monitor Agent on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}
            </p>
        </body>
        </html>
        """)
        
        return template.render(
            prs=prs,
            repo_name=repo_name,
            repo_url=repo_url,
            datetime=datetime
        )
    
    def _send_email(self, recipients: List[str], subject: str, content: str) -> bool:
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = ', '.join(recipients)
            
            # Attach HTML content
            html_part = MIMEText(content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False 