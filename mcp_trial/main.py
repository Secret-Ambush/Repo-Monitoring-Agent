#!/usr/bin/env python3
"""
MCP-based Repository Monitor Email Agent

This version uses Model Context Protocol (MCP) for GitHub and email operations
instead of direct API calls.
"""

import asyncio
import sys
import os
import yaml
from datetime import datetime
from dotenv import load_dotenv
from src import MCPRepoMonitorWorkflow, MCPRepoMonitorState


def load_config() -> dict:
    """Load configuration from YAML file with environment variable substitution."""
    load_dotenv()
    
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Substitute environment variables
    def substitute_env_vars(obj):
        if isinstance(obj, dict):
            return {key: substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(f"Environment variable {env_var} not found")
            return value
        else:
            return obj
    
    return substitute_env_vars(config)


async def run_monitoring_cycle():
    """Run a single monitoring cycle using MCP."""
    try:
        print(f"\n{'='*60}")
        print(f"MCP Agent - Starting monitoring cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Load configuration
        config = load_config()
        
        # Create workflow and initial state
        workflow = MCPRepoMonitorWorkflow(config)
        initial_state = MCPRepoMonitorState(
            repo_owner=config['repository']['owner'],
            repo_name=config['repository']['name'],
            issue_threshold_days=config['monitoring']['issue_threshold_days'],
            email_recipients=config['email']['recipients']
        )
        
        # Run the workflow
        final_state = await workflow.run(initial_state)
        
        print(f"\nMCP monitoring cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Emails sent: {len(final_state.sent_notifications)}")
        
        # Cleanup
        await workflow.cleanup()
        
    except Exception as e:
        print(f"Error during MCP monitoring cycle: {e}")
        import traceback
        traceback.print_exc()


async def run_scheduled():
    """Run the MCP agent on a schedule."""
    config = load_config()
    interval_hours = config['monitoring']['check_interval_hours']
    
    print(f"Starting MCP Repository Monitor Email Agent")
    print(f"Repository: {config['repository']['owner']}/{config['repository']['name']}")
    print(f"Monitoring interval: Every {interval_hours} hours")
    print(f"Email recipients: {', '.join(config['email']['recipients'])}")
    print(f"Press Ctrl+C to stop\n")
    
    # Run initial cycle immediately
    await run_monitoring_cycle()
    
    # Keep running scheduled cycles
    while True:
        try:
            await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
            await run_monitoring_cycle()
        except KeyboardInterrupt:
            print("\nShutting down MCP Repository Monitor Email Agent...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying


async def run_once():
    """Run the MCP agent once."""
    print("Running MCP Repository Monitor Email Agent (single run)")
    await run_monitoring_cycle()


async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        await run_once()
    else:
        await run_scheduled()


if __name__ == "__main__":
    asyncio.run(main()) 