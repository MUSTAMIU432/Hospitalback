from django.db import migrations

# Stray / duplicate sections created by the old placeholder hack or test data.
# Their capabilities go with them (payment:* are not part of any real workflow,
# and the space-key sections duplicate the real underscore-key ones).
JUNK_KEYS = ["finance", "Further studies", "field requests"]

# Precise, role-scoped titles so the Sections page reads clearly with no
# confusing duplicates. "ADR" is spelled out as "Assistant Director".
# (The staff sidebar uses its own short labels from registry.ts — untouched.)
SECTION_TITLES = {
    # Personal
    "further_studies":          "Further Studies",
    "app_tracking":             "Application Tracking",
    "staff_change_request":     "Change Requests",
    "app_feedback":             "Application Feedback",
    "notifications":            "Notifications",
    # HR
    "hr_field_requests":        "HR · Student Field Requests",
    "hr_dept_handoff":          "HR · Department Handoff",
    # Head of Department (current hub)
    "hod_hub_review":           "Head of Department · Review Applications",
    "hod_hub_change_request":   "Head of Department · Change Requests",
    "hod_hub_review_feedback":  "Head of Department · Review Feedback",
    "hod_field_requests":       "Head of Department · Field Requests",
    "hod_final_feedback":       "Head of Department · Final Feedback",
    "hod_department_staff":     "Head of Department · Department Staff",
    # Head of Department (legacy reviewer flow)
    "hod_review":               "Head of Department · Review Applications (reviewer flow)",
    "hod_send_feedback":        "Head of Department · Send Feedback (reviewer flow)",
    # Assistant Director (current hub)
    "adr_hub_review":           "Assistant Director · Review Applications",
    "adr_hub_change_request":   "Assistant Director · Change Requests",
    "adr_hub_review_feedback":  "Assistant Director · Review Feedback",
    # Assistant Director (legacy reviewer flow)
    "adr_review":               "Assistant Director · Review Applications (reviewer flow)",
    "adr_send_feedback":        "Assistant Director · Send Feedback (reviewer flow)",
    "adr_hod_change_req":       "Assistant Director · HOD Change Requests (reviewer flow)",
    "adr_final_feedback":       "Assistant Director · Final Feedback (reviewer flow)",
    # Top Management (current hub)
    "top_mgmt_review":          "Top Management · Review Applications",
    "top_mgmt_change_request":  "Top Management · Change Requests",
    "top_mgmt_review_feedback": "Top Management · Review Feedback",
    # Top Management (legacy reviewer flow)
    "top_review":               "Top Management · Review Applications (reviewer flow)",
    "top_send_feedback":        "Top Management · Send Feedback (reviewer flow)",
    "top_adr_change_req":       "Top Management · Assistant Director Change Requests (reviewer flow)",
}


def clean_sections(apps, schema_editor):
    CapabilitySection = apps.get_model("employees", "CapabilitySection")
    StaffCapability = apps.get_model("employees", "StaffCapability")

    # 1. Remove junk sections and the capabilities that lived under them.
    StaffCapability.objects.filter(module__in=JUNK_KEYS).delete()
    CapabilitySection.objects.filter(key__in=JUNK_KEYS).delete()

    # 2. Apply precise titles.
    for key, label in SECTION_TITLES.items():
        CapabilitySection.objects.filter(key=key).update(label=label)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0009_capabilitysection"),
    ]

    operations = [
        migrations.RunPython(clean_sections, noop),
    ]
