#!/usr/bin/env python3
"""
Beautiful Captions GUI - Simple Interface
Easy-to-use interface for creating shorts with beautiful captions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
from pathlib import Path
import tempfile
import re

class BeautifulCaptionsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Beautiful Captions Shorts Creator")
        self.root.geometry("800x700")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.is_running = False
        self.process = None
        
        # Create the interface
        self.create_interface()
        
    def create_interface(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="Beautiful Captions Shorts Creator",
            font=("Arial", 18, "bold"),
            fg='#ffffff',
            bg='#2b2b2b'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Create professional shorts with word-by-word highlighting",
            font=("Arial", 10),
            fg='#cccccc',
            bg='#2b2b2b'
        )
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Steam URL section
        url_frame = tk.LabelFrame(
            main_frame,
            text="🔗 Steam URL",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#3b3b3b',
            relief='groove',
            bd=2
        )
        url_frame.pack(fill='x', pady=5)
        
        self.url_text = tk.Text(
            url_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.url_text.pack(fill='x', padx=10, pady=10)
        
        # Description section
        desc_frame = tk.LabelFrame(
            main_frame,
            text="📝 Description/Script",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#3b3b3b',
            relief='groove',
            bd=2
        )
        desc_frame.pack(fill='x', pady=5)
        
        self.desc_text = tk.Text(
            desc_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.desc_text.pack(fill='x', padx=10, pady=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#2b2b2b')
        button_frame.pack(fill='x', pady=10)
        
        self.run_button = tk.Button(
            button_frame,
            text="🚀 Create Beautiful Captions Video",
            font=("Arial", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            command=self.run_creation,
            cursor='hand2'
        )
        self.run_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            font=("Arial", 12, "bold"),
            bg='#f44336',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            command=self.stop_creation,
            cursor='hand2',
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            font=("Arial", 10),
            bg='#9E9E9E',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=10,
            command=self.clear_all,
            cursor='hand2'
        )
        self.clear_button.pack(side='right', padx=5)
        
        # Progress section
        progress_frame = tk.LabelFrame(
            main_frame,
            text="Progress & Logs",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#3b3b3b',
            relief='groove',
            bd=2
        )
        progress_frame.pack(fill='both', expand=True, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(fill='x', padx=10, pady=5)
        
        # Status label
        self.status_label = tk.Label(
            progress_frame,
            text="Ready to create beautiful captions",
            font=("Arial", 10),
            fg='#cccccc',
            bg='#3b3b3b'
        )
        self.status_label.pack(pady=2)
        
        # Log area
        log_container = tk.Frame(progress_frame, bg='#3b3b3b')
        log_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(
            log_container,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg='#1e1e1e',
            fg='#00ff00',
            insertbackground='#ffffff',
            relief='flat',
            bd=0,
            state='disabled'
        )
        self.log_area.pack(fill='both', expand=True)
        
        # Configure progress bar style
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styles for the interface"""
        style = ttk.Style()
        style.configure(
            'Custom.Horizontal.TProgressbar',
            troughcolor='#404040',
            background='#4CAF50',
            lightcolor='#4CAF50',
            darkcolor='#4CAF50'
        )
    
    def extract_game_name(self, steam_url):
        """Extract game name from Steam URL"""
        try:
            # Try to extract from URL path
            match = re.search(r'/app/\d+/([^/?]+)', steam_url)
            if match:
                game_name = match.group(1).replace('_', ' ').replace('-', ' ')
                # Clean up and capitalize
                game_name = ' '.join(word.capitalize() for word in game_name.split())
                return game_name
        except:
            pass
        return "Unknown Game"
    
    def log_message(self, message, color='#00ff00'):
        """Add a message to the log area"""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log area"""
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def clear_all(self):
        """Clear all input fields and logs"""
        self.url_text.delete(1.0, tk.END)
        self.desc_text.delete(1.0, tk.END)
        self.clear_log()
        self.update_status("Ready to create beautiful captions")
    
    def validate_inputs(self):
        """Validate the inputs before running"""
        steam_url = self.url_text.get(1.0, tk.END).strip()
        description = self.desc_text.get(1.0, tk.END).strip()
        
        if not steam_url:
            messagebox.showerror("Error", "Please enter a Steam URL")
            return False
            
        if 'steampowered.com' not in steam_url:
            messagebox.showerror("Error", "Please enter a valid Steam URL")
            return False
            
        if not description:
            messagebox.showerror("Error", "Please enter a description/script")
            return False
            
        return True
    
    def run_creation(self):
        """Run the video creation process"""
        if not self.validate_inputs():
            return
            
        if self.is_running:
            messagebox.showwarning("Warning", "A video creation is already in progress")
            return
        
        # Get inputs
        steam_url = self.url_text.get(1.0, tk.END).strip()
        description = self.desc_text.get(1.0, tk.END).strip()
        game_name = self.extract_game_name(steam_url)
        
        # Update UI
        self.is_running = True
        self.run_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start(10)
        self.clear_log()
        
        # Start creation in a separate thread
        thread = threading.Thread(
            target=self.create_video_thread,
            args=(steam_url, description, game_name),
            daemon=True
        )
        thread.start()
    
    def create_video_thread(self, steam_url, description, game_name):
        """Thread function for video creation"""
        try:
            self.update_status("Starting video creation...")
            self.log_message("🎮 Beautiful Captions Shorts Creator")
            self.log_message("=" * 50)
            self.log_message(f"Game: {game_name}")
            self.log_message(f"Steam URL: {steam_url}")
            self.log_message(f"Script: {description[:50]}...")
            self.log_message("")
            
            # Create temporary script file
            temp_script_file = "temp_custom_script.txt"
            with open(temp_script_file, 'w', encoding='utf-8') as f:
                f.write(description)
            
            self.update_status("Running Python script...")
            self.log_message("🐍 Starting Python script execution...")
            
            # Run the Python script directly
            cmd = [
                sys.executable,
                "shortscreatorwithbeautifulcaptions.py",
                "--game", game_name,
                "--steam-url", steam_url,
                "--custom-script-file", temp_script_file,
                "--no-input"
            ]
            
            self.log_message(f"💻 Command: {' '.join(cmd)}")
            self.log_message("")
            
            # Execute the command
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=os.getcwd()
            )
            
            # Read output in real-time
            for line in iter(self.process.stdout.readline, ''):
                if not self.is_running:  # Check if stopped
                    break
                    
                line = line.strip()
                if line:
                    self.log_message(line)
                    
                    # Update status based on log content
                    if "Downloading assets" in line:
                        self.update_status("Downloading game assets...")
                    elif "Generating TTS audio" in line:
                        self.update_status("Generating narration audio...")
                    elif "Creating video" in line:
                        self.update_status("Creating video...")
                    elif "Adding beautiful captions" in line:
                        self.update_status("Adding beautiful captions...")
                    elif "SUCCESS!" in line:
                        self.update_status("Video created successfully!")
                    elif "❌" in line or "ERROR" in line:
                        self.update_status("Error occurred")
            
            # Wait for process to complete
            return_code = self.process.wait()
            
            # Clean up temporary file
            try:
                if os.path.exists(temp_script_file):
                    os.remove(temp_script_file)
            except:
                pass
            
            if return_code == 0 and self.is_running:
                self.log_message("")
                self.log_message("🎉 SUCCESS! Video creation completed!")
                self.log_message("📁 Check the 'output' folder for your video")
                self.update_status("Completed successfully!")
                messagebox.showinfo("Success", "Video created successfully!\nCheck the 'output' folder for your video.")
            elif return_code != 0 and self.is_running:
                self.log_message("")
                self.log_message(f"Process failed with return code: {return_code}")
                self.update_status("Failed - check logs for details")
                messagebox.showerror("Error", "Video creation failed. Check the logs for details.")
                
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            self.update_status("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Reset UI
            self.root.after(0, self.reset_ui)
    
    def stop_creation(self):
        """Stop the current video creation process"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_message("Process stopped by user")
        
        self.is_running = False
        self.update_status("Stopped")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset the UI to initial state"""
        self.is_running = False
        self.process = None
        self.run_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
        
        if self.status_label.cget('text') == "Stopped":
            pass  # Keep the stopped status
        elif "✅" not in self.status_label.cget('text') and "❌" not in self.status_label.cget('text'):
            self.update_status("Ready to create beautiful captions")

def main():
    """Main function to run the GUI"""
    # Check if we're in the right directory
    if not os.path.exists("shortscreatorwithbeautifulcaptions.py"):
        messagebox.showerror(
            "Error", 
            "shortscreatorwithbeautifulcaptions.py not found!\n"
            "Please run this GUI from the same directory as the script."
        )
        return
    
    root = tk.Tk()
    app = BeautifulCaptionsGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main() 