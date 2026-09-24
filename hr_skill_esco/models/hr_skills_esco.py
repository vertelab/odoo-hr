from odoo import models, fields, api


class HrSkill(models.Model):
    _inherit = 'hr.skill'

    esco = fields.Char(string='ESCO Code')
    display_name = fields.Char(
        string='Name', compute='_compute_display_name', store=True, readonly=True,
    )

    @api.depends('name', 'esco')
    def _compute_display_name(self):
        for record in self:
            if record.esco:
                record.display_name = f"[{record.esco}] {record.name}"
            else:
                record.display_name = record.name


class HrSkillType(models.Model):
    _inherit = 'hr.skill.type'

    esco = fields.Char(string='ESCO Code')
