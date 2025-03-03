#!/usr/bin/env python
"""
Script to start a new task by creating a task document and updating tracking.
"""
import sys
import os
import argparse
import logging
import uuid
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_task_document(workitem_id: str, component_name: str) -> bool:
    """Creates a new task document based on the task template."""
    task_doc_path = Path(f"docs/tasks/WORKITEM-{workitem_id}.md")
    
    try:
        if task_doc_path.exists():
            logger.warning(f"Task document already exists: {task_doc_path}")
            return True

        task_doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(task_doc_path, 'w') as f:
            f.write(f"# WORKITEM-{workitem_id}: Implement {component_name} Improvements\n\n")
            f.write("## Task Details\n\n")
            f.write(f"Component: {component_name}\n\n")
            f.write("## Implementation Notes\n\n")
            f.write("## Testing Steps\n\n")
            f.write("## Verification Results\n\n")
        
        logger.info(f"Created task document: {task_doc_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating task document: {e}")
        return False

def update_work_tracking(workitem_id: str, component_name: str) -> bool:
    """Updates the work tracking document with the new task."""
    work_tracking_path = Path("docs/work_tracking.md")
    
    try:
        if not work_tracking_path.exists():
            logger.error("Work tracking document not found")
            return False

        with open(work_tracking_path, 'r') as f:
            content = f.read()
        
        # Look for existing work item
        pattern = f"### WORKITEM-{workitem_id}: .*?\nStatus: Pending"
        replacement = f"### WORKITEM-{workitem_id}: Implement {component_name} Improvements\nStatus: In Progress"
        
        if pattern in content:
            content = content.replace(pattern, replacement)
            
            with open(work_tracking_path, 'w') as f:
                f.write(content)
            
            logger.info("Updated work tracking status to In Progress")
            return True
        else:
            # If work item doesn't exist, add it to Active Work Items section
            active_section = "## Active Work Items\n\n"
            if active_section in content:
                insert_pos = content.find(active_section) + len(active_section)
                new_item = f"### WORKITEM-{workitem_id}: Implement {component_name} Improvements\n"
                new_item += "Status: In Progress\n"
                new_item += f"Component: {component_name}\n"
                new_item += f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                content = content[:insert_pos] + new_item + content[insert_pos:]
                
                with open(work_tracking_path, 'w') as f:
                    f.write(content)
                
                logger.info("Added new work item to tracking document")
                return True
            else:
                logger.error("Could not find Active Work Items section in tracking document")
                return False
    except Exception as e:
        logger.error(f"Error updating work tracking: {e}")
        return False

def start_task(workitem_id: str, component_name: str) -> bool:
    """Start a new task by creating a task document and updating tracking."""
    # Create task document
    if not create_task_document(workitem_id, component_name):
        return False
    
    # Update work tracking status
    if not update_work_tracking(workitem_id, component_name):
        return False
    
    logger.info(f"Task WORKITEM-{workitem_id} started!")
    logger.info(f"You can now switch to the new branch with:")
    logger.info(f"git checkout -b workitem-{workitem_id}")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Start a new task and update tracking')
    parser.add_argument('workitem_id', help='Work item ID (number only)')
    parser.add_argument('component', help='Component that will be worked on')
    
    args = parser.parse_args()
    
    if not start_task(args.workitem_id, args.component):
        logger.error("Failed to start task. Please check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
