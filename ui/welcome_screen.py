import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import logging

class WelcomeScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Welcome to Hospital Management System")
        self.geometry("900x600")
        self.configure(bg='#1a73e8')  # Modern blue background
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Center the window
        self.center_window()
        
        # Create main frame with gradient effect
        main_frame = tk.Frame(self, bg='#1a73e8')
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)  # Increased padding
        
        # Create inner frame with white background for contrast
        inner_frame = tk.Frame(main_frame, bg='white', relief='solid')
        inner_frame.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Add subtle shadow effect
        shadow_frame = tk.Frame(inner_frame, bg='#e8f0fe', height=5)
        shadow_frame.pack(fill='x', side='top')
        
        # Load and display logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "hospital_icon.png")
            logo_image = Image.open(logo_path)
            # Resize image to reasonable dimensions while maintaining aspect ratio
            basewidth = 300  # Increased logo size
            wpercent = (basewidth / float(logo_image.size[0]))
            hsize = int((float(logo_image.size[1]) * float(wpercent)))
            logo_image = logo_image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
            
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_frame = tk.Frame(inner_frame, bg='white', height=hsize + 60)  # Increased frame height
            logo_frame.pack(fill='x', pady=(40, 30))  # Increased padding
            logo_frame.pack_propagate(False)
            
            logo_label = tk.Label(logo_frame, image=self.logo_photo, bg='white')
            logo_label.place(relx=0.5, rely=0.5, anchor='center')
        except Exception as e:
            logging.error(f"Error loading logo: {e}")
            # Fallback text if logo fails to load
            logo_label = tk.Label(inner_frame, text="Hospital\nManagement\nSystem", 
                                font=('Segoe UI', 36, 'bold'), bg='white', fg='#1a73e8')
            logo_label.pack(pady=30)
        
        # Welcome text with enhanced typography
        welcome_label = tk.Label(inner_frame, 
                               text="Welcome to Hospital Management System",
                               font=('Segoe UI', 32, 'bold'),
                               bg='white',
                               fg='#1a73e8')  # Matching blue color
        welcome_label.pack(pady=(20, 10))
        
        # Enhanced subtitle
        subtitle_label = tk.Label(inner_frame,
                                text="Providing Quality Healthcare Services",
                                font=('Segoe UI', 18),
                                bg='white',
                                fg='#5f6368')  # Google-style gray
        subtitle_label.pack(pady=(0, 30))
        
        # Progress bar in a frame
        progress_frame = tk.Frame(inner_frame, bg='white')
        progress_frame.pack(fill='x', padx=80, pady=(30, 0))
        
        # Style the progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor='#e8f0fe',
                       background='#1a73e8',
                       thickness=8)
        
        self.progress = ttk.Progressbar(progress_frame,
                                      style="Custom.Horizontal.TProgressbar",
                                      length=400,
                                      mode='determinate')
        self.progress.pack(fill='x')
        
        # Loading text
        self.loading_label = tk.Label(inner_frame,
                                    text="Loading...",
                                    font=('Segoe UI', 14),
                                    bg='white',
                                    fg='#5f6368')
        self.loading_label.pack(pady=(15, 0))
        
        # Start progress
        self.start_progress()
    
    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 900
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def start_progress(self):
        self.progress['value'] = 0
        self.progress_step()
    
    def progress_step(self):
        if self.progress['value'] < 100:
            self.progress['value'] += 1
            self.after(30, self.progress_step)
        else:
            self.after(500, self.destroy)  # Close welcome screen after completion

# References
# 1. **Tkinter**
#    - Python's standard GUI library
#    - Used for: Main application interface
#    - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
# 2. **Pillow**
#    - Used for: Image handling and processing
#    - Documentation: [Pillow Documentation](https://pillow.readthedocs.io/)
