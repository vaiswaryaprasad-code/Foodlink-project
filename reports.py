from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.http import FileResponse
from donor.models import FoodDonation




def donation_report(request):

    from io import BytesIO

    from django.http import FileResponse
    from django.utils import timezone

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
    )

    from donor.models import FoodDonation

    # Create PDF buffer
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A3),
        rightMargin=20,
        leftMargin=20,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()
    cell_style = styles["BodyText"]
    cell_style.fontSize = 7
    cell_style.leading = 9

    # Report title
    title = Paragraph(
        "<b>FoodLink - Food Donation Report</b>",
        styles["Title"],
    )

    # Table headings
    data = [[
        "ID",
        "Food Name",
        "Donor",
        "Food Type",
        "Quantity",
        "City",
        "Created Date",
        "Created Time",
        "Prepared Time",
        "Expiry Time",
        "Status",
        "Safety Score",
        "Safety Status",
        "Priority",
        "Recommended NGO",
    ]]

    # Retrieve donations
    donations = (
        FoodDonation.objects
        .select_related("donor")
        .order_by("-created_at")
    )

    for donation in donations:

        created_at = (
            timezone.localtime(donation.created_at)
            if donation.created_at
            else None
        )

        prepared_at = (
            timezone.localtime(donation.prepared_time)
            if donation.prepared_time
            else None
        )

        expiry_at = (
            timezone.localtime(donation.expiry_time)
            if donation.expiry_time
            else None
        )

        data.append([
            str(donation.id),
            Paragraph(str(donation.food_name), cell_style),
            Paragraph(str(donation.donor.username), cell_style),
            donation.get_food_type_display(),
            str(donation.quantity),
            Paragraph(str(donation.city), cell_style),

            created_at.strftime("%d-%m-%Y")
            if created_at else "-",

            created_at.strftime("%I:%M %p")
            if created_at else "-",

            prepared_at.strftime("%d-%m-%Y %I:%M %p")
            if prepared_at else "-",

            expiry_at.strftime("%d-%m-%Y %I:%M %p")
            if expiry_at else "-",

            donation.status,
            str(donation.food_safety_score),
            Paragraph(str(donation.food_status), cell_style),
            str(donation.priority_score),

            Paragraph(
                str(donation.recommended_ngo or "Not Assigned"),
                cell_style,
            ),
        ])

    # Create table and repeat headings on every page
    table = Table(
        data,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )

    # Generate PDF
    pdf.build([title, table])

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename="Donation_Report.pdf",
        content_type="application/pdf",
    )

