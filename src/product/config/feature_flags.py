"""
Feature Flags für den Product-Microservice.

Hierüber lassen sich bestimmte Funktionen (wie z.B. Excel-Export)
global aktivieren oder deaktivieren – z.B. über Umgebungsvariablen.
"""

import os

from product.config import env


# 🔁 Excel-Export aktivieren (z. B. für Admins, Debugging, Reporting)
excel_export_enabled: bool = env.EXCEL_EXPORT_ENABLED
# os.getenv(
#     "EXCEL_EXPORT_ENABLED", "false"
# ).lower() in (
#     "1",
#     "true",
#     "yes",
# )
