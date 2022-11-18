from odoo import api, models, fields, _
import logging
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import validators
from validators import ValidationFailure
from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"
    
    context = fields.Char(string="Context", compute="_get_context")
    user_datetime = fields.Datetime(compute="user_date", store=True)
    lunch_id = fields.Many2many("lunch.choice")

    @api.depends('lunch_id')
    def user_date(self):
        updates = self.env["res.users"].search([])
        #user = self.env["res.users"].browse(self.env.uid)
        lunch = self.env["lunch.choice"].search([])
        user = self.env["res.users"].browse(self.env.user.id)
        #_logger.warning(f"{user.id}")
        #user_tz = self.env.user.tz or pytz.utc
        #_logger.warning(f"{user_tz}")
        local = pytz.timezone(str(self.env.user.tz)) if self.env.user.tz is not False else pytz.timezone(str(pytz.utc))
        current_time = datetime.now()
        trimmed = current_time.isoformat(' ', 'seconds')
        #_logger.warning(f"{local}")
        #_logger.warning(f"trimmed version: {trimmed}")
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(str(trimmed),
            DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y-%m-%d %H:%M:%S")
        #_logger.warning(f"datetime-format: {display_date_result}") 
        for record in updates:
            #_logger.info(record.id)
            if record.id == user.id:
                #_logger.warning(f"user_date: {record.name}")
                record.update({"user_datetime": display_date_result})
            else:
                #_logger.warning(f"user hasn't voted")
                continue

    #def _get_context(self):
    #    self.context = dict(self.env.context)
    #    _logger.warning(f"{self.context}")

class LunchFields(models.Model):
    _name = "lunch.choice"
    _description = "Lunch Choices"
    
    def clear_all(self):
        if self.env.is_admin() == True:
            #_logger.warning(f"clear all was pressed")
            restaurants = self.env["lunch.choice"].search([])
            for rec in restaurants:
                restaurante = self.env["lunch.choice"].browse(rec.id)
                restaurante.update({"voted_on": [(5)]})
            return True
        else:
            #_logger.warning(f"user is not admin")
            return False

    def valid_url(self) -> bool:
        url_string = str(self.link_to_menu).strip()
        #_logger.error(self.link_to_menu)
        result = validators.url(url_string)
        if isinstance(result, ValidationFailure):
            #_logger.warning(f"invalid url")
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
                #_logger.warning(f"{record.link_to_menu}")
                return {
                    "type": "ir.actions.act_url", 
                    "url": record.link_to_menu,
                    "target": "new"
                }
            else:
                #_logger.warning(f"link to menu is invalid")
                return f"url is not valid"
      
    @api.depends('voted_on')
    def list_all_voters(self):
        for rec in self:
            rec.voter_id=len(rec.voted_on)

    #context = fields.Char(string="Context", compute="_get_context")
    rest_name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="link_to_menu")
    user_id = fields.Integer(compute="get_current_user")
    voted_on  = fields.Many2many("res.users", string="Employees", store=True)
    show_button = fields.Boolean(compute="_show_button")
    voter_id = fields.Integer(compute="list_all_voters", store=True)
    menu_button = fields.Boolean(compute="_menu_button")
    rest_address = fields.Char(string="address")
    clear_button = fields.Boolean(compute="clear_all")
   
    @api.onchange('voted_on')
    def voted(self):
        for rec in self:
            self.update({"voted_on": [(4, self.env.user.id, 0)]})
            #_logger.error(f"{self.id}")
            #_logger.error(f"{self._context.get('uid')}")
            #_logger.warning(f"voted on {self.voted_on.mapped('id')}")
            choice = self.id
            restaurants = self.env["lunch.choice"].search([])
            for restaurant in restaurants:
                if restaurant.id == choice:
                    continue
                restaurante = self.env["lunch.choice"].browse(restaurant.id)
                restaurante.update({"voted_on": [(3, self.env.user.id, 0)]})

