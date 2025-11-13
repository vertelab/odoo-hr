from odoo import models, fields, api, _


class TierDefinition(models.Model):
    _inherit = 'tier.definition'

    hr_department_id = fields.Many2one('hr.department', string="Department")
    project_id = fields.Many2one('project.project', string="Project")
    amount = fields.Float(string="Amount")

    @api.onchange('hr_department_id', 'amount', 'project_id')
    def set_domain_tier(self):
        domain = [('amount_total', '>=', self.amount)]
        if self.project_id:
            domain += [('project_id', '=', self.project_id.id)]
        if self.hr_department_id:
            domain += [('hr_department_id', '=', self.hr_department_id.id)]

        self.definition_domain = domain

    @api.onchange('model_id', 'project_id', 'hr_department_id')
    def set_reviewer_field(self):
        if self.hr_department_id and self.model_id:
            self.review_type = "field"

            if self.project_id:
                self.reviewer_field_id = self.model_id.field_id.filtered(
                    lambda field: field.name == 'project_hr_manager_user_id'
                ).id
            else:
                self.reviewer_field_id = self.model_id.field_id.filtered(
                    lambda field: field.name == 'hr_manager_user_id'
                ).id


