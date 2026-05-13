from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApplicationsConfig(AppConfig):
    """
    Installed as ``apps.applications.apps.ApplicationsConfig`` so settings and admin
    show a clear title. The Python package and DB label remain ``applications`` so
    migrations and table names stay stable.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.applications"
    label = "applications"
    verbose_name = _("STUD — Further studies & field attachment requests")
