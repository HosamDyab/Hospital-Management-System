-- Create a new database
CREATE DATABASE IF NOT EXISTS hospital_management_system;

-- Use the new database
USE hospital_management_system;

-- Table for DEPARTMENT (must come before DOCTOR and ROOM)
CREATE TABLE IF NOT EXISTS DEPARTMENT (
   DEPARTMENT_ID varchar(20) NOT NULL,                                                    
   DEPARTMENT_NAME varchar(100) NOT NULL,                                           
   HEAD_OF_DEPARTMENT varchar(20),
   LOCATION varchar(50),
   PRIMARY KEY (DEPARTMENT_ID)
);

-- Table for STAFF (it is needed before other tables)
CREATE TABLE IF NOT EXISTS STAFF ( 
   STAFF_ID varchar(20) NOT NULL, 
   STAFF_NAME varchar(100) NOT NULL, 
   ROLE varchar(20) NOT NULL,                                                
   SHIFT varchar(20) NOT NULL,                                               
   CONTACT_INFO varchar(255),
   DEPARTMENT_ID VARCHAR(20), -- Foreign key to DEPARTMENT table
   PRIMARY KEY (STAFF_ID), 
   FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENT (DEPARTMENT_ID)
          ON DELETE SET NULL
          ON UPDATE CASCADE
);

-- Table for DOCTOR (must come after DEPARTMENT and STAFF)
CREATE TABLE IF NOT EXISTS DOCTOR ( 
   DOCTOR_ID varchar(20) NOT NULL, 
   DOCTOR_NAME varchar(100) NOT NULL, 
   SPECIALIZATION varchar(100) NOT NULL, 
   CONTACT_INFO varchar(255),                                       
   DEPARTMENT_ID VARCHAR(20),                              
   STAFF_ID VARCHAR(20),  -- Foreign key to STAFF table
   SUPER_ID VARCHAR(20),  -- Self-referencing for supervisor
   PRIMARY KEY (DOCTOR_ID), 
   FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENT(DEPARTMENT_ID)
          ON DELETE SET NULL
          ON UPDATE CASCADE,
   FOREIGN KEY (SUPER_ID) REFERENCES DOCTOR(DOCTOR_ID)
          ON DELETE SET NULL
          ON UPDATE CASCADE,
   FOREIGN KEY (STAFF_ID) REFERENCES STAFF(STAFF_ID)
          ON DELETE SET NULL
          ON UPDATE CASCADE
);

-- Table for ROOM (needs DEPARTMENT table already created for foreign key reference)
CREATE TABLE IF NOT EXISTS ROOM (
    ROOM_ID VARCHAR(20) NOT NULL, 
    ROOM_TYPE VARCHAR(20) NOT NULL,                                 
    CAPACITY INT NOT NULL, 
    OCCUPIED INT NOT NULL DEFAULT 0,                                  
    DEPARTMENT_ID VARCHAR(20), -- Foreign key to DEPARTMENT table
    PRIMARY KEY (ROOM_ID),
    FOREIGN KEY (DEPARTMENT_ID) REFERENCES DEPARTMENT(DEPARTMENT_ID) 
          ON DELETE CASCADE
          ON UPDATE CASCADE
);

