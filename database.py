import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import config

class GoogleSheetsDatabase:
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']
        
        try:
            # Authenticate with Google Sheets
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                config.GOOGLE_SHEETS_CREDENTIALS_FILE, self.scope)
            self.client = gspread.authorize(credentials)
            
            # Open the spreadsheet
            self.spreadsheet = self.client.open_by_key(config.SPREADSHEET_ID)
            
            # Initialize worksheets if they don't exist
            self._initialize_worksheets()
            
            print("Successfully connected to Google Sheets!")
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            self.client = None
            self.spreadsheet = None
    
    def _initialize_worksheets(self):
        """Initialize the required worksheets if they don't exist"""
        worksheet_names = [sheet.title for sheet in self.spreadsheet.worksheets()]
        
        # Create patients worksheet if it doesn't exist
        if "Patients" not in worksheet_names:
            patients_sheet = self.spreadsheet.add_worksheet(title="Patients", rows=1000, cols=10)
            patients_sheet.append_row([
                "PatientID", "Name", "Email", "Phone", "DateOfBirth", 
                "Address", "MedicalHistory", "RegisteredDate"
            ])
        
        # Create doctors worksheet if it doesn't exist
        if "Doctors" not in worksheet_names:
            doctors_sheet = self.spreadsheet.add_worksheet(title="Doctors", rows=100, cols=10)
            doctors_sheet.append_row([
                "DoctorID", "Name", "Specialty", "Email", "Phone", "Schedule"
            ])
        
        # Create appointments worksheet if it doesn't exist
        if "Appointments" not in worksheet_names:
            appointments_sheet = self.spreadsheet.add_worksheet(title="Appointments", rows=1000, cols=10)
            appointments_sheet.append_row([
                "AppointmentID", "PatientID", "DoctorID", "Date", "Time", 
                "Status", "Notes", "CreatedAt"
            ])
    
    def add_patient(self, patient_data):
        """Add a new patient to the database"""
        if not self.spreadsheet:
            return False, "Database connection error"
        
        try:
            patients_sheet = self.spreadsheet.worksheet("Patients")
            
            # Check if patient with same email already exists
            existing_emails = patients_sheet.col_values(3)[1:]  # Skip header
            if patient_data["email"] in existing_emails:
                return False, "Patient with this email already exists"
            
            # Generate patient ID (simple implementation)
            all_ids = patients_sheet.col_values(1)[1:]  # Skip header
            new_id = f"P{len(all_ids) + 1:04d}"
            
            # Prepare row data
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                new_id,
                patient_data["name"],
                patient_data["email"],
                patient_data["phone"],
                patient_data["dob"],
                patient_data["address"],
                patient_data["medical_history"],
                now
            ]
            
            # Add the new patient
            patients_sheet.append_row(row_data)
            return True, new_id
        except Exception as e:
            return False, f"Error adding patient: {str(e)}"
    
    def get_all_patients(self):
        """Get all patients from the database"""
        if not self.spreadsheet:
            return []
        
        try:
            patients_sheet = self.spreadsheet.worksheet("Patients")
            records = patients_sheet.get_all_records()
            return records
        except Exception as e:
            print(f"Error getting patients: {e}")
            return []
    
    def get_patient_by_id(self, patient_id):
        """Get a patient by ID"""
        if not self.spreadsheet:
            return None
        
        try:
            patients_sheet = self.spreadsheet.worksheet("Patients")
            patient_data = patients_sheet.get_all_records()
            
            for patient in patient_data:
                if patient["PatientID"] == patient_id:
                    return patient
            
            return None
        except Exception as e:
            print(f"Error getting patient: {e}")
            return None
    
    def add_doctor(self, doctor_data):
        """Add a new doctor to the database"""
        if not self.spreadsheet:
            return False, "Database connection error"
        
        try:
            doctors_sheet = self.spreadsheet.worksheet("Doctors")
            
            # Check if doctor with same email already exists
            existing_emails = doctors_sheet.col_values(4)[1:]  # Skip header
            if doctor_data["email"] in existing_emails:
                return False, "Doctor with this email already exists"
            
            # Generate doctor ID
            all_ids = doctors_sheet.col_values(1)[1:]  # Skip header
            new_id = f"D{len(all_ids) + 1:04d}"
            
            # Prepare row data
            row_data = [
                new_id,
                doctor_data["name"],
                doctor_data["specialty"],
                doctor_data["email"],
                doctor_data["phone"],
                doctor_data["schedule"]
            ]
            
            # Add the new doctor
            doctors_sheet.append_row(row_data)
            return True, new_id
        except Exception as e:
            return False, f"Error adding doctor: {str(e)}"
    
    def get_all_doctors(self):
        """Get all doctors from the database"""
        if not self.spreadsheet:
            return []
        
        try:
            doctors_sheet = self.spreadsheet.worksheet("Doctors")
            records = doctors_sheet.get_all_records()
            return records
        except Exception as e:
            print(f"Error getting doctors: {e}")
            return []
    
    def get_doctors_by_specialty(self, specialty):
        """Get doctors by specialty"""
        if not self.spreadsheet:
            return []
        
        try:
            doctors_sheet = self.spreadsheet.worksheet("Doctors")
            all_doctors = doctors_sheet.get_all_records()
            
            # Filter doctors by specialty
            filtered_doctors = [doc for doc in all_doctors if doc["Specialty"] == specialty]
            return filtered_doctors
        except Exception as e:
            print(f"Error getting doctors by specialty: {e}")
            return []
    
    def book_appointment(self, appointment_data):
        """Book a new appointment"""
        if not self.spreadsheet:
            return False, "Database connection error"
        
        try:
            appointments_sheet = self.spreadsheet.worksheet("Appointments")
            
            # Check if the time slot is available
            existing_appointments = appointments_sheet.get_all_records()
            for appt in existing_appointments:
                if (appt["DoctorID"] == appointment_data["doctor_id"] and
                    appt["Date"] == appointment_data["date"] and
                    appt["Time"] == appointment_data["time"] and
                    appt["Status"] != "Cancelled"):
                    return False, "This time slot is already booked"
            
            # Generate appointment ID
            all_ids = appointments_sheet.col_values(1)[1:]  # Skip header
            new_id = f"A{len(all_ids) + 1:04d}"
            
            # Prepare row data
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                new_id,
                appointment_data["patient_id"],
                appointment_data["doctor_id"],
                appointment_data["date"],
                appointment_data["time"],
                "Scheduled",
                appointment_data.get("notes", ""),
                now
            ]
            
            # Add the new appointment
            appointments_sheet.append_row(row_data)
            return True, new_id
        except Exception as e:
            return False, f"Error booking appointment: {str(e)}"
    
    def get_patient_appointments(self, patient_id):
        """Get all appointments for a specific patient"""
        if not self.spreadsheet:
            return []
        
        try:
            appointments_sheet = self.spreadsheet.worksheet("Appointments")
            all_appointments = appointments_sheet.get_all_records()
            
            # Filter appointments by patient ID
            patient_appointments = [appt for appt in all_appointments if appt["PatientID"] == patient_id]
            
            # Enrich with doctor information
            doctors = {doc["DoctorID"]: doc for doc in self.get_all_doctors()}
            
            for appt in patient_appointments:
                doctor = doctors.get(appt["DoctorID"], {})
                appt["DoctorName"] = doctor.get("Name", "Unknown")
                appt["Specialty"] = doctor.get("Specialty", "Unknown")
            
            return patient_appointments
        except Exception as e:
            print(f"Error getting patient appointments: {e}")
            return []
    
    def get_doctor_appointments(self, doctor_id, date=None):
        """Get all appointments for a specific doctor, optionally filtered by date"""
        if not self.spreadsheet:
            return []
        
        try:
            appointments_sheet = self.spreadsheet.worksheet("Appointments")
            all_appointments = appointments_sheet.get_all_records()
            
            # Filter appointments by doctor ID and optionally by date
            if date:
                doctor_appointments = [
                    appt for appt in all_appointments 
                    if appt["DoctorID"] == doctor_id and appt["Date"] == date
                ]
            else:
                doctor_appointments = [
                    appt for appt in all_appointments 
                    if appt["DoctorID"] == doctor_id
                ]
            
            # Enrich with patient information
            patients = {pat["PatientID"]: pat for pat in self.get_all_patients()}
            
            for appt in doctor_appointments:
                patient = patients.get(appt["PatientID"], {})
                appt["PatientName"] = patient.get("Name", "Unknown")
                appt["PatientPhone"] = patient.get("Phone", "Unknown")
            
            return doctor_appointments
        except Exception as e:
            print(f"Error getting doctor appointments: {e}")
            return []
    
    def update_appointment_status(self, appointment_id, new_status):
        """Update the status of an appointment"""
        if not self.spreadsheet:
            return False, "Database connection error"
        
        try:
            appointments_sheet = self.spreadsheet.worksheet("Appointments")
            
            # Find the appointment
            all_appointments = appointments_sheet.get_all_records()
            row_idx = None
            
            for idx, appt in enumerate(all_appointments, start=2):  # Start from 2 to account for header row
                if appt["AppointmentID"] == appointment_id:
                    row_idx = idx
                    break
            
            if row_idx is None:
                return False, "Appointment not found"
            
            # Update the status (column 6)
            appointments_sheet.update_cell(row_idx, 6, new_status)
            return True, "Appointment status updated successfully"
        except Exception as e:
            return False, f"Error updating appointment status: {str(e)}"