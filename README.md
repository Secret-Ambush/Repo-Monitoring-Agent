# Repository Monitor Email Agent

A LangGraph-based intelligent agent that monitors GitHub repositories and sends email notifications for:
- **Issues** that have been open beyond a configurable threshold
- **Pull Requests** that have been recently merged or closed

## Features

- 🔍 **Intelligent Monitoring**: Uses LangGraph workflows for sophisticated decision-making
- 📧 **Rich Email Notifications**: Beautiful HTML emails with issue/PR details
- ⚙️ **Configurable Thresholds**: Set custom time limits for issue alerts
- 🔄 **Scheduled Monitoring**: Runs automatically at configurable intervals
- 🛡️ **Error Handling**: Robust error handling and logging
- 🔐 **Secure Configuration**: Environment variable-based secrets management

## Architecture

The agent uses LangGraph to create a sophisticated workflow:

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│ Fetch Data  │───▶│ Analyze      │───▶│ Send Emails  │
│ (GitHub API)│    │ (Issues/PRs) │    │ (SMTP)       │
└─────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│ State       │    │ Conditional  │    │ Update       │
│ Management  │    │ Logic        │    │ Tracking     │
└─────────────┘    └──────────────┘    └──────────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Email-Agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. **Copy the example environment file:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   # GitHub Configuration
   GITHUB_TOKEN=ghp_your_github_token_here
   
   # Email Configuration (Gmail example)
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password_here
   ```

3. **Update `config.yaml` with your repository details:**
   ```yaml
   repository:
     owner: "your-org"
     name: "your-repo"
     token: "${GITHUB_TOKEN}"
   
   monitoring:
     issue_threshold_days: 7
     check_interval_hours: 24
     pr_lookback_hours: 24
   
   email:
     smtp_host: "smtp.gmail.com"
     smtp_port: 587
     username: "${EMAIL_USERNAME}"
     password: "${EMAIL_PASSWORD}"
     recipients:
       - "admin@company.com"
       - "team@company.com"
   ```

### 3. Running the Agent

**Run once (for testing):**
```bash
python main.py --once
```

**Run continuously (production):**
```bash
python main.py
```

## Configuration Options

### Repository Settings
- `owner`: GitHub organization or username
- `name`: Repository name
- `token`: GitHub Personal Access Token

### Monitoring Settings
- `issue_threshold_days`: Number of days after which to alert about open issues
- `check_interval_hours`: How often to run the monitoring cycle
- `pr_lookback_hours`: How far back to look for PR activity

### Email Settings
- `smtp_host`: SMTP server hostname
- `smtp_port`: SMTP server port
- `username`: Email username
- `password`: Email password (use app passwords for Gmail)
- `recipients`: List of email addresses to notify

## Email Templates

### Issue Alert Email
- **Subject**: `[ALERT] Issues Open Beyond X Days - {repo_name}`
- **Content**: List of issues with age, labels, assignees, and links
- **Styling**: Red header for urgency, organized issue cards

### PR Notification Email
- **Subject**: `[UPDATE] Pull Requests Merged - {repo_name}`
- **Content**: List of merged/closed PRs with status and details
- **Styling**: Green header for success, color-coded PR status

## LangGraph Workflow

The agent uses a sophisticated LangGraph workflow with the following nodes:

1. **`fetch_data`**: Retrieves current issues and PRs from GitHub
2. **`analyze_issues`**: Identifies issues exceeding the threshold
3. **`analyze_prs`**: Identifies recently processed PRs
4. **`send_issue_alert`**: Sends email alerts for old issues
5. **`send_pr_notification`**: Sends email notifications for PR activity
6. **`update_state`**: Updates tracking and resets workflow state

### Conditional Logic
- **Issue Alerts**: Only sent when issues exceed the configured threshold
- **PR Notifications**: Only sent when PRs were merged/closed recently
- **State Tracking**: Prevents duplicate notifications

## GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following scopes:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories)
3. Copy the token to your `.env` file

## Email Setup

### Gmail (Recommended)
1. Enable 2-factor authentication
2. Generate an App Password: Google Account → Security → App passwords
3. Use the app password in your `.env` file

### Other Providers
Update the SMTP settings in `config.yaml`:
```yaml
email:
  smtp_host: "smtp.your-provider.com"
  smtp_port: 587  # or 465 for SSL
  username: "your_email@domain.com"
  password: "your_password"
```

## Development

### Project Structure
```
Email-Agent/
├── src/
│   ├── __init__.py
│   ├── state.py              # LangGraph state management
│   ├── github_client.py      # GitHub API integration
│   ├── email_service.py      # Email sending service
│   ├── workflow.py           # LangGraph workflow definition
│   └── config_manager.py     # Configuration management
├── main.py                   # Application entry point
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Adding New Features

1. **New Email Types**: Add methods to `EmailService`
2. **New Monitoring Rules**: Add nodes to the LangGraph workflow
3. **New Data Sources**: Extend `GitHubClient` or create new clients
4. **Enhanced Logic**: Use LangGraph's conditional edges for complex decision-making

## Troubleshooting

### Common Issues

**GitHub API Rate Limits**
- The agent respects GitHub's rate limits
- Consider using a GitHub App token for higher limits

**Email Sending Failures**
- Verify SMTP settings and credentials
- Check firewall/proxy settings
- Use app passwords for Gmail

**Configuration Errors**
- Ensure all required environment variables are set
- Validate YAML syntax in `config.yaml`
- Check file permissions

### Debug Mode
Run with verbose logging:
```bash
python -u main.py --once 2>&1 | tee debug.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review GitHub issues
3. Create a new issue with detailed information 