-- Table for PATIENT (must come before APPOINTMENT as APPOINTMENT references it)
CREATE TABLE IF NOT EXISTS PATIENT (
    PATIENT_ID VARCHAR(20) NOT NULL, 
    PATIENT_NAME VARCHAR(100) NOT NULL, 
    AGE INT NOT NULL, 
    ADDRESS VARCHAR(255) NOT NULL, 
    PHONE VARCHAR(15) NOT NULL,                                       
    ROOM_ID VARCHAR(20),  -- Foreign key to ROOM table
    GENDER VARCHAR(10) NOT NULL, 
    DATE datetime,
    DOCTOR_ID VARCHAR(20),  -- Foreign key to DOCTOR table
    PRIMARY KEY (PATIENT_ID),
    FOREIGN KEY (DOCTOR_ID) REFERENCES DOCTOR(DOCTOR_ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
    FOREIGN KEY (ROOM_ID) REFERENCES ROOM(ROOM_ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

-- Table for APPOINTMENT (now that PATIENT exists, we can reference it)
CREATE TABLE IF NOT EXISTS APPOINTMENT ( 
   APPOINTMENT_ID varchar(20) NOT NULL, 
   PATIENT_ID varchar(20) NOT NULL, 
   DOCTOR_ID varchar(20) NOT NULL, 
   APPOINTMENT_DATE datetime NOT NULL, 
   STATUS varchar(20) NOT NULL DEFAULT 'Scheduled',      
   NOTES text,                                                                   
   PRIMARY KEY (APPOINTMENT_ID), 
   FOREIGN KEY (PATIENT_ID) REFERENCES PATIENT(PATIENT_ID) 
   ON DELETE CASCADE 
   ON UPDATE CASCADE, 
   FOREIGN KEY (DOCTOR_ID) REFERENCES DOCTOR(DOCTOR_ID) 
   ON DELETE CASCADE 
   ON UPDATE CASCADE 
);

-- Table for BILLING (references PATIENT table)
CREATE TABLE IF NOT EXISTS BILLING (
    BILL_ID VARCHAR(20) NOT NULL, 
    PATIENT_ID VARCHAR(20) NOT NULL, 
    AMOUNT DECIMAL(10, 3) NOT NULL, 
    PAYMENT_STATUS VARCHAR(20) NOT NULL DEFAULT 'Unpaid',  
    BILL_DATE DATETIME NOT NULL,
    PRIMARY KEY (BILL_ID), 
    FOREIGN KEY (PATIENT_ID) REFERENCES PATIENT(PATIENT_ID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Table for DEPENDENTS (references PATIENT table)
CREATE TABLE IF NOT EXISTS DEPENDENTS (
   DEPENDENT_ID varchar(20) NOT NULL,
   PATIENT_ID varchar(20) NOT NULL,
   NAME varchar(100) NOT NULL,
   RELATIONSHIP varchar(50) NOT NULL,
   CONTACT_INFO varchar(255),
   PRIMARY KEY (DEPENDENT_ID),
   FOREIGN KEY (PATIENT_ID) REFERENCES PATIENT(PATIENT_ID)
      ON DELETE CASCADE
      ON UPDATE CASCADE
);

-- Insert sample data only if tables are empty
INSERT IGNORE INTO DEPARTMENT (DEPARTMENT_ID, DEPARTMENT_NAME, HEAD_OF_DEPARTMENT, LOCATION) VALUES
('D001', 'Cardiology', 'Ahmed Al-Masri', 'Building A, Floor 2'),
('D002', 'Neurology', 'Sara El-Sayed', 'Building B, Floor 3'),
('D003', 'Orthopedics', 'Mohamed Taha', 'Building A, Floor 1'),
('D004', 'Pediatrics', 'Laila Hassan', 'Building C, Floor 2'),
('D005', 'Oncology', 'Rania Farouk', 'Building D, Floor 1'),
('D006', 'Dermatology', 'Hossam Ahmed', 'Building B, Floor 1'),
('D007', 'ENT', 'Fatima Nour', 'Building C, Floor 3'),
('D008', 'Psychiatry', 'Omar Khalil', 'Building D, Floor 2'),
('D009', 'Radiology', 'Yasmin Samir', 'Building A, Floor 3'),
('D010', 'Emergency', 'Karim Mostafa', 'Building A, Ground Floor');

INSERT IGNORE INTO STAFF (STAFF_ID, STAFF_NAME, ROLE, SHIFT, CONTACT_INFO, DEPARTMENT_ID) VALUES
('S001', 'Amina Ali', 'Nurse', 'Morning', '123456789', 'D001'),
('S002', 'Hassan Zaki', 'Receptionist', 'Afternoon', '987654321', 'D002'),
('S003', 'Mona Yasser', 'Nurse', 'Night', '456123789', 'D003'),
('S004', 'Khaled Hussein', 'Cleaner', 'Morning', '321654987', 'D004'),
('S005', 'Nour Farid', 'Doctor', 'Morning', '852963741', 'D005'),
('S006', 'Zainab Mahmoud', 'Nurse', 'Night', '741852963', 'D006'),
('S007', 'Ahmed Samy', 'Doctor', 'Morning', '963852741', 'D007'),
('S008', 'Mariam Hany', 'Receptionist', 'Afternoon', '159753468', 'D008'),
('S009', 'Youssef Ali', 'Nurse', 'Night', '357159852', 'D009'),
('S010', 'Heba Nabil', 'Doctor', 'Morning', '852741963', 'D010');

INSERT IGNORE INTO DOCTOR (DOCTOR_ID, DOCTOR_NAME, SPECIALIZATION, CONTACT_INFO, DEPARTMENT_ID, STAFF_ID, SUPER_ID) VALUES
('DOC001', 'Dr. John Smith', 'Cardiologist', '123-456-7890', 'D001', 'S001', NULL),
('DOC002', 'Dr. Sarah Johnson', 'Neurologist', '123-456-7891', 'D002', 'S002', 'DOC001'),
('DOC003', 'Dr. Michael Brown', 'Orthopedic', '123-456-7892', 'D003', 'S003', 'DOC001'),
('DOC004', 'Dr. Emily Davis', 'Pediatrician', '123-456-7893', 'D004', 'S004', 'DOC002'),
('DOC005', 'Dr. James Wilson', 'Oncologist', '123-456-7894', 'D005', 'S005', 'DOC002'),
('DOC006', 'Dr. Aisha Hassan', 'Dermatologist', '123-456-7895', 'D006', 'S006', 'DOC003'),
('DOC007', 'Dr. Kamal Adel', 'ENT Specialist', '123-456-7896', 'D007', 'S007', 'DOC003'),
('DOC008', 'Dr. Noha Saber', 'Psychiatrist', '123-456-7897', 'D008', 'S008', 'DOC004'),
('DOC009', 'Dr. Tamer Hosny', 'Radiologist', '123-456-7898', 'D009', 'S009', 'DOC004'),
('DOC010', 'Dr. Dina Farid', 'Emergency Medicine', '123-456-7899', 'D010', 'S010', 'DOC005');

INSERT IGNORE INTO ROOM (ROOM_ID, ROOM_TYPE, CAPACITY, OCCUPIED, DEPARTMENT_ID) VALUES
('R001', 'ICU', 4, 2, 'D001'),
('R002', 'General', 2, 1, 'D002'),
('R003', 'Private', 1, 1, 'D003'),
('R004', 'Pediatrics', 3, 1, 'D004'),
('R005', 'Oncology', 2, 2, 'D005'),
('R006', 'Private', 1, 0, 'D006'),
('R007', 'General', 3, 2, 'D007'),
('R008', 'ICU', 2, 1, 'D008'),
('R009', 'General', 4, 3, 'D009'),
('R010', 'Emergency', 5, 2, 'D010');

INSERT IGNORE INTO PATIENT (PATIENT_ID, PATIENT_NAME, AGE, ADDRESS, PHONE, ROOM_ID, GENDER, DATE, DOCTOR_ID) VALUES
('P001', 'Alice Johnson', 45, '123 Main St', '555-0101', 'R001', 'Female', '2024-01-15 10:00:00', 'DOC001'),
('P002', 'Bob Wilson', 62, '456 Oak Ave', '555-0102', 'R002', 'Male', '2024-01-16 11:30:00', 'DOC002'),
('P003', 'Carol Smith', 35, '789 Pine St', '555-0103', 'R003', 'Female', '2024-01-17 14:15:00', 'DOC003'),
('P004', 'David Brown', 8, '321 Elm St', '555-0104', 'R004', 'Male', '2024-01-18 09:45:00', 'DOC004'),
('P005', 'Eve Davis', 55, '654 Maple St', '555-0105', 'R005', 'Female', '2024-01-19 16:20:00', 'DOC005'),
('P006', 'Hassan Ahmed', 28, '789 Cedar St', '555-0106', 'R006', 'Male', '2024-01-20 13:30:00', 'DOC006'),
('P007', 'Fatima Omar', 42, '456 Birch St', '555-0107', 'R007', 'Female', '2024-01-21 10:15:00', 'DOC007'),
('P008', 'Mahmoud Samy', 33, '123 Walnut St', '555-0108', 'R008', 'Male', '2024-01-22 15:45:00', 'DOC008'),
('P009', 'Nadia Kamal', 50, '987 Pine St', '555-0109', 'R009', 'Female', '2024-01-23 11:20:00', 'DOC009'),
('P010', 'Yasser Hany', 65, '654 Oak St', '555-0110', 'R010', 'Male', '2024-01-24 14:00:00', 'DOC010');

INSERT IGNORE INTO APPOINTMENT (APPOINTMENT_ID, PATIENT_ID, DOCTOR_ID, APPOINTMENT_DATE, STATUS, NOTES) VALUES
('A001', 'P001', 'DOC001', '2024-01-20 09:00:00', 'Scheduled', 'Regular checkup'),
('A002', 'P002', 'DOC002', '2024-01-21 10:30:00', 'Scheduled', 'Follow-up'),
('A003', 'P003', 'DOC003', '2024-01-22 14:00:00', 'Scheduled', 'Initial consultation'),
('A004', 'P004', 'DOC004', '2024-01-23 11:15:00', 'Scheduled', 'Vaccination'),
('A005', 'P005', 'DOC005', '2024-01-24 15:45:00', 'Scheduled', 'Treatment review'),
('A006', 'P006', 'DOC006', '2024-01-25 13:30:00', 'Scheduled', 'Skin examination'),
('A007', 'P007', 'DOC007', '2024-01-26 10:45:00', 'Scheduled', 'Throat infection'),
('A008', 'P008', 'DOC008', '2024-01-27 15:00:00', 'Scheduled', 'Therapy session'),
('A009', 'P009', 'DOC009', '2024-01-28 11:30:00', 'Scheduled', 'X-ray review'),
('A010', 'P010', 'DOC010', '2024-01-29 14:15:00', 'Scheduled', 'Emergency consultation');

INSERT IGNORE INTO BILLING (BILL_ID, PATIENT_ID, AMOUNT, PAYMENT_STATUS, BILL_DATE) VALUES
('B001', 'P001', 500.00, 'Paid', '2024-01-15 15:00:00'),
('B002', 'P002', 1200.00, 'Pending', '2024-01-16 16:30:00'),
('B003', 'P003', 800.00, 'Paid', '2024-01-17 17:45:00'),
('B004', 'P004', 300.00, 'Pending', '2024-01-18 12:15:00'),
('B005', 'P005', 1500.00, 'Paid', '2024-01-19 18:00:00'),
('B006', 'P006', 400.00, 'Pending', '2024-01-20 14:30:00'),
('B007', 'P007', 600.00, 'Paid', '2024-01-21 11:45:00'),
('B008', 'P008', 900.00, 'Pending', '2024-01-22 16:15:00'),
('B009', 'P009', 700.00, 'Paid', '2024-01-23 13:00:00'),
('B010', 'P010', 1000.00, 'Pending', '2024-01-24 15:30:00');

INSERT IGNORE INTO DEPENDENTS (DEPENDENT_ID, PATIENT_ID, NAME, RELATIONSHIP, CONTACT_INFO) VALUES
('DEP001', 'P001', 'John Johnson', 'Son', '555-0201'),
('DEP002', 'P002', 'Mary Wilson', 'Daughter', '555-0202'),
('DEP003', 'P003', 'Tom Smith', 'Spouse', '555-0203'),
('DEP004', 'P004', 'Sarah Brown', 'Mother', '555-0204'),
('DEP005', 'P005', 'Mike Davis', 'Brother', '555-0205'),
('DEP006', 'P006', 'Laila Ahmed', 'Sister', '555-0206'),
('DEP007', 'P007', 'Karim Omar', 'Son', '555-0207'),
('DEP008', 'P008', 'Nour Samy', 'Daughter', '555-0208'),
('DEP009', 'P009', 'Ahmed Kamal', 'Spouse', '555-0209'),
('DEP010', 'P010', 'Mona Hany', 'Wife', '555-0210');
