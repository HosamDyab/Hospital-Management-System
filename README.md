![Screenshot 2024-12-21 082934](https://github.com/user-attachments/assets/8ad95e4e-4205-4ba0-9c71-9dbe16e9ad4a)
![Screenshot 2024-12-21 083045](https://github.com/user-attachments/assets/c4b7a15b-e33d-4fad-a5f7-75e63ea6dcc7)
![Screenshot 2024-12-21 083153](https://github.com/user-attachments/assets/d15c57f6-bdb0-4945-9110-8a83d593138a)
![Screenshot 2024-12-21 083342](https://github.com/user-attachments/assets/fe087340-d0b4-486b-b862-de7e9d9d764a)
![Screenshot 2024-12-21 083452](https://github.com/user-attachments/assets/a0df1724-a24f-40c5-9b01-d598f3950bfe)
![Screenshot 2024-12-21 083606](https://github.com/user-attachments/assets/8686534c-6474-4fc4-b392-2d056a0c0a45)
![Screenshot 2024-12-21 083719](https://github.com/user-attachments/assets/553a460b-f7b2-461f-9e9e-141ddd04f821)
![Screenshot 2024-12-21 083828](https://github.com/user-attachments/assets/b10a91d1-319d-44a3-af51-68f2d3903620)
![Screenshot 2024-12-21 083856](https://github.com/user-attachments/assets/da3c1575-c1e7-4e3d-be81-152beb55c5aa)


# Hospital Management System

A modern and user-friendly hospital management system built with Python and Tkinter. This application helps manage patients, doctors, appointments, and other hospital-related data efficiently.

## Features

- Modern and intuitive user interface
- Patient management
- Doctor management
- Appointment scheduling
- Billing system
- Department management
- Staff management
- Room management
- Dependents tracking
- Advanced search and filtering
- Secure database operations
- Inventory management

## Requirements

- Python 3.9 or higher
- MySQL 8.0 or higher
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up the MySQL database:
- Create a new MySQL database
- Update the database configuration in `config/database.py`
- Run the SQL script in `database/init_database.sql`

4. Run the application:
```bash
python run.py
```

## Project Structure

- `assets/` - Contains application assets like images
- `config/` - Configuration files
- `database/` - Database related files and SQL scripts
- `src/` - Source code
  - `app.py` - Main application window
  - `dashboard.py` - Dashboard interface
  - `table_view.py` - Data table views
- `ui/` - User interface components
- `run.py` - Application entry point

## Configuration

1. Database Configuration (`config/database.py`):
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'hospital_management_system'
}
```

## Usage

1. Start the application using `python run.py`
2. Use the sidebar to navigate between different sections
3. Use the search and filter options to find specific records
4. Add, edit, or delete records using the form interface
5. View and manage relationships between different entities

## Security

- Password fields are properly handled
- Database connections are pooled and managed securely
- Input validation and sanitization
- Error handling and logging

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References & Resources Used

### Core Libraries
1. **Tkinter**
   - Python's standard GUI library
   - Used for: Main application interface
   - Documentation: [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)

2. **MySQL Connector/Python (8.0.33)**
   - Used for: Database connectivity and operations
   - Documentation: [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)

3. **Pillow (9.5.0)**
   - Used for: Image handling and processing
   - Documentation: [Pillow Documentation](https://pillow.readthedocs.io/)

4. **tkcalendar (1.6.1)**
   - Used for: Calendar widget in appointment scheduling
   - Documentation: [tkcalendar Documentation](https://tkcalendar.readthedocs.io/)

### Security & Authentication
1. **python-dotenv (1.0.0)**
   - Used for: Managing environment variables and configuration
   - Documentation: [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

2. **cryptography (41.0.1)**
   - Used for: Data encryption and security
   - Documentation: [cryptography Documentation](https://cryptography.io/en/latest/)

3. **bcrypt (4.0.1)**
   - Used for: Password hashing
   - Documentation: [bcrypt Documentation](https://pypi.org/project/bcrypt/)

### Data Processing & Reporting
1. **pandas (2.0.3)**
   - Used for: Data manipulation and analysis
   - Documentation: [pandas Documentation](https://pandas.pydata.org/docs/)

2. **openpyxl (3.1.2)**
   - Used for: Excel file handling
   - Documentation: [openpyxl Documentation](https://openpyxl.readthedocs.io/)

3. **reportlab (4.0.4)**
   - Used for: PDF report generation
   - Documentation: [reportlab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

4. **python-dateutil (2.8.2)**
   - Used for: Date and time handling
   - Documentation: [dateutil Documentation](https://dateutil.readthedocs.io/)

### Design Resources Used
1. **Color Scheme**
   - Google Material Design Colors
   - Reference: [Material Design Color System](https://material.io/design/color/the-color-system.html)

2. **Icons and UI Elements**
   - Material Design Icons
   - Reference: [Material Design Icons](https://material.io/resources/icons/)

3. **Font Families**
   - Segoe UI (Primary font)
   - Consolas (Monospace font for time display)
   - Reference: [Microsoft Typography](https://docs.microsoft.com/en-us/typography/)

### Technical References
1. **Database Design**
   - MySQL Documentation: [MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
   - Database normalization: [Database Normalization Basics](https://www.studytonight.com/dbms/database-normalization.php)

2. **Python Best Practices**
   - PEP 8 Style Guide: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
   - Clean Code principles: [Clean Code in Python](https://github.com/zedr/clean-code-python)

3. **Security Guidelines**
   - OWASP Security Guidelines: [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
   - Python Security: [Python Security Guide](https://python-security.readthedocs.io/)

### Healthcare Management References
1. **Hospital Information System Standards**
   - HL7 Standards: [Health Level Seven International](http://www.hl7.org/)
   - HIPAA Guidelines: [HIPAA Journal](https://www.hipaajournal.com/)

2. **Healthcare Management Best Practices**
   - WHO Guidelines: [WHO Digital Health](https://www.who.int/health-topics/digital-health)
   - Healthcare Information Management: [HIMSS](https://www.himss.org/)

### UI/UX Design Principles
1. **Modern UI Design**
   - Material Design Guidelines: [Material Design](https://material.io/design)
   - Nielsen Norman Group: [UX Research Articles](https://www.nngroup.com/articles/)

2. **Healthcare UI/UX**
   - Healthcare Design Magazine: [Healthcare Design](https://healthcaredesignmagazine.com/)
   - HIMSS UX Guide: [HIMSS UX Resources](https://www.himss.org/resources-healthcare-user-experience)

### Additional Resources
1. **Project Management**
   - Agile Methodology: [Agile Alliance](https://www.agilealliance.org/)
   - Software Development Life Cycle: [SDLC Models](https://www.tutorialspoint.com/sdlc/sdlc_overview.htm)

2. **Version Control**
   - Git Documentation: [Git SCM](https://git-scm.com/doc)
   - GitHub Guides: [GitHub Guides](https://guides.github.com/)

3. **Testing Resources**
   - Python unittest: [unittest Documentation](https://docs.python.org/3/library/unittest.html)
   - Software Testing Fundamentals: [Software Testing Help](https://www.softwaretestinghelp.com/)
