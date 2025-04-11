import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import time
import random
from database import GoogleSheetsDatabase
from models import Patient, Doctor, Appointment
from utils import (
    validate_email, validate_phone, validate_date, generate_time_slots,
    calculate_age, format_date_for_display, get_next_available_dates,
    is_valid_password, sanitize_input
)
import config

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'
if 'db' not in st.session_state:
    st.session_state.db = GoogleSheetsDatabase()

# Set page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
    }
    .warning-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #FFC107;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #F44336;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
    .appointment-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #757575;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def show_login_page():
    """Show the login page"""
    st.markdown('<h2 class="sub-header">Login</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### Patient Login")
        email = st.text_input("Email", key="patient_email")
        password = st.text_input("Password", type="password", key="patient_password")
        
        if st.button("Login as Patient"):
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                # In a real app, you would verify against hashed passwords in the database
                # For demo purposes, we'll just check if the patient exists
                patients = st.session_state.db.get_all_patients()
                patient_found = False
                
                for patient in patients:
                    if patient["Email"] == email:
                        patient_found = True
                        st.session_state.logged_in = True
                        st.session_state.user_type = "patient"
                        st.session_state.user_id = patient["PatientID"]
                        st.session_state.user_name = patient["Name"]
                        st.session_state.current_page = "dashboard"
                        st.success("Login successful!")
                        time.sleep(1)
                        st.experimental_rerun()
                        break
                
                if not patient_found:
                    st.error("Invalid email or password")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### Doctor Login")
        doctor_email = st.text_input("Email", key="doctor_email")
        doctor_password = st.text_input("Password", type="password", key="doctor_password")
        
        if st.button("Login as Doctor"):
            if not doctor_email or not doctor_password:
                st.error("Please enter both email and password")
            else:
                # In a real app, you would verify against hashed passwords in the database
                # For demo purposes, we'll just check if the doctor exists
                doctors = st.session_state.db.get_all_doctors()
                doctor_found = False
                
                for doctor in doctors:
                    if doctor["Email"] == doctor_email:
                        doctor_found = True
                        st.session_state.logged_in = True
                        st.session_state.user_type = "doctor"
                        st.session_state.user_id = doctor["DoctorID"]
                        st.session_state.user_name = doctor["Name"]
                        st.session_state.current_page = "dashboard"
                        st.success("Login successful!")
                        time.sleep(1)
                        st.experimental_rerun()
                        break
                
                if not doctor_found:
                    st.error("Invalid email or password")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("Don't have an account? Go to the Register page to create one.")

def show_registration_page():
    """Show the registration page"""
    st.markdown('<h2 class="sub-header">Patient Registration</h2>', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Phone Number*")
            dob = st.date_input("Date of Birth*", min_value=datetime(1900, 1, 1), max_value=datetime.now())
        
        with col2:
            address = st.text_area("Address*")
            medical_history = st.text_area("Medical History (Optional)")
            password = st.text_input("Password*", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
        
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            # Validate inputs
            if not name or not email or not phone or not address or not password:
                st.error("Please fill in all required fields")
            elif not validate_email(email):
                st.error("Please enter a valid email address")
            elif not validate_phone(phone):
                st.error("Please enter a valid 10-digit phone number")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif not is_valid_password(password):
                st.error("Password must be at least 8 characters with at least one uppercase letter, one lowercase letter, and one digit")
            else:
                # Sanitize inputs
                name = sanitize_input(name)
                email = sanitize_input(email)
                phone = sanitize_input(phone)
                address = sanitize_input(address)
                medical_history = sanitize_input(medical_history)
                
                # Format date of birth
                dob_str = dob.strftime("%Y-%m-%d")
                
                # Create patient data
                patient_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "dob": dob_str,
                    "address": address,
                    "medical_history": medical_history
                }
                
                # Add patient to database
                success, result = st.session_state.db.add_patient(patient_data)
                
                if success:
                    st.success(f"Registration successful! Your patient ID is {result}")
                    st.info("You can now login with your email and password")
                else:
                    st.error(f"Registration failed: {result}")

def show_admin_login_page():
    """Show the admin login page"""
    st.markdown('<h2 class="sub-header">Admin Login</h2>', unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login as Admin"):
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            # Set both admin_logged_in and logged_in to True
            st.session_state.admin_logged_in = True
            st.session_state.logged_in = True
            st.session_state.user_type = "admin"
            st.session_state.user_id = "admin_id"
            st.session_state.user_name = "Admin User"
            st.session_state.current_page = "dashboard"
            st.success("Admin login successful!")
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("Invalid admin credentials")

def show_patient_dashboard():
    """Show the patient dashboard"""
    st.markdown('<h2 class="sub-header">Patient Dashboard</h2>', unsafe_allow_html=True)
    
    # Get patient data
    patient = st.session_state.db.get_patient_by_id(st.session_state.user_id)
    
    if not patient:
        st.error("Could not retrieve patient information")
        return
    
    # Get upcoming appointments
    appointments = st.session_state.db.get_patient_appointments(st.session_state.user_id)
    upcoming_appointments = [appt for appt in appointments if appt["Status"] == "Scheduled" and datetime.strptime(appt["Date"], "%Y-%m-%d") >= datetime.now()]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### Personal Information")
        st.write(f"**Name:** {patient['Name']}")
        st.write(f"**Email:** {patient['Email']}")
        st.write(f"**Phone:** {patient['Phone']}")
        
        if patient['DateOfBirth']:
            age = calculate_age(patient['DateOfBirth'])
            st.write(f"**Age:** {age} years")
        
        st.write(f"**Address:** {patient['Address']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### Upcoming Appointments")
        
        if upcoming_appointments:
            for appt in upcoming_appointments[:3]:  # Show only the next 3 appointments
                st.markdown(f"""
                <div class="appointment-card">
                    <strong>Date:</strong> {format_date_for_display(appt['Date'])}<br>
                    <strong>Time:</strong> {appt['Time']}<br>
                    <strong>Doctor:</strong> Dr. {appt['DoctorName']}<br>
                    <strong>Specialty:</strong> {appt['Specialty']}
                </div>
                """, unsafe_allow_html=True)
            
            if len(upcoming_appointments) > 3:
                st.info(f"You have {len(upcoming_appointments) - 3} more upcoming appointments. View all in 'My Appointments'.")
        else:
            st.write("No upcoming appointments.")
            st.button("Book an Appointment", on_click=lambda: st.session_state.update({"current_page": "book_appointment"}))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Book New Appointment"):
            st.session_state.current_page = "book_appointment"
            st.experimental_rerun()
    
    with col2:
        if st.button("View All Appointments"):
            st.session_state.current_page = "my_appointments"
            st.experimental_rerun()
    
    with col3:
        if st.button("Update Profile"):
            st.session_state.current_page = "my_profile"
            st.experimental_rerun()
    
    # Health tips
    st.markdown("### Health Tips")
    health_tips = [
        "Stay hydrated by drinking at least 8 glasses of water daily.",
        "Regular exercise can help reduce stress and improve your mood.",
        "Aim for 7-9 hours of sleep each night for optimal health.",
        "Include a variety of fruits and vegetables in your diet for essential nutrients.",
        "Regular check-ups can help detect health issues early."
    ]
    tip_index = random.randint(0, len(health_tips) - 1)
    st.markdown(f'<div class="success-box">💡 {health_tips[tip_index]}</div>', unsafe_allow_html=True)

def show_book_appointment_page():
    """Show the book appointment page"""
    st.markdown('<h2 class="sub-header">Book an Appointment</h2>', unsafe_allow_html=True)
    
    # Step 1: Select specialty
    st.markdown("### Step 1: Select Medical Specialty")
    specialty = st.selectbox("Choose a specialty", config.SPECIALTIES)
    
    # Step 2: Select doctor
    st.markdown("### Step 2: Select Doctor")
    doctors = st.session_state.db.get_doctors_by_specialty(specialty)
    
    if not doctors:
        st.warning(f"No doctors available for {specialty}. Please select another specialty.")
        return
    
    doctor_options = [f"Dr. {doc['Name']} - {doc['Specialty']}" for doc in doctors]
    selected_doctor_index = st.selectbox("Choose a doctor", range(len(doctor_options)), format_func=lambda x: doctor_options[x])
    selected_doctor = doctors[selected_doctor_index]
    
    # Step 3: Select date
    st.markdown("### Step 3: Select Date")
    available_dates = get_next_available_dates(14)  # Get dates for the next 2 weeks
    selected_date = st.selectbox("Choose a date", available_dates, format_func=format_date_for_display)
    
    # Step 4: Select time
    st.markdown("### Step 4: Select Time")
    
    # Get doctor's existing appointments for the selected date
    doctor_appointments = st.session_state.db.get_doctor_appointments(selected_doctor["DoctorID"], selected_date)
    booked_times = [appt["Time"] for appt in doctor_appointments if appt["Status"] != "Cancelled"]
    
    # Generate available time slots
    all_time_slots = generate_time_slots(
        config.WORKING_HOURS["start"], 
        config.WORKING_HOURS["end"], 
        config.APPOINTMENT_DURATION
    )
    
    # Filter out booked times
    available_time_slots = [slot for slot in all_time_slots if slot not in booked_times]
    
    if not available_time_slots:
        st.warning("No available time slots for the selected date. Please choose another date.")
        return
    
    selected_time = st.selectbox("Choose a time", available_time_slots)
    
    # Step 5: Additional notes
    st.markdown("### Step 5: Additional Information")
    notes = st.text_area("Notes for the doctor (optional)", max_chars=500)
    
    # Confirm booking
    if st.button("Book Appointment"):
        # Create appointment data
        appointment_data = {
            "patient_id": st.session_state.user_id,
            "doctor_id": selected_doctor["DoctorID"],
            "date": selected_date,
            "time": selected_time,
            "notes": notes
        }
        
        # Book appointment
        success, result = st.session_state.db.book_appointment(appointment_data)
        
        if success:
            st.success(f"Appointment booked successfully! Your appointment ID is {result}")
            st.markdown(f"""
            <div class="success-box">
                <h3>Appointment Details</h3>
                <p><strong>Doctor:</strong> Dr. {selected_doctor['Name']}</p>
                <p><strong>Specialty:</strong> {selected_doctor['Specialty']}</p>
                <p><strong>Date:</strong> {format_date_for_display(selected_date)}</p>
                <p><strong>Time:</strong> {selected_time}</p>
                <p><strong>Appointment ID:</strong> {result}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Failed to book appointment: {result}")

def show_my_appointments_page():
    """Show the patient's appointments page"""
    st.markdown('<h2 class="sub-header">My Appointments</h2>', unsafe_allow_html=True)
    
    # Get all appointments for the patient
    appointments = st.session_state.db.get_patient_appointments(st.session_state.user_id)
    
    if not appointments:
        st.info("You don't have any appointments yet.")
        if st.button("Book an Appointment"):
            st.session_state.current_page = "book_appointment"
            st.experimental_rerun()
        return
    
    # Filter options
    st.markdown("### Filter Appointments")
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["Scheduled", "Completed", "Cancelled"],
            default=["Scheduled"]
        )
    
    with col2:
        date_filter = st.radio(
            "Filter by Date",
            ["All", "Upcoming", "Past"]
        )
    
    # Apply filters
    filtered_appointments = []
    today = datetime.now().date()
    
    for appt in appointments:
        appt_date = datetime.strptime(appt["Date"], "%Y-%m-%d").date()
        
        # Apply status filter
        if appt["Status"] not in status_filter:
            continue
        
        # Apply date filter
        if date_filter == "Upcoming" and appt_date < today:
            continue
        if date_filter == "Past" and appt_date >= today:
            continue
        
        filtered_appointments.append(appt)
    
    # Sort appointments by date (newest first)
    filtered_appointments.sort(key=lambda x: (x["Date"], x["Time"]), reverse=(date_filter == "Past"))
    
    # Display appointments
    st.markdown("### Appointment List")
    
    if not filtered_appointments:
        st.info("No appointments match your filters.")
        return
    
    for appt in filtered_appointments:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="appointment-card">
                <h4>Appointment on {format_date_for_display(appt['Date'])} at {appt['Time']}</h4>
                <p><strong>Doctor:</strong> Dr. {appt['DoctorName']}</p>
                <p><strong>Specialty:</strong> {appt['Specialty']}</p>
                <p><strong>Status:</strong> {appt['Status']}</p>
                <p><strong>Appointment ID:</strong> {appt['AppointmentID']}</p>
                {f"<p><strong>Notes:</strong> {appt['Notes']}</p>" if appt['Notes'] else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Only allow cancellation for upcoming scheduled appointments
            appt_date = datetime.strptime(appt["Date"], "%Y-%m-%d").date()
            if appt["Status"] == "Scheduled" and appt_date >= today:
                if st.button("Cancel", key=f"cancel_{appt['AppointmentID']}"):
                    success, message = st.session_state.db.update_appointment_status(appt['AppointmentID'], "Cancelled")
                    if success:
                        st.success("Appointment cancelled successfully!")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error(f"Failed to cancel appointment: {message}")

def show_patient_profile_page():
    """Show the patient profile page"""
    st.markdown('<h2 class="sub-header">My Profile</h2>', unsafe_allow_html=True)
    
    # Get patient data
    patient = st.session_state.db.get_patient_by_id(st.session_state.user_id)
    
    if not patient:
        st.error("Could not retrieve patient information")
        return
    
    # Display current profile
    st.markdown("### Current Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {patient['Name']}")
        st.write(f"**Email:** {patient['Email']}")
        st.write(f"**Phone:** {patient['Phone']}")
        st.write(f"**Date of Birth:** {patient['DateOfBirth']}")
    
    with col2:
        st.write(f"**Address:** {patient['Address']}")
        st.write(f"**Medical History:** {patient['MedicalHistory'] or 'None provided'}")
        st.write(f"**Registered Date:** {patient['RegisteredDate']}")
    
    # In a real application, you would implement profile update functionality here
    st.markdown("### Update Profile")
    st.info("Profile update functionality would be implemented here in a real application.")
    
    # For demonstration purposes, we'll just show a form without actual update functionality
    with st.form("update_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=patient['Name'])
            email = st.text_input("Email", value=patient['Email'])
            phone = st.text_input("Phone Number", value=patient['Phone'])
        
        with col2:
            address = st.text_area("Address", value=patient['Address'])
            medical_history = st.text_area("Medical History", value=patient['MedicalHistory'] or "")
        
        submit_button = st.form_submit_button("Update Profile")
        
        if submit_button:
            st.success("Profile would be updated in a real application!")
            # In a real app, you would update the patient's profile in the database here

def show_doctor_dashboard():
    """Show the doctor dashboard"""
    st.markdown('<h2 class="sub-header">Doctor Dashboard</h2>', unsafe_allow_html=True)
    
    # Get doctor data
    doctors = st.session_state.db.get_all_doctors()
    doctor = next((doc for doc in doctors if doc["DoctorID"] == st.session_state.user_id), None)
    
    if not doctor:
        st.error("Could not retrieve doctor information")
        return
    
    # Get today's appointments
    today = datetime.now().strftime("%Y-%m-%d")
    appointments = st.session_state.db.get_doctor_appointments(st.session_state.user_id, today)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### Doctor Information")
        st.write(f"**Name:** Dr. {doctor['Name']}")
        st.write(f"**Specialty:** {doctor['Specialty']}")
        st.write(f"**Email:** {doctor['Email']}")
        st.write(f"**Phone:** {doctor['Phone']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown(f"### Today's Appointments ({len(appointments)})")
        
        if appointments:
            for appt in appointments:
                st.markdown(f"""
                <div class="appointment-card">
                    <strong>Time:</strong> {appt['Time']}<br>
                    <strong>Patient:</strong> {appt['PatientName']}<br>
                    <strong>Status:</strong> {appt['Status']}<br>
                    <strong>Notes:</strong> {appt['Notes'] or 'None'}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No appointments scheduled for today.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View Schedule"):
            st.session_state.current_page = "my_schedule"
            st.experimental_rerun()
    
    with col2:
        if st.button("Patient Records"):
            st.session_state.current_page = "patient_records"
            st.experimental_rerun()
    
    with col3:
        if st.button("Update Profile"):
            st.session_state.current_page = "my_profile"
            st.experimental_rerun()

def show_doctor_schedule_page():
    """Show the doctor's schedule page"""
    st.markdown('<h2 class="sub-header">My Schedule</h2>', unsafe_allow_html=True)
    
    # Date selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        view_type = st.radio("View", ["Daily", "Weekly"])
    
    with col2:
        if view_type == "Daily":
            selected_date = st.date_input("Select Date", datetime.now())
            date_str = selected_date.strftime("%Y-%m-%d")
            
            # Get appointments for the selected date
            appointments = st.session_state.db.get_doctor_appointments(st.session_state.user_id, date_str)
            
            st.markdown(f"### Appointments for {format_date_for_display(date_str)}")
            
            if not appointments:
                st.info("No appointments scheduled for this date.")
            else:
                # Sort appointments by time
                appointments.sort(key=lambda x: x["Time"])
                
                # Display appointments
                for appt in appointments:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="appointment-card">
                            <h4>Appointment at {appt['Time']}</h4>
                            <p><strong>Patient:</strong> {appt['PatientName']}</p>
                            <p><strong>Phone:</strong> {appt['PatientPhone']}</p>
                            <p><strong>Status:</strong> {appt['Status']}</p>
                            <p><strong>Notes:</strong> {appt['Notes'] or 'None'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Allow updating appointment status
                        if appt["Status"] == "Scheduled":
                            if st.button("Complete", key=f"complete_{appt['AppointmentID']}"):
                                success, message = st.session_state.db.update_appointment_status(appt['AppointmentID'], "Completed")
                                if success:
                                    st.success("Appointment marked as completed!")
                                    time.sleep(1)
                                    st.experimental_rerun()
                                else:
                                    st.error(f"Failed to update status: {message}")
                            
                            if st.button("Cancel", key=f"cancel_{appt['AppointmentID']}"):
                                success, message = st.session_state.db.update_appointment_status(appt['AppointmentID'], "Cancelled")
                                if success:
                                    st.success("Appointment cancelled!")
                                    time.sleep(1)
                                    st.experimental_rerun()
                                else:
                                    st.error(f"Failed to update status: {message}")
        else:
            # Weekly view
            today = datetime.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            dates = [start_of_week + timedelta(days=i) for i in range(7)]
            
            st.markdown(f"### Week of {dates[0].strftime('%B %d')} - {dates[6].strftime('%B %d, %Y')}")
            
            # Create a table for the weekly view
            weekly_data = []
            
            for date in dates:
                date_str = date.strftime("%Y-%m-%d")
                appointments = st.session_state.db.get_doctor_appointments(st.session_state.user_id, date_str)
                
                # Count appointments by status
                scheduled = len([a for a in appointments if a["Status"] == "Scheduled"])
                completed = len([a for a in appointments if a["Status"] == "Completed"])
                
                cancelled = len([a for a in appointments if a["Status"] == "Cancelled"])
                
                weekly_data.append({
                    "Date": date.strftime("%a, %b %d"),
                    "Total": len(appointments),
                    "Scheduled": scheduled,
                    "Completed": completed,
                    "Cancelled": cancelled
                })
            
            # Display weekly data as a table
            weekly_df = pd.DataFrame(weekly_data)
            st.table(weekly_df)
            
            # Allow selecting a specific day from the week
            selected_day = st.selectbox("Select a day to view details", range(7), format_func=lambda i: dates[i].strftime("%A, %B %d"))
            selected_date = dates[selected_day]
            date_str = selected_date.strftime("%Y-%m-%d")
            
            # Get appointments for the selected date
            appointments = st.session_state.db.get_doctor_appointments(st.session_state.user_id, date_str)
            
            st.markdown(f"### Appointments for {format_date_for_display(date_str)}")
            
            if not appointments:
                st.info("No appointments scheduled for this date.")
            else:
                # Sort appointments by time
                appointments.sort(key=lambda x: x["Time"])
                
                # Display appointments
                for appt in appointments:
                    st.markdown(f"""
                    <div class="appointment-card">
                        <h4>Appointment at {appt['Time']}</h4>
                        <p><strong>Patient:</strong> {appt['PatientName']}</p>
                        <p><strong>Status:</strong> {appt['Status']}</p>
                    </div>
                    """, unsafe_allow_html=True)

def show_patient_records_page():
    """Show the patient records page"""
    st.markdown('<h2 class="sub-header">Patient Records</h2>', unsafe_allow_html=True)
    
    # Get all patients who have appointments with this doctor
    all_appointments = st.session_state.db.get_doctor_appointments(st.session_state.user_id)
    patient_ids = list(set([appt["PatientID"] for appt in all_appointments]))
    
    if not patient_ids:
        st.info("No patient records found.")
        return
    
    # Get patient details
    patients = st.session_state.db.get_all_patients()
    doctor_patients = [p for p in patients if p["PatientID"] in patient_ids]
    
    # Search functionality
    search_term = st.text_input("Search patients by name or ID")
    
    if search_term:
        filtered_patients = [
            p for p in doctor_patients 
            if search_term.lower() in p["Name"].lower() or search_term.lower() in p["PatientID"].lower()
        ]
    else:
        filtered_patients = doctor_patients
    
    # Display patients
    st.markdown(f"### Patient List ({len(filtered_patients)})")
    
    if not filtered_patients:
        st.info("No patients match your search.")
        return
    
    for patient in filtered_patients:
        with st.expander(f"{patient['Name']} ({patient['PatientID']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {patient['Name']}")
                st.write(f"**Email:** {patient['Email']}")
                st.write(f"**Phone:** {patient['Phone']}")
                
                if patient['DateOfBirth']:
                    age = calculate_age(patient['DateOfBirth'])
                    st.write(f"**Age:** {age} years")
            
            with col2:
                st.write(f"**Address:** {patient['Address']}")
                st.write(f"**Medical History:** {patient['MedicalHistory'] or 'None provided'}")
            
            # Get patient's appointments with this doctor
            patient_appointments = [
                appt for appt in all_appointments 
                if appt["PatientID"] == patient["PatientID"]
            ]
            
            st.markdown("#### Appointment History")
            
            if patient_appointments:
                # Sort by date (newest first)
                patient_appointments.sort(key=lambda x: (x["Date"], x["Time"]), reverse=True)
                
                for appt in patient_appointments:
                    st.markdown(f"""
                    <div class="appointment-card">
                        <p><strong>Date:</strong> {format_date_for_display(appt['Date'])}</p>
                        <p><strong>Time:</strong> {appt['Time']}</p>
                        <p><strong>Status:</strong> {appt['Status']}</p>
                        <p><strong>Notes:</strong> {appt['Notes'] or 'None'}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No appointment history found.")

def show_doctor_profile_page():
    """Show the doctor profile page"""
    st.markdown('<h2 class="sub-header">My Profile</h2>', unsafe_allow_html=True)
    
    # Get doctor data
    doctors = st.session_state.db.get_all_doctors()
    doctor = next((doc for doc in doctors if doc["DoctorID"] == st.session_state.user_id), None)
    
    if not doctor:
        st.error("Could not retrieve doctor information")
        return
    
    # Display current profile
    st.markdown("### Current Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** Dr. {doctor['Name']}")
        st.write(f"**Specialty:** {doctor['Specialty']}")
        st.write(f"**Email:** {doctor['Email']}")
    
    with col2:
        st.write(f"**Phone:** {doctor['Phone']}")
        st.write(f"**Schedule:** {doctor['Schedule']}")
    
    # In a real application, you would implement profile update functionality here
    st.markdown("### Update Profile")
    st.info("Profile update functionality would be implemented here in a real application.")
    
    # For demonstration purposes, we'll just show a form without actual update functionality
    with st.form("update_doctor_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=doctor['Name'])
            email = st.text_input("Email", value=doctor['Email'])
        
        with col2:
            phone = st.text_input("Phone Number", value=doctor['Phone'])
            schedule = st.text_input("Schedule", value=doctor['Schedule'])
        
        submit_button = st.form_submit_button("Update Profile")
        
        if submit_button:
            st.success("Profile would be updated in a real application!")
            # In a real app, you would update the doctor's profile in the database here

def show_admin_dashboard():
    """Show the admin dashboard"""
    st.markdown('<h2 class="sub-header">Admin Dashboard</h2>', unsafe_allow_html=True)
    
    # Get statistics
    patients = st.session_state.db.get_all_patients()
    doctors = st.session_state.db.get_all_doctors()
    
    # In a real app, you would get all appointments
    # For demo purposes, we'll just show placeholder data
    total_appointments = 150
    scheduled_appointments = 75
    completed_appointments = 50
    cancelled_appointments = 25
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric("Total Patients", len(patients))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric("Total Doctors", len(doctors))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric("Total Appointments", total_appointments)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
         
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric("Scheduled Appointments", scheduled_appointments)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activity (placeholder)
    st.markdown("### Recent Activity")
    
    activity_data = [
        {"time": "Today, 10:30 AM", "activity": "New patient registered: John Smith"},
        {"time": "Today, 09:15 AM", "activity": "Appointment scheduled: Patient P0023 with Dr. Johnson"},
        {"time": "Yesterday, 3:45 PM", "activity": "Appointment cancelled: Patient P0015"},
        {"time": "Yesterday, 1:20 PM", "activity": "New doctor added: Dr. Emily Wilson (Cardiology)"},
        {"time": "2 days ago", "activity": "Appointment completed: Patient P0008 with Dr. Davis"}
    ]
    
    for activity in activity_data:
        st.markdown(f"""
        <div style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
            <small style="color: #666;">{activity['time']}</small><br>
            {activity['activity']}
        </div>
        """, unsafe_allow_html=True)
    
    # System status (placeholder)
    st.markdown("### System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.write("✅ Database connection: Active")
        st.write("✅ Google Sheets API: Connected")
        st.write("✅ System running normally")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.write("📊 System load: Normal")
        st.write("🔄 Last backup: Today, 03:00 AM")
        st.write("🔒 Security status: All systems secure")
        st.markdown('</div>', unsafe_allow_html=True)

def show_manage_doctors_page():
    """Show the manage doctors page"""
    st.markdown('<h2 class="sub-header">Manage Doctors</h2>', unsafe_allow_html=True)
    
    # Tabs for different actions
    tab1, tab2 = st.tabs(["View Doctors", "Add Doctor"])
    
    with tab1:
        # View doctors
        doctors = st.session_state.db.get_all_doctors()
        
        if not doctors:
            st.info("No doctors found in the system.")
        else:
            # Display doctors
            st.markdown(f"### Doctor List ({len(doctors)})")
            
            for doctor in doctors:
                with st.expander(f"Dr. {doctor['Name']} - {doctor['Specialty']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {doctor['DoctorID']}")
                        st.write(f"**Name:** Dr. {doctor['Name']}")
                        st.write(f"**Specialty:** {doctor['Specialty']}")
                    
                    with col2:
                        st.write(f"**Email:** {doctor['Email']}")
                        st.write(f"**Phone:** {doctor['Phone']}")
                        st.write(f"**Schedule:** {doctor['Schedule']}")
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Edit", key=f"edit_{doctor['DoctorID']}"):
                            st.info("Edit functionality would be implemented in a real application.")
                    
                    with col2:
                        if st.button("Delete", key=f"delete_{doctor['DoctorID']}"):
                            st.error("Delete functionality would be implemented in a real application.")
    
    with tab2:
        # Add new doctor form
        st.markdown("### Add New Doctor")
        
        with st.form("add_doctor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*")
                email = st.text_input("Email*")
                phone = st.text_input("Phone Number*")
            
            with col2:
                specialty = st.selectbox("Specialty*", config.SPECIALTIES)
                schedule = st.text_input("Schedule* (e.g., Mon-Fri, 9AM-5PM)")
                password = st.text_input("Temporary Password*", type="password")
            
            submit_button = st.form_submit_button("Add Doctor")
            
            if submit_button:
                # Validate inputs
                if not name or not email or not phone or not specialty or not schedule or not password:
                    st.error("Please fill in all required fields")
                elif not validate_email(email):
                    st.error("Please enter a valid email address")
                elif not validate_phone(phone):
                    st.error("Please enter a valid 10-digit phone number")
                elif not is_valid_password(password):
                    st.error("Password must be at least 8 characters with at least one uppercase letter, one lowercase letter, and one digit")
                else:
                    # Sanitize inputs
                    name = sanitize_input(name)
                    email = sanitize_input(email)
                    phone = sanitize_input(phone)
                    schedule = sanitize_input(schedule)
                    
                    # Create doctor data
                    doctor_data = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "specialty": specialty,
                        "schedule": schedule
                    }
                    
                    # Add doctor to database
                    success, result = st.session_state.db.add_doctor(doctor_data)
                    
                    if success:
                        st.success(f"Doctor added successfully! Doctor ID: {result}")
                    else:
                        st.error(f"Failed to add doctor: {result}")

def show_manage_patients_page():
    """Show the manage patients page"""
    st.markdown('<h2 class="sub-header">Manage Patients</h2>', unsafe_allow_html=True)
    
    # Get all patients
    patients = st.session_state.db.get_all_patients()
    
    if not patients:
        st.info("No patients found in the system.")
        return
    
    # Search functionality
    search_term = st.text_input("Search patients by name, email, or ID")
    
    if search_term:
        filtered_patients = [
            p for p in patients 
            if search_term.lower() in p["Name"].lower() or 
               search_term.lower() in p["Email"].lower() or 
               search_term.lower() in p["PatientID"].lower()
        ]
    else:
        filtered_patients = patients
    
    # Display patients
    st.markdown(f"### Patient List ({len(filtered_patients)})")
    
    if not filtered_patients:
        st.info("No patients match your search.")
        return
    
    for patient in filtered_patients:
        with st.expander(f"{patient['Name']} ({patient['PatientID']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {patient['PatientID']}")
                st.write(f"**Name:** {patient['Name']}")
                st.write(f"**Email:** {patient['Email']}")
                st.write(f"**Phone:** {patient['Phone']}")
            
            with col2:
                st.write(f"**Date of Birth:** {patient['DateOfBirth']}")
                st.write(f"**Address:** {patient['Address']}")
                st.write(f"**Medical History:** {patient['MedicalHistory'] or 'None provided'}")
                st.write(f"**Registered Date:** {patient['RegisteredDate']}")
            
            # In a real app, you would implement edit and delete functionality here
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Edit", key=f"edit_{patient['PatientID']}"):
                    st.info("Edit functionality would be implemented in a real application.")
            
            with col2:
                if st.button("Delete", key=f"delete_{patient['PatientID']}"):
                    st.error("Delete functionality would be implemented in a real application.")
            
            with col3:
                if st.button("View Appointments", key=f"view_{patient['PatientID']}"):
                    st.info("View appointments functionality would be implemented in a real application.")

def show_appointment_reports_page():
    """Show the appointment reports page"""
    st.markdown('<h2 class="sub-header">Appointment Reports</h2>', unsafe_allow_html=True)
    
    # In a real app, you would get actual appointment data
    # For demo purposes, we'll create placeholder data
    
    # Placeholder data for appointments by status
    status_data = {
        "Scheduled": 75,
        "Completed": 50,
        "Cancelled": 25
    }
    
    # Placeholder data for appointments by specialty
    specialty_data = {
        "General Medicine": 30,
        "Cardiology": 25,
        "Dermatology": 15,
        "Orthopedics": 20,
        "Pediatrics": 18,
        "Neurology": 12,
        "Gynecology": 10,
        "Ophthalmology": 8,
        "Dentistry": 7,
        "Psychiatry": 5
    }
    
    # Placeholder data for appointments by date
    today = datetime.now().date()
    date_data = {
        (today - timedelta(days=6)).strftime("%Y-%m-%d"): 12,
        (today - timedelta(days=5)).strftime("%Y-%m-%d"): 15,
        (today - timedelta(days=4)).strftime("%Y-%m-%d"): 10,
        (today - timedelta(days=3)).strftime("%Y-%m-%d"): 18,
        (today - timedelta(days=2)).strftime("%Y-%m-%d"): 20,
        (today - timedelta(days=1)).strftime("%Y-%m-%d"): 22,
        today.strftime("%Y-%m-%d"): 25
    }
    
    # Display reports
    tab1, tab2, tab3 = st.tabs(["Status Report", "Specialty Report", "Date Report"])
    
    with tab1:
        st.markdown("### Appointments by Status")
        
        # Create DataFrame for status data
        status_df = pd.DataFrame({
            "Status": list(status_data.keys()),
            "Count": list(status_data.values())
        })
        
        # Display as a bar chart
        st.bar_chart(status_df.set_index("Status"))
        
        # Display as a table
        st.table(status_df)
    
    with tab2:
        st.markdown("### Appointments by Specialty")
        
        # Create DataFrame for specialty data
        specialty_df = pd.DataFrame({
            "Specialty": list(specialty_data.keys()),
            "Count": list(specialty_data.values())
        })
        
        # Display as a bar chart
        st.bar_chart(specialty_df.set_index("Specialty"))
        
        # Display as a table
        st.table(specialty_df)
    
    with tab3:
        st.markdown("### Appointments by Date (Last 7 Days)")
        
        # Create DataFrame for date data
        date_df = pd.DataFrame({
            "Date": [format_date_for_display(date) for date in date_data.keys()],
            "Count": list(date_data.values())
        })
        
        # Display as a line chart
        st.line_chart(date_df.set_index("Date"))
        
        # Display as a table
        st.table(date_df)
    
    # Export options (placeholder)
    st.markdown("### Export Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export as CSV"):
            st.success("In a real application, this would download a CSV file.")
    
    with col2:
        if st.button("Export as Excel"):
            st.success("In a real application, this would download an Excel file.")
    
    with col3:
        if st.button("Export as PDF"):
            st.success("In a real application, this would download a PDF file.")

def main():
    """Main application function"""
    # Always render the sidebar first before any other content
    # This ensures the sidebar is displayed properly
    with st.sidebar:
        st.title("Medical Appointment System")
        
        if st.session_state.admin_logged_in:
            st.title("Admin Panel")
            menu_options = ["Dashboard", "Manage Doctors", "Manage Patients", "Appointment Reports", "Logout"]
            choice = st.radio("Admin Menu", menu_options)
            
            st.write(f"Logged in as: {st.session_state.user_name}")
            st.write(f"User Type: {st.session_state.user_type}")
            
            # Handle sidebar selection
            if choice == "Dashboard":
                st.session_state.current_page = "dashboard"
            elif choice == "Manage Doctors":
                st.session_state.current_page = "manage_doctors"
            elif choice == "Manage Patients":
                st.session_state.current_page = "manage_patients"
            elif choice == "Appointment Reports":
                st.session_state.current_page = "appointment_reports"
            elif choice == "Logout":
                st.session_state.admin_logged_in = False
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.current_page = "login"
                st.experimental_rerun()
        elif st.session_state.logged_in:
            if st.session_state.user_type == "patient":
                menu_options = ["Dashboard", "Book Appointment", "My Appointments", "My Profile", "Logout"]
                choice = st.radio("Patient Menu", menu_options)
                
                st.write(f"Logged in as: {st.session_state.user_name}")
                
                # Handle sidebar selection
                if choice == "Dashboard":
                    st.session_state.current_page = "dashboard"
                elif choice == "Book Appointment":
                    st.session_state.current_page = "book_appointment"
                elif choice == "My Appointments":
                    st.session_state.current_page = "my_appointments"
                elif choice == "My Profile":
                    st.session_state.current_page = "my_profile"
                elif choice == "Logout":
                    st.session_state.logged_in = False
                    st.session_state.user_type = None
                    st.session_state.user_id = None
                    st.session_state.user_name = None
                    st.session_state.current_page = "login"
                    st.experimental_rerun()
            elif st.session_state.user_type == "doctor":
                menu_options = ["Dashboard", "My Schedule", "Patient Records", "My Profile", "Logout"]
                choice = st.radio("Doctor Menu", menu_options)
                
                st.write(f"Logged in as: Dr. {st.session_state.user_name}")
                
                # Handle sidebar selection
                if choice == "Dashboard":
                    st.session_state.current_page = "dashboard"
                elif choice == "My Schedule":
                    st.session_state.current_page = "my_schedule"
                elif choice == "Patient Records":
                    st.session_state.current_page = "patient_records"
                elif choice == "My Profile":
                    st.session_state.current_page = "my_profile"
                elif choice == "Logout":
                    st.session_state.logged_in = False
                    st.session_state.user_type = None
                    st.session_state.user_id = None
                    st.session_state.user_name = None
                    st.session_state.current_page = "login"
                    st.experimental_rerun()
        else:
            menu_options = ["Login", "Register", "Admin Login"]
            choice = st.radio("Menu", menu_options)
            
            if choice == "Login":
                st.session_state.current_page = "login"
            elif choice == "Register":
                st.session_state.current_page = "register"
            elif choice == "Admin Login":
                st.session_state.current_page = "admin_login"

    # Main content area
    if not st.session_state.logged_in:
        if st.session_state.current_page == "login":
            show_login_page()
        elif st.session_state.current_page == "register":
            show_registration_page()
        elif st.session_state.current_page == "admin_login":
            show_admin_login_page()
    else:
        if st.session_state.admin_logged_in:
            # Display the appropriate page based on sidebar selection
            if st.session_state.current_page == "dashboard":
                show_admin_dashboard()
            elif st.session_state.current_page == "manage_doctors":
                show_manage_doctors_page()
            elif st.session_state.current_page == "manage_patients":
                show_manage_patients_page()
            elif st.session_state.current_page == "appointment_reports":
                show_appointment_reports_page()
        elif st.session_state.user_type == "patient":
            if st.session_state.current_page == "dashboard":
                show_patient_dashboard()
            elif st.session_state.current_page == "book_appointment":
                show_book_appointment_page()
            elif st.session_state.current_page == "my_appointments":
                show_my_appointments_page()
            elif st.session_state.current_page == "my_profile":
                show_patient_profile_page()
        elif st.session_state.user_type == "doctor":
            if st.session_state.current_page == "dashboard":
                show_doctor_dashboard()
            elif st.session_state.current_page == "my_schedule":
                show_doctor_schedule_page()
            elif st.session_state.current_page == "patient_records":
                show_patient_records_page()
            elif st.session_state.current_page == "my_profile":
                show_doctor_profile_page()

# Run the app
if __name__ == "__main__":
    main()