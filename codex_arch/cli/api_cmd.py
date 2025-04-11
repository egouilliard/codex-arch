"""
Command-line interface for the Codex-Arch REST API service.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional

from codex_arch.api.app import create_app

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Start the Codex-Arch REST API server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind the server to"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the server in debug mode"
    )
    
    parser.add_argument(
        "--env",
        choices=["dev", "test", "prod"],
        default="dev",
        help="Environment to run the server in"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Base directory for analysis output files"
    )
    
    parser.add_argument(
        "--cors-origins",
        type=str,
        help="CORS allowed origins (comma-separated)"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the Codex-Arch REST API server."""
    parsed_args = parse_args(args)
    
    try:
        # Set environment variables
        os.environ["API_ENV"] = parsed_args.env
        
        if parsed_args.output_dir:
            os.environ["OUTPUT_DIR"] = parsed_args.output_dir
            
        if parsed_args.cors_origins:
            os.environ["CORS_ORIGINS"] = parsed_args.cors_origins
        
        # Create and configure Flask app
        app = create_app()
        
        # Display startup info
        host = parsed_args.host
        port = parsed_args.port
        env = parsed_args.env
        debug = parsed_args.debug
        
        print(f"Starting Codex-Arch API server on http://{host}:{port}")
        print(f"Environment: {env.upper()}")
        print(f"Debug mode: {'ON' if debug else 'OFF'}")
        print(f"Press CTRL+C to quit")
        
        # Start the Flask server
        app.run(
            host=host,
            port=port,
            debug=debug
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\nServer shutdown requested. Exiting...")
        return 0
    except Exception as e:
        logger.error(f"Error running API server: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 