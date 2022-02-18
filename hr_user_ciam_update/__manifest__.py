{
    "name": "HR User CIAM Update",
    "version": "12.0.0.5",
    "category": "Human resources",
    "description": """This module adds a button that runs an action that adds the user to the CIAM server. \n
     v12.0.0.4 Added an upper case letter in the automatic password.
     v12.0.0.5 Adapted password to new rules.""",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "http://www.vertel.se",
    "depends": [
        "hr_employee_ciam_client",
        "hr_employee_legacy_id",
        "hr_employee_firstname_extension",
        "partner_legacy_id",
        "hr_employee_ssn",
    ],
    "data": ["views/hr_employee_view.xml"],
    "installable": True,
}
