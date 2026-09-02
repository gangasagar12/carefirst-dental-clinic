import urllib.parse
import datetime
from django.utils import timezone


def get_slot_datetimes(preferred_date, preferred_time: str):
    """
    Returns (start_dt, end_dt) formatted as naive/Kathmandu datetime for calendar exports.
    """
    date_val = preferred_date or (timezone.now().date() + datetime.timedelta(days=1))
    
    # Map slots to realistic Kathmandu time (UTC+5:45)
    time_map = {
        'morning': (datetime.time(9, 0), datetime.time(10, 0)),
        'afternoon': (datetime.time(13, 0), datetime.time(14, 0)),
        'evening': (datetime.time(17, 0), datetime.time(18, 0)),
    }
    
    start_time, end_time = time_map.get(preferred_time, (datetime.time(10, 0), datetime.time(11, 0)))
    start_dt = datetime.datetime.combine(date_val, start_time)
    end_dt = datetime.datetime.combine(date_val, end_time)
    return start_dt, end_dt


def generate_google_calendar_url(appointment, request=None) -> str:
    """
    Constructs a Google Calendar 1-click template link.
    """
    start_dt, end_dt = get_slot_datetimes(appointment.preferred_date, appointment.preferred_time)
    
    # Format for Google Calendar: YYYYMMDDTHHmmss
    fmt_start = start_dt.strftime('%Y%m%dT%H%M%S')
    fmt_end = end_dt.strftime('%Y%m%dT%H%M%S')

    service_title = appointment.service.title if appointment.service else (appointment.get_treatment_display() or "Dental Consultation")
    title = f"Dental Visit: {service_title} — CareFirst Dental"
    location = "CareFirst Dental Clinic, Pragatinagar Road, Shankhamul-31, Kathmandu, Nepal"
    
    manage_url = appointment.get_manage_url()
    if request:
        manage_url = request.build_absolute_uri(manage_url)

    desc_lines = [
        f"CareFirst Dental Clinic Appointment Confirmation",
        f"Booking ID: {appointment.display_booking_id}",
        f"Patient: {appointment.full_name}",
        f"Service: {service_title}",
        f"Time Slot: {appointment.get_preferred_time_display() or 'Flexible'}",
        f"Status: {appointment.get_status_display()}",
        f"Clinic Helpline: +977 980-7464136",
        f"Manage Appointment: {manage_url}",
    ]
    if appointment.status in ['pending', 'new']:
        desc_lines.insert(1, "Note: This appointment is awaiting clinic confirmation. Our desk will call/WhatsApp you shortly.")

    params = {
        'action': 'TEMPLATE',
        'text': title,
        'dates': f"{fmt_start}/{fmt_end}",
        'details': "\n".join(desc_lines),
        'location': location,
        'ctz': 'Asia/Kathmandu',
    }

    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"


def generate_icalendar_content(appointment, request=None) -> str:
    """
    Generates standard RFC-5545 iCalendar (.ics) string.
    """
    start_dt, end_dt = get_slot_datetimes(appointment.preferred_date, appointment.preferred_time)
    dtstamp = timezone.now().strftime('%Y%m%dT%H%M%SZ')
    dtstart = start_dt.strftime('%Y%m%dT%H%M%S')
    dtend = end_dt.strftime('%Y%m%dT%H%M%S')

    service_title = appointment.service.title if appointment.service else (appointment.get_treatment_display() or "Dental Consultation")
    summary = f"Dental Appointment: {service_title} - CareFirst Dental"
    location = "CareFirst Dental Clinic\\, Pragatinagar Road\\, Shankhamul-31\\, Kathmandu\\, Nepal"
    
    manage_url = appointment.get_manage_url()
    if request:
        manage_url = request.build_absolute_uri(manage_url)

    description = (
        f"CareFirst Dental Clinic Appointment Confirmation\\n"
        f"Booking ID: {appointment.display_booking_id}\\n"
        f"Patient: {appointment.full_name}\\n"
        f"Service: {service_title}\\n"
        f"Status: {appointment.get_status_display()}\\n"
        f"Helpline: +977 980-7464136\\n"
        f"Manage URL: {manage_url}"
    )

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//CareFirst Dental Clinic//Appointment System//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{appointment.access_token or appointment.display_booking_id}@carefirstdental.com\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART;TZID=Asia/Kathmandu:{dtstart}\r\n"
        f"DTEND;TZID=Asia/Kathmandu:{dtend}\r\n"
        f"SUMMARY:{summary}\r\n"
        f"DESCRIPTION:{description}\r\n"
        f"LOCATION:{location}\r\n"
        "STATUS:CONFIRMED\r\n"
        "BEGIN:VALARM\r\n"
        "TRIGGER:-PT2H\r\n"
        "ACTION:DISPLAY\r\n"
        f"DESCRIPTION:Reminder: Upcoming Dental Appointment at CareFirst Dental Clinic\r\n"
        "END:VALARM\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return ics_content
