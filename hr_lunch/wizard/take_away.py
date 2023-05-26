from odoo import api, models, fields, _
from datetime import datetime, date

class TakeAwayWizard(models.TransientModel):
    _name = "take.away.wizard"
    _description = "Take Away Wizard"


    rest_name = fields.Char(string="Restaurant name")
    link_to_menu = fields.Char(string="Link to restaurant")
    input_food = fields.Char(string="Food")
    input_drink = fields.Char(string="Drink")
    input_other = fields.Char(string="Other")

    top_3_food_wiz = fields.Char(string="Top 3 Food Items")
    is_readonly = fields.Boolean(string = "Edit Order", default = False)
    edit_order_active = fields.Boolean(string = "Edit Order", default = False)


    @api.model
    def default_get(self, fields):
        res = super(TakeAwayWizard, self).default_get(fields)

        lunch_choice = self.env['lunch.choice'].search([('daily_winner_rest', '=', True)], limit=1)
        rest_name = lunch_choice.rest_name if lunch_choice else False
        link_to_menu = lunch_choice.link_to_menu if lunch_choice else False
        res['rest_name'] = rest_name
        res['link_to_menu'] = link_to_menu

        if lunch_choice:
            top_3_food_new = self.env['lunch.choice.order'].search([('restaurant_id', '=', lunch_choice.id)], order='id desc', limit=1).top_3_food
            res['top_3_food_wiz'] = top_3_food_new

        existing_order = self.env['lunch.choice.order'].search([
            ('user_id', '=', self.env.user.id),
            ('restaurant_id', '=', lunch_choice.id),
            ('create_date', '>=', datetime.combine(date.today(), datetime.min.time())),
        ], limit=1)
        res['input_food'] = existing_order.food
        res['input_drink'] = existing_order.drink
        res['input_other'] = existing_order.other

        if existing_order:
            res['is_readonly'] = True

        return res
    
    def create_order(self):
        order_values = {
            'restaurant_id': self.env['lunch.choice'].search([('daily_winner_rest', '=', True)], limit=1).id,
            'user_id': self.env.user.id,
            'food': self.input_food,
            'drink': self.input_drink,
            'other': self.input_other,
        }
        lunch_choice = self.env['lunch.choice'].search([('daily_winner_rest', '=', True)], limit=1)
        existing_order = self.env['lunch.choice.order'].search([
            ('user_id', '=', self.env.user.id),
            ('restaurant_id', '=', lunch_choice.id),
            ('create_date', '>=', datetime.combine(date.today(), datetime.min.time())),
        ], limit=1)
        if existing_order:
            existing_order.write(order_values)
            return {'type': 'ir.actions.act_window_close'}
        else:
            self.env['lunch.choice.order'].create(order_values)
            return {'type': 'ir.actions.act_window_close'}
        
    
    def edit_order(self):
        self.write({
        'is_readonly': False,
        'edit_order_active': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'take.away.wizard',
            'name': 'Take Away',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }
    
    
