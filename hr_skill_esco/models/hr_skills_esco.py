from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


_logger.info("Detta är ett loggmeddelande")

class HrSkill(models.Model):
    _inherit = 'hr.skill'

    esco = fields.Char(string='ESCO Code')
    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    _rec_name = "display_name"
    
    @api.depends('name', 'esco')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.esco if record.esco else ''}] {record.name}"
    # ~ display_name = fields.Char(store=True)


class HrSkillType(models.Model):
    _inherit = 'hr.skill.type'

    esco = fields.Char(string='ESCO Code')

    def name_get(self):
        result = []
        raise user_error('lägg ut en text')
        for rec in self:
            name = rec.name
            if rec.esco:
                name = f"[{rec.esco}] {name}"
            _logger.error(f"name_get: id={rec.id}, name={name}")
            result.append((rec.id, name))
        return result


# ~ class HrSkillLevel(models.Model):
    # ~ _inherit = 'hr.skill.level'

    # ~ esco = fields.Char(string='ESCO Code')

    # ~ def name_get(self):
        # ~ result = []
        # ~ for rec in self:
            # ~ name = rec.name
            # ~ if rec.esco:
                # ~ name = f"[{rec.esco}] {name}"
            # ~ result.append((rec.id, name))
        # ~ return result
