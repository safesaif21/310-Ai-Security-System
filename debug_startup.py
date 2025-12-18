
import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())

# Configure logging to stdout
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

from backend.app import startup_event, camera_manager, stop_events

async def test_startup():
    print("Testing startup_event...")
    try:
        await startup_event()
        print("Startup completed successfully.")
        
        print(f"Detected cameras: {camera_manager.cameras.keys()}")
        print(f"Stop events created: {stop_events.keys()}")
        
        # Cleanup
        for event in stop_events.values():
            event.set()
        camera_manager.release_all()
        
    except Exception as e:
        print(f"Startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_startup())
