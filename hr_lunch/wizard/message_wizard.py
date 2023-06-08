from odoo import models, fields, api
import base64
import os

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'
    _description = 'Message Wizard'

    image = fields.Binary(string='Image')
    logo = fields.Binary(string='Logo') 
    text1 = fields.Text(string="Text 1")
    text2 = fields.Text(string="Text 2")
    text3 = fields.Text(string="Text 3")
    text4 = fields.Text(string="Text 4")
    text5 = fields.Text(string="Text 5")
    show_wizard = fields.Boolean(string="Show Wizard", default=True)
    user_id = fields.Many2one('res.users', string="User")


    @api.model
    def default_get(self, fields_list):
        defaults = super(MessageWizard, self).default_get(fields_list)

        defaults.update({
            'text1': "Vertels vote module - VOTE EVERY FRIDAY!\n",
            'text2': "Everyone goes to the winning restaurant or choose to order by take away.\n",
            'text3': "The restaurant with green color in kanban view has the no.1 ranking!\n",
            'text5': "The restaurant with yellow color in kanban view has second best ranking!\n",
            'text4': "Company: Vertel",
            'image': self.get_encoded_image('icon.png'),
            'logo': self.get_encoded_image('logo.png'),
        })
        return defaults

    def get_encoded_image(self, image_filename):
        module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        image_path = os.path.join(module_path, 'static', 'src', 'img', image_filename)

        with open(image_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        return encoded_image

    def action_ok(self):
        return {'type': 'ir.actions.act_window_close'}

    def _open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Welcome to Hr_lunch!',
            'res_model': 'message.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self.env.context,
        }
