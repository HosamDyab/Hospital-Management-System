import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import time
from database.db_manager import DatabaseManager
from ui.components import SidebarButton
from .dashboard import Dashboard
from .table_view import TableView
import random

class HospitalManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the main window initially
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Check database connection
        if not self.db.connection:
            messagebox.showerror("Error", "Could not connect to database")
            root.destroy()
            return
        
        # Configure main window
        self.root.title("Hospital Management System")
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#f0f0f0')
        self.main_container.pack(fill='both', expand=True)
        
        # Initialize components
        self.content_area = None
        self.dashboard = None
        
        # Create sidebar and content area first
        self.create_sidebar()
        self.setup_content_area()
        
        # Initialize table_view after content area is created
        self.table_view = TableView(self.content_area, self.db)
        
        # Show welcome screen
        self.show_welcome_screen()

    def create_sidebar(self):
        sidebar = tk.Frame(self.main_container, bg='#2c3e50', width=200)
        sidebar.pack(side='left', fill='y', padx=0, pady=0)
        sidebar.pack_propagate(False)

        # Header
        header = tk.Frame(sidebar, bg='#2c3e50', height=100)
        header.pack(fill='x', padx=10, pady=20)
        tk.Label(header, text="Hospital\nManagement", font=('Arial', 16, 'bold'),
                bg='#2c3e50', fg='white', justify='center').pack(pady=10)

        # Menu buttons
        menu_items = [
            ("Dashboard", self.show_dashboard),
            ("Departments", lambda: self.show_table_view("DEPARTMENT")),
            ("Staff", lambda: self.show_table_view("STAFF")),
            ("Doctors", lambda: self.show_table_view("DOCTOR")),
            ("Rooms", lambda: self.show_table_view("ROOM")),
            ("Patients", lambda: self.show_table_view("PATIENT")),
            ("Appointments", lambda: self.show_table_view("APPOINTMENT")),
            ("Billing", lambda: self.show_table_view("BILLING")),
            ("Dependents", lambda: self.show_table_view("DEPENDENTS"))
        ]

        for text, command in menu_items:
            SidebarButton(sidebar, text=text, command=command).pack(fill='x', padx=5, pady=2)

    def setup_content_area(self):
        """Setup the main content area"""
        self.content_area = tk.Frame(self.main_container, bg='white')
        self.content_area.pack(side='right', fill='both', expand=True)
        
        # Initialize dashboard
        self.dashboard = Dashboard(self.content_area, self.root, self.db)

    def show_welcome_screen(self):
        welcome = tk.Toplevel(self.root)
        welcome.title("Welcome")
        welcome.attributes('-topmost', True)
        welcome.state('zoomed')
        welcome.configure(bg='#f8f9fa')
        welcome.overrideredirect(True)
        welcome.focus_force()
        
        # Create main canvas for animations
        self.canvas = tk.Canvas(welcome, bg='#f8f9fa', highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        
        # Create animated particles with glowing effect
        self.particles = []
        for _ in range(40):
            x = random.randint(0, welcome.winfo_screenwidth())
            y = random.randint(0, welcome.winfo_screenheight())
            particle = {
                'x': x, 'y': y,
                'dx': random.uniform(-1.5, 1.5),
                'dy': random.uniform(-1.5, 1.5),
                'size': random.randint(2, 6),
                'alpha': random.uniform(0.3, 0.8),
                'color': random.choice(['#bbdefb', '#90caf9', '#64b5f6', '#42a5f5'])
            }
            self.particles.append(particle)
        
        # Enhanced gradient background
        self.gradient_colors = []
        gradient_stops = ['#ffffff', '#f5f9ff', '#e3f2fd', '#bbdefb']
        segments = len(gradient_stops) - 1
        steps_per_segment = 40
        
        for i in range(segments):
            start_color = gradient_stops[i]
            end_color = gradient_stops[i+1]
            for step in range(steps_per_segment):
                fraction = step / steps_per_segment
                color = self._interpolate_color(start_color, end_color, fraction)
                self.gradient_colors.append(color)
                height = welcome.winfo_screenheight() / (segments * steps_per_segment)
                y = (i * steps_per_segment + step) * height
                self.canvas.create_rectangle(0, y, welcome.winfo_screenwidth(), y + height + 1,
                                          fill=color, outline='')
        
        # Create glass morphism container
        container = tk.Frame(welcome, bg='white')
        container.place(relx=0.5, rely=0.5, anchor='center')
        container.configure(highlightbackground='#e3f2fd',
                          highlightthickness=2,
                          padx=40, pady=40)
        
        # Add glass effect to container
        glass_canvas = tk.Canvas(container, bg='white', highlightthickness=0)
        glass_canvas.place(relwidth=1, relheight=1)
        
        for i in range(15):
            alpha = 0.02 * i
            color = self._interpolate_color('#ffffff', '#e3f2fd', alpha)
            glass_canvas.create_rectangle(0, i*10, glass_canvas.winfo_reqwidth(),
                                       (i+1)*10, fill=color, outline='')
        
        # Hospital icon with pulsing effect
        self.icon_label = tk.Label(container,
                                 text="🏥",
                                 font=('Segoe UI Emoji', 80),
                                 bg='white',
                                 fg='#2196f3')
        self.icon_label.pack(pady=(0,20))
        
        # Welcome text with enhanced typewriter effect
        self.welcome_text = tk.Label(container,
                                   text="",
                                   font=('Segoe UI Light', 32),
                                   bg='white',
                                   fg='#1976d2')
        self.welcome_text.pack()
        
        self.hospital_text = tk.Label(container,
                                    text="",
                                    font=('Segoe UI', 48, 'bold'),
                                    bg='white',
                                    fg='#1565c0')
        self.hospital_text.pack(pady=(0, 40))
        
        # Modern progress bar with glow effect
        progress_frame = tk.Frame(container, bg='white')
        progress_frame.pack(fill='x', padx=50)
        
        # Create progress bar glow
        self.progress_canvas = tk.Canvas(progress_frame, height=20, 
                                       bg='white', highlightthickness=0)
        self.progress_canvas.pack(fill='x')
        
        style = ttk.Style()
        style.configure("Modern.Horizontal.TProgressbar",
                       thickness=8,
                       troughcolor='#e3f2fd',
                       background='#2196f3',
                       bordercolor='#2196f3',
                       lightcolor='#64b5f6',
                       darkcolor='#1976d2')
        
        self.progress = ttk.Progressbar(progress_frame,
                                      length=600,
                                      mode='determinate',
                                      style="Modern.Horizontal.TProgressbar")
        self.progress.pack(fill='x')
        
        # Status labels with modern styling
        self.loading_label = tk.Label(container,
                                    text="Initializing System...",
                                    font=('Segoe UI Light', 14),
                                    bg='white',
                                    fg='#757575')
        self.loading_label.pack(pady=(20, 0))
        
        self.status_label = tk.Label(container,
                                   text="",
                                   font=('Segoe UI Light', 12),
                                   bg='white',
                                   fg='#9e9e9e')
        self.status_label.pack(pady=(5, 0))
        
        # Version info with separator
        separator = ttk.Separator(container, orient='horizontal')
        separator.pack(fill='x', pady=(30, 15))
        
        version_frame = tk.Frame(container, bg='white')
        version_frame.pack()
        
        tk.Label(version_frame,
                text="Version 2.0",
                font=('Segoe UI', 10),
                bg='white',
                fg='#9e9e9e').pack(side='left', padx=5)
        
        tk.Label(version_frame,
                text="•",
                font=('Segoe UI', 10),
                bg='white',
                fg='#9e9e9e').pack(side='left', padx=5)
        
        tk.Label(version_frame,
                text="Professional Edition",
                font=('Segoe UI', 10),
                bg='white',
                fg='#9e9e9e').pack(side='left', padx=5)
        
        # Save references and start animations
        self.welcome_window = welcome
        self.pulse_alpha = 0
        self.pulse_increasing = True
        
        # Start all animations
        self.animate_particles()
        self.pulse_icon()
        self.typewriter_text("Welcome to", self.welcome_text, 
                           "Hospital Management System", self.hospital_text)
        self.welcome_window.after(500, self.update_progress)
    
    def animate_particles(self):
        """Animate floating particles"""
        if not hasattr(self, 'welcome_window'):
            return
            
        try:
            self.canvas.delete('particle')
            width = self.welcome_window.winfo_width()
            height = self.welcome_window.winfo_height()
            
            for particle in self.particles:
                # Update position
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                
                # Bounce off walls
                if particle['x'] < 0 or particle['x'] > width:
                    particle['dx'] *= -1
                if particle['y'] < 0 or particle['y'] > height:
                    particle['dy'] *= -1
                
                # Draw particle
                self.canvas.create_oval(
                    particle['x'] - particle['size'],
                    particle['y'] - particle['size'],
                    particle['x'] + particle['size'],
                    particle['y'] + particle['size'],
                    fill=particle['color'],
                    outline='',
                    tags='particle'
                )
            
            self.welcome_window.after(50, self.animate_particles)
            
        except Exception as e:
            logging.error(f"Error in particle animation: {e}")
    
    def pulse_icon(self):
        """Create pulsing effect for hospital icon"""
        if not hasattr(self, 'welcome_window'):
            return
            
        try:
            if self.pulse_increasing:
                self.pulse_alpha += 0.05
                if self.pulse_alpha >= 1:
                    self.pulse_increasing = False
            else:
                self.pulse_alpha -= 0.05
                if self.pulse_alpha <= 0.3:
                    self.pulse_increasing = True
            
            color = self._interpolate_color('#bbdefb', '#2196f3', self.pulse_alpha)
            self.icon_label.configure(fg=color)
            
            self.welcome_window.after(50, self.pulse_icon)
            
        except Exception as e:
            logging.error(f"Error in icon pulse animation: {e}")
    
    def typewriter_text(self, text1, label1, text2, label2, index1=0, index2=0):
        """Create typewriter effect for text"""
        if not hasattr(self, 'welcome_window'):
            return
            
        try:
            if index1 < len(text1):
                label1.configure(text=text1[:index1+1])
                self.welcome_window.after(100, 
                    lambda: self.typewriter_text(text1, label1, text2, label2, index1+1, index2))
            elif index2 < len(text2):
                label2.configure(text=text2[:index2+1])
                self.welcome_window.after(50, 
                    lambda: self.typewriter_text(text1, label1, text2, label2, index1, index2+1))
                
        except Exception as e:
            logging.error(f"Error in typewriter animation: {e}")

    def _interpolate_color(self, color1, color2, fraction):
        """Interpolate between two colors"""
        c1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        c2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        rgb = [int(c1[i] + (c2[i] - c1[i]) * fraction) for i in range(3)]
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def update_progress(self):
        """Update the welcome screen progress"""
        status_messages = [
            "Loading modules...",
            "Connecting to database...",
            "Initializing interface...",
            "Loading patient records...",
            "Setting up dashboard...",
            "Almost ready..."
        ]
        
        try:
            for i in range(101):
                self.progress['value'] = i
                
                # Update status message
                if i < 95:
                    status_index = (i // 16) % len(status_messages)
                    self.status_label['text'] = status_messages[status_index]
                    
                self.loading_label['text'] = f"Loading... {i}%"
                
                # Fade in text effect
                if i < 30:
                    alpha = i / 30
                    self.welcome_text['fg'] = self._interpolate_color('#f8f9fa', '#1976d2', alpha)
                    self.hospital_text['fg'] = self._interpolate_color('#f8f9fa', '#1565c0', alpha)
                
                self.welcome_window.update()
                time.sleep(0.02)
            
            # Cleanup and show main window
            self.welcome_window.destroy()
            self.root.deiconify()
            
        except Exception as e:
            logging.error(f"Error during welcome screen progress: {e}")
            # Ensure main window is shown even if there's an error
            if hasattr(self, 'welcome_window'):
                self.welcome_window.destroy()
            self.root.deiconify()

    def show_dashboard(self):
        # Clear existing content
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Create new dashboard
        self.dashboard = Dashboard(self.content_area, self.root, self.db)
        self.update_datetime()

    def show_table_view(self, table_name):
        self.table_view.setup(self.content_area, table_name)

    def update_datetime(self):
        try:
            if hasattr(self.dashboard, 'time_label') and self.dashboard.time_label.winfo_exists():
                current_time = time.strftime('%I:%M %p')
                current_date = time.strftime('%B %d, %Y')
                self.dashboard.time_label.config(text=current_time)
                self.dashboard.date_label.config(text=current_date)
                self.root.after(1000, self.update_datetime)
        except Exception as e:
            logging.error(f"Error updating datetime: {e}")

    def __del__(self):
        try:
            if hasattr(self, 'db'):
                self.db.disconnect()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

# Add project root directory to Python path if running directly
if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    import tkinter as tk
    from tkinter import ttk, messagebox
    import time
    from database.db_manager import DatabaseManager
    from ui.components import SidebarButton
    from .dashboard import Dashboard
    from .table_view import TableView

    root = tk.Tk()
    app = HospitalManagementSystem(root)
    app.update_progress()
    root.mainloop()

# References
# 1. **Tkinter**
#    - Python's standard GUI library
#    - Used for: Main application interface
#    - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
# 2. **Python logging module**
#    - Used for: Logging errors and information
#    - Documentation: [Python logging Documentation](https://docs.python.org/3/library/logging.html)
# 3. **Pathlib**
#    - Used for: Path manipulations
#    - Documentation: [Pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
# 4. **Random**
#    - Used for: Generating random numbers
#    - Documentation: [Random Documentation](https://docs.python.org/3/library/random.html)
