import re
from datetime import datetime, timedelta
import config

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Validate phone number format"""
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    # Check if the phone number has 10 digits
    return len(phone) == 10

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def generate_time_slots(start_hour=9, end_hour=17, interval_minutes=30):
    """Generate time slots for appointments"""
    slots = []
    current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
    end_time = datetime.strptime(f"{end_hour}:00", "%H:%M")
    
    while current_time < end_time:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=interval_minutes)
    
    return slots

def calculate_age(birth_date_str):
    """Calculate age from birth date"""
    try:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def format_date_for_display(date_str):
    """Format date for display (e.g., 'Monday, January 1, 2023')"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%A, %B %d, %Y')
    except ValueError:
        return date_str

def get_next_available_dates(days=7):
    """Get a list of the next available dates"""
    dates = []
    today = datetime.now()
    
    for i in range(days):
        next_date = today + timedelta(days=i)
        dates.append(next_date.strftime('%Y-%m-%d'))
    
    return dates

def is_valid_password(password):
    """Check if password meets security requirements"""
    # At least 8 characters, with at least one uppercase, one lowercase, and one digit
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def sanitize_input(text):
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';]', '', text)
    return sanitized