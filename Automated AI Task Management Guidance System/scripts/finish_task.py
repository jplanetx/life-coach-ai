#!/usr/bin/env python
"""
Task completion script that verifies work and updates tracking.
"""
import sys
import os
import argparse
import logging
import subprocess
from pathlib import Path
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_implementation(component: str) -> tuple[bool, str]:
    """Run verification tests for the component."""
    try:
        logger.info(f"Verifying implementation of {component}...")
        result = subprocess.run(
            ["python", "scripts/verify_implementation.py", component], 
            capture_output=True, 
            text=True,
            check=True
        )
        return True, result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        logger.error(f"Verification failed: {e}")
        return False, e.stdout + e.stderr
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return False, str(e)

def update_task_document(workitem_id: str, verification_output: str) -> bool:
    """Update task document with verification results."""
    task_doc_path = Path(f"docs/tasks/WORKITEM-{workitem_id}.md")
    
    try:
        if not task_doc_path.exists():
            logger.error(f"Task document not found: {task_doc_path}")
            return False
            
        with open(task_doc_path, 'r') as f:
            content = f.read()
        
        # Add verification results
        if "## Verification Results" in content:
            content = re.sub(
                r"## Verification Results.*?(?=^#|\Z)", 
                f"## Verification Results\n\n```\n{verification_output}\n```\n\n", 
                content, 
                flags=re.DOTALL | re.MULTILINE
            )
        else:
            content += f"\n## Verification Results\n\n```\n{verification_output}\n```\n"
        
        with open(task_doc_path, 'w') as f:
            f.write(content)
        
        logger.info("Updated task document with verification results")
        return True
        
    except Exception as e:
        logger.error(f"Error updating task document: {e}")
        return False

def update_work_tracking(workitem_id: str, component_name: str) -> bool:
    """Update work tracking status to Complete."""
    work_tracking_path = Path("docs/work_tracking.md")
    
    try:
        if not work_tracking_path.exists():
            logger.error("Work tracking document not found")
            return False
            
        with open(work_tracking_path, 'r') as f:
            content = f.read()
        
        # Update status from "In Progress" to "Complete"
        pattern = rf"### WORKITEM-{workitem_id}: Implement {component_name} Improvements\nStatus: In Progress"
        replacement = f"### WORKITEM-{workitem_id}: Implement {component_name} Improvements\nStatus: Complete\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if pattern in content:
            content = content.replace(pattern, replacement)
            
            with open(work_tracking_path, 'w') as f:
                f.write(content)
            
            logger.info("Updated work tracking status to Complete")
            return True
        else:
            logger.error(f"Could not find WORKITEM-{workitem_id} with 'In Progress' status")
            return False
            
    except Exception as e:
        logger.error(f"Error updating work tracking: {e}")
        return False

def complete_task(workitem_id: str, component_name: str) -> bool:
    """Complete a task by running verification and updating tracking."""
    # Verify implementation
    success, verification_output = verify_implementation(component_name)
    if not success:
        logger.error("Verification failed")
        return False
    
    # Update task document with verification results
    if not update_task_document(workitem_id, verification_output):
        return False
    
    # Update work tracking status
    if not update_work_tracking(workitem_id, component_name):
        return False
    
    logger.info(f"Task WORKITEM-{workitem_id} completed successfully!")
    logger.info("You can now commit your changes with:")
    logger.info(f"git add . && git commit -m \"WORKITEM-{workitem_id}: Complete {component_name} implementation\"")
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Complete task and update tracking')
    parser.add_argument('workitem_id', help='Work item ID (number only)')
    parser.add_argument('component', help='Component that was worked on')
    
    args = parser.parse_args()
    
    if not complete_task(args.workitem_id, args.component):
        logger.error("Failed to complete task. Please check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
