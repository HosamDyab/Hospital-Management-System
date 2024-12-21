import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import logging
import os
import re
from PIL import Image, ImageTk
import time

# Set up logging
logging.basicConfig(level=logging.INFO)

class SidebarButton(tk.Button):
    def __init__(self, parent, text, command):
        super().__init__(
            parent,
            text=text,
            font=('Segoe UI', 11),
            bg='#2c3e50',
            fg='#ecf0f1',
            bd=0,
            padx=25,
            pady=12,
            width=18,
            anchor='w',
            activebackground='#34495e',
            activeforeground='#3498db',
            cursor='hand2',
            relief='flat',
            highlightthickness=0,
            command=command
        )
        
        # Create a blue indicator for active state
        self.indicator = tk.Frame(self, bg='#3498db', width=4)
        self.indicator.place(x=0, y=0, relheight=1)
        self.indicator.place_forget()  # Hide initially
        
        # Bind hover events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, e):
        self['bg'] = '#34495e'
        self.indicator.place(x=0, y=0, relheight=1)  # Show indicator
        
    def on_leave(self, e):
        self['bg'] = '#2c3e50'
        self.indicator.place_forget()  # Hide indicator

class DataEntryForm(ttk.Frame):
    def __init__(self, parent, fields, db=None):
        super().__init__(parent)
        self.fields = fields
        self.db = db
        self.entries = {}
        self.time_entries = {}  # Store time-related entries
        self.create_fields()
        self.update_live_time()  # Start time updates
        
    def create_fields(self):
        """Create form fields based on database schema"""
        row = 0
        for field_name, field_info in self.fields.items():
            # Skip auto-increment fields
            if field_info.get('auto_increment'):
                continue
                
            # Create label
            label = ttk.Label(self, text=field_name.replace('_', ' ').title())
            label.grid(row=row, column=0, padx=5, pady=2, sticky='e')
            
            # Create appropriate widget based on field type
            widget = self.create_widget(field_name, field_info)
            widget.grid(row=row, column=1, padx=5, pady=2, sticky='ew')
            
            # Store reference to widget
            self.entries[field_name] = widget
            
            row += 1
            
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
    def create_widget(self, field_name, field_info):
        """Create appropriate widget based on field type"""
        field_type = field_info['type'].lower()
        
        # Define choices for specific fields
        field_choices = {
            'gender': ['Male', 'Female'],
            'role': ['Doctor', 'Nurse', 'Administrator', 'Receptionist', 'Technician'],
            'shift': ['Morning', 'Afternoon', 'Night'],
            'room_type': ['General', 'Private', 'ICU', 'Operating', 'Emergency'],
            'status': ['Scheduled', 'Completed', 'Cancelled', 'In Progress'],
            'payment_status': ['Paid', 'Pending', 'Cancelled', 'Refunded'],
            'specialization': ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Oncology', 
                             'Dermatology', 'Ophthalmology', 'Psychiatry', 'General Medicine'],
            'department_name': ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Oncology',
                              'Dermatology', 'Ophthalmology', 'Psychiatry', 'General Medicine']
        }
        
        # Check if field name contains time-related keywords
        is_time_field = any(keyword in field_name.lower() for keyword in ['time', 'hour', 'schedule'])
        
        # Check if this field should be a dropdown
        if field_name.lower() in field_choices:
            widget = ttk.Combobox(self, values=field_choices[field_name.lower()], state='readonly', width=20)
            widget.current(0) if widget['values'] else None
            widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
            return widget
            
        if field_type in ['date', 'datetime']:
            # Date picker with time if it's datetime
            if 'datetime' in field_type or is_time_field:
                frame = ttk.Frame(self)
                date_widget = DateEntry(frame, width=15, background='darkblue',
                                     foreground='white', borderwidth=2)
                date_widget.pack(side='left', padx=(0, 5))
                
                time_widget = ttk.Entry(frame, width=10)
                time_widget.pack(side='left')
                
                # Store references to both widgets in the frame
                frame.date_widget = date_widget
                frame.time_widget = time_widget
                
                # Store in time entries for live updates
                self.time_entries[field_name] = time_widget
                
                # Add methods to frame to make it compatible with entry interface
                def get():
                    try:
                        date = date_widget.get_date().strftime('%Y-%m-%d')
                        time_str = time_widget.get().strip()
                        if time_str:
                            # Already in 24-hour format, just validate
                            try:
                                time_obj = datetime.strptime(time_str, '%H:%M:%S')
                                return f"{date} {time_str}"
                            except ValueError:
                                # If seconds are not included
                                try:
                                    time_obj = datetime.strptime(time_str, '%H:%M')
                                    return f"{date} {time_str}:00"
                                except ValueError:
                                    return date
                        return date
                    except Exception as e:
                        logging.error(f"Error formatting datetime: {e}")
                        return None
                
                def delete(first, last):
                    time_widget.delete(first, last)
                
                def insert(index, string):
                    time_widget.insert(index, string)
                
                frame.get = get
                frame.delete = delete
                frame.insert = insert
                
                # Bind Enter key to both widgets
                date_widget.bind('<Return>', lambda e: self.focus_next_widget(time_widget))
                time_widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
                
                return frame
            else:
                widget = DateEntry(self, width=20, background='darkblue',
                                 foreground='white', borderwidth=2)
                widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
        elif field_type in ['tinyint', 'bool', 'boolean']:
            # Checkbox
            var = tk.BooleanVar()
            widget = ttk.Checkbutton(self, variable=var)
            widget.var = var  # Store reference to var
            widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
        elif field_type in ['int', 'bigint', 'smallint', 'tinyint']:
            # Spinbox for numbers
            widget = ttk.Spinbox(self, from_=0, to=999999, width=20)
            widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
        elif field_type in ['decimal', 'float', 'double']:
            # Entry with validation for decimals
            vcmd = (self.register(self.validate_float), '%P')
            widget = ttk.Entry(self, validate='key', validatecommand=vcmd, width=20)
            widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
        elif field_type in ['text', 'longtext']:
            # Text area for long text
            widget = tk.Text(self, height=4, width=30)
            widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
        else:
            # Default to Entry
            widget = ttk.Entry(self, width=20)
            # If it's a time field, add to time entries
            if is_time_field:
                self.time_entries[field_name] = widget
            widget.bind('<Return>', lambda e: self.focus_next_widget(e.widget))
            
        return widget

    def update_live_time(self):
        """Update all time-related fields with current time"""
        current_time = time.strftime('%H:%M:%S')  # 24-hour format
        
        # Update all time entries with current time
        for widget in self.time_entries.values():
            if widget.winfo_exists():  # Check if widget still exists
                if isinstance(widget, (ttk.Entry, tk.Entry)):
                    widget.delete(0, tk.END)
                    widget.insert(0, current_time)
        
        # Schedule next update in 1 second
        self.after(1000, self.update_live_time)
        
    def focus_next_widget(self, current_widget):
        """Move focus to the next widget in the form"""
        widgets = list(self.entries.values())
        try:
            current_idx = widgets.index(current_widget)
            next_idx = (current_idx + 1) % len(widgets)
            next_widget = widgets[next_idx]
            next_widget.focus_set()
            
            # If it's a combobox or entry, select all text
            if isinstance(next_widget, (ttk.Entry, ttk.Combobox, ttk.Spinbox)):
                next_widget.select_range(0, tk.END)
        except ValueError:
            # If current widget is not found, focus the first widget
            if widgets:
                widgets[0].focus_set()
                if isinstance(widgets[0], (ttk.Entry, ttk.Combobox, ttk.Spinbox)):
                    widgets[0].select_range(0, tk.END)
                    
    def validate_float(self, value):
        """Validate float input"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
            
    def get_data(self):
        """Get form data as dictionary"""
        data = {}
        for field_name, widget in self.entries.items():
            field_info = self.fields[field_name]
            field_type = field_info['type'].lower()

            try:
                if isinstance(widget, ttk.Frame) and hasattr(widget, 'date_widget'):
                    # Handle datetime frame
                    value = widget.get()  # This now returns properly formatted datetime
                    if value:
                        data[field_name] = value
                    else:
                        data[field_name] = None
                elif isinstance(widget, DateEntry):
                    # Handle date fields
                    date_value = widget.get_date()
                    if date_value:
                        data[field_name] = date_value.strftime('%Y-%m-%d')
                    else:
                        data[field_name] = None
                elif isinstance(widget, ttk.Checkbutton):
                    # Handle boolean fields
                    data[field_name] = 1 if widget.var.get() else 0
                    
                elif isinstance(widget, tk.Text):
                    # Handle text fields
                    value = widget.get('1.0', 'end-1c').strip()
                    data[field_name] = value if value else None
                    
                elif isinstance(widget, ttk.Spinbox):
                    # Handle numeric fields
                    value = widget.get().strip()
                    if value:
                        if 'decimal' in field_type or 'float' in field_type:
                            data[field_name] = float(value)
                        else:
                            data[field_name] = int(value)
                    else:
                        data[field_name] = None
                        
                elif isinstance(widget, ttk.Combobox):
                    # Handle dropdown fields
                    value = widget.get().strip()
                    data[field_name] = value if value else None
                    
                else:
                    # Handle all other fields (mostly string types)
                    value = widget.get().strip()
                    if value:
                        if 'int' in field_type:
                            data[field_name] = int(value)
                        elif 'decimal' in field_type or 'float' in field_type:
                            data[field_name] = float(value)
                        else:
                            data[field_name] = value
                    elif not field_info.get('nullable', True):
                        messagebox.showwarning("Validation Error", f"Field '{field_name}' is required")
                        return None
                    else:
                        data[field_name] = None

            except (ValueError, TypeError) as e:
                messagebox.showerror("Data Error", f"Invalid value for field '{field_name}': {str(e)}")
                return None

        return data
        
    def set_data(self, data):
        """Set form data from dictionary"""
        self.clear()
        for field_name, value in data.items():
            if field_name in self.entries:
                widget = self.entries[field_name]
                if isinstance(widget, ttk.Frame) and hasattr(widget, 'date_widget'):
                    # Handle datetime frame
                    if value:
                        try:
                            # Try to split datetime value
                            if ' ' in value:
                                date_str, time_str = value.split(' ', 1)
                                date_value = datetime.strptime(date_str, '%Y-%m-%d')
                                widget.date_widget.set_date(date_value)
                                widget.time_widget.delete(0, tk.END)
                                widget.time_widget.insert(0, time_str)
                            else:
                                date_value = datetime.strptime(value, '%Y-%m-%d')
                                widget.date_widget.set_date(date_value)
                        except ValueError as e:
                            logging.error(f"Error parsing datetime: {e}")
                elif isinstance(widget, DateEntry):
                    if value:
                        try:
                            # Try datetime format first
                            date_value = datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                # Try date format
                                date_value = datetime.strptime(str(value), '%Y-%m-%d')
                            except ValueError:
                                logging.error(f"Invalid date format for {field_name}: {value}")
                                continue
                        widget.set_date(date_value)
                elif isinstance(widget, ttk.Checkbutton):
                    widget.var.set(bool(value))
                elif isinstance(widget, tk.Text):
                    widget.delete('1.0', 'end')
                    if value:
                        widget.insert('1.0', str(value))
                elif isinstance(widget, ttk.Combobox):
                    if value:
                        widget.set(value)
                else:
                    widget.delete(0, tk.END)
                    if value is not None:
                        widget.insert(0, str(value))
                        
    def clear(self):
        """Clear all form fields"""
        for widget in self.entries.values():
            if isinstance(widget, DateEntry):
                widget.set_date(datetime.now())
            elif isinstance(widget, ttk.Checkbutton):
                widget.var.set(False)
            elif isinstance(widget, tk.Text):
                widget.delete('1.0', 'end')
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)

class DataTable(ttk.Frame):
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.columns = columns
        self.setup_table()

    def setup_table(self):
        """Set up the table with scrollbars"""
        # Create treeview with scrollbars
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill='both', expand=True)

        # Create treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings')
        
        # Create scrollbars
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        self.vsb.grid(column=1, row=0, sticky='ns')
        self.hsb.grid(column=0, row=1, sticky='ew')
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        # Configure column headings
        for col in self.columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(), 
                            command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=100, minwidth=50)

        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Return>', self.on_double_click)

    def insert_data(self, data):
        """Insert data into the table"""
        # Clear existing items
        self.clear()
        
        # Insert new data
        for item in data:
            values = [str(item.get(col, '')) for col in self.columns]
            self.tree.insert('', 'end', values=values)

    def clear(self):
        """Clear all items from the table"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected(self):
        """Get the selected item"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        return dict(zip(self.columns, item['values']))

    def sort_column(self, col):
        """Sort table by column"""
        # Get all items
        data = [(self.tree.set(child, col), child) 
                for child in self.tree.get_children('')]
        
        # Sort data
        data.sort(reverse=self.tree.heading(col).get('reverse', False))
        
        # Rearrange items
        for idx, (_, child) in enumerate(data):
            self.tree.move(child, '', idx)
        
        # Toggle sort direction
        self.tree.heading(col, 
                         reverse=not self.tree.heading(col).get('reverse', False))

    def on_double_click(self, event):
        """Handle double click event"""
        if self.tree.selection():
            self.event_generate('<<TableItemSelected>>')

    def get_all_data(self):
        """Get all data from the table"""
        data = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            data.append(dict(zip(self.columns, values)))
        return data

    def select_item(self, item_id):
        """Select a specific item by ID"""
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == item_id:
                self.tree.selection_set(item)
                self.tree.focus(item)
                self.tree.see(item)
                break

    def update_item(self, item_id, new_values):
        """Update a specific item"""
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == item_id:
                self.tree.item(item, values=[new_values.get(col, '') 
                                           for col in self.columns])
                break

class StatBox(tk.Frame):
    def __init__(self, parent, title, value="0", icon="📊", color="#3498db"):
        super().__init__(parent, bg='white')
        
        # Store properties
        self._title = title
        self._value = value
        self._icon = icon
        self._color = color
        
        # Create main container with shadow effect
        self.container = tk.Frame(self, bg='white')
        self.container.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Add subtle shadow effect
        self._create_shadow()
        
        # Create content
        self._create_content()
        
        # Bind hover effects
        self._bind_hover_effects()
    
    def _create_shadow(self):
        """Create shadow effect for the box"""
        shadow_color = "#0001"
        shadow_size = 2
        
        for i in range(shadow_size):
            shadow = tk.Frame(self)
            shadow.place(x=i, y=i, relwidth=1, relheight=1)
            shadow.configure(bg=shadow_color)
            shadow.lower()
    
    def _create_content(self):
        """Create the content of the stat box"""
        # Icon
        icon_label = tk.Label(self.container,
                            text=self._icon,
                            font=('Segoe UI', 24),
                            bg='white',
                            fg=self._color)
        icon_label.pack(side='left', padx=15)
        
        # Info container
        info_frame = tk.Frame(self.container, bg='white')
        info_frame.pack(side='left', fill='both', expand=True, padx=(0, 15), pady=10)
        
        # Title
        title_label = tk.Label(info_frame,
                             text=self._title,
                             font=('Segoe UI', 10),
                             bg='white',
                             fg='#7f8c8d')
        title_label.pack(anchor='w')
        
        # Value
        self.value_label = tk.Label(info_frame,
                                  text=self._value,
                                  font=('Segoe UI', 24, 'bold'),
                                  bg='white',
                                  fg='#2c3e50')
        self.value_label.pack(anchor='w')
    
    def _bind_hover_effects(self):
        """Bind hover effects to the stat box"""
        def on_enter(e):
            self.container.configure(bg='#f8f9fa')
            for widget in self.container.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg='#f8f9fa')
                elif isinstance(widget, tk.Frame):
                    widget.configure(bg='#f8f9fa')
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(bg='#f8f9fa')
        
        def on_leave(e):
            self.container.configure(bg='white')
            for widget in self.container.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg='white')
                elif isinstance(widget, tk.Frame):
                    widget.configure(bg='white')
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(bg='white')
        
        # Bind events
        self.container.bind('<Enter>', on_enter)
        self.container.bind('<Leave>', on_leave)
        
        # Bind to all child widgets
        for widget in self.container.winfo_children():
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    child.bind('<Enter>', on_enter)
                    child.bind('<Leave>', on_leave)
    
    def update_value(self, value):
        """Update the displayed value"""
        self._value = value
        self.value_label.configure(text=str(value))
    
    def update_color(self, color):
        """Update the color theme"""
        self._color = color
        for widget in self.container.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget('text') == self._icon:
                widget.configure(fg=color)

class NavigationButton(ttk.Frame):
    def __init__(self, parent, text, icon, command):
        super().__init__(parent)
        
        # Create button with icon and text
        btn = ttk.Button(self, text=f"{icon} {text}", command=command)
        btn.pack(fill='x', padx=5, pady=2)
        
        # Hover effect
        def on_enter(e):
            btn.state(['active'])
        
        def on_leave(e):
            btn.state(['!active'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

class StatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Status message (left)
        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack(side='left', padx=5)
        
        # Right side container
        right_container = ttk.Frame(self)
        right_container.pack(side='right', fill='y')
        
        # Additional status indicators can be added here
        
    def set_status(self, message):
        self.status_label.config(text=message)

class WelcomeScreen(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        # Configure the window
        self.title("Welcome to Hospital Management System")
        self.state('zoomed')  # Full screen
        self.configure(bg='#ffffff')
        self.overrideredirect(True)  # Remove window decorations
        
        # Center the content
        content_frame = tk.Frame(self, bg='#ffffff')
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Add hospital logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "hospital_icon.png")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((200, 200), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(content_frame, image=self.logo_photo, bg='#ffffff')
            logo_label.pack(pady=(0, 30))
        except Exception as e:
            logging.error(f"Error loading logo: {e}")
        
        # Welcome text
        tk.Label(content_frame,
                text="Welcome to",
                font=('Arial', 24),
                bg='#ffffff',
                fg='#2c3e50').pack()
        
        tk.Label(content_frame,
                text="Hospital Management System",
                font=('Arial', 32, 'bold'),
                bg='#ffffff',
                fg='#2c3e50').pack(pady=(0, 30))
        
        # Subtitle
        tk.Label(content_frame,
                text="Providing Quality Healthcare Services",
                font=('Arial', 14),
                bg='#ffffff',
                fg='#7f8c8d').pack(pady=(0, 40))
        
        # Progress bar frame
        progress_frame = tk.Frame(content_frame, bg='#ffffff')
        progress_frame.pack(fill='x', padx=50)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.pack(fill='x')
        
        # Loading text
        self.loading_label = tk.Label(content_frame,
                                    text="Loading...",
                                    font=('Arial', 10),
                                    bg='#ffffff',
                                    fg='#95a5a6')
        self.loading_label.pack(pady=(10, 0))
        
        # Start progress
        self.start_progress()
    
    def start_progress(self):
        """Start the progress animation"""
        def update_progress():
            if self.progress['value'] < 100:
                self.progress['value'] += 2
                self.after(50, update_progress)
            else:
                self.after(500, self.finish)
        
        update_progress()
    
    def finish(self):
        """Close the welcome screen and call the callback"""
        self.callback()  # Call the callback function
        self.destroy()  # Close the welcome screen

# References
# 1. **Tkinter**
#    - Python's standard GUI library
#    - Used for: Main application interface
#    - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
# 2. **Pillow**
#    - Used for: Image handling and processing
#    - Documentation: [Pillow Documentation](https://pillow.readthedocs.io/)
# 3. **tkcalendar**
#    - Used for: Calendar widget in appointment scheduling
#    - Documentation: [tkcalendar Documentation](https://tkcalendar.readthedocs.io/)
# 4. **Python logging module**
#    - Used for: Logging errors and information
#    - Documentation: [Python logging Documentation](https://docs.python.org/3/library/logging.html)
# 5. **Datetime**
#    - Used for: Handling date and time
#    - Documentation: [Datetime Documentation](https://docs.python.org/3/library/datetime.html)
# 6. **Time**
#    - Used for: Time-related functions
#    - Documentation: [Time Documentation](https://docs.python.org/3/library/time.html)
