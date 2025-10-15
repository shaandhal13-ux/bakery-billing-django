from django.shortcuts import render, redirect, get_object_or_404
from .models import Bill, BillItem, Customer_details, Product
from .forms import CustomerForm
from django.core.mail import EmailMessage
from io import BytesIO
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.contrib import messages
from django.shortcuts import render
import os
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



def home(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_success')
    else:
        form = CustomerForm()

    # Fetch all products with name and price
    products = Product.objects.all().values('id', 'name', 'price').order_by('name')

    return render(request, 'billing/home.html', {'form': form, 'products': products})


#to save bill
def save_bill(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            existing_customer = Customer_details.objects.filter(name=customer.name, email=customer.email).first()
            if existing_customer:
                customer = existing_customer
            else:
                customer.save()

            bill = Bill.objects.create(customer=customer)

            item_names = request.POST.getlist("item_name[]")
            quantities = request.POST.getlist("item_qty[]")
            prices = request.POST.getlist("item_price[]")
            totals = request.POST.getlist("item_total[]")

            subtotal = 0
            for i in range(len(item_names)):
                if item_names[i] and quantities[i] and prices[i] and totals[i]:
                    qty = int(quantities[i])
                    price = float(prices[i])
                    total = float(totals[i])

                    BillItem.objects.create(
                        bill=bill,
                        item_name=item_names[i],
                        quantity=qty,
                        price=price,
                        total=total,
                    )
                    subtotal += total

            # Read discount as percentage
            discount_percentage = float(request.POST.get("discount", 0))

            # Calculate discount amount from percentage
            discount_amount = round((subtotal * discount_percentage) / 100,2)

            # Apply discount to subtotal
            subtotal_after_discount = round(subtotal - discount_amount if subtotal > discount_amount else subtotal,2)

            # GST rate total (e.g, 5%)
            gst_rate = 0.05

            # Calculate total GST amount
            gst_amount = round(subtotal_after_discount * gst_rate ,2)

            # Calculate CGST and SGST as half of total GST each
            cgst = round(gst_amount / 2,2)
            sgst = round(gst_amount / 2,2)

            # Calculate final total amount including GST
            final_total = subtotal_after_discount + gst_amount

            # Assign values to your bill model fields
            bill.subtotal = subtotal
            bill.discount = discount_amount
            bill.gst = gst_amount
            bill.cgst = cgst  # make sure you have this field in your Bill model
            bill.sgst = sgst  # make sure you have this field in your Bill model
            bill.total = final_total
            bill.save()

            return redirect("invoice_preview", bill_id=bill.id)
        else:
            # Return form with errors to template
            return render(request, 'billing/home.html', {'form': form})

    return redirect("home")

def invoice_preview(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = bill.items.all()

    return render(request, "billing/invoice.html", {
        "bill": bill,
        "items": items,
        "gst": bill.gst,
        "final_amount": bill.total,
    })

def send_bill_email(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = bill.items.all()

    # === 1) Register full DejaVu family so <b> works ===


    FONT_DIR = os.path.join(settings.BASE_DIR, "billing", "fonts", "dejavu-fonts-ttf-2.37", "ttf")

    pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-BoldOblique", os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf")))

    registerFontFamily(
        "DejaVuSans",
        normal="DejaVuSans",
        bold="DejaVuSans-Bold",
        italic="DejaVuSans-Oblique",
        boldItalic="DejaVuSans-BoldOblique",
    )

    #PDF doc
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=40)
    elements = []

    #Styles 
    styles = getSampleStyleSheet()
    normal = styles["Normal"];  normal.fontName = "DejaVuSans";  normal.fontSize = 11
    title  = styles["Heading1"]; title.fontName = "DejaVuSans-Bold"; title.alignment = TA_CENTER
    right  = ParagraphStyle("right", parent=normal, alignment=TA_RIGHT)

    P  = lambda html: Paragraph(html, normal)
    PR = lambda html: Paragraph(html, right)

    # Header (title)
    centered = ParagraphStyle(
        "centered",
        parent=normal,
        alignment=TA_CENTER
        )
    elements.append(Paragraph("Baker Street", title))  
    elements.append(Paragraph("13, Busy street | +91 7628739456", centered))
    elements.append(Spacer(1, 8))

    # Bill info 
    bill_table = Table(
        [[P(f"Bill No: {bill.invoice_number}"), PR(f"Date: {bill.date.strftime('%d %b %Y')}")]],
        colWidths=[250, 250],
    )
    bill_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 6))
    elements.append(Table([[""]], colWidths=[500], style=[("LINEABOVE", (0,0), (-1,0), 0.25, colors.grey)]))
    elements.append(Spacer(1, 8))

    # Customer details
    cust_data = [
        [
            Paragraph("<b>Customer Name:</b> " + bill.customer.name, normal),
            Paragraph("<b>Email ID:</b> " + bill.customer.email, normal),
        ],
        [
            Paragraph("<b>Phone Number:</b> " + bill.customer.phone, normal),
            Paragraph("", normal),  # empty cell for spacing
        ],
    ]

    cust_table = Table(cust_data, colWidths=[250, 250])  # left + right side
    cust_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),  # align email column to the right
    ]))
    elements.append(cust_table)
    elements.append(Spacer(1, 8))


    # Items table 
    data = [[P("<b>Item No</b>"), P("<b>Item Name</b>"), P("<b>Qty</b>"), P("<b>Price (₹)</b>"), P("<b>Total (₹)</b>")]]
    for i, it in enumerate(items, start=1):
        data.append([P(str(i)), P(it.item_name), P(str(it.quantity)), PR(f"{it.price:.2f}"), PR(f"{it.total:.2f}")])

    items_table = Table(data, colWidths=[60, 200, 60, 100, 100])
    items_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # Totals (right aligned, bold final) 
    totals = [
        [P(""), PR("Subtotal:"), PR(f"₹ {bill.subtotal:.2f}")],
        [P(""), PR("Discount:"), PR(f"₹ {bill.discount:.2f}")],
        [P(""), PR("GST (5%):"), PR(f"₹ {bill.gst:.2f}")],
        [P(""), PR("<b>Final Total:</b>"), PR(f"<b>₹ {bill.total:.2f}</b>")],
    ]
    totals_table = Table(totals, colWidths=[300, 120, 120])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("BOTTOMPADDING", (0, 0), (-1, -2), 4),
        ("TOPPADDING", (0, -1), (-1, -1), 6),
        ("LINEABOVE", (1, -1), (-1, -1), 0.5, colors.black),  # line above final total
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 18))

    # Footer
    elements.append(Paragraph("Thank you for making your day sweeter with us! Have a nice day!",centered))
    elements.append(Paragraph("Visit us again!",centered))

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # Email
    subject = f"Invoice #{bill.invoice_number} from Baker Street"
    message = f"Dear {bill.customer.name},\n\nPlease find attached your invoice.\n\nThanks for shopping with us!"
    email = EmailMessage(subject, message, "shaandhal13@gmail.com", [bill.customer.email])
    email.attach(f"invoice_{bill.invoice_number}.pdf", pdf, "application/pdf")
    email.send()


#Add success message
    messages.success(request, f"Invoice has been sent successfully to {bill.customer.email}")

    return redirect("invoice_preview", bill_id=bill.id)


    
