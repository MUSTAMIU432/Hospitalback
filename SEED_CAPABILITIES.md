# Seeding the Capabilities Catalog

The system's permissions are stored in the **`staff_capabilities_catalog`** table
(`apps.employees.models.StaffCapability`). This document explains how to load all
**61 capabilities** into a fresh database on any machine.

A ready-made, idempotent seeder ships with the repo:
`apps/employees/management/commands/seed_capabilities.py`. Running it creates any
missing capabilities and updates existing ones by `code` — it never duplicates, so
it is safe to run as many times as you like.

---

## Quick run (capabilities already defined in the repo)

> Prerequisite: the database must exist and be reachable (settings come from `.env`),
> and migrations must be applied so the table exists.

### Windows — PowerShell
```powershell
python manage.py migrate
python manage.py seed_capabilities
```

### Windows — Command Prompt (cmd)
```bat
python manage.py migrate && python manage.py seed_capabilities
```

### Linux / macOS
```bash
python manage.py migrate
python manage.py seed_capabilities
```

If you use a virtual environment and have not activated it, call its Python directly:

- Windows: `.venv\Scripts\python.exe manage.py seed_capabilities`
- Linux/macOS: `.venv/bin/python manage.py seed_capabilities`

On success you will see:
```
Capabilities seeded: <created> created, <updated> updated, 61 total.
```

---

## Full setup on a new machine (one line)

Creates the venv, installs deps, copies `.env`, migrates, then seeds.

### Windows — PowerShell
```powershell
cd C:\path\to\STUDBACK; python -m venv .venv; .\.venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install -r requirements.txt; if (!(Test-Path .env)) { copy .env.example .env }; python manage.py migrate; python manage.py seed_capabilities
```

### Windows — Command Prompt (cmd)
```bat
cd C:\path\to\STUDBACK && python -m venv .venv && .venv\Scripts\activate && python -m pip install --upgrade pip && pip install -r requirements.txt && (if not exist .env copy .env.example .env) && python manage.py migrate && python manage.py seed_capabilities
```

### Linux / macOS
```bash
cd /path/to/STUDBACK && python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && [ -f .env ] || cp .env.example .env && python manage.py migrate && python manage.py seed_capabilities
```

> After copying `.env`, edit the database credentials to match the local PostgreSQL
> instance, then re-run from `python manage.py migrate` if needed.

---

## Verify what was loaded

```bash
python manage.py shell -c "from apps.employees.models import StaffCapability; print(StaffCapability.objects.count(), 'capabilities')"
```

Expected: `61 capabilities`.

---

## Capabilities included (61)

| # | code | module | active |
|---|------|--------|--------|
| 1 | fs_create | further_studies | yes |
| 2 | fs_existing | further_studies | yes |
| 3 | fs_edit | further_studies | yes |
| 4 | fs_delete | further_studies | yes |
| 5 | fs_cancel | further_studies | yes |
| 6 | fs_view_all | further_studies | no |
| 7 | track_notices | app_tracking | yes |
| 8 | track_progress | app_tracking | yes |
| 9 | fb_final_report | app_feedback | yes |
| 10 | fb_hod_report | app_feedback | yes |
| 11 | fb_hod_changes | staff_change_request | yes |
| 12 | notif_view | notifications | yes |
| 13 | notif_send | notifications | yes |
| 14 | notif_reply | notifications | yes |
| 15 | hod_assess_details | hod_review | yes |
| 16 | hod_review_doc | hod_review | yes |
| 17 | hod_send_changes | hod_review | yes |
| 18 | hod_view_department_staff | hod_review | yes |
| 19 | hod_create_feedback | hod_send_feedback | yes |
| 20 | hod_send_to_adr | hod_send_feedback | yes |
| 21 | hod_accept_adr_req | hod_send_feedback | yes |
| 22 | hod_view_hr_approved | hod_field_requests | yes |
| 23 | hod_view_final_letter | hod_final_feedback | yes |
| 24 | hod_hub_app_review | hod_hub_review | yes |
| 25 | hod_hub_cr_send | hod_hub_change_request | yes |
| 26 | hod_hub_cr_view | hod_hub_change_request | yes |
| 27 | hod_hub_fb_send | hod_hub_review_feedback | yes |
| 28 | hod_hub_fb_reports | hod_hub_review_feedback | yes |
| 29 | adr_assess_details | adr_review | yes |
| 30 | adr_review_doc | adr_review | yes |
| 31 | adr_review_hod_fb | adr_review | yes |
| 32 | adr_send_changes | adr_review | yes |
| 33 | adr_create_feedback | adr_send_feedback | yes |
| 34 | adr_send_to_top | adr_send_feedback | yes |
| 35 | adr_accept_hod_req | adr_hod_change_req | yes |
| 36 | adr_view_final_letter | adr_final_feedback | yes |
| 37 | adr_hub_app_review | adr_hub_review | yes |
| 38 | adr_hub_cr_send | adr_hub_change_request | yes |
| 39 | adr_hub_cr_view | adr_hub_change_request | yes |
| 40 | adr_hub_fb_send | adr_hub_review_feedback | yes |
| 41 | adr_hub_fb_reports | adr_hub_review_feedback | yes |
| 42 | top_assess_details | top_review | no |
| 43 | top_review_doc | top_review | yes |
| 44 | top_review_adr_fb | top_review | yes |
| 45 | top_send_changes | top_review | yes |
| 46 | top_create_feedback | top_send_feedback | yes |
| 47 | top_send_final | top_send_feedback | yes |
| 48 | top_accept_adr_req | top_adr_change_req | yes |
| 49 | top_mgmt_app_review | top_mgmt_review | yes |
| 50 | top_mgmt_cr_send | top_mgmt_change_request | yes |
| 51 | top_mgmt_cr_view | top_mgmt_change_request | yes |
| 52 | top_mgmt_fb_send | top_mgmt_review_feedback | yes |
| 53 | top_mgmt_fb_reports | top_mgmt_review_feedback | yes |
| 54 | hr_view_requests | hr_field_requests | yes |
| 55 | hr_assess_request | hr_field_requests | yes |
| 56 | hr_feedback_student | hr_field_requests | yes |
| 57 | hr_dept_handoff | hr_dept_handoff | yes |
| 58 | field.requestfeedback | field requests | no |
| 59 | send_furtherrequest | Further studies | no |
| 60 | payment:view | finance | no |
| 61 | payment:approve | finance | no |

---

## Notes

- **Idempotent:** re-running `seed_capabilities` updates rows by `code`; no duplicates.
- This seeds the **catalog only**. Role to capability assignments
  (`StaffRoleCapability`) and per-user overrides are managed separately in the app.
- Four capabilities are intentionally inactive (`is_active = no`) — legacy / finance
  placeholders kept so the catalog matches the source machine exactly.
