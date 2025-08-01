#!/usr/bin/env python3
"""
Repository Monitor Email Agent

A LangGraph-based agent that monitors GitHub repositories for:
- Issues that have been open beyond a configurable threshold
- Recently merged or closed pull requests

Sends email notifications when conditions are met.
"""

import sys
import time
import schedule
from datetime import datetime
from src import RepoMonitorWorkflow, ConfigManager


def run_monitoring_cycle():
    """Run a single monitoring cycle."""
    try:
        print(f"\n{'='*60}")
        print(f"Starting monitoring cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Create workflow and initial state
        workflow = RepoMonitorWorkflow(config)
        initial_state = config_manager.create_initial_state(config)
        
        # Run the workflow
        final_state = workflow.run(initial_state)
        
        print(f"\nMonitoring cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Emails sent: {len(final_state.sent_notifications)}")
        
    except Exception as e:
        print(f"Error during monitoring cycle: {e}")
        import traceback
        traceback.print_exc()


def run_scheduled():
    """Run the monitoring agent on a schedule."""
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    interval_hours = config['monitoring']['check_interval_hours']
    
    print(f"Starting Repository Monitor Email Agent")
    print(f"Repository: {config['repository']['owner']}/{config['repository']['name']}")
    print(f"Monitoring interval: Every {interval_hours} hours")
    print(f"Email recipients: {', '.join(config['email']['recipients'])}")
    print(f"Press Ctrl+C to stop\n")
    
    # Schedule the monitoring cycle
    schedule.every(interval_hours).hours.do(run_monitoring_cycle)
    
    # Run initial cycle immediately
    run_monitoring_cycle()
    
    # Keep running scheduled cycles
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nShutting down Repository Monitor Email Agent...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying


def run_once():
    """Run the monitoring agent once."""
    print("Running Repository Monitor Email Agent (single run)")
    run_monitoring_cycle()


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        run_scheduled()


if __name__ == "__main__":
    main() 