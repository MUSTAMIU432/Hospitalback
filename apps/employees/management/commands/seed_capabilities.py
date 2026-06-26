"""Seed the staff capabilities catalog.

Idempotent: safe to run repeatedly. Existing rows are updated by `code`,
missing rows are created. Run with:

    python manage.py seed_capabilities
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.employees.models import StaffCapability

CAPABILITIES: list[dict] = [
    {"code": "fs_create", "label": "Create New Application", "description": "Submit a new further studies application", "module": "further_studies", "is_active": True, "sort_order": 4},
    {"code": "fs_existing", "label": "Existing application", "description": "Resume, edit, or view a draft / submitted application", "module": "further_studies", "is_active": True, "sort_order": 0},
    {"code": "fs_edit", "label": "Edit Application", "description": "Edit draft or returned applications", "module": "further_studies", "is_active": True, "sort_order": 1},
    {"code": "fs_delete", "label": "Delete Application", "description": "Delete own applications", "module": "further_studies", "is_active": True, "sort_order": 2},
    {"code": "fs_cancel", "label": "Cancel / Withdraw Application", "description": "Withdraw applications from the review pipeline", "module": "further_studies", "is_active": True, "sort_order": 3},
    {"code": "fs_view_all", "label": "View All Applications", "description": "Access the full application list", "module": "further_studies", "is_active": False, "sort_order": 0},

    {"code": "track_notices", "label": "Application tracking notices", "description": "System messages about application status changes", "module": "app_tracking", "is_active": True, "sort_order": 10},
    {"code": "track_progress", "label": "Track application review progress", "description": "Visual stage tracker: HoD → assistant director → top management", "module": "app_tracking", "is_active": True, "sort_order": 11},

    {"code": "fb_final_report", "label": "View final feedback report", "description": "Final acceptance / rejection letter with all three e-signatures (downloadable)", "module": "app_feedback", "is_active": True, "sort_order": 21},
    {"code": "fb_hod_report", "label": "Final report from HOD", "description": "View HOD stage review letters for own applications", "module": "app_feedback", "is_active": True, "sort_order": 22},
    {"code": "fb_hod_changes", "label": "Change requests from head of department", "description": "View and act on rectification requests sent by the head of department", "module": "staff_change_request", "is_active": True, "sort_order": 20},

    {"code": "notif_view", "label": "View notifications", "description": "View all incoming system notifications", "module": "notifications", "is_active": True, "sort_order": 30},
    {"code": "notif_send", "label": "Send messages", "description": "Compose and send in-system messages", "module": "notifications", "is_active": True, "sort_order": 31},
    {"code": "notif_reply", "label": "Reply to messages", "description": "Reply to received in-system messages", "module": "notifications", "is_active": True, "sort_order": 32},

    # ── HOD ──
    {"code": "hod_assess_details", "label": "Assess application details", "description": "Read and assess the staff further studies application", "module": "hod_review", "is_active": True, "sort_order": 100},
    {"code": "hod_review_doc", "label": "Review application document", "description": "Open and review attached application documents", "module": "hod_review", "is_active": True, "sort_order": 101},
    {"code": "hod_send_changes", "label": "Send change requests to staff", "description": "Request rectification of application details from the staff member", "module": "hod_review", "is_active": True, "sort_order": 102},
    {"code": "hod_view_department_staff", "label": "View department staff (read-only)", "description": "View names of staff belonging to assigned department mappings", "module": "hod_review", "is_active": True, "sort_order": 103},
    {"code": "hod_create_feedback", "label": "Create review feedback", "description": "Use the review-feedback template and apply HoD e-signature", "module": "hod_send_feedback", "is_active": True, "sort_order": 110},
    {"code": "hod_send_to_adr", "label": "Send review feedback to assistant director", "description": "Forward the signed HoD review to the assistant director", "module": "hod_send_feedback", "is_active": True, "sort_order": 111},
    {"code": "hod_accept_adr_req", "label": "Accept change request from assistant director and respond", "description": "Receive and act on a change request sent down from the assistant director", "module": "hod_send_feedback", "is_active": True, "sort_order": 112},
    {"code": "hod_view_hr_approved", "label": "View field-requests approved students", "description": "Read-only view of approved student handoff list from HR", "module": "hod_field_requests", "is_active": True, "sort_order": 120},
    {"code": "hod_view_final_letter", "label": "View approval or rejection letter from top management", "description": "Downloadable final letter carrying all three e-signatures", "module": "hod_final_feedback", "is_active": True, "sort_order": 130},
    {"code": "hod_hub_app_review", "label": "Application review", "description": "Review staff applications as the first review stage via the HOD workspace", "module": "hod_hub_review", "is_active": True, "sort_order": 600},
    {"code": "hod_hub_cr_send", "label": "Send Change Request", "description": "Send a change request to the Staff applicant", "module": "hod_hub_change_request", "is_active": True, "sort_order": 610},
    {"code": "hod_hub_cr_view", "label": "View Change Requests", "description": "View change requests sent to Staff and received from the Assistant Director", "module": "hod_hub_change_request", "is_active": True, "sort_order": 611},
    {"code": "hod_hub_fb_send", "label": "Send Review Feedback", "description": "Compose and send a signed HOD review feedback to the Assistant Director", "module": "hod_hub_review_feedback", "is_active": True, "sort_order": 620},
    {"code": "hod_hub_fb_reports", "label": "Final Application Reports", "description": "View finalised application reports forwarded from the Assistant Director", "module": "hod_hub_review_feedback", "is_active": True, "sort_order": 621},

    # ── Assistant Director (ADR) ──
    {"code": "adr_assess_details", "label": "Assess application details", "description": "Read and assess the staff further studies application", "module": "adr_review", "is_active": True, "sort_order": 200},
    {"code": "adr_review_doc", "label": "Review application document", "description": "Open and review attached application documents", "module": "adr_review", "is_active": True, "sort_order": 201},
    {"code": "adr_review_hod_fb", "label": "Review head of department review feedback", "description": "Read the review feedback submitted by the head of department", "module": "adr_review", "is_active": True, "sort_order": 202},
    {"code": "adr_send_changes", "label": "Send change requests to head of department", "description": "Request amendments from the head of department", "module": "adr_review", "is_active": True, "sort_order": 203},
    {"code": "adr_create_feedback", "label": "Create review feedback", "description": "Use the review-feedback template and apply assistant director e-signature", "module": "adr_send_feedback", "is_active": True, "sort_order": 210},
    {"code": "adr_send_to_top", "label": "Send review feedback to top management", "description": "Forward the signed ADR review to top management", "module": "adr_send_feedback", "is_active": True, "sort_order": 211},
    {"code": "adr_accept_hod_req", "label": "Accept change request from head of department and respond", "description": "Receive and act on a change request sent up from the head of department", "module": "adr_hod_change_req", "is_active": True, "sort_order": 220},
    {"code": "adr_view_final_letter", "label": "View approval or rejection letter from top management", "description": "Downloadable final letter carrying all three e-signatures", "module": "adr_final_feedback", "is_active": True, "sort_order": 230},
    {"code": "adr_hub_app_review", "label": "Application review", "description": "Review staff applications via the ADR workspace", "module": "adr_hub_review", "is_active": True, "sort_order": 500},
    {"code": "adr_hub_cr_send", "label": "Send Change Request", "description": "Send a change request to HoD or Staff applicant", "module": "adr_hub_change_request", "is_active": True, "sort_order": 510},
    {"code": "adr_hub_cr_view", "label": "View Change Requests", "description": "View outstanding and resolved change requests", "module": "adr_hub_change_request", "is_active": True, "sort_order": 511},
    {"code": "adr_hub_fb_send", "label": "Send Review Feedback", "description": "Issue the signed ADR review feedback to Top Management", "module": "adr_hub_review_feedback", "is_active": True, "sort_order": 520},
    {"code": "adr_hub_fb_reports", "label": "Final Application Reports", "description": "View and forward final reports from Top Management to HoD", "module": "adr_hub_review_feedback", "is_active": True, "sort_order": 521},

    # ── Top Management ──
    {"code": "top_assess_details", "label": "Assess application details", "description": "Read and assess the staff further studies application", "module": "top_review", "is_active": True, "sort_order": 300},
    {"code": "top_review_doc", "label": "Review application document", "description": "Open and review attached application documents", "module": "top_review", "is_active": True, "sort_order": 301},
    {"code": "top_review_adr_fb", "label": "Review assistant director review feedback", "description": "Read the review feedback submitted by the assistant director", "module": "top_review", "is_active": True, "sort_order": 302},
    {"code": "top_send_changes", "label": "Send change requests to assistant director", "description": "Request amendments from the assistant director", "module": "top_review", "is_active": True, "sort_order": 303},
    {"code": "top_create_feedback", "label": "Create review feedback", "description": "Use the review-feedback template and apply top management e-signature", "module": "top_send_feedback", "is_active": True, "sort_order": 310},
    {"code": "top_send_final", "label": "Send final review feedback to assistant director", "description": "Final letter with third e-signature — propagates down the review chain", "module": "top_send_feedback", "is_active": True, "sort_order": 311},
    {"code": "top_accept_adr_req", "label": "Accept change request from assistant director and respond", "description": "Receive and act on a change request sent up from the assistant director", "module": "top_adr_change_req", "is_active": True, "sort_order": 320},
    {"code": "top_mgmt_app_review", "label": "Top Mgmt — Application Review", "description": "Access the top management application review queue", "module": "top_mgmt_review", "is_active": True, "sort_order": 50},
    {"code": "top_mgmt_cr_send", "label": "Top Mgmt — Send Change Request", "description": "Send a change request to the Assistant Director", "module": "top_mgmt_change_request", "is_active": True, "sort_order": 51},
    {"code": "top_mgmt_cr_view", "label": "Top Mgmt — View Change Requests", "description": "View all sent change requests", "module": "top_mgmt_change_request", "is_active": True, "sort_order": 52},
    {"code": "top_mgmt_fb_send", "label": "Top Mgmt — Send Review Feedback", "description": "Send final review feedback / formal report", "module": "top_mgmt_review_feedback", "is_active": True, "sort_order": 53},
    {"code": "top_mgmt_fb_reports", "label": "Top Mgmt — Final Application Reports", "description": "View archive of final application reports", "module": "top_mgmt_review_feedback", "is_active": True, "sort_order": 54},

    # ── HR (field requests) ──
    {"code": "hr_view_requests", "label": "View all student field requests", "description": "Open and view a field request; delete a request after assessment", "module": "hr_field_requests", "is_active": True, "sort_order": 50},
    {"code": "hr_assess_request", "label": "Assess field request", "description": "View student details and downloadable application letter from the university", "module": "hr_field_requests", "is_active": True, "sort_order": 51},
    {"code": "hr_feedback_student", "label": "Send feedback to student", "description": "Deliver feedback via in-system message or email notification", "module": "hr_field_requests", "is_active": True, "sort_order": 52},
    {"code": "hr_dept_handoff", "label": "Send feedback of approved student to head of department", "description": "Forward approved student field request to the head of department", "module": "hr_dept_handoff", "is_active": True, "sort_order": 60},

    # ── Inactive / legacy ──
    {"code": "field.requestfeedback", "label": "field application report", "description": "", "module": "field requests", "is_active": False, "sort_order": 0},
    {"code": "send_furtherrequest", "label": "send furtherrequest", "description": "", "module": "Further studies", "is_active": False, "sort_order": 0},
    {"code": "payment:view", "label": "View Payments", "description": "View payment records and history", "module": "finance", "is_active": False, "sort_order": 20},
    {"code": "payment:approve", "label": "Approve Payments", "description": "Approve or reject payment requests", "module": "finance", "is_active": False, "sort_order": 21},
]


class Command(BaseCommand):
    help = "Seed / update the staff capabilities catalog (idempotent)."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for cap in CAPABILITIES:
            _, was_created = StaffCapability.objects.update_or_create(
                code=cap["code"],
                defaults={
                    "label": cap["label"],
                    "description": cap["description"],
                    "module": cap["module"],
                    "is_active": cap["is_active"],
                    "sort_order": cap["sort_order"],
                },
            )
            created += int(was_created)
            updated += int(not was_created)
        self.stdout.write(
            self.style.SUCCESS(
                f"Capabilities seeded: {created} created, {updated} updated, "
                f"{len(CAPABILITIES)} total."
            )
        )
