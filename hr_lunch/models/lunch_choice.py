from odoo import api, models, fields, _
import logging
import validators
import datetime
import random
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class lunchChoiceWinnerHistory(models.Model):
    _name = "lunch.choice.winner.history"
    _description = "History of winners"
    _order = "date desc"

    date = fields.Date(compute="_compute_date", store=True)
    winner_id = fields.Many2one(comodel_name="lunch.choice", string="Winner", required=True, ondelete="cascade")
    winner_restaurant = fields.Char(string="Name of restaurant", related="winner_id.rest_name")
    winner_url = fields.Char(string="Url to menu", related="winner_id.link_to_menu")
    winner_address = fields.Char(string="Address", related="winner_id.rest_address")
    winner_highscore = fields.Integer(string="Amounts of wins", related="winner_id.highscore")
    winner_tags = fields.Many2many(comodel_name='lunch.tag', string='Tags', related="winner_id.tag_ids")


    @api.depends("winner_id")
    def _compute_date(self):
        self.date = datetime.datetime.now()

    

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
    _translate = True

    rest_name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="Url to menu")
    show_vote_button = fields.Boolean(compute="_show_vote_button")
    show_clear_button = fields.Boolean(compute="_show_clear_button", store=True)
    voter_amount = fields.Integer(compute="list_all_voters", store=True)
    show_menu_button = fields.Boolean(compute="_show_menu_button")
    rest_address = fields.Char(string="Address", default="\u00A0")
    line_ids = fields.One2many(comodel_name="lunch.choice.line", inverse_name="parent_id")
    winner_ids = fields.One2many(comodel_name="lunch.choice.winner.history", inverse_name="winner_id")
    highscore = fields.Integer(string="Amounts of wins", readonly=True)
    daily_rest = fields.Boolean(string="Daily restaurant", default=False)
    color = fields.Integer(compute="compute_color",string="Color")
    tag_ids = fields.Many2many(comodel_name='lunch.tag', string='Tags')
    daily_winner_rest = fields.Boolean(string="Daily Winner", default=False)
    show_take_away_button = fields.Boolean(compute="_show_take_away_button")

    _sql_constraints = [
        ('rest_name_unique',
            'UNIQUE(rest_name)',
            "Restaurant name already exists!"),
    ]

    def clear_all(self):
        self.line_ids.unlink()


    def clear_self_vote(self):
        self.line_ids.filtered(lambda r: r.vote_user == self.env.user).unlink()


    def valid_url(self) -> bool:
        url_string = str(self.link_to_menu).strip()
        if not url_string:
            self.link_to_menu = ""
            return False
        if url_string.lower() == "false":
            self.link_to_menu = ""
        elif not url_string.startswith("http://") and not url_string.startswith("https://"):
            self.link_to_menu = "https://" + url_string
        result = validators.url(url_string)
        if isinstance(result, validators.ValidationFailure):
            return False
        return result


    def open_url(self):
        logging.warning("Opening url")
        for record in self:
            if record.valid_url():
                return {
                    "type": "ir.actions.act_url", 
                    "url": record.link_to_menu,
                    "target": "new"
                }
        return "Invalid URL"
            

    @api.depends('link_to_menu', 'show_menu_button')
    def _show_menu_button(self):
        for rec in self:
            for rec in self:
                rec.show_menu_button = rec.valid_url()

      
    @api.depends('line_ids')
    def list_all_voters(self):
        self.voter_amount=len(self.line_ids)

    
    @api.depends('line_ids')
    def vote_random_restaurant(self):
        restaurants = self.search([])
        if restaurants:
            random_restaurant = random.choice(restaurants)
            random_restaurant.voted()
        return {
        'type': 'ir.actions.client',
        'tag': 'reload'
        }
        

    
    def random_rest(self):
        restaurants = self.search([('daily_rest', '=', True)])
        if restaurants:
            restaurant_ids = [restaurant.id for restaurant in restaurants]
            random.shuffle(restaurant_ids)
            random_restaurants = self.browse(restaurant_ids[:3])
            return {
                'name': 'Random Restaurants',
                'type': 'ir.actions.act_window',
                'res_model': 'lunch.choice',
                'view_mode': 'tree,form,kanban',
                'domain': [('id', 'in', random_restaurants.ids)],
            }
        else:
            raise UserError("No restaurants found")


    def daily_procedure(self):
        restaurants = self.env["lunch.choice"].search([])
        restaurants.write({'daily_rest': False})
        restaurants.write({'daily_winner_rest': False})
        random_restaurants = restaurants.sorted(lambda r: random.random())[:3]
        random_restaurants.write({'daily_rest': True})


    @api.model
    def show_top_three(self):
        lunch_records = self.search([])
        top_three_restaurants = lunch_records.filtered(lambda r: len(r.line_ids) > 0).sorted(key=lambda r: len(r.line_ids), reverse=True)[:3]
        if top_three_restaurants:
            return {
                'name': 'Top 3 Restaurants',
                'type': 'ir.actions.act_window',
                'res_model': 'lunch.choice',
                'view_mode': 'tree,form,kanban',
                'domain': [('id', 'in', top_three_restaurants.ids)],
            }
        else:
            raise UserError("No restaurants with votes found")


    @api.onchange('line_ids')
    def _show_vote_button(self):       
        for lunch in self.env["lunch.choice"].search([]):
            lunch.show_vote_button = True
            lunch.show_clear_button = False
            for line in lunch.line_ids:
                if line.vote_user.id == self.env.user.id:
                    lunch.show_vote_button = False
                    lunch.show_clear_button = True


    @api.onchange('line_ids')
    def _show_clear_button(self):
        for lunch in self.env["lunch.choice"].search([]):
            if lunch.show_vote_button:
                lunch.show_clear_button = False
            else:
                lunch.show_clear_button = True


    @api.depends('line_ids')
    def voted(self):
       user_votes = self.env['lunch.choice.line'].search([('vote_user', '=', self.env.user.id)])
    #   UNCOMMENT TO PREVENT ADMIN USERS FROM VOTING
    #    if self.env.user.has_group('base.group_erp_manager'):
    #     raise UserError("Admin users are not allowed to vote.")
       if len(user_votes) >= 3:
           raise UserError("You've already voted for 3 restaurants")
       else:
           selected_restaurants = user_votes.mapped('parent_id')
           if self in selected_restaurants:
               raise UserError("You've already voted for this restaurant")
           else:
               self.env['lunch.choice.line'].create({'vote_user': self.env.user.id, 'parent_id': self.id})

    
    @api.model
    def compute_color(self):
        restaurants = self.search([])
        sorted_restaurants = restaurants.sorted('highscore', reverse=True)
        second_best_highscore = sorted_restaurants[1].highscore if len(sorted_restaurants) > 1 else 0
        
        for restaurant in restaurants:
            if restaurant.highscore == sorted_restaurants[0].highscore:
                restaurant.color = 10
            elif restaurant.highscore == second_best_highscore:
                restaurant.color = 3
            else:
                restaurant.color = 0

    def daily_rest_winner(self):
        restaurants = self.env["lunch.choice"].search([])
        if not restaurants:
            return
        winner_restaurant = None
        winner_vote_count = 0
        for restaurant in restaurants:
            vote_count = len(restaurant.line_ids)
            if vote_count > winner_vote_count:
                winner_restaurant = restaurant
                winner_vote_count = vote_count
        if winner_restaurant:
            winner_restaurant.highscore +=1
            winner_restaurant.daily_winner_rest = True

        self.add_to_winner_history()

    @api.onchange('line_ids')
    def _show_take_away_button(self):
        for lunch in self.env["lunch.choice"].search([]):
            if lunch.daily_winner_rest: #add 'and not self.env.user.has_group('base.group_erp_manager')' to prevent admin users from ordering
                lunch.show_take_away_button = True
            else:
                lunch.show_take_away_button = False


    @api.depends('winner_ids')
    def add_to_winner_history(self):
        for restaurant in self.env["lunch.choice"].search([]):
            if restaurant.daily_winner_rest:
                self.env['lunch.choice.winner.history'].create({'winner_id': restaurant.id, 'winner_restaurant': restaurant.rest_name})

