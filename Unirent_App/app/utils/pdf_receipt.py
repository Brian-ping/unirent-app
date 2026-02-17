from fpdf import FPDF
from datetime import datetime

def generate_booking_receipt(booking_details):
    pdf = FPDF()
    pdf.add_page()
    
    # Title (centered, larger font)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 15, 'UniRent Booking Receipt', 0, 1, 'C')
    pdf.ln(5)  # Add some space
    
    # Receipt header info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Receipt #: UNI-{booking_details['booking_id']}", 0, 1)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(10)  # Add space
    
    # Customer Info section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Customer Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"Name: {booking_details['customer_name']}", 0, 1)
    pdf.cell(0, 8, f"Email: {booking_details['email']}", 0, 1)
    pdf.ln(10)
    
    # Booking Details section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Booking Details', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    # Create a table-like structure
    col_width = 90
    row_height = 10
    
    # Table headers
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(col_width, row_height, 'Description', 1, 0, 'L', 1)
    pdf.cell(0, row_height, 'Details', 1, 1, 'L', 1)
    
    # Table rows
    pdf.cell(col_width, row_height, 'Item Booked:', 1)
    pdf.cell(0, row_height, booking_details['item_name'], 1, 1)
    pdf.cell(col_width, row_height, 'Booking Period:', 1)
    pdf.cell(0, row_height, f"{booking_details['start_date']} to {booking_details['end_date']}", 1, 1)
    pdf.cell(col_width, row_height, 'Location:', 1)
    pdf.cell(0, row_height, booking_details['location'], 1, 1)
    pdf.cell(col_width, row_height, 'Total Amount:', 1)
    pdf.cell(0, row_height, f"KES {booking_details['price']}", 1, 1)
    
    # Footer
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 8, 'Thank you for choosing UniRent!', 0, 1, 'C')
    pdf.cell(0, 8, 'For inquiries: support@unirent.com', 0, 1, 'C')
    
    # Save to temporary file
    filename = f"receipt_{booking_details['booking_id']}.pdf"
    filepath = f"/tmp/{filename}"
    pdf.output(filepath)
    
    return filepath, filename