#!/usr/bin/env python3
"""
PRGAVI GUI - Modern interface using the new modular system
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import subprocess
import sys
import os
from pathlib import Path
import tempfile
import re
import requests
import json
import urllib.parse

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from lib import validate_steam_url, extract_game_name_from_url

class PRGAVIModernGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PRGAVI - YouTube Shorts Creator")
        self.root.geometry("900x750")
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.is_running = False
        self.process = None
        
        # Create the interface
        self.create_interface()
        
        # Configure styles
        self.setup_styles()
        
    def create_interface(self):
        # Title section
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(fill='x', padx=20, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="PRGAVI - YouTube Shorts Creator",
            font=("Segoe UI", 20, "bold"),
            fg='#ffffff',
            bg='#1e1e1e'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Create professional gaming shorts with AI narration and captions",
            font=("Segoe UI", 10),
            fg='#cccccc',
            bg='#1e1e1e'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel for inputs
        left_panel = tk.Frame(main_frame, bg='#1e1e1e')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Mode selection
        mode_frame = tk.LabelFrame(
            left_panel,
            text="🎬 Creation Mode",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        mode_frame.pack(fill='x', pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="beautiful_captions")
        
        modes = [
            ("beautiful_captions", "Beautiful Captions (Recommended)"),
            ("standard", "Standard Quality"),
            ("4x", "4X Strategy Games")
        ]
        
        for value, text in modes:
            radio = tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                font=("Segoe UI", 10),
                fg='#ffffff',
                bg='#2d2d2d',
                selectcolor='#404040',
                activebackground='#2d2d2d',
                activeforeground='#ffffff'
            )
            radio.pack(anchor='w', padx=10, pady=2)
        
        # Steam URL section
        url_frame = tk.LabelFrame(
            left_panel,
            text="🔗 Steam Game URL",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        url_frame.pack(fill='x', pady=(0, 10))
        
        self.url_text = tk.Text(
            url_frame,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.url_text.pack(fill='x', padx=10, pady=10)
        self.url_text.bind('<KeyRelease>', self.on_url_change)
        
        # Game name section
        name_frame = tk.LabelFrame(
            left_panel,
            text="🎮 Game Name",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        name_frame.pack(fill='x', pady=(0, 10))
        
        self.name_entry = tk.Entry(
            name_frame,
            font=("Segoe UI", 11),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.name_entry.pack(fill='x', padx=10, pady=10)
        
        # Script section
        script_frame = tk.LabelFrame(
            left_panel,
            text="📝 Script/Description",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        script_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.script_text = tk.Text(
            script_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.script_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Right panel for controls and logs
        right_panel = tk.Frame(main_frame, bg='#1e1e1e')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Control buttons
        button_frame = tk.Frame(right_panel, bg='#1e1e1e')
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.create_button = tk.Button(
            button_frame,
            text="🚀 Create Video",
            font=("Segoe UI", 12, "bold"),
            bg='#0d7377',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=12,
            command=self.create_video,
            cursor='hand2'
        )
        self.create_button.pack(fill='x', pady=(0, 5))
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            font=("Segoe UI", 10, "bold"),
            bg='#d63031',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.stop_creation,
            cursor='hand2',
            state='disabled'
        )
        self.stop_button.pack(fill='x', pady=(0, 5))
        
        # Additional options
        options_frame = tk.LabelFrame(
            right_panel,
            text="⚙️ Options",
            font=("Segoe UI", 10, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        options_frame.pack(fill='x', pady=(0, 10))
        
        # Video start time
        time_frame = tk.Frame(options_frame, bg='#2d2d2d')
        time_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            time_frame,
            text="Video Start Time:",
            font=("Segoe UI", 9),
            fg='#cccccc',
            bg='#2d2d2d'
        ).pack(side='left')
        
        self.start_time_var = tk.StringVar(value="10")
        start_time_entry = tk.Entry(
            time_frame,
            textvariable=self.start_time_var,
            width=5,
            font=("Segoe UI", 9),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        start_time_entry.pack(side='right')
        
        tk.Label(
            time_frame,
            text="seconds",
            font=("Segoe UI", 9),
            fg='#cccccc',
            bg='#2d2d2d'
        ).pack(side='right', padx=(5, 10))
        
        # No input option
        self.no_input_var = tk.BooleanVar()
        no_input_check = tk.Checkbutton(
            options_frame,
            text="Skip script input prompt",
            variable=self.no_input_var,
            font=("Segoe UI", 9),
            fg='#cccccc',
            bg='#2d2d2d',
            selectcolor='#404040',
            activebackground='#2d2d2d',
            activeforeground='#ffffff'
        )
        no_input_check.pack(anchor='w', padx=10, pady=2)
        
        # Utility buttons
        utils_frame = tk.Frame(right_panel, bg='#1e1e1e')
        utils_frame.pack(fill='x', pady=(0, 10))
        
        catalog_button = tk.Button(
            utils_frame,
            text="📊 Show Catalog",
            font=("Segoe UI", 9),
            bg='#6c5ce7',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.show_catalog,
            cursor='hand2'
        )
        catalog_button.pack(side='left', padx=(0, 5))
        
        clear_button = tk.Button(
            utils_frame,
            text="🗑 Clear",
            font=("Segoe UI", 9),
            bg='#636e72',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.clear_all,
            cursor='hand2'
        )
        clear_button.pack(side='right')
        
        load_script_button = tk.Button(
            utils_frame,
            text="📁 Load Script",
            font=("Segoe UI", 9),
            bg='#00b894',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.load_script_file,
            cursor='hand2'
        )
        load_script_button.pack(side='left', padx=5)
        
        generate_script_button = tk.Button(
            utils_frame,
            text="🤖 Generate Script",
            font=("Segoe UI", 9),
            bg='#fd79a8',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.open_script_generator,
            cursor='hand2'
        )
        generate_script_button.pack(side='left', padx=5)
        
        # Progress section
        progress_frame = tk.LabelFrame(
            right_panel,
            text="📊 Progress & Logs",
            font=("Segoe UI", 10, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        progress_frame.pack(fill='both', expand=True)
        
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
            text="Ready to create shorts",
            font=("Segoe UI", 10),
            fg='#00b894',
            bg='#2d2d2d'
        )
        self.status_label.pack(pady=2)
        
        # Log area
        log_container = tk.Frame(progress_frame, bg='#2d2d2d')
        log_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(
            log_container,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg='#1a1a1a',
            fg='#00ff88',
            insertbackground='#ffffff',
            relief='flat',
            bd=0,
            state='disabled'
        )
        self.log_area.pack(fill='both', expand=True)
    
    def setup_styles(self):
        """Setup custom styles for the interface"""
        style = ttk.Style()
        style.configure(
            'Custom.Horizontal.TProgressbar',
            troughcolor='#404040',
            background='#0d7377',
            lightcolor='#0d7377',
            darkcolor='#0d7377'
        )
    
    def on_url_change(self, event=None):
        """Handle Steam URL changes to auto-extract game name"""
        url = self.url_text.get(1.0, tk.END).strip()
        if url and validate_steam_url(url):
            game_name = extract_game_name_from_url(url)
            if game_name != "Unknown Game":
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, game_name)
    
    def load_script_file(self):
        """Load script from file"""
        file_path = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                self.script_text.delete(1.0, tk.END)
                self.script_text.insert(1.0, script_content)
                
                self.log_message(f"✅ Script loaded from: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load script file:\n{e}")
    
    def validate_inputs(self):
        """Validate user inputs"""
        steam_url = self.url_text.get(1.0, tk.END).strip()
        game_name = self.name_entry.get().strip()
        script = self.script_text.get(1.0, tk.END).strip()
        
        if not steam_url and not game_name:
            messagebox.showerror("Error", "Please provide either a Steam URL or game name")
            return False
        
        if steam_url and not validate_steam_url(steam_url):
            messagebox.showerror("Error", "Please enter a valid Steam URL")
            return False
        
        if not game_name:
            messagebox.showerror("Error", "Please enter a game name")
            return False
        
        return True
    
    def create_video(self):
        """Start video creation process"""
        if not self.validate_inputs():
            return
        
        if self.is_running:
            messagebox.showwarning("Warning", "Video creation is already in progress")
            return
        
        # Get inputs
        steam_url = self.url_text.get(1.0, tk.END).strip() or None
        game_name = self.name_entry.get().strip()
        script = self.script_text.get(1.0, tk.END).strip() or None
        mode = self.mode_var.get()
        video_start_time = int(self.start_time_var.get() or 10)
        no_input = self.no_input_var.get()
        
        # Update UI
        self.is_running = True
        self.create_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start(10)
        self.clear_log()
        self.update_status("Starting video creation...", "#00b894")
        
        # Start creation in separate thread
        thread = threading.Thread(
            target=self.create_video_thread,
            args=(steam_url, game_name, script, mode, video_start_time, no_input),
            daemon=True
        )
        thread.start()
    
    def create_video_thread(self, steam_url, game_name, script, mode, video_start_time, no_input):
        """Thread function for video creation"""
        try:
            self.log_message("🎮 PRGAVI - Unified Shorts Creator")
            self.log_message("=" * 50)
            self.log_message(f"Game: {game_name}")
            self.log_message(f"Mode: {mode}")
            if steam_url:
                self.log_message(f"Steam URL: {steam_url}")
            if script:
                self.log_message(f"Script: {script[:50]}...")
            self.log_message("")
            
            # Create command
            cmd = [
                sys.executable,
                "prgavi_unified.py",
                "--game", game_name,
                "--mode", mode,
                "--video-start-time", str(video_start_time)
            ]
            
            if steam_url:
                cmd.extend(["--steam-url", steam_url])
            
            if script:
                # Create temporary script file
                temp_script_file = "temp_gui_script.txt"
                with open(temp_script_file, 'w', encoding='utf-8') as f:
                    f.write(script)
                cmd.extend(["--script-file", temp_script_file])
            
            if no_input:
                cmd.append("--no-input")
            
            self.log_message(f"💻 Command: {' '.join(cmd)}")
            self.log_message("")
            
            # Execute command
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
                    self.update_status_from_log(line)
            
            # Wait for completion
            return_code = self.process.wait()
            
            # Clean up temporary script file
            if script and os.path.exists("temp_gui_script.txt"):
                try:
                    os.remove("temp_gui_script.txt")
                except:
                    pass
            
            # Handle completion
            if return_code == 0 and self.is_running:
                self.log_message("")
                self.log_message("🎉 SUCCESS! Video creation completed!")
                self.log_message("📁 Check the 'output' folder for your video")
                self.update_status("Completed successfully!", "#00b894")
                messagebox.showinfo("Success", "Video created successfully!\nCheck the 'output' folder for your video.")
            elif return_code != 0 and self.is_running:
                self.log_message("")
                self.log_message(f"❌ Process failed with return code: {return_code}")
                self.update_status("Failed - check logs", "#d63031")
                messagebox.showerror("Error", "Video creation failed. Check the logs for details.")
        
        except Exception as e:
            self.log_message(f"❌ ERROR: {str(e)}")
            self.update_status("Error occurred", "#d63031")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Reset UI
            self.root.after(0, self.reset_ui)
    
    def update_status_from_log(self, line):
        """Update status based on log content"""
        if "📥" in line or "Downloading" in line:
            self.update_status("Downloading assets...", "#e17055")
        elif "🔊" in line or "Generating TTS" in line:
            self.update_status("Generating narration...", "#fdcb6e")
        elif "🎬" in line or "Creating video" in line:
            self.update_status("Creating video...", "#74b9ff")
        elif "📝" in line or "Adding captions" in line:
            self.update_status("Adding captions...", "#a29bfe")
        elif "🎉" in line or "SUCCESS" in line:
            self.update_status("Video created successfully!", "#00b894")
        elif "❌" in line or "ERROR" in line or "Failed" in line:
            self.update_status("Error occurred", "#d63031")
    
    def stop_creation(self):
        """Stop the current video creation process"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_message("🛑 Process stopped by user")
        
        self.is_running = False
        self.update_status("Stopped", "#fdcb6e")
        self.reset_ui()
    
    def show_catalog(self):
        """Show catalog in separate window"""
        try:
            mode = self.mode_var.get()
            cmd = [sys.executable, "prgavi_unified.py", "--catalog", "--mode", mode]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Create catalog window
            catalog_window = tk.Toplevel(self.root)
            catalog_window.title(f"Game Catalog - {mode.upper()}")
            catalog_window.geometry("600x500")
            catalog_window.configure(bg='#1e1e1e')
            
            # Catalog text area
            catalog_text = scrolledtext.ScrolledText(
                catalog_window,
                wrap=tk.WORD,
                font=("Consolas", 10),
                bg='#1a1a1a',
                fg='#ffffff',
                relief='flat',
                bd=10
            )
            catalog_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Insert catalog content
            catalog_text.insert(tk.END, result.stdout)
            catalog_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load catalog: {e}")
    
    def clear_all(self):
        """Clear all input fields and logs"""
        self.url_text.delete(1.0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.script_text.delete(1.0, tk.END)
        self.clear_log()
        self.update_status("Ready to create shorts", "#00b894")
    
    def log_message(self, message):
        """Add message to log area"""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear log area"""
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
    
    def update_status(self, message, color="#cccccc"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.is_running = False
        self.process = None
        self.create_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
    
    def open_script_generator(self):
        """Open the script generator window"""
        steam_url = self.url_text.get(1.0, tk.END).strip()
        if not steam_url:
            messagebox.showwarning("Warning", "Please enter a Steam URL first to generate a script.")
            return
        
        if not validate_steam_url(steam_url):
            messagebox.showerror("Error", "Please enter a valid Steam URL.")
            return
        
        # Open script generator window
        generator_window = ScriptGeneratorWindow(self.root, steam_url, self.update_script_from_generator)
    
    def update_script_from_generator(self, generated_script):
        """Update the main window script text with generated script"""
        self.script_text.delete(1.0, tk.END)
        self.script_text.insert(1.0, generated_script)
        self.log_message("✅ Script generated and loaded successfully!")

class ScriptGeneratorWindow:
    def __init__(self, parent, steam_url, callback):
        self.parent = parent
        self.steam_url = steam_url
        self.callback = callback
        self.api_key = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("AI Script Generator")
        self.window.geometry("600x700")
        self.window.configure(bg='#1e1e1e')
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Load API key
        self.load_api_key()
        
        # Create interface
        self.create_interface()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = 600
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_api_key(self):
        """Load OpenRouter API key from file"""
        api_key_file = "openrouter_api_key.txt"
        if os.path.exists(api_key_file):
            try:
                with open(api_key_file, 'r', encoding='utf-8') as f:
                    self.api_key = f.read().strip()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load API key: {e}")
        else:
            messagebox.showwarning("API Key Missing", 
                                 f"Please create '{api_key_file}' file with your OpenRouter API key.")
    
    def create_interface(self):
        """Create the script generator interface"""
        # Title
        title_frame = tk.Frame(self.window, bg='#1e1e1e')
        title_frame.pack(fill='x', padx=20, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 AI Script Generator",
            font=("Segoe UI", 16, "bold"),
            fg='#ffffff',
            bg='#1e1e1e'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Generate engaging scripts using OpenRouter AI",
            font=("Segoe UI", 10),
            fg='#cccccc',
            bg='#1e1e1e'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Steam URL display
        url_frame = tk.LabelFrame(
            self.window,
            text="🔗 Steam Game URL",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        url_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        url_label = tk.Label(
            url_frame,
            text=self.steam_url,
            font=("Segoe UI", 9),
            fg='#74b9ff',
            bg='#2d2d2d',
            wraplength=500
        )
        url_label.pack(padx=10, pady=5)
        
        # Tone selection
        tone_frame = tk.LabelFrame(
            self.window,
            text="🎭 Script Tone",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        tone_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.tone_var = tk.StringVar(value="excited")
        
        tones = [
            ("excited", "🔥 Excited & Energetic"),
            ("critical", "🔍 Critical & Analytical"),
            ("questioning", "🤔 Questioning & Curious"),
            ("balanced", "⚖️ Balanced & Informative"),
            ("dramatic", "🎬 Dramatic & Cinematic")
        ]
        
        tone_grid = tk.Frame(tone_frame, bg='#2d2d2d')
        tone_grid.pack(padx=10, pady=5)
        
        for i, (value, text) in enumerate(tones):
            radio = tk.Radiobutton(
                tone_grid,
                text=text,
                variable=self.tone_var,
                value=value,
                font=("Segoe UI", 9),
                fg='#ffffff',
                bg='#2d2d2d',
                selectcolor='#404040',
                activebackground='#2d2d2d',
                activeforeground='#ffffff'
            )
            radio.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
        
        # System prompt
        prompt_frame = tk.LabelFrame(
            self.window,
            text="📝 System Prompt (Optional)",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        prompt_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.system_prompt_text = tk.Text(
            prompt_frame,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.system_prompt_text.pack(fill='x', padx=10, pady=10)
        
        # Default system prompt
        default_prompt = "Write ONLY a 30-second YouTube Shorts script about this game. Return just the script text with no explanations, comments, or additional text."
        self.system_prompt_text.insert(1.0, default_prompt)
        
        # Generation controls
        controls_frame = tk.Frame(self.window, bg='#1e1e1e')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        self.generate_button = tk.Button(
            controls_frame,
            text="✨ Generate Script",
            font=("Segoe UI", 12, "bold"),
            bg='#fd79a8',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=12,
            command=self.generate_script,
            cursor='hand2'
        )
        self.generate_button.pack(side='left')
        
        self.close_button = tk.Button(
            controls_frame,
            text="❌ Close",
            font=("Segoe UI", 10),
            bg='#636e72',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.window.destroy,
            cursor='hand2'
        )
        self.close_button.pack(side='right')
        
        # Generated script area
        script_frame = tk.LabelFrame(
            self.window,
            text="📜 Generated Script",
            font=("Segoe UI", 11, "bold"),
            fg='#ffffff',
            bg='#2d2d2d',
            relief='groove',
            bd=2
        )
        script_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        self.generated_script_text = scrolledtext.ScrolledText(
            script_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg='#404040',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='flat',
            bd=5
        )
        self.generated_script_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Use script button
        use_frame = tk.Frame(self.window, bg='#1e1e1e')
        use_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.use_script_button = tk.Button(
            use_frame,
            text="✅ Use This Script",
            font=("Segoe UI", 11, "bold"),
            bg='#00b894',
            fg='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            command=self.use_generated_script,
            cursor='hand2',
            state='disabled'
        )
        self.use_script_button.pack()
    
    def generate_script(self):
        """Generate script using OpenRouter API"""
        if not self.api_key:
            messagebox.showerror("Error", "OpenRouter API key not found. Please create 'openrouter_api_key.txt' file.")
            return
        
        # Disable generate button
        self.generate_button.config(state='disabled', text="🔄 Generating...")
        self.generated_script_text.delete(1.0, tk.END)
        self.generated_script_text.insert(1.0, "Generating script, please wait...")
        self.use_script_button.config(state='disabled')
        
        # Start generation in thread
        thread = threading.Thread(target=self.generate_script_thread, daemon=True)
        thread.start()
    
    def generate_script_thread(self):
        """Thread function for script generation"""
        try:
            # Get user inputs
            tone = self.tone_var.get()
            system_prompt = self.system_prompt_text.get(1.0, tk.END).strip()
            
            # Fetch Steam page info
            self.window.after(0, lambda: self.generated_script_text.delete(1.0, tk.END))
            self.window.after(0, lambda: self.generated_script_text.insert(1.0, "Fetching game information from Steam..."))
            
            game_info = self.fetch_steam_info()
            
            # Create tone-specific instructions
            tone_instructions = {
                "excited": "Write in an excited, energetic tone. Use exclamation points and enthusiastic language!",
                "critical": "Write in a critical, analytical tone. Point out both strengths and potential weaknesses.",
                "questioning": "Write in a questioning, curious tone. Ask rhetorical questions to engage viewers.",
                "balanced": "Write in a balanced, informative tone. Present facts objectively.",
                "dramatic": "Write in a dramatic, cinematic tone. Build suspense and excitement."
            }
            
            # Build the prompt
            prompt = f"""
{system_prompt}

Game Information:
{game_info}

Tone Instructions: {tone_instructions.get(tone, tone_instructions["balanced"])}

CRITICAL REQUIREMENTS:
- Write ONLY the script - no explanations, comments, or extra text
- Maximum 30 seconds when read aloud (approximately 75-80 words)
- Start with an immediate hook in first 3 seconds
- End with a call to action
- Make it punchy and engaging for YouTube Shorts

Script:
"""
            
            self.window.after(0, lambda: self.generated_script_text.delete(1.0, tk.END))
            self.window.after(0, lambda: self.generated_script_text.insert(1.0, "Generating script with AI..."))
            
            # Make API request
            response = self.make_openrouter_request(prompt)
            
            # Update UI with result
            self.window.after(0, lambda: self.update_generated_script(response))
            
        except Exception as e:
            error_msg = f"Error generating script: {str(e)}"
            self.window.after(0, lambda: self.show_generation_error(error_msg))
    
    def fetch_steam_info(self):
        """Fetch game information from Steam URL"""
        try:
            # Simple approach - extract game info from URL and try to get basic info
            # This is a simplified version - in a full implementation, you might want to scrape the Steam page
            game_name = extract_game_name_from_url(self.steam_url)
            return f"Game: {game_name}\nSteam URL: {self.steam_url}"
        except Exception as e:
            return f"Game URL: {self.steam_url}\nNote: Could not fetch additional game information ({str(e)})"
    
    def make_openrouter_request(self, prompt):
        """Make request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {"role": "system", "content": "You are a professional YouTube Shorts script writer. Return ONLY the script text with no additional commentary, explanations, or formatting. Keep scripts under 80 words for 30-second videos."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            script = result["choices"][0]["message"]["content"]
            return self.post_process_script(script)
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    def post_process_script(self, script):
        """Clean up the generated script"""
        # Remove quotes at the beginning and end
        script = script.strip()
        if (script.startswith('"') and script.endswith('"')) or (script.startswith("'") and script.endswith("'")):
            script = script[1:-1]
        
        # Remove common unwanted prefixes/suffixes
        unwanted_prefixes = [
            "Script:",
            "Here's the script:",
            "Here is the script:",
            "The script:",
            "YouTube Shorts Script:",
            "**Script:**",
            "Script: ",
        ]
        
        unwanted_suffixes = [
            "[End of script]",
            "[Script ends]",
            "That's the script!",
            "Hope this helps!",
            "[Duration: 30 seconds]",
            "(30 seconds)",
        ]
        
        # Remove prefixes
        for prefix in unwanted_prefixes:
            if script.lower().startswith(prefix.lower()):
                script = script[len(prefix):].strip()
        
        # Remove suffixes
        for suffix in unwanted_suffixes:
            if script.lower().endswith(suffix.lower()):
                script = script[:-len(suffix)].strip()
        
        # Remove extra quotes and asterisks
        script = script.strip('"\'*')
        
        # Remove markdown formatting
        script = re.sub(r'\*\*(.*?)\*\*', r'\1', script)  # Remove **bold**
        script = re.sub(r'\*(.*?)\*', r'\1', script)      # Remove *italic*
        script = re.sub(r'__(.*?)__', r'\1', script)      # Remove __bold__
        script = re.sub(r'_(.*?)_', r'\1', script)        # Remove _italic_
        
        # Clean up extra whitespace
        script = re.sub(r'\n\s*\n', '\n\n', script)       # Multiple newlines to double
        script = re.sub(r' +', ' ', script)               # Multiple spaces to single
        script = script.strip()
        
        return script
    
    def update_generated_script(self, script):
        """Update the generated script text area"""
        self.generated_script_text.delete(1.0, tk.END)
        self.generated_script_text.insert(1.0, script)
        self.use_script_button.config(state='normal')
        self.generate_button.config(state='normal', text="✨ Generate Script")
        
        # Automatically update main window script area
        self.callback(script)
    
    def show_generation_error(self, error_msg):
        """Show error in the script area"""
        self.generated_script_text.delete(1.0, tk.END)
        self.generated_script_text.insert(1.0, f"❌ {error_msg}")
        self.generate_button.config(state='normal', text="✨ Generate Script")
        messagebox.showerror("Generation Error", error_msg)
    
    def use_generated_script(self):
        """Use the generated script in the main window"""
        script = self.generated_script_text.get(1.0, tk.END).strip()
        if script and not script.startswith("❌"):
            self.callback(script)
            self.window.destroy()
        else:
            messagebox.showwarning("Warning", "No valid script to use.")

def main():
    """Main function to run the GUI"""
    # Check if unified script exists
    if not os.path.exists("prgavi_unified.py"):
        messagebox.showerror(
            "Error",
            "prgavi_unified.py not found!\n"
            "Please run this GUI from the same directory as the unified script."
        )
        return
    
    root = tk.Tk()
    app = PRGAVIModernGUI(root)
    
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