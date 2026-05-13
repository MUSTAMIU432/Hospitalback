from django.apps import AppConfig


class HospitalDirectoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.hospital_directory"
    label = "hospital_directory"
    verbose_name = "Hospital directory (departments, designations, sites)"
