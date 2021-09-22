from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Hide personnummer for GDPR reasons
    ssnid = fields.Char(
        track_visibility=False,
        groups="base_user_groups_dafa.group_dafa_employees_write,base_user_groups_dafa.group_dafa_org_admin_write,base_user_groups_dafa.1_line_support")
