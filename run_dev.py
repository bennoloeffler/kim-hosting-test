#!/usr/bin/env python3
"""
Development server with auto-reload for FastAPI backend
"""

import uvicorn
import logging

# Configure logging to see reload messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point for development server"""
    # Run with auto-reload enabled
    uvicorn.run(
        "backend:app",  # app module and instance
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload on file changes
        reload_dirs=["./"],  # Watch current directory for changes
        reload_includes=["*.py", "*.html", ".env"],  # Watch these file types
        log_level="info"
    )

if __name__ == "__main__":
    main()