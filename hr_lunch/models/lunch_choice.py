from odoo import api, models, fields
import logging
 
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"
    lunch_id = fields.Many2many("lunch.choice")

class LunchFields(models.Model):
    _name = "lunch.choice"
    
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
           _logger.warning(f"{record.show_button=}")
    
    def open_url(self):
        return {
            "type": "ir.actions.act_url", 
            "url": "https://www.google.com",
            "target": "new"
        }
   
    #fix url part
    #fix form-view many2many with vote button read-only 
    @api.depends('voted_on')
    def list_all_voters(self):
        for rec in self:
            rec.voter_id=len(rec.voted_on)

    #context = fields.Char(string="Context", compute="_get_context")
    name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="Link to menu")
    user_id = fields.Integer(compute="get_current_user")
    voted_on  = fields.Many2many("res.users", string="Employees")
    show_button = fields.Boolean(compute="_show_button")
    voter_id = fields.Integer(compute="list_all_voters")

    def voted(self):
        for rec in self:
            #_logger.warning("you have voted, did you really")
            #_logger.error(f"{rec.name=}")
            #_logger.error(f"{rec.link_to_menu=}")
            #_logger.error(f"{rec.voted_on=}")
            self.update({"voted_on": [(4, self.env.user.id, 0)]})
            _logger.error(f"{self.id}")
            #choice = self.update gave choice = NONE
            _logger.error(f"{self._context.get('uid')}")
            _logger.warning(f"{self.voted_on.mapped('id')}")
            choice = self.id
            restaurants = self.env["lunch.choice"].search([])
            for restaurant in restaurants:
                if restaurant.id == choice:
                    continue
                restaurante = self.env["lunch.choice"].browse(restaurant.id)
                restaurante.update({"voted_on": [(3, self.env.user.id, 0)]})
                
            #penguin = self.env["lunch.choice"].search_read([("id", "=", restaurants[0][0].id)],[])
            #_logger.error(f"{penguin}")
            #penguin["voted_on"]=[(3, self.env.user.id, 0)]

