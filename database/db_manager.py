import mysql.connector
from mysql.connector import Error
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            # Get database configuration from environment variables
            db_config = {
                'host': os.getenv('DB_HOST', '127.0.0.1'),
                'port': int(os.getenv('DB_PORT', '3306')),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'auth_plugin': 'caching_sha2_password',
                'allow_local_infile': True,
                'use_pure': True
            }
            
            # First try to connect without database
            logging.info(f"Attempting to connect to MySQL at {db_config['host']}")
            self.connection = mysql.connector.connect(**db_config)
            
            # Create database if it doesn't exist
            db_name = os.getenv('DB_NAME', 'hospital_management_system')
            self.cursor = self.connection.cursor(dictionary=True)
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            self.cursor.execute(f"USE {db_name}")
            
            logging.info("Successfully connected to the database")
            
            # Initialize database tables
            self._initialize_database()
            
        except Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def _create_database(self):
        """Create the database if it doesn't exist"""
        try:
            # Connect without database selected
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
            }
            
            temp_connection = mysql.connector.connect(**config)
            temp_cursor = temp_connection.cursor()
            
            # Create database
            db_name = os.getenv('DB_NAME', 'hospital_management_system')
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            
            # Close temporary connection
            temp_cursor.close()
            temp_connection.close()
            
            # Now connect with the database
            self.connect()
            
        except Error as e:
            logging.error(f"Error creating database: {e}")
            raise

    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        try:
            # Read SQL file
            sql_file_path = os.path.join(os.path.dirname(__file__), 'init_database.sql')
            if os.path.exists(sql_file_path):
                with open(sql_file_path, 'r') as file:
                    sql_script = file.read()
                
                # Execute the entire script at once
                self.cursor.execute("SET FOREIGN_KEY_CHECKS=0")
                self.cursor.execute(sql_script, multi=True)
                self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                self.connection.commit()
                logging.info("Database tables initialized successfully")
            
        except Error as e:
            logging.error(f"Error initializing database tables: {e}")
            raise

    def disconnect(self):
        """Safely close database connection"""
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                if self.connection.in_transaction:
                    self.connection.rollback()
                self.connection.close()
            logging.info("Database connection closed successfully")
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")

    def execute_query(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            # Check connection and reconnect if needed
            if not self.connection.is_connected():
                self.connection.reconnect()
                self.cursor = self.connection.cursor(dictionary=True)

            # Execute query
            self.cursor.execute(query, params or ())
            logging.info("Query executed successfully")
            return self.cursor
        except Error as e:
            logging.error(f"Query attempt failed: {e}")
            logging.error(f"Query was: {query}")
            if params:
                logging.error(f"Parameters were: {params}")
            raise

    def get_table_fields(self, table_name):
        """Get field information for a table"""
        try:
            query = """
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    CHARACTER_MAXIMUM_LENGTH,
                    COLUMN_KEY,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            self.cursor.execute(query, (table_name,))
            columns = {}
            for row in self.cursor.fetchall():
                columns[row['COLUMN_NAME']] = {
                    'type': row['DATA_TYPE'],
                    'required': row['IS_NULLABLE'] == 'NO',
                    'nullable': row['IS_NULLABLE'] == 'YES',
                    'default': row['COLUMN_DEFAULT'],
                    'max_length': row['CHARACTER_MAXIMUM_LENGTH'],
                    'key': row['COLUMN_KEY'],
                    'auto_increment': row['EXTRA'] == 'auto_increment'
                }
            return columns
        except Error as e:
            logging.error(f"Error getting table fields: {e}")
            raise

    def get_records(self, table_name, conditions=None):
        """Get all records from a table"""
        try:
            query = f"SELECT * FROM {table_name}"
            if conditions:
                query += f" WHERE {conditions}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            logging.error(f"Error getting records: {e}")
            raise

    def insert_record(self, table_name, data):
        """Insert a new record"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, list(data.values()))
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            self.connection.rollback()
            logging.error(f"Error inserting record: {e}")
            raise

    def update_record(self, table_name, data):
        """Update an existing record"""
        try:
            # Get the primary key column name
            primary_key = self.get_primary_key(table_name)
            if not primary_key:
                raise ValueError(f"No primary key found for table {table_name}")

            # Extract primary key value from data
            record_id = data.get(primary_key)
            if not record_id:
                raise ValueError(f"Primary key value not found in data")

            # Remove primary key from update data
            update_data = {k: v for k, v in data.items() if k != primary_key}
            if not update_data:
                raise ValueError("No data to update")

            # Get column types for proper type conversion
            column_types = self.get_table_column_types(table_name)
            
            # Build the SET clause and parameters
            updates = []
            params = []
            
            for key, value in update_data.items():
                updates.append(f"{key} = %s")
                
                # Convert value based on column type
                col_type = column_types.get(key, '').lower()
                if value is None:
                    params.append(None)
                elif 'int' in col_type:
                    params.append(int(value))
                elif 'decimal' in col_type or 'float' in col_type or 'double' in col_type:
                    params.append(float(value))
                elif 'date' in col_type:
                    if isinstance(value, str):
                        params.append(value)
                    else:
                        params.append(value.strftime('%Y-%m-%d'))
                elif 'datetime' in col_type:
                    if isinstance(value, str):
                        params.append(value)
                    else:
                        params.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    params.append(str(value))

            # Add the WHERE clause parameter (record_id)
            params.append(record_id)

            # Construct and execute the query
            set_clause = ', '.join(updates)
            query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s"
            
            self.cursor.execute(query, params)
            self.connection.commit()
            return True

        except Exception as e:
            self.connection.rollback()
            logging.error(f"Error updating record: {e}")
            raise

    def delete_record(self, table_name, record_id):
        """Delete a record"""
        try:
            # Get the primary key column name
            primary_key = self.get_primary_key(table_name)
            if not primary_key:
                raise ValueError(f"No primary key found for table {table_name}")

            # Delete the record
            query = f"DELETE FROM {table_name} WHERE {primary_key} = %s"
            self.cursor.execute(query, (record_id,))
            
            # Commit the changes
            self.connection.commit()
            return True

        except Exception as e:
            # Rollback on error
            self.connection.rollback()
            logging.error(f"Error deleting record: {e}")
            raise

    def get_table_columns(self, table_name):
        """Get column names for a table"""
        try:
            query = """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s 
                ORDER BY ORDINAL_POSITION
            """
            
            if not self.execute_query(query, (table_name,)):
                return []
                
            return [row['COLUMN_NAME'] for row in self.cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Error getting columns for {table_name}: {e}")
            return []

    def get_table_column_types(self, table_name):
        """Get column names and their types for a given table"""
        try:
            query = f"DESCRIBE {table_name}"
            self.execute_query(query)
            columns = self.cursor.fetchall()
            return {col['Field']: col['Type'] for col in columns}  # Return column name to type mapping
        except Exception as e:
            logging.error(f"Error getting column types: {e}")
            return {}

    def get_primary_key(self, table_name):
        """Get the primary key column name for a table"""
        try:
            query = """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
                AND CONSTRAINT_NAME = 'PRIMARY'
            """
            
            if not self.execute_query(query, (table_name,)):
                return None
                
            result = self.cursor.fetchall()
            return result[0]['COLUMN_NAME'] if result else None
            
        except Exception as e:
            logging.error(f"Error getting primary key for {table_name}: {e}")
            return None

    def get_foreign_keys(self, table_name):
        """Get foreign key relationships for a table"""
        try:
            query = """
                SELECT 
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """
            
            if not self.execute_query(query, (table_name,)):
                return {}
                
            foreign_keys = {}
            for row in self.cursor.fetchall():
                foreign_keys[row['COLUMN_NAME']] = {
                    'referenced_table': row['REFERENCED_TABLE_NAME'],
                    'referenced_column': row['REFERENCED_COLUMN_NAME']
                }
            return foreign_keys
            
        except Exception as e:
            logging.error(f"Error getting foreign keys for {table_name}: {e}")
            return {}

    def get_related_records(self, table_name, column_name, value):
        """Get records from a table that reference the given value"""
        try:
            query = f"SELECT * FROM {table_name} WHERE {column_name} = %s"
            
            if not self.execute_query(query, (value,)):
                return []
                
            columns = self.get_table_columns(table_name)
            rows = self.cursor.fetchall()
            
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[col]
                result.append(row_dict)
            return result
            
        except Exception as e:
            logging.error(f"Error getting related records from {table_name}: {e}")
            return []

    def get_table_data(self, table_name, search_term=None):
        """Get all records from a table with optional search"""
        try:
            # Get table columns and their types
            columns = self.get_table_columns(table_name)
            column_types = self.get_table_column_types(table_name)
            
            # Build the query based on table name and search term
            query = f"SELECT * FROM {table_name}"
            params = None
            
            if search_term:
                search_conditions = []
                for col in columns:
                    search_conditions.append(f"CAST({col} AS CHAR) LIKE %s")
                where_clause = " OR ".join(search_conditions)
                query += f" WHERE {where_clause}"
                params = tuple(f"%{search_term}%" for _ in columns)
            
            # Execute query with retry mechanism
            if not self.execute_query(query, params):
                return []
            
            # Convert results to list of dictionaries
            rows = self.cursor.fetchall()
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[col]
                    # Handle different data types
                    if value is not None:
                        col_type = column_types.get(col, '').lower()
                        if 'datetime' in col_type:
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        elif 'date' in col_type:
                            value = value.strftime('%Y-%m-%d')
                        elif 'decimal' in col_type:
                            value = float(value)
                        elif 'int' in col_type:
                            value = int(value)
                    row_dict[col] = value
                result.append(row_dict)
            return result
            
        except Exception as e:
            logging.error(f"Error fetching data from {table_name}: {e}")
            return []

    def count_records(self, table_name, condition=""):
        """Count records in a table with optional condition"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        if condition:
            query += f" {condition}"
        try:
            self.execute_query(query)
            result = self.cursor.fetchone()
            return result['COUNT(*)'] if result else 0
        except Exception as e:
            print(f"Error counting records: {e}")
            return 0

    def get_record_count(self, table_name, condition=""):
        """Get count of records in a table with optional condition"""
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            if condition:
                query += f" {condition}"
            self.execute_query(query)
            result = self.cursor.fetchone()
            return result['COUNT(*)'] if result else 0
        except Exception as e:
            print(f"Error getting record count: {e}")
            return 0

    def get_patient_data(self, search_term=None):
        """Get patient data with dependent count"""
        try:
            # First check connection
            if not self.connection.is_connected():
                logging.info("Reconnecting to database...")
                self.connection.reconnect()
                self.cursor = self.connection.cursor(dictionary=True)
                
            base_query = """
                SELECT 
                    p.PATIENT_ID,
                    p.PATIENT_NAME,
                    p.AGE,
                    p.ADDRESS,
                    p.PHONE,
                    p.ROOM_ID,
                    p.GENDER,
                    p.DATE,
                    p.DOCTOR_ID,
                    COALESCE(COUNT(d.DEPENDENT_ID), 0) as DEPENDENTS_COUNT
                FROM PATIENT p
                LEFT JOIN DEPENDENTS d ON p.PATIENT_ID = d.PATIENT_ID
            """
            
            if search_term:
                base_query += """
                    WHERE (
                        p.PATIENT_ID LIKE %s OR 
                        p.PATIENT_NAME LIKE %s OR 
                        p.PHONE LIKE %s
                    )
                """
                params = tuple(f"%{search_term}%" for _ in range(3))
            else:
                params = None
            
            base_query += " GROUP BY p.PATIENT_ID, p.PATIENT_NAME, p.AGE, p.ADDRESS, p.PHONE, p.ROOM_ID, p.GENDER, p.DATE, p.DOCTOR_ID"
            
            logging.info(f"Executing patient query: {base_query}")
            if params:
                logging.info(f"With parameters: {params}")
            
            if not self.execute_query(base_query, params):
                logging.error("Patient query execution failed")
                return []
                
            result = self.cursor.fetchall()
            logging.info(f"Patient query successful, retrieved {len(result)} records")
            if len(result) > 0:
                logging.info(f"First patient record: {result[0]}")
            return result
            
        except Exception as e:
            logging.error(f"Error in get_patient_data: {e}")
            return []

    def get_dependent_data(self, search_term=None):
        """Get dependent data with patient information"""
        try:
            base_query = """
                SELECT 
                    d.DEPENDENT_ID,
                    d.PATIENT_ID,
                    d.NAME,
                    d.RELATIONSHIP,
                    d.CONTACT_INFO,
                    p.PATIENT_NAME as PATIENT_NAME
                FROM DEPENDENTS d
                LEFT JOIN PATIENT p ON d.PATIENT_ID = p.PATIENT_ID
            """
            
            if search_term:
                base_query += """
                    WHERE (
                        d.DEPENDENT_ID LIKE %s OR 
                        d.NAME LIKE %s OR 
                        p.PATIENT_NAME LIKE %s
                    )
                """
                params = tuple(f"%{search_term}%" for _ in range(3))
            else:
                params = None

            logging.info(f"Executing dependent query: {base_query}")
            if params:
                logging.info(f"With parameters: {params}")

            if not self.execute_query(base_query, params):
                logging.error("Dependent query execution failed")
                return []

            result = self.cursor.fetchall()
            logging.info(f"Dependent query successful, retrieved {len(result)} records")
            if len(result) > 0:
                logging.info(f"First dependent record: {result[0]}")
            return result

        except Exception as e:
            logging.error(f"Error fetching dependent data: {e}")
            return []

    def count_today_appointments(self):
        """Count appointments scheduled for today"""
        return self.get_record_count("APPOINTMENT", "WHERE DATE(date) = CURRENT_DATE")

    def count_available_rooms(self):
        """Count available rooms"""
        return self.get_record_count("ROOM", "WHERE status='Available'")

    def count_pending_bills(self):
        """Count pending bills"""
        return self.get_record_count("BILLING", "WHERE status='Pending'")

    def get_total_revenue(self):
        """Calculate total revenue from paid bills"""
        try:
            self.execute_query("SELECT SUM(amount) FROM BILLING WHERE status='Paid'")
            result = self.cursor.fetchone()
            return float(result['SUM(amount)']) if result and result['SUM(amount)'] else 0.0
        except Exception as e:
            print(f"Error calculating revenue: {e}")
            return 0.0

    def __del__(self):
        """Ensure connection is closed on deletion"""
        self.disconnect()
