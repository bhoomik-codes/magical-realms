import tkinter as tk
from tkinter import scrolledtext, font as tkfont
import sys
import threading
import queue
import os
import time
import subprocess
import locale
import codecs
import io

# Set UTF-8 as default encoding
if sys.platform == "win32":
    # Force UTF-8 encoding on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Set locale to user's default
    locale.setlocale(locale.LC_ALL, '')

# Force the environment to use UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

# Custom stdout redirection
class TextRedirector:
    def __init__(self, text_widget, queue, tag=""):
        self.text_widget = text_widget
        self.tag = tag
        self.queue = queue

    def write(self, string):
        self.queue.put((self.tag, string))

    def flush(self):
        pass

class RPGGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Adventure Game")
        self.root.geometry("800x600")
        self.root.minsize(640, 480)
        self.root.configure(bg="#2e2e2e")
        
        # Create custom fonts
        self.game_font = tkfont.Font(family="Consolas", size=11)
        self.input_font = tkfont.Font(family="Consolas", size=12)
        self.header_font = tkfont.Font(family="Consolas", size=16, weight="bold")
        
        # Create message queue for thread-safe updates
        self.msg_queue = queue.Queue()
        
        # Create the main frame
        self.main_frame = tk.Frame(root, bg="#2e2e2e")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        self.title_label = tk.Label(
            self.main_frame, 
            text="🎮 RPG ADVENTURE GAME 🎮", 
            font=self.header_font,
            fg="#ffffff",
            bg="#2e2e2e"
        )
        self.title_label.pack(pady=(0, 10))
        
        # Create game output text area
        self.output_frame = tk.Frame(self.main_frame, bg="#2e2e2e")
        self.output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.game_output = scrolledtext.ScrolledText(
            self.output_frame,
            wrap=tk.WORD,
            font=self.game_font,
            bg="#000000",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.game_output.pack(fill=tk.BOTH, expand=True)
        self.game_output.config(state=tk.DISABLED)
        
        # Create input frame
        self.input_frame = tk.Frame(self.main_frame, bg="#2e2e2e")
        self.input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Input prompt label
        self.prompt_label = tk.Label(
            self.input_frame, 
            text="Command:", 
            font=self.input_font,
            fg="#ffffff",
            bg="#2e2e2e"
        )
        self.prompt_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Text input
        self.input_entry = tk.Entry(
            self.input_frame,
            font=self.input_font,
            bg="#111111",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.focus_set()
        
        # Submit button
        self.submit_button = tk.Button(
            self.input_frame, 
            text="Submit", 
            command=self.on_submit,
            bg="#4a6cd4",
            fg="#ffffff",
            activebackground="#395ab9",
            activeforeground="#ffffff"
        )
        self.submit_button.pack(side=tk.LEFT, padx=(5, 0))

        # Status bar
        self.status_bar = tk.Label(
            root, 
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#333333",
            fg="#cccccc"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Game process variables
        self.game_process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.input_queue = queue.Queue()
        
        # Color and text styles
        self.game_output.tag_config("error", foreground="#ff6b6b")
        self.game_output.tag_config("info", foreground="#6bff6b")
        self.game_output.tag_config("warning", foreground="#ffff6b")
        self.game_output.tag_config("input", foreground="#6b9fff")
        
        # Start checking message queue
        self.check_msg_queue()
        
        # Start the game
        self.start_game()
        
    def start_game(self):
        """Start the RPG game as a subprocess"""
        self.update_status("Starting game...")
        
        # Set environment variables to force UTF-8 encoding
        env_copy = os.environ.copy()
        env_copy["PYTHONIOENCODING"] = "utf-8"
        
        # On Windows, try to set the console mode to handle UTF-8
        if sys.platform == "win32":
            self.append_text("Running on Windows - Using UTF-8 mode\n", "info")
            os.system("chcp 65001 > NUL")  # Set Windows console to UTF-8
        
        try:
            # Use sys.executable to ensure we use the same Python interpreter
            # Start the game in a new process with UTF-8 encoding
            self.game_process = subprocess.Popen(
                [sys.executable, "rpg_game.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',  # Replace any characters that can't be decoded
                env=env_copy
            )
            
            # Set up threads to read stdout and stderr
            self.stdout_thread = threading.Thread(
                target=self.read_output,
                args=(self.game_process.stdout, "normal")
            )
            self.stderr_thread = threading.Thread(
                target=self.read_output,
                args=(self.game_process.stderr, "error")
            )
            
            # Set up input writer thread
            self.input_thread = threading.Thread(
                target=self.write_input
            )
            
            # Start threads
            self.stdout_thread.daemon = True
            self.stderr_thread.daemon = True
            self.input_thread.daemon = True
            
            self.stdout_thread.start()
            self.stderr_thread.start()
            self.input_thread.start()
            
            # Monitor process state
            self.monitor_process()
            
            self.update_status("Game running")
        except Exception as e:
            self.append_text(f"Error starting game: {str(e)}\n", "error")
            self.update_status("Error starting game")
    
    def write_input(self):
        """Thread to write input to the game process"""
        while True:
            try:
                # Get input from the queue
                input_text = self.input_queue.get()
                
                # Check if process is still running and stdin is available
                if (self.game_process and self.game_process.poll() is None 
                    and self.game_process.stdin is not None):
                    try:
                        # Try to encode the text as UTF-8 and handle errors
                        safe_text = input_text.encode('utf-8', errors='replace').decode('utf-8')
                        
                        # Write to stdin and flush
                        self.game_process.stdin.write(safe_text + "\n")
                        self.game_process.stdin.flush()
                    except Exception as e:
                        self.msg_queue.put(("error", f"Input encoding error: {str(e)}\n"))
                        
                # Mark as done
                self.input_queue.task_done()
            except Exception as e:
                self.msg_queue.put(("error", f"Input error: {str(e)}\n"))
                time.sleep(0.1)
    
    def read_output(self, pipe, tag):
        """Thread to read output from the game process with encoding error handling"""
        for line in iter(pipe.readline, ''):
            try:
                # Try to clean the line of any problematic characters
                clean_line = line.encode('utf-8', errors='replace').decode('utf-8')
                self.msg_queue.put((tag, clean_line))
            except Exception as e:
                # If there's an encoding error, report it but continue
                self.msg_queue.put(("error", f"[Output encoding error: {str(e)}]\n"))
        
        pipe.close()
    
    def monitor_process(self):
        """Check if the game process is still running"""
        if self.game_process:
            returncode = self.game_process.poll()
            if returncode is not None:
                # Process has ended
                if returncode != 0:
                    self.msg_queue.put(("error", f"\nGame exited with error code {returncode}\n"))
                else:
                    self.msg_queue.put(("info", "\nGame has ended. You can close this window.\n"))
                self.update_status("Game ended")
                return
        
        # Check again after 500ms
        self.root.after(500, self.monitor_process)
    
    def check_msg_queue(self):
        """Check for messages in the queue and update the text widget"""
        try:
            while True:
                tag, text = self.msg_queue.get_nowait()
                self.append_text(text, tag)
                self.msg_queue.task_done()
        except queue.Empty:
            pass
        
        # Schedule to check again after 100ms
        self.root.after(100, self.check_msg_queue)
    
    def append_text(self, text, tag=None):
        """Append text to the output widget with error handling"""
        try:
            # First try to handle text directly
            self.game_output.config(state=tk.NORMAL)
            self.game_output.insert(tk.END, text, tag if tag else "")
            self.game_output.see(tk.END)
            self.game_output.config(state=tk.DISABLED)
        except UnicodeEncodeError:
            # If that fails, try to replace problematic characters
            try:
                safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
                self.game_output.config(state=tk.NORMAL)
                self.game_output.insert(tk.END, safe_text, tag if tag else "")
                self.game_output.see(tk.END)
                self.game_output.config(state=tk.DISABLED)
            except Exception as e:
                # If all else fails, show a generic message
                self.game_output.config(state=tk.NORMAL)
                self.game_output.insert(tk.END, f"[Text with encoding error: {str(e)}]", "error")
                self.game_output.see(tk.END)
                self.game_output.config(state=tk.DISABLED)
    
    def on_enter(self, event):
        """Handle Enter key in the input field"""
        self.on_submit()
        
    def on_submit(self):
        """Process user input"""
        text = self.input_entry.get().strip()
        if text:
            # Add user input to the display
            self.append_text(f"> {text}\n", "input")
            
            # Send to the game process
            self.input_queue.put(text)
            
            # Clear the input field
            self.input_entry.delete(0, tk.END)
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_bar.config(text=message)
    
    def on_closing(self):
        """Handle window closing"""
        if self.game_process and self.game_process.poll() is None:
            try:
                self.game_process.terminate()
            except:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = RPGGameGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()