import io
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image as RLImage, KeepTogether, HRFlowable
)
from .qr_services import generate_qr_png_bytes, get_appointment_verification_url


def generate_appointment_confirmation_pdf(appointment, request=None) -> bytes:
    """
    Generates a PDF Appointment Confirmation document using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    navy = colors.HexColor("#07192F")
    blue = colors.HexColor("#0284C7")
    light_blue = colors.HexColor("#F0F9FF")
    light_gray = colors.HexColor("#F8FAFC")
    border_gray = colors.HexColor("#E2E8F0")
    dark_gray = colors.HexColor("#334155")
    warning_gold = colors.HexColor("#D97706")
    success_green = colors.HexColor("#059669")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=navy,
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_gray,
    )

    section_heading = ParagraphStyle(
        'SectionHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=navy,
        spaceAfter=6
    )

    label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=dark_gray
    )

    value_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=navy
    )

    badge_style = ParagraphStyle(
        'StatusBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white,
        alignment=1
    )

    qr_caption_style = ParagraphStyle(
        'QRCaption',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=dark_gray,
        alignment=1
    )

    story = []

    # 1. HEADER BRANDING BLOCK
    header_data = [
        [
            Paragraph("<b>CareFirst Dental Clinic</b><br/><font size=8 color='#0284C7'>Excellence in Gentle & Modern Dentistry</font>", title_style),
            Paragraph("<b>Clinic Desk:</b> +977 980-7464136<br/><b>Location:</b> Pragatinagar Road, Shankhamul-31, Kathmandu<br/><b>Hours:</b> Open Daily 7:30 AM – 7:30 PM", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[3.2 * inch, 4.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=blue, spaceBefore=0, spaceAfter=14))

    # 2. DOCUMENT TITLE & BOOKING ID BAR
    status_bg = success_green if appointment.status == 'confirmed' else (warning_gold if appointment.status in ['pending', 'new'] else blue)
    status_label = appointment.get_status_display().upper()

    ref_data = [
        [
            Paragraph(f"<font size=8 color='#64748B'>BOOKING REFERENCE ID</font><br/><b><font size=14 color='#07192F'>{appointment.display_booking_id}</font></b>", ParagraphStyle('Ref', parent=styles['Normal'], leading=16)),
            Paragraph(f"<font size=8 color='#64748B'>CURRENT STATUS</font><br/><b><font size=12 color='{status_bg.hexval()}'>{status_label}</font></b>", ParagraphStyle('Stat', parent=styles['Normal'], leading=16, alignment=2))
        ]
    ]
    ref_table = Table(ref_data, colWidths=[3.8 * inch, 3.4 * inch])
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('BOX', (0, 0), (-1, -1), 1, border_gray),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 14))

    # 3. DETAILS & QR CODE SPLIT GRID
    service_title = appointment.service.title if appointment.service else (appointment.get_treatment_display() or "General Consultation")
    doctor_name = f"Dr. {appointment.doctor.name}" if appointment.doctor else "CareFirst Clinical Specialist Team"
    branch_name = appointment.branch.name if appointment.branch else "CareFirst Main Clinic (Shankhamul, Kathmandu)"
    pref_date_str = appointment.preferred_date.strftime("%B %d, %Y (%A)") if appointment.preferred_date else "To be scheduled"
    pref_time_str = appointment.get_preferred_time_display() or "Flexible Slot"

    details_matrix = [
        [Paragraph("Patient Name:", label_style), Paragraph(f"<b>{appointment.full_name}</b>", value_style)],
        [Paragraph("Contact Phone:", label_style), Paragraph(f"<b>{appointment.phone}</b>", value_style)],
        [Paragraph("Email Address:", label_style), Paragraph(appointment.email or "Not Provided", value_style)],
        [Paragraph("Clinical Service:", label_style), Paragraph(f"<b>{service_title}</b>", value_style)],
        [Paragraph("Appointment Date:", label_style), Paragraph(f"<b>{pref_date_str}</b>", value_style)],
        [Paragraph("Time Slot:", label_style), Paragraph(f"<b>{pref_time_str}</b>", value_style)],
        [Paragraph("Attending Doctor:", label_style), Paragraph(doctor_name, value_style)],
        [Paragraph("Clinic Branch:", label_style), Paragraph(branch_name, value_style)],
    ]

    if appointment.pricing_option:
        details_matrix.append([Paragraph("Material / Option:", label_style), Paragraph(appointment.pricing_option, value_style)])
    if appointment.estimated_amount:
        details_matrix.append([Paragraph("Price Estimate:", label_style), Paragraph(f"NPR {appointment.estimated_amount} (Informational)", value_style)])
    if appointment.message:
        details_matrix.append([Paragraph("Patient Notes:", label_style), Paragraph(appointment.message, value_style)])

    details_table = Table(details_matrix, colWidths=[1.5 * inch, 3.4 * inch])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
    ]))

    # QR Code generation for right panel
    manage_url = get_appointment_verification_url(appointment, request=request)
    qr_bytes = generate_qr_png_bytes(manage_url, box_size=6, border=1)
    qr_img = RLImage(io.BytesIO(qr_bytes), width=1.4 * inch, height=1.4 * inch)

    qr_panel_data = [
        [qr_img],
        [Paragraph("<b>Scan QR Code</b><br/>Verify appointment & check live status on mobile", qr_caption_style)],
        [Spacer(1, 4)],
        [Paragraph(f"<font size=6 color='#64748B'>{manage_url}</font>", ParagraphStyle('URL', parent=styles['Normal'], alignment=1, fontSize=6, leading=8))]
    ]
    qr_table = Table(qr_panel_data, colWidths=[2.1 * inch])
    qr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('BOX', (0, 0), (-1, -1), 1, border_gray),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    body_split_data = [
        [details_table, qr_table]
    ]
    body_split_table = Table(body_split_data, colWidths=[5.0 * inch, 2.2 * inch])
    body_split_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(body_split_table)
    story.append(Spacer(1, 14))

    # 4. IMPORTANT INSTRUCTIONS & ADVISORY
    instruction_text = (
        "<b>Important Patient Information:</b><br/>"
        "• Please present this confirmation or show your Booking ID / QR Code at reception upon arrival.<br/>"
        "• If your appointment status is <b>Pending</b>, our reception desk will contact you via phone or WhatsApp shortly to confirm availability.<br/>"
        "• Please arrive approximately 10 minutes prior to your scheduled time.<br/>"
        "• For rescheduling, questions, or emergencies, please contact our helpline at <b>+977 980-7464136</b>."
    )
    instruction_p = Paragraph(instruction_text, ParagraphStyle('Inst', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=dark_gray))
    instruction_table = Table([[instruction_p]], colWidths=[7.2 * inch])
    instruction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_blue),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BAE6FD")),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(instruction_table)
    story.append(Spacer(1, 16))

    # 5. FOOTER COMPLIANCE
    footer_text = (
        f"<font color='#64748B'>CareFirst Dental Clinic • Clinical Director: Dr. Subash Banjade (NMC #31229) • "
        f"Generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} NPT</font>"
    )
    story.append(Paragraph(footer_text, ParagraphStyle('Foot', parent=styles['Normal'], alignment=1, fontSize=7.5, leading=10)))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
