import io
import base64
import urllib.parse

try:
    import qrcode
    from qrcode.image.pil import PilImage
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def generate_qr_png_bytes(content: str, box_size: int = 8, border: int = 2) -> bytes:
    """
    Generates a high-quality PNG QR code byte stream from the given URL or content.
    """
    if HAS_QRCODE:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#07192F", back_color="#FFFFFF")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()
    
    # Fallback to pure-Python 1x1 placeholder PNG byte buffer
    # 1x1 transparent PNG header
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    )


def generate_qr_base64(content: str, box_size: int = 8, border: int = 2) -> str:
    """
    Generates a data URI string (data:image/png;base64,...) for embedding directly in HTML.
    If local qrcode is available, generates instant high-res base64.
    If not, falls back to dynamic QR rendering endpoint.
    """
    if HAS_QRCODE:
        png_bytes = generate_qr_png_bytes(content, box_size=box_size, border=border)
        encoded = base64.b64encode(png_bytes).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    
    # Dynamic web QR URL fallback
    encoded_url = urllib.parse.quote_plus(content)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={encoded_url}&color=07192F"


def get_appointment_verification_url(appointment, request=None) -> str:
    """
    Builds the absolute public secure verification/management URL for an appointment.
    """
    relative_url = appointment.get_manage_url()
    if request:
        return request.build_absolute_uri(relative_url)
    
    # Fallback to standard domain
    return f"https://carefirstdental.com{relative_url}"
