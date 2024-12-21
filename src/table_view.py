import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from ui.components import DataEntryForm, DataTable
import logging

class TableView:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.content_area = None
        self.form = None
        self.table = None
        self.current_table = None
        self.search_var = None
        self.sort_reverse = False
        self.columns = []
        self.setup_styles()

    def setup(self, content_area, table_name):
        """Initialize the table view with the given content area and table name"""
        try:
            logging.info(f"Setting up table view for {table_name}")
            self.content_area = content_area
            self.current_table = table_name
            
            # Clear any existing content
            self.clear_content()
            
            # Show the table view
            self.show_table_view(table_name)
            
        except Exception as e:
            logging.error(f"Error in setup: {e}")
            messagebox.showerror("Error", f"Failed to set up table view: {str(e)}")

    def show_table_view(self, table_name):
        """Display the table view for the given table name"""
        try:
            # Clear existing content
            self.clear_content()
            self.current_table = table_name
            
            # Create main container
            main_frame = ttk.Frame(self.content_area)
            main_frame.pack(fill='both', expand=True, padx=35, pady=25)
            
            # Create header frame
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill='x', padx=15, pady=(10, 0))
            
            # Create title frame
            title_frame = ttk.Frame(header_frame)
            title_frame.pack(side='left', fill='x')
            
            # Add title
            title_label = ttk.Label(
                title_frame,
                text=table_name.replace('_', ' ').title(),
                font=('Helvetica', 16, 'bold')
            )
            title_label.pack(side='left')
            
            # Create status frame
            self.status_frame = ttk.Frame(main_frame)
            self.status_frame.pack(fill='x', padx=15, pady=(5, 0))
            
            # Create status label
            self.status_label = ttk.Label(
                self.status_frame,
                text="",
                foreground='gray'
            )
            self.status_label.pack(side='left')
            
            # Create form and table first
            self.create_form_and_table(main_frame, table_name)
            
            # Then create search section
            search_frame = ttk.Frame(header_frame)
            search_frame.pack(side='right')
            
            # Add search entry and filter
            self._setup_search_widgets(search_frame, table_name)
            
        except Exception as e:
            logging.error(f"Error in show_table_view: {e}")
            messagebox.showerror("Error", f"Failed to show table view: {str(e)}")

    def _setup_search_widgets(self, parent, table_name):
        """Setup search entry and filter widgets"""
        try:
            # Create search container
            search_container = ttk.Frame(parent)
            search_container.pack(fill='x', pady=5)
            
            # Search entry
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(
                search_container,
                textvariable=self.search_var,
                width=30
            )
            search_entry.pack(side='left', padx=5)
            
            # Search button
            search_btn = ttk.Button(
                search_container,
                text="Search",
                command=self._on_search,
                style='Search.TButton'
            )
            search_btn.pack(side='left', padx=2)
            
            # Reset button
            reset_btn = ttk.Button(
                search_container,
                text="Reset",
                command=lambda: self._clear_search(search_entry),
                style='Reset.TButton'
            )
            reset_btn.pack(side='left', padx=2)
            
            # Filter frame
            filter_frame = ttk.Frame(parent)
            filter_frame.pack(fill='x', pady=5)
            
            # Filter label
            ttk.Label(filter_frame, text="Search in:").pack(side='left', padx=(0, 5))
            
            # Get columns for filter
            columns = self.db.get_table_columns(table_name)
            self.filter_column = tk.StringVar(value="All Columns")
            
            # Filter combobox
            filter_combo = ttk.Combobox(
                filter_frame,
                textvariable=self.filter_column,
                values=["All Columns"] + columns,
                state="readonly",
                width=20
            )
            filter_combo.pack(side='left')
            filter_combo.bind('<<ComboboxSelected>>', lambda e: self._on_search())
            
        except Exception as e:
            logging.error(f"Error setting up search widgets: {e}")
            self.update_status("Error setting up search", "error")

    def _on_search(self, *args):
        """Handle search input"""
        try:
            search_text = self.search_var.get().strip()
            filter_col = self.filter_column.get()
            
            if not search_text:
                self._refresh_table(self.current_table)
                self.update_status("Showing all records", "info")
                return
                
            # Get all records
            records = self.db.get_table_data(self.current_table)
            if not records:
                self.table.clear()
                self.update_status("No records found", "info")
                return
                
            # Filter records
            filtered_records = []
            for record in records:
                if filter_col == "All Columns":
                    # Search in all columns
                    if any(str(value).lower().find(search_text.lower()) != -1 
                          for value in record.values()):
                        filtered_records.append(record)
                else:
                    # Search in specific column
                    value = str(record.get(filter_col, "")).lower()
                    if value.find(search_text.lower()) != -1:
                        filtered_records.append(record)
            
            # Update table
            self.table.clear()
            self.table.insert_data(filtered_records)
            
            # Update status
            count = len(filtered_records)
            status = f"Found {count} record{'s' if count != 1 else ''}"
            if search_text:
                status += f" matching '{search_text}'"
            if filter_col != "All Columns":
                status += f" in {filter_col}"
            self.update_status(status, "info")
            
        except Exception as e:
            logging.error(f"Error in search: {e}")
            self.update_status("Search error occurred", "error")

    def _add_placeholder(self, entry, placeholder):
        """Add placeholder text to entry widget"""
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.configure(foreground='#2c3e50')

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(foreground='#95a5a6')

        entry.insert(0, placeholder)
        entry.configure(foreground='#95a5a6')
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def _clear_search(self, entry):
        """Clear search and reset table"""
        try:
            self.search_var.set("")
            self._add_placeholder(entry, "Type to search...")
            self._refresh_table(self.current_table)
            self.update_status("Search cleared", "info")
            
        except Exception as e:
            logging.error(f"Error clearing search: {e}")
            self.update_status("Error clearing search", "error")

    def create_form_and_table(self, parent, table_name):
        """Create the form and table view with separate scrollable sections"""
        try:
            # Get table fields
            fields = self.db.get_table_fields(table_name)
            if not fields:
                raise ValueError(f"No fields found for table {table_name}")

            # Create main container
            container = ttk.Frame(parent)
            container.pack(fill='both', expand=True, padx=15, pady=10)

            # Create form frame
            form_frame = ttk.LabelFrame(container, text=f"Add/Edit {table_name}", padding=10)
            form_frame.pack(side='left', fill='y', padx=(0, 10))

            # Create form
            self.form = DataEntryForm(form_frame, fields, self.db)
            self.form.pack(fill='x', expand=True)

            # Add buttons
            btn_frame = ttk.Frame(form_frame)
            btn_frame.pack(fill='x', pady=(10, 0))

            save_btn = ttk.Button(btn_frame, text="Save", 
                                  command=lambda: self._save_record(table_name), style='Save.TButton')
            save_btn.pack(side='left', padx=2)
            
            update_btn = ttk.Button(btn_frame, text="Update", 
                                    command=lambda: self._update_record(table_name), style='Update.TButton')
            update_btn.pack(side='left', padx=2)
            
            delete_btn = ttk.Button(btn_frame, text="Delete", 
                                    command=lambda: self._delete_record(table_name), style='Delete.TButton')
            delete_btn.pack(side='left', padx=2)
            
            clear_btn = ttk.Button(btn_frame, text="Clear", 
                                   command=self.form.clear, style='Clear.TButton')
            clear_btn.pack(side='left', padx=2)

            # Create table frame with scrollbar
            table_frame = ttk.Frame(container)
            table_frame.pack(side='left', fill='both', expand=True)

            # Create table with columns
            columns = [col for col in fields.keys() if not col.startswith('_')]
            self.table = DataTable(table_frame, columns)
            self.table.pack(fill='both', expand=True)

            # Bind table selection
            self.table.tree.bind('<<TreeviewSelect>>', lambda e: self._on_select(e, table_name))

            # Initial data load
            self._refresh_table(table_name)

        except Exception as e:
            logging.error(f"Error creating form and table: {e}")
            messagebox.showerror("Error", f"Failed to create form and table: {str(e)}")

    def _refresh_table(self, table_name):
        """Refresh table data"""
        try:
            if not self.table:
                logging.error("Table not initialized")
                return

            # Get fresh data
            records = self.db.get_table_data(table_name)
            if not records:
                self.update_status("No records found", "info")
                self.table.clear()
                return

            # Update table with new data
            self.table.clear()
            self.table.insert_data(records)
            self.update_status(f"Showing {len(records)} records", "info")

        except Exception as e:
            logging.error(f"Error refreshing table: {e}")
            messagebox.showerror("Error", f"Failed to refresh table: {str(e)}")

    def _save_record(self, table_name):
        """Save a new record"""
        try:
            # Validate form data
            data = self.form.get_data()
            if not data:
                return

            # Insert record
            self.db.insert_record(table_name, data)
            
            # Update status and show message
            self.update_status("Record saved successfully", "success")
            
            # Refresh and clear
            self._refresh_table(table_name)
            self.form.clear()
            
        except Exception as e:
            logging.error(f"Error saving record: {e}")
            self.update_status(f"Failed to save record: {str(e)}", "error")

    def _update_record(self, table_name):
        """Update existing record"""
        try:
            # Get selected item
            selection = self.table.tree.selection()
            if not selection:
                self.update_status("Please select a record to update", "warning")
                return

            # Get form data
            data = self.form.get_data()
            if not data:
                return

            # Get the selected record's primary key
            item = selection[0]
            values = self.table.tree.item(item)['values']
            if not values:
                self.update_status("Failed to get record data", "error")
                return

            # Get primary key column
            primary_key = self.db.get_primary_key(table_name)
            if not primary_key:
                self.update_status("Failed to get primary key", "error")
                return

            # Get column names
            columns = self.db.get_table_columns(table_name)
            if not columns:
                self.update_status("Failed to get table columns", "error")
                return

            # Add primary key value to data
            primary_key_index = columns.index(primary_key)
            data[primary_key] = values[primary_key_index]

            # Update record
            self.db.update_record(table_name, data)
            
            # Update status and show message
            self.update_status("Record updated successfully", "success")
            
            # Refresh and clear
            self._refresh_table(table_name)
            self.form.clear()

        except Exception as e:
            logging.error(f"Error updating record: {e}")
            self.update_status(f"Failed to update record: {str(e)}", "error")

    def _delete_record(self, table_name):
        """Delete selected record"""
        try:
            # Get selected item
            selection = self.table.tree.selection()
            if not selection:
                self.update_status("Please select a record to delete", "warning")
                return

            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
                return

            # Get the selected record's primary key value
            item = selection[0]
            values = self.table.tree.item(item)['values']
            if not values:
                self.update_status("Failed to get record data", "error")
                return

            # Get primary key column
            primary_key = self.db.get_primary_key(table_name)
            if not primary_key:
                self.update_status("Failed to get primary key", "error")
                return

            # Get column names to find primary key index
            columns = self.db.get_table_columns(table_name)
            if not columns:
                self.update_status("Failed to get table columns", "error")
                return

            # Get primary key value from values using its index
            primary_key_index = columns.index(primary_key)
            record_id = values[primary_key_index]

            # Delete record
            self.db.delete_record(table_name, record_id)
            
            # Update status
            self.update_status("Record deleted successfully", "success")
            
            # Refresh and clear
            self._refresh_table(table_name)
            self.form.clear()
            
        except Exception as e:
            logging.error(f"Error deleting record: {e}")
            self.update_status(f"Failed to delete record: {str(e)}", "error")

    def _on_select(self, event, table_name):
        """Handle table row selection"""
        try:
            # Get selected item
            selection = self.table.tree.selection()
            if not selection:
                return

            # Get the first selected item
            item = selection[0]
            
            # Get all values for the selected row
            values = self.table.tree.item(item)['values']
            if not values:
                return

            # Get column names
            columns = self.db.get_table_columns(table_name)
            
            # Create dictionary of column names and values
            data = dict(zip(columns, values))
            
            # Set the form data
            self.form.set_data(data)
            
        except Exception as e:
            logging.error(f"Error selecting record: {e}")
            messagebox.showerror("Error", f"Failed to select record: {str(e)}")

    def add_record(self, table_name):
        """Add a new record to the database"""
        try:
            # Get form data
            data = self.form.get_data()
            if not data:
                return
                
            # Insert record
            self.db.insert_record(table_name, data)
            messagebox.showinfo("Success", "Record added successfully")
            
            # Refresh table and clear form
            self._refresh_table(table_name)
            self.form.clear()
            
        except Exception as e:
            logging.error(f"Error adding record: {e}")
            messagebox.showerror("Error", f"Failed to add record: {str(e)}")
            
    def update_record(self, table_name):
        """Update the selected record"""
        try:
            # Get selected record
            selection = self.table.tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a record to update")
                return
                
            # Get form data
            new_data = self.form.get_data()
            if not new_data:
                return
                
            # Update record
            self.db.update_record(table_name, selection, new_data)
            messagebox.showinfo("Success", "Record updated successfully")
            
            # Refresh table and clear form
            self._refresh_table(table_name)
            self.form.clear()
            
        except Exception as e:
            logging.error(f"Error updating record: {e}")
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")
            
    def delete_record(self, table_name):
        """Delete the selected record"""
        try:
            # Get selected record
            selection = self.table.tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a record to delete")
                return
                
            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
                return
                
            # Delete record
            self.db.delete_record(table_name, selection)
            messagebox.showinfo("Success", "Record deleted successfully")
            
            # Refresh table and clear form
            self._refresh_table(table_name)
            self.form.clear()
            
        except Exception as e:
            logging.error(f"Error deleting record: {e}")
            messagebox.showerror("Error", f"Failed to delete record: {str(e)}")
            
    def _on_record_select(self, event):
        """Handle record selection in table"""
        try:
            # Get selected record
            selection = self.table.tree.selection()
            if selection:
                # Populate form with selected record data
                self.form.set_data(self.table.tree.item(selection[0])['values'])
        except Exception as e:
            logging.error(f"Error handling record selection: {e}")

    def refresh_table(self):
        """Refresh the table data"""
        try:
            if self.table and self.current_table:
                data = self.db.get_table_data(self.current_table)
                self.table.load_data(data)
        except Exception as e:
            logging.error(f"Error refreshing table: {e}")
            messagebox.showerror("Error", f"Failed to refresh table: {str(e)}")

    def clear_content(self):
        """Clear all widgets from the content area"""
        if self.content_area:
            for widget in self.content_area.winfo_children():
                widget.destroy()

    def setup_styles(self):
        """Setup custom styles for widgets"""
        style = ttk.Style()
        
        # Configure button layout to show full background
        style.layout('TButton', [
            ('Button.padding', {'children': [
                ('Button.label', {'sticky': 'nswe'})
            ], 'sticky': 'nswe'})
        ])
        
        # Card style
        style.configure('Card.TFrame', background='white')
        
        # Search entry style
        style.configure('Search.TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid',
                       padding=5)
                       
        # Search frame style
        style.configure('Search.TFrame',
                       background='white',
                       relief='flat')
                       
        # Status label style
        style.configure('Status.TLabel',
                       background='white',
                       foreground='#7f8c8d',
                       padding=2)

        # Search button style - Purple
        style.configure('Search.TButton',
                       background='#8e44ad',  
                       foreground='white',
                       padding=(15, 8),
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10),
                       width=8,
                       anchor='center')
        style.map('Search.TButton',
                 background=[('active', '#9b59b6'), ('pressed', '#8e44ad')],
                 foreground=[('pressed', 'white')],
                 relief=[('pressed', 'flat')])

        # Reset button style - Orange
        style.configure('Reset.TButton',
                       background='#d35400',  
                       foreground='white',
                       padding=(15, 8),
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10),
                       width=8,
                       anchor='center')
        style.map('Reset.TButton',
                 background=[('active', '#e67e22'), ('pressed', '#d35400')],
                 foreground=[('pressed', 'white')],
                 relief=[('pressed', 'flat')])

        # Save button style - Vibrant Green
        style.configure('Save.TButton',
                       background='#00b894',  
                       foreground='white',
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'),
                       width=12,
                       anchor='center')
        style.map('Save.TButton',
                 background=[('active', '#00a187'), ('pressed', '#008876')],
                 foreground=[('pressed', 'white')],
                 relief=[('pressed', 'flat')])
                       
        # Update button style - Vibrant Blue
        style.configure('Update.TButton',
                       background='#0984e3',  
                       foreground='white',
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'),
                       width=12,
                       anchor='center')
        style.map('Update.TButton',
                 background=[('active', '#0876cc'), ('pressed', '#0769b5')],
                 foreground=[('pressed', 'white')],
                 relief=[('pressed', 'flat')])

        # Delete button style - Vibrant Red
        style.configure('Delete.TButton',
                       background='#ff4757',  
                       foreground='white',
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'),
                       width=12,
                       anchor='center')
        style.map('Delete.TButton',
                 background=[('active', '#ff3346'), ('pressed', '#ff1f35')],
                 foreground=[('pressed', 'white')],
                 relief=[('pressed', 'flat')])

        # Clear button style - Deep Gray
        style.configure('Clear.TButton',
                       background='#636e72',  
                       foreground='white',
                       padding=(20, 10),
                       relief='flat',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'),
                       width=12,
                       anchor='center')
        style.map('Clear.TButton',
                 background=[('active', '#576165'), ('pressed', '#4b5558')],
                 foreground=[('pressed', 'white')],
                 relief=[('pressed', 'flat')])
        
    def _get_table_icon(self, table_name):
        """Get appropriate icon for table"""
        icons = {
            'patients': '👤',       # Patient icon
            'doctors': '👨‍⚕️',        # Doctor icon
            'appointments': '📅',   # Calendar icon
            'prescriptions': '📋',  # Clipboard icon
            'departments': '🏥',    # Hospital icon
            'medications': '💊',    # Pill icon
            'staff': '👥',          # Multiple people icon
            'rooms': '🚪',          # Door icon
            'bills': '💰',          # Money bag icon
            'inventory': '📦',      # Box icon
            'lab_results': '🔬',    # Microscope icon
            'medical_records': '📄' # Document icon
        }
        return icons.get(table_name.lower(), '📊')  # Default to chart icon if table not found

    def update_status(self, message, status_type="info"):
        """Update status message"""
        try:
            if hasattr(self, 'status_label'):
                color = {
                    "info": "gray",
                    "success": "green",
                    "error": "red",
                    "warning": "orange"
                }.get(status_type, "gray")
                
                self.status_label.configure(text=message, foreground=color)
                
        except Exception as e:
            logging.error(f"Error updating status: {e}")

logging.basicConfig(level=logging.INFO)

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
