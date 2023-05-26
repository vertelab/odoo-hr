from odoo import models, fields

class LunchTag(models.Model):
    _name = 'lunch.tag'
    _description = 'Lunch Tag'

    name = fields.Char(string='Tag Name', required=True)
    tag_color = fields.Integer(string="Color Index")

    _sql_constraints = [
            ('tag_name_unique',
                'UNIQUE(name)',
                "Tag already exists!"),
        ]