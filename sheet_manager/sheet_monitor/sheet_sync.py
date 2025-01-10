import threading
import time
from typing import Optional, Callable
from queue import Queue
import logging

class SheetMonitor:
    def __init__(self, sheet_manager, check_interval: float = 1.0):
        """
        Initialize SheetMonitor with a sheet manager instance.
        
        Args:
            sheet_manager: Instance of SheetManager class
            check_interval: Time interval between checks in seconds
        """
        self.sheet_manager = sheet_manager
        self.check_interval = check_interval
        
        # Threading control
        self.monitor_thread = None
        self.is_running = threading.Event()
        self.pause_monitoring = threading.Event()
        self.monitor_paused = threading.Event()
        
        # Value tracking
        self.last_values = []
        self.value_changed = threading.Event()
        
        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.logger.warning("Monitoring thread is already running")
            return

        self.is_running.set()
        self.pause_monitoring.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("Started monitoring thread")

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.is_running.clear()
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Stopped monitoring thread")

    def pause(self):
        """Pause the monitoring."""
        self.pause_monitoring.set()
        self.monitor_paused.wait()  # Wait until monitoring is actually paused
        self.logger.info("Monitoring paused")

    def resume(self):
        """Resume the monitoring."""
        self.pause_monitoring.clear()
        self.monitor_paused.clear()
        self.logger.info("Monitoring resumed")

    def _monitor_loop(self):
        """Main monitoring loop that checks for changes in the sheet."""
        self.last_values = self.sheet_manager.get_all_values()
        
        while self.is_running.is_set():
            if self.pause_monitoring.is_set():
                self.monitor_paused.set()  # Signal that monitoring is paused
                self.pause_monitoring.wait()  # Wait for resume signal
                self.monitor_paused.clear()
                continue

            try:
                current_values = self.sheet_manager.get_all_values()
                
                # Check for new values
                if len(current_values) > len(self.last_values):
                    self.logger.info("Detected new value in sheet")
                    self.value_changed.set()
                
                self.last_values = current_values
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(self.check_interval)

class MainLoop:
    def __init__(self, sheet_manager, sheet_monitor, callback_function: Callable = None):
        """
        Initialize MainLoop with sheet manager and monitor instances.
        
        Args:
            sheet_manager: Instance of SheetManager class
            sheet_monitor: Instance of SheetMonitor class
            callback_function: Custom function to be called after processing new value
        """
        self.sheet_manager = sheet_manager
        self.monitor = sheet_monitor
        self.callback = callback_function
        self.is_running = threading.Event()
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start the main processing loop."""
        self.is_running.set()
        self.monitor.start_monitoring()
        self._main_loop()

    def stop(self):
        """Stop the main processing loop."""
        self.is_running.clear()
        self.monitor.stop_monitoring()

    def process_new_value(self):
        """Process new value by calling pop function and custom callback."""
        try:
            popped_value = self.sheet_manager.pop()
            if popped_value:
                self.logger.info(f"Processed value: {popped_value}")
                if self.callback:
                    self.callback(popped_value)  # 커스텀 함수 실행
            return popped_value
        except Exception as e:
            self.logger.error(f"Error processing value: {str(e)}")
            return None

    def _main_loop(self):
        """Main processing loop."""
        while self.is_running.is_set():
            # Wait for value change signal
            if self.monitor.value_changed.wait(timeout=1.0):
                # Pause monitoring
                self.monitor.pause()
                
                # Process the new value
                self.process_new_value()
                
                # Clear the value changed flag and resume monitoring
                self.monitor.value_changed.clear()
                self.monitor.resume()

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from sheet_manager.sheet_crud.sheet_crud import SheetManager
    def my_custom_function(value):
        print(f"어쩔껀데 어쩔껀데 뭐 어쩔껀데: {value}")
    # Initialize components
    sheet_manager = SheetManager()
    monitor = SheetMonitor(sheet_manager, check_interval=1.0)
    main_loop = MainLoop(sheet_manager, monitor, callback_function=my_custom_function)

    try:
        # Start the main loop
        main_loop.start()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Clean shutdown on Ctrl+C
        main_loop.stop()