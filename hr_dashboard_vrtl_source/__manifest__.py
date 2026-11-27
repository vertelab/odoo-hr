# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Vertel Dashboard — HR Sources",
    "version": "18.0.1.0.0",
    "category": "Reporting/Human Resources",
    "summary": "HR analytics adapters for dashboard_vrtl — workforce, payroll, absence, turnover",
    "author": "Vertel Sverige AB",
    "website": "https://vertel.se",
    "license": "AGPL-3",
    "depends": ["dashboard_vrtl", "hr", "hr_holidays", "hr_contract", "hr_payroll"],
    "data": [
        "security/ir.model.access.csv",
        "data/sources.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
