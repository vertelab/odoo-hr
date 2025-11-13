from odoo import models, fields, api, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    tier_definition_ids = fields.One2many('tier.definition', 'hr_department_id', string="Tier Definition")
    tier_validation_count = fields.Integer(string='Tier Validation Count', compute='_compute_tier_definition')

    @api.depends('tier_definition_ids')
    def _compute_tier_definition(self):
        for rec in self:
            rec.tier_validation_count = len(rec.tier_definition_ids)

    def action_hr_department_validation(self):
        return {
            'name': _('Department Tier Validation'),
            'view_mode': 'list,form',
            'res_model': 'tier.definition',
            'domain': [('hr_department_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {
                'default_hr_department_id': self.id,
                'default_review_type': 'field',
                'default_definition_domain': f'[("amount_total", ">=", 0), ("hr_department_id", "=", {self.id})]'
            }
        }