from odoo import models, fields

class LunchTag(models.Model):
    _name = 'lunch.tag'
    _description = 'Lunch Tag'

    name = fields.Char(string='Tag Name', required=True)
    tag_color = fields.Integer(string="Color Index")
    # A tag used to be one string holding both a cuisine and a format
    # ("libanesiska restaurang, Lunchbuffé"). The type keeps them apart, so a
    # cuisine can be filtered without dragging a format along.
    tag_type = fields.Selection(
        selection=[
            ('cuisine', 'Cuisine'),
            ('format', 'Format'),
            ('price', 'Price'),
        ],
        string="Tag type",
        required=True,
        default='cuisine',
    )

    _sql_constraints = [
            ('tag_name_unique',
                'UNIQUE(name)',
                "Tag already exists!"),
        ]