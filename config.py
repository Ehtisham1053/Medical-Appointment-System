import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
APP_NAME = "Medical Appointment Booking System"
VERSION = "1.0.0"

# Google Sheets configuration
# The user will need to provide these values in a .env file
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Appointment settings
WORKING_HOURS = {
    "start": 9,  # 9 AM
    "end": 17,   # 5 PM
}
APPOINTMENT_DURATION = 30  # minutes

# Available specialties
SPECIALTIES = [
    "General Medicine",
    "Cardiology",
    "Dermatology",
    "Orthopedics",
    "Pediatrics",
    "Neurology",
    "Gynecology",
    "Ophthalmology",
    "Dentistry",
    "Psychiatry"
]

# Admin credentials (in a real app, use a more secure approach)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")