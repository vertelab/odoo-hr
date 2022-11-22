from odoo import api, models, fields, _
import logging
import validators
import datetime
import pytz

_logger = logging.getLogger(__name__)

class LunchChoiceLine(models.Model):
    _name = "lunch.choice.line"
    _description = "Votes on a lunch choice"

    @api.depends("parent_id", "vote_user")
    def _compute_vote_date(self):
        self.vote_date = datetime.datetime.now()

    parent_id = fields.Many2one("lunch.choice", string="Lunch field", required=True, ondelete="cascade")
    vote_user = fields.Many2one("res.users", string="Votes", required=True, ondelete="cascade")
    vote_date = fields.Datetime(compute="_compute_vote_date", store=True)

class LunchChoice(models.Model):
    _name = "lunch.choice"
    _description = "Lets you vote for restaurants"
    
    def clear_all(self):
        for lunch in self:
            for line in lunch.line_ids:
                line.unlink()

    def valid_url(self) -> bool:
        url_string = str(self.link_to_menu).strip()
        result = validators.url(url_string)
        if isinstance(result, validators.ValidationFailure):
            return False
        return result

    @api.onchange('line_ids')
    def _show_vote_button(self):        
        for lunch in self.env["lunch.choice"].search([]):
            lunch.show_vote_button = True
            for line in lunch.line_ids:
                if line.vote_user.id == self.env.user.id:
                    lunch.show_vote_button = False
    
    @api.depends('link_to_menu', 'show_menu_button')
    def _show_menu_button(self):
        for rec in self:
            _result = rec.valid_url()
            if _result == False:
                rec.show_menu_button = False
            else:
                rec.show_menu_button = True

    def open_url(self):
        for record in self:
            _result = record.valid_url()
            if _result == True:
                return {
                    "type": "ir.actions.act_url", 
                    "url": record.link_to_menu,
                    "target": "new"
                }
            else:
                return f"url is not valid"
      
    @api.depends('line_ids')
    def list_all_voters(self):
        self.voter_amount=len(self.line_ids)

    rest_name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="Url to menu")
    show_vote_button = fields.Boolean(compute="_show_vote_button")
    voter_amount = fields.Integer(compute="list_all_voters", store=True)
    show_menu_button = fields.Boolean(compute="_show_menu_button")
    rest_address = fields.Char(string="Address")
    clear_button = fields.Boolean(compute="_show_clear")
    line_ids = fields.One2many(comodel_name="lunch.choice.line", inverse_name="parent_id")

    def voted(self):
        for lunch in self.env["lunch.choice"].search([]):
            if len(lunch.line_ids) > 0:
                for line in lunch.line_ids:
                    if line.vote_user.id == self.env.user.id:
                        line.unlink()
        self.update({"line_ids": [(0, 0, {'vote_user': self.env.user.id, 'parent_id': self})]})

