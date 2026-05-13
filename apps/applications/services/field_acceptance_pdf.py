"""Generate a simple field acceptance letter PDF for approved attachment applications."""

from __future__ import annotations

from io import BytesIO

from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.applications.models import Application
from apps.students.models import StudentProfile
from core.constants import ApplicationStatus, ApplicationType


def build_field_acceptance_pdf(application: Application) -> bytes:
    if application.app_type != ApplicationType.ATTACHMENT:
        raise ValueError("Not an attachment application.")
    if application.status != ApplicationStatus.APPROVED or not application.field_records_shared_at:
        raise ValueError("Field acceptance is only available after HR has published the placement.")

    try:
        stud = StudentProfile.objects.get(user_id=application.applicant_id)
    except StudentProfile.DoesNotExist as exc:
        raise ValueError("Student profile not found for applicant.") from exc

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 72
    line = 16

    def write_heading(text: str) -> None:
        nonlocal y
        c.setFont("Helvetica-Bold", 14)
        c.drawString(72, y, text)
        y -= line + 4

    def write_line(text: str) -> None:
        nonlocal y
        c.setFont("Helvetica", 11)
        for part in _wrap(text, 90):
            c.drawString(72, y, part)
            y -= line

    write_heading("Field training — acceptance letter")
    write_line(f"Issued: {timezone.localdate().isoformat()}")
    write_line(f"Reference: {application.app_ref or str(application.id)}")
    y -= 6
    write_line(f"Student name: {stud.full_name}")
    write_line(f"Registration number: {stud.registration_no}")
    write_line(f"Programme / course: {stud.programme}")
    write_line(f"Year of study: {stud.year_of_study}")
    write_line(f"Faculty: {stud.faculty}")
    y -= 6
    site = (application.placement_conducted_site or "").strip()
    write_line(f"Field training conducted at: {site}")
    if application.attachment_start:
        write_line(f"Period: {application.attachment_start} to {application.attachment_end or '—'}")
    y -= 12
    write_line(
        "This letter was generated from the STUD placement system. "
        "Present it to your university office as confirmation of hospital field placement."
    )
    c.showPage()
    c.save()
    return buf.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + len(cur) > width and cur:
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines
