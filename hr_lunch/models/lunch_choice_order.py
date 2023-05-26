from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError

class LunchChoiceOrder(models.Model):
    _name = 'lunch.choice.order'
    _description = 'Lunch Choice Order'

    restaurant_id = fields.Many2one('lunch.choice', string='Restaurant')
    user_id = fields.Many2one('res.users', string="User",default=lambda self: self.env.user.id)
    food = fields.Char(string="Food")
    drink = fields.Char(string="Drink")
    other = fields.Char(string="Other")
    top_3_food = fields.Char(string="Top 3 Food", compute='_compute_top_3_food', store=True)


    @api.onchange('restaurant_id')
    def onchange_restaurant_id(self):
        lunch_choice = self.env['lunch.choice'].search([('daily_winner_rest', '=', True)], limit=1)
        if lunch_choice:
            self.restaurant_id = lunch_choice.id


    @api.depends('restaurant_id')
    def _compute_top_3_food(self):
        for order in self:
            top_3_food = ''
            if order.restaurant_id:
                restaurant_id = order.restaurant_id.id
                lunch_choice = self.env['lunch.choice'].search([('id', '=', restaurant_id), ('daily_winner_rest', '=', True)], limit=1)
                if lunch_choice:
                    order_ids = self.search([('restaurant_id', '=', restaurant_id)])
                    food_counts = {}
                    for order_id in order_ids:
                        if order_id.food:
                            food_counts[order_id.food] = food_counts.get(order_id.food, 0) + 1
                    top_3 = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    top_3_food = ', '.join([food[0] for food in top_3])
            order.top_3_food = top_3_food




    def _compute_domain(self):
        domain = [
            ('restaurant_id.daily_winner_rest', '=', True),
            ('create_date', '>=', fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.now()).replace(hour=0, minute=0, second=0)))
        ]
        return domain

    def open_take_away_orders(self):
        domain = self._compute_domain()
        lunch_choice = self.env['lunch.choice'].search([('daily_winner_rest', '=', True)], limit=1)
        if not lunch_choice:
            raise UserError("No restaurant have won yet!")
        else:    
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Take Away Order for ' + lunch_choice.rest_name,
                'res_model': 'lunch.choice.order',
                'view_mode': 'tree,form',
                'domain' : domain
            }
            return action



