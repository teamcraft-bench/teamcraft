import subprocess
import signal
import sys
import shutil
import os
import tempfile
import threading
import traceback
import atexit
import logging
import time
import psutil

class MCServerManager:
    def __init__(self, port, world_save_path, log_path):
        self.port = port
        self.original_world_save_path = world_save_path
        self.temp_dir = None
        self.world_copy_path = None
        self.process = None
        self.output_thread = None
        self.is_running = False
        self.server_ready_event = threading.Event()
        self.server_error = None
        self.log_path = log_path
        self.name = "minecraft"
        
        
        # Set up logging
        start_time = time.strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(self.log_path, f"{start_time}.log")
        self.logger = logging.getLogger(self.name)
        handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def start(self):
        print("Initializing Minecraft server startup...")
        # Create a temporary directory to store the copied world
        self.temp_dir = tempfile.mkdtemp()
        self.world_copy_path = os.path.join(self.temp_dir, 'world')

        # Copy the world save folder to the temporary directory
        try:
            print(f"Copying world folder from '{self.original_world_save_path}' to '{self.world_copy_path}'")
            shutil.copytree(self.original_world_save_path, self.world_copy_path)
        except Exception as e:
            print(f"Error copying world save folder: {e}")
            self.cleanup()
            raise
        jar_path = os.path.abspath(os.path.dirname(__file__))
        # Command to run the server with the copied world and specified port
        command = [
            'java', '-Xmx4096M', '-Xms4096M', '-jar', 'server.jar', 'nogui',
            '--port', str(self.port), '--world', self.world_copy_path
        ]

        # Start the subprocess and capture the output
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, text=True, cwd=jar_path
        )
        
        self.is_running = True

        # Register cleanup to be called on script exit
        atexit.register(self.cleanup)

        # Start reading output in a separate thread
        self.output_thread = threading.Thread(target=self.read_output)
        # self.output_thread.daemon = True
        self.output_thread.start()
        # Wait until the server is fully ready
        print(f"Subprocess for Minecraft server started with PID {self.process.pid}, loading...")

        self.server_ready_event.wait()

        # Check if there was an error during startup
        if self.server_error:
            print(f"Server failed to start: {self.server_error}")
            self.stop()
            raise Exception("Server failed to start.")

    def read_output(self):
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.logger.info(f"SERVER OUTPUT: {line.strip()}")
                    # Check if the "Done" message is in the output
                    if 'Done' in line and 'For help, type "help"' in line:
                        print("Minecraft server is now running.")
                        self.server_ready_event.set()  # Signal that the server is ready
                    elif 'ERROR' in line or 'Exception' in line:
                        print("Server encountered an error during startup.")
                        self.server_error = line.strip()
                        self.server_ready_event.set()  # Signal that the server is not going to start
                else:
                    break
        except Exception as e:
            print(f"Error reading server output: {e}")
            traceback.print_exc()
            self.server_error = e
            self.server_ready_event.set()
            
    def send_command(self, command):
        if self.is_running and self.process.stdin:
            print(f"Sending command to Minecraft server: {command}")
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
        else:
            print("Server is not running or input stream is closed.")

    def stop(self):
        if self.is_running:
            print("Stopping the Minecraft server...")
            self.cleanup()

    def cleanup(self):
        print("Performing cleanup operations...")
        # Terminate the server process if it's still running
        if self.process and self.process.poll() is None:
            self.process.terminate()  # Send SIGTERM to the subprocess
            try:
                self.process.wait(timeout=10)  # Wait for process to clean up
            except subprocess.TimeoutExpired:
                print("Server did not terminate in time, killing it forcefully.")
                self.process.kill()  # Kill the process if it doesn't terminate in time
                print("Server process killed.")
        else:
            print("Server process is not running or already terminated.")

        # Remove the copied world folder
        if self.world_copy_path and os.path.exists(self.world_copy_path):
            shutil.rmtree(self.world_copy_path)

        # Clean up temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        self.is_running = False

    def wait_for_exit(self):
        if self.process:
            try:
                self.process.wait()
            except KeyboardInterrupt:
                print("KeyboardInterrupt received during wait.")
                self.stop()
            except Exception as e:
                print(f"Unexpected exception while waiting for server process: {e}")
                traceback.print_exc()
                self.stop()
