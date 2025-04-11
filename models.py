from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Dict, Optional

@dataclass
class Patient:
    """Patient data model"""
    id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    dob: str = ""
    address: str = ""
    medical_history: str = ""
    registered_date: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Patient':
        """Create a Patient object from a dictionary"""
        return cls(
            id=data.get("PatientID", ""),
            name=data.get("Name", ""),
            email=data.get("Email", ""),
            phone=data.get("Phone", ""),
            dob=data.get("DateOfBirth", ""),
            address=data.get("Address", ""),
            medical_history=data.get("MedicalHistory", ""),
            registered_date=data.get("RegisteredDate", "")
        )

@dataclass
class Doctor:
    """Doctor data model"""
    id: str = ""
    name: str = ""
    specialty: str = ""
    email: str = ""
    phone: str = ""
    schedule: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Doctor':
        """Create a Doctor object from a dictionary"""
        return cls(
            id=data.get("DoctorID", ""),
            name=data.get("Name", ""),
            specialty=data.get("Specialty", ""),
            email=data.get("Email", ""),
            phone=data.get("Phone", ""),
            schedule=data.get("Schedule", "")
        )

@dataclass
class Appointment:
    """Appointment data model"""
    id: str = ""
    patient_id: str = ""
    doctor_id: str = ""
    date: str = ""
    time: str = ""
    status: str = "Scheduled"
    notes: str = ""
    created_at: str = ""
    
    # Additional fields for display purposes
    patient_name: str = ""
    doctor_name: str = ""
    specialty: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Appointment':
        """Create an Appointment object from a dictionary"""
        return cls(
            id=data.get("AppointmentID", ""),
            patient_id=data.get("PatientID", ""),
            doctor_id=data.get("DoctorID", ""),
            date=data.get("Date", ""),
            time=data.get("Time", ""),
            status=data.get("Status", "Scheduled"),
            notes=data.get("Notes", ""),
            created_at=data.get("CreatedAt", ""),
            patient_name=data.get("PatientName", ""),
            doctor_name=data.get("DoctorName", ""),
            specialty=data.get("Specialty", "")
        )