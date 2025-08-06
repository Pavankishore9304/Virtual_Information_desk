import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Configuration ---
SCRIPT_TO_RUN = "app.py"
DIRECTORIES_TO_WATCH = ["./", "./agents", "./core"]

class ChangeHandler(FileSystemEventHandler):
    """A handler for file system events that restarts a subprocess."""
    def __init__(self):
        self.process = None
        self.start_process()

    def start_process(self):
        """Starts or restarts the Streamlit subprocess."""
        if self.process:
            print("🚨 Change detected. Terminating old process...")
            self.process.terminate()
            self.process.wait()
        
        print(f"🚀 Starting '{SCRIPT_TO_RUN}' in a new process...")
        # We use 'streamlit run' to start the app.
        self.process = subprocess.Popen(["streamlit", "run", SCRIPT_TO_RUN])

    def on_any_event(self, event):
        """
        This method is called when any file event occurs.
        We restart the process only for modifications to .py files.
        """
        if event.is_directory or not event.src_path.endswith(".py"):
            return
        
        # On modification, restart the process.
        if event.event_type == 'modified':
            self.start_process()

if __name__ == "__main__":
    print("🔥 Starting hot-reload development server...")
    event_handler = ChangeHandler()
    observer = Observer()

    for path in DIRECTORIES_TO_WATCH:
        observer.schedule(event_handler, path, recursive=True)
        print(f"  - Watching for changes in: {path}")

    observer.start()
    print("✅ Server is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            event_handler.process.wait()
    
    observer.join()
    print("🛑 Server stopped.")