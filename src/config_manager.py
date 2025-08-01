import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration loading and environment variable substitution."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        load_dotenv()  # Load environment variables from .env file
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Substitute environment variables
        config = self._substitute_env_vars(config)
        
        # Validate configuration
        self._validate_config(config)
        
        return config
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in configuration values."""
        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]  # Remove ${ and }
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(f"Environment variable {env_var} not found")
            return value
        else:
            return obj
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration structure and required fields."""
        required_sections = ['repository', 'monitoring', 'email']
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate repository section
        repo_config = config['repository']
        required_repo_fields = ['owner', 'name', 'token']
        for field in required_repo_fields:
            if field not in repo_config:
                raise ValueError(f"Missing required repository field: {field}")
        
        # Validate monitoring section
        monitoring_config = config['monitoring']
        required_monitoring_fields = ['issue_threshold_days', 'check_interval_hours', 'pr_lookback_hours']
        for field in required_monitoring_fields:
            if field not in monitoring_config:
                raise ValueError(f"Missing required monitoring field: {field}")
        
        # Validate email section
        email_config = config['email']
        required_email_fields = ['smtp_host', 'smtp_port', 'username', 'password', 'recipients']
        for field in required_email_fields:
            if field not in email_config:
                raise ValueError(f"Missing required email field: {field}")
        
        # Validate data types
        if not isinstance(monitoring_config['issue_threshold_days'], int):
            raise ValueError("issue_threshold_days must be an integer")
        
        if not isinstance(monitoring_config['check_interval_hours'], int):
            raise ValueError("check_interval_hours must be an integer")
        
        if not isinstance(monitoring_config['pr_lookback_hours'], int):
            raise ValueError("pr_lookback_hours must be an integer")
        
        if not isinstance(email_config['smtp_port'], int):
            raise ValueError("smtp_port must be an integer")
        
        if not isinstance(email_config['recipients'], list):
            raise ValueError("recipients must be a list")
        
        if not email_config['recipients']:
            raise ValueError("At least one email recipient must be specified")
    
    def create_initial_state(self, config: Dict[str, Any]) -> 'RepoMonitorState':
        """Create initial state from configuration."""
        from .state import RepoMonitorState
        
        return RepoMonitorState(
            repo_owner=config['repository']['owner'],
            repo_name=config['repository']['name'],
            github_token=config['repository']['token'],
            issue_threshold_days=config['monitoring']['issue_threshold_days'],
            email_recipients=config['email']['recipients'],
            smtp_host=config['email']['smtp_host'],
            smtp_port=config['email']['smtp_port'],
            email_username=config['email']['username'],
            email_password=config['email']['password']
        ) 