from odoo import api, models, fields, _
import logging
import validators
from validators import ValidationFailure

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"
    lunch_id = fields.Many2many("lunch.choice")

class LunchFields(models.Model):
    _name = "lunch.choice"

    def valid_url(self) -> bool:
        url_string = str(self.link_to_menu).strip()
        _logger.error(self.link_to_menu)
        result = validators.url(url_string)
        if isinstance(result, ValidationFailure):
            _logger.warning(f"invalid url")
            return False
        return result

    #def _get_context(self):
        #self.context = dict(self.env.context)

    def get_current_user(self):
        self.user_id = self.env.user.id

    @api.depends('voted_on', 'user_id')
    def _show_button(self):
        for record in self:
           if record.user_id in record.voted_on.ids:
              record.show_button = False
           else:
              record.show_button = True
           #_logger.warning(f"{record.show_button=}")
    
    @api.depends('link_to_menu', 'menu_button')
    def _menu_button(self):
        for rec in self:
            _result = rec.valid_url()
            if _result == False:
                rec.menu_button = False
            else:
                rec.menu_button = True

    def open_url(self):
        for record in self:
            _result = record.valid_url()
            if _result == True:
                _logger.warning(f"{record.link_to_menu}")
                return {
                    "type": "ir.actions.act_url", 
                    "url": record.link_to_menu,
                    "target": "new"
                }
            else:
                _logger.warning(f"{record.link_to_menu} is broken")
                return f"url is not valid"
      
    @api.depends('voted_on')
    def list_all_voters(self):
        for rec in self:
            rec.voter_id=len(rec.voted_on)

    #context = fields.Char(string="Context", compute="_get_context")
    name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="link_to_menu")
    user_id = fields.Integer(compute="get_current_user")
    voted_on  = fields.Many2many("res.users", string="Employees")
    show_button = fields.Boolean(compute="_show_button")
    voter_id = fields.Integer(compute="list_all_voters")
    menu_button = fields.Boolean(compute="_menu_button")
    
    def voted(self):
        for rec in self:
            self.update({"voted_on": [(4, self.env.user.id, 0)]})
            _logger.error(f"{self.id}")
            _logger.error(f"{self._context.get('uid')}")
            _logger.warning(f"{self.voted_on.mapped('id')}")
            choice = self.id
            restaurants = self.env["lunch.choice"].search([])
            for restaurant in restaurants:
                if restaurant.id == choice:
                    continue
                restaurante = self.env["lunch.choice"].browse(restaurant.id)
                restaurante.update({"voted_on": [(3, self.env.user.id, 0)]})

