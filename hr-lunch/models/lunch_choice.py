from odoo import api, models, fields
import logging
 
_logger = logging.Logger('.........')

class LunchFields(models.Model):
    _name = "lunch.choice"

    name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="Link to menu")
    voted_on = fields.One2many("res.partner", "display_name", "Employees")
    
    def voted(self):
        for rec in self:
            _logger.warning("you have voted, did you really want to vote?")
