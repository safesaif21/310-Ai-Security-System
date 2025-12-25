"""Main entry point for the backend server"""
""" run with: python -m backend.main """

import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting Camera Server...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8040, reload=True)
