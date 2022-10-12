from odoo import api, models, fields
import logging
 
_logger = logging.Logger('.........')

class LunchFields(models.Model):
    _name = "lunch.choice"

    name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="Link to menu")
    vote_bool = fields.Boolean(string="Vote status")