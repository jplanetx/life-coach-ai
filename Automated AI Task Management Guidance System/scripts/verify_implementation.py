#!/usr/bin/env python
"""
Script to verify the implementation of a component.
"""
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, Callable
import importlib.util
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VerificationError(Exception):
    """Custom exception for verification failures."""
    pass

def load_component_verifier(component: str) -> Optional[Callable]:
    """
    Attempts to load a component-specific verifier from the tests directory.
    Returns None if no specific verifier is found.
    """
    try:
        # Convert component name to module name (e.g. "Authentication" -> "test_authentication")
        module_name = f"test_{component.lower()}"
        module_path = Path("tests") / f"{module_name}.py"
        
        if not module_path.exists():
            logger.debug(f"No specific verifier found for component: {component}")
            return None
            
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec or not spec.loader:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for a verify_component function
        if hasattr(module, 'verify_component'):
            verifier = getattr(module, 'verify_component')
            if inspect.isfunction(verifier):
                return verifier
                
        return None
        
    except Exception as e:
        logger.warning(f"Error loading component verifier: {e}")
        return None

def basic_verification(component: str) -> None:
    """
    Performs basic verification checks that apply to all components.
    Raises VerificationError if verification fails.
    """
    try:
        # Check for component source files
        component_dir = Path("src") / component.lower()
        if not component_dir.exists():
            raise VerificationError(f"Component directory not found: {component_dir}")
        
        # Check for required documentation
        docs_dir = Path("docs")
        if not docs_dir.exists():
            raise VerificationError("Documentation directory not found")
            
        # Add more basic verification steps here as needed
        logger.info("Basic verification checks passed")
        
    except Exception as e:
        raise VerificationError(f"Basic verification failed: {e}")

def verify_component(component: str) -> None:
    """
    Verify the implementation of a component.
    Raises VerificationError if verification fails.
    """
    logger.info(f"Verifying component: {component}")
    
    try:
        # Run basic verification first
        basic_verification(component)
        
        # Try to load and run component-specific verifier
        verifier = load_component_verifier(component)
        if verifier:
            logger.info(f"Running {component}-specific verification...")
            try:
                verifier()
                logger.info(f"{component}-specific verification passed")
            except Exception as e:
                raise VerificationError(f"{component}-specific verification failed: {e}")
        else:
            logger.info(f"No specific verification tests found for {component}")
            
        logger.info(f"{component} verification completed successfully")
        
    except VerificationError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}")
        raise VerificationError(f"Verification failed: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Verify the implementation of a component')
    parser.add_argument('component', help='Component to verify')
    
    args = parser.parse_args()
    
    try:
        verify_component(args.component)
        return 0
    except VerificationError:
        return 1
    except Exception as e:
        logger.critical(f"Critical error during verification: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
