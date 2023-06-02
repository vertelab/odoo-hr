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

    @api.model
    def default_get(self, fields_list):
        defaults = super(MessageWizard, self).default_get(fields_list)

        # Populate the default values
        defaults.update({
            'text1': "Vertels röstningsmodul - RÖSTA VARJE FREDAG!\n",
            'text2': "Vinnarrestaurangen går alla till, eller väljer take away.\n",
            'text3': "Grön färg i kanban view = Vinnare!\n",
            'text5': "Blå färg i kanban view = Vunnit flest gånger!\n",
            'text4': "Vertel ",
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

    @api.model
    def force_show_wizard(self):
        # Create a record in lunch.choice.user.check to simulate an existing record
        self.env['lunch.choice.user.check'].create({
            'intro_user_ids': self.env.uid
        })
        return self._open_wizard()

    def _should_show_wizard(self):
        check_exist = self.env['lunch.choice.user.check'].search([])
        return len(check_exist) == 0

    def action_ok(self):
        if self._should_show_wizard():
            # Create a record in lunch.choice.user.check to track user interaction
            self.env['lunch.choice.user.check'].create({
                'intro_user_ids': self.env.uid
            })
        return {'type': 'ir.actions.act_window_close'}

    def _open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Välkommen till Hr_lunch!',
            'res_model': 'message.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self.env.context,
        }
