import tkinter as tk
from tkinter import ttk
import time
from tkinter import messagebox
import threading
from datetime import datetime, timedelta
import math
import logging

class Dashboard(tk.Frame):
    def __init__(self, parent, root, db):
        super().__init__(parent)
        self.root = root
        self.db = db
        self.configure(bg='#f0f2f5')  # Modern light background
        self.setup_font()
        self.create_dashboard()
        self.update_time()

    def setup_font(self):
        """Setup digital font for clock, fallback to a similar font if not available"""
        try:
            # List of fonts to try, in order of preference
            digital_fonts = ['DS-Digital', 'LCD', 'Digital-7', 'Segment7', 'Consolas', 'Courier']
            
            # Get list of available system fonts
            available_fonts = list(tk.font.families())
            
            # Find the first available digital-style font
            self.clock_font = next((font for font in digital_fonts if font in available_fonts), 'Courier')
            
        except Exception as e:
            logging.error(f"Error setting up font: {e}")
            self.clock_font = 'Courier'  # Fallback to Courier if all else fails

    def create_dashboard(self):
        """Create modern dashboard layout"""
        self.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top section - Header with Time
        top_frame = tk.Frame(self, bg='#ffffff')
        top_frame.pack(fill='x', pady=(0, 20))
        self.create_header(top_frame)
        
        # Main content area with statistics and activities
        main_frame = tk.Frame(self, bg='#ffffff')
        main_frame.pack(fill='both', expand=True)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=3)  # Stats section takes more space
        main_frame.grid_columnconfigure(1, weight=2)  # Activities section takes less space
        
        # Left side - Statistics
        left_frame = tk.Frame(main_frame, bg='#ffffff')
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.create_stats_section(left_frame)
        
        # Right side - Recent Activities
        right_frame = tk.Frame(main_frame, bg='#ffffff')
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        self.create_recent_activities(right_frame)

    def create_header(self, parent):
        """Create modern header with enhanced time display"""
        header_frame = tk.Frame(parent, bg='#ffffff')
        header_frame.pack(fill='x', padx=20, pady=10)

        # Left side - Welcome message with gradient effect
        welcome_frame = tk.Frame(header_frame, bg='#ffffff')
        welcome_frame.pack(side='left', fill='y')

        welcome_label = tk.Label(welcome_frame, 
                               text="Hospital Management System",
                               font=('Segoe UI', 24, 'bold'),
                               bg='#ffffff',
                               fg='#1a73e8')
        welcome_label.pack(side='top')

        self.status_label = tk.Label(welcome_frame,
                                   text="System Online",
                                   font=('Segoe UI', 12),
                                   bg='#ffffff',
                                   fg='#34a853')
        self.status_label.pack(side='top')

        # Right side - Advanced time display with modern styling
        time_frame = tk.Frame(header_frame, bg='#ffffff', relief='ridge', bd=1)
        time_frame.pack(side='right', padx=20, pady=10)

        # Create a container for the clock with a modern look
        clock_container = tk.Frame(time_frame, bg='#ffffff', pady=10)
        clock_container.pack(fill='x')

        # Digital time display with modern monospace font
        self.time_label = tk.Label(clock_container, 
                                 font=('Consolas', 48, 'bold'),  # Using Consolas as it's commonly available
                                 bg='#ffffff', 
                                 fg='#1a73e8')
        self.time_label.pack()

        # Date container with modern styling
        date_container = tk.Frame(time_frame, bg='#f8f9fa', pady=5)
        date_container.pack(fill='x')

        # Day of week with custom styling
        self.day_label = tk.Label(date_container, 
                                 font=('Segoe UI', 14, 'bold'),
                                 bg='#f8f9fa', 
                                 fg='#5f6368')
        self.day_label.pack()

        # Full date with elegant styling
        self.date_label = tk.Label(date_container, 
                                  font=('Segoe UI', 12),
                                  bg='#f8f9fa', 
                                  fg='#5f6368')
        self.date_label.pack()

        # Additional time info container
        info_container = tk.Frame(time_frame, bg='#ffffff', pady=5)
        info_container.pack(fill='x')

        # Time zone display
        self.timezone_label = tk.Label(info_container,
                                     font=('Segoe UI', 10),
                                     bg='#ffffff',
                                     fg='#5f6368')
        self.timezone_label.pack(side='left', padx=10)

        # Week number display
        self.week_label = tk.Label(info_container,
                                 font=('Segoe UI', 10),
                                 bg='#ffffff',
                                 fg='#5f6368')
        self.week_label.pack(side='right', padx=10)

        self.update_time()
        self.animate_status()

    def animate_status(self):
        """Animate the status label with a pulsing effect"""
        try:
            colors = ['#34a853', '#1a73e8', '#34a853']  # Green to blue to green
            current_color = getattr(self, '_color_index', 0)
            
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.configure(fg=colors[current_color])
                
            self._color_index = (current_color + 1) % len(colors)
            self.root.after(2000, self.animate_status)
        except Exception as e:
            logging.error(f"Error in status animation: {e}")

    def create_stats_section(self, parent):
        """Create modern statistics section"""
        frame = tk.Frame(parent, bg='#ffffff')
        frame.pack(fill='x', pady=20)
        
        # Section title
        tk.Label(frame, text='Hospital Statistics',
                font=('Segoe UI', 20, 'bold'),
                bg='#ffffff', fg='#333333').pack(padx=20, pady=(0, 20))
        
        # Stats cards with increased size
        cards_frame = tk.Frame(frame, bg='#ffffff')
        cards_frame.pack(fill='x', padx=20)
        
        # Configure grid columns
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
        # Create enlarged stat cards
        stats = [
            ('Total Patients', self.get_patient_count(), '#1a73e8', '👥'),
            ('Doctors', self.get_doctor_count(), '#34a853', '👨‍⚕️'),
            ('Available Rooms', self.get_room_count(), '#fbbc04', '🏥'),
            ('Appointments Today', self.get_appointment_count(), '#ea4335', '📅')
        ]
        
        for i, (title, count, color, icon) in enumerate(stats):
            row = i // 2
            col = i % 2
            
            card = tk.Frame(cards_frame, bg=color, relief='flat', bd=0)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Add padding inside card
            inner_frame = tk.Frame(card, bg=color)
            inner_frame.pack(padx=20, pady=20, fill='both', expand=True)
            
            # Icon and count in larger size
            tk.Label(inner_frame, text=icon,
                    font=('Segoe UI', 36),
                    bg=color, fg='white').pack()
            
            tk.Label(inner_frame, text=str(count),
                    font=('Segoe UI', 32, 'bold'),
                    bg=color, fg='white').pack()
            
            tk.Label(inner_frame, text=title,
                    font=('Segoe UI', 16),
                    bg=color, fg='white').pack()

    def get_patient_count(self):
        """Get count of patients"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM PATIENT")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logging.error(f"Error getting patient count: {e}")
            return 0

    def get_doctor_count(self):
        """Get count of doctors"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM DOCTOR")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logging.error(f"Error getting doctor count: {e}")
            return 0

    def get_room_count(self):
        """Get count of available rooms"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM ROOM WHERE OCCUPIED < CAPACITY")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logging.error(f"Error getting room count: {e}")
            return 0

    def get_appointment_count(self):
        """Get count of appointments today"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE DATE(APPOINTMENT_DATE) = CURDATE()")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logging.error(f"Error getting appointment count: {e}")
            return 0

    def create_recent_activities(self, parent):
        """Create modern recent activities section"""
        frame = tk.Frame(parent, bg='#ffffff')
        frame.pack(fill='both', expand=True, pady=20)
        
        # Section title
        tk.Label(frame, text='Recent Activities',
                font=('Segoe UI', 20, 'bold'),
                bg='#ffffff', fg='#333333').pack(padx=20, pady=(0, 20))
        
        # Activities list with larger text
        activities = self.get_recent_activities()
        for activity in activities:
            activity_frame = tk.Frame(frame, bg='#ffffff')
            activity_frame.pack(fill='x', padx=20, pady=10)
            
            tk.Label(activity_frame, text=activity['icon'],
                    font=('Segoe UI', 20),
                    bg='#ffffff', fg='#666666').pack(side='left', padx=(0, 10))
            
            details_frame = tk.Frame(activity_frame, bg='#ffffff')
            details_frame.pack(side='left', fill='x', expand=True)
            
            tk.Label(details_frame, text=activity['title'],
                    font=('Segoe UI', 14, 'bold'),
                    bg='#ffffff', fg='#333333').pack(anchor='w')
            
            tk.Label(details_frame, text=activity['time'],
                    font=('Segoe UI', 12),
                    bg='#ffffff', fg='#666666').pack(anchor='w')

    def get_recent_activities(self):
        """Get recent activities from database"""
        activities = []
        try:
            cursor = self.db.connection.cursor()
            
            # Get recent appointments
            cursor.execute("""
                SELECT 'APPOINTMENT', APPOINTMENT_DATE, PATIENT_ID 
                FROM APPOINTMENT 
                ORDER BY APPOINTMENT_DATE DESC 
                LIMIT 10
            """)
            
            for activity_type, date, patient_id in cursor.fetchall():
                activities.append({
                    'icon': '📅',
                    'title': f'New appointment scheduled for Patient #{patient_id}',
                    'time': date.strftime('%Y-%m-%d %H:%M:%S') if date else 'N/A'
                })
            
            # Get recent patients
            cursor.execute("""
                SELECT 'PATIENT', PATIENT_NAME, DATE 
                FROM PATIENT 
                ORDER BY DATE DESC 
                LIMIT 10
            """)
            
            for activity_type, name, date in cursor.fetchall():
                activities.append({
                    'icon': '👤',
                    'title': f'New patient registered: {name}',
                    'time': date.strftime('%Y-%m-%d %H:%M:%S') if date else 'N/A'
                })
            
            cursor.close()
        except Exception as e:
            logging.error(f"Error getting recent activities: {e}")
            # Fallback activities if database query fails
            activities = [
                {'icon': '📅', 'title': 'System is ready', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                {'icon': '🏥', 'title': 'Welcome to HMS', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            ]
        
        return activities

    def update_time(self):
        """Update the time display every second with enhanced format and animations"""
        try:
            # Get current time components
            current = datetime.now()
            
            # Format time with blinking colon
            hour = current.strftime("%H")
            minute = current.strftime("%M")
            second = current.strftime("%S")
            colon = ':' if int(second) % 2 == 0 else ' '  # Blinking colon
            time_str = f"{hour}{colon}{minute}{colon}{second}"
            
            # Format date components
            date_str = current.strftime("%B %d, %Y")
            day_str = current.strftime("%A")
            
            # Get week number and timezone
            week_num = current.isocalendar()[1]
            timezone = time.strftime("%Z")
            
            # Update all labels with new information
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                self.time_label.config(text=time_str)
                
            if hasattr(self, 'date_label') and self.date_label.winfo_exists():
                self.date_label.config(text=date_str)
                
            if hasattr(self, 'day_label') and self.day_label.winfo_exists():
                self.day_label.config(text=day_str)
                
            if hasattr(self, 'timezone_label') and self.timezone_label.winfo_exists():
                self.timezone_label.config(text=f"Timezone: {timezone}")
                
            if hasattr(self, 'week_label') and self.week_label.winfo_exists():
                self.week_label.config(text=f"Week {week_num}")

            # Schedule the next update
            self.root.after(1000, self.update_time)
        except Exception as e:
            logging.error(f"Error updating time: {e}")

# References
# 1. **Tkinter**
#    - Python's standard GUI library
#    - Used for: Main application interface
#    - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
# 2. **Python logging module**
#    - Used for: Logging errors and information
#    - Documentation: [Python logging Documentation](https://docs.python.org/3/library/logging.html)
# 3. **Datetime**
#    - Used for: Handling date and time
#    - Documentation: [Datetime Documentation](https://docs.python.org/3/library/datetime.html)
# 4. **Math**
#    - Used for: Mathematical operations
#    - Documentation: [Math Documentation](https://docs.python.org/3/library/math.html)
