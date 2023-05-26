from odoo import models, fields, api
import base64
import os

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'
    _description = 'message wizard'

    authors = fields.Text(string="authors")
    image = fields.Binary(string='image') #Image
    text1 = fields.Text(string="text1")
    text2 = fields.Text(string="text2")
    text3 = fields.Text(string="text3")
    text4 = fields.Text(string="text4")
    text5 = fields.Text(string="text5")


    @api.model
    def default_get(self, fields_list):
        defaults = super(MessageWizard, self).default_get(fields_list)

        relative_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

        # Read the image file and encode it to base64
        with open(relative_path + "/static/description/icon.png", 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        defaults.update({
            'authors': "Emma Jarlvi Skog, Dmitri Iseson, Jimmie Hinke, Ruben Riddarhaage & Andreas Kuylenstierna",
            'name': "Vilken restaurang vinner denna vecka?",
            'text1': "Vertels röstningsmodul - RÖSTA VARJE FREDAG!\n",
            'text2': "Vinnarrestaurangen går alla till, eller väljer take away.\n", 
            'text3': "Grön färg i kanban view = Vinnare!\n",
            'text5': "Blå färg i kanban view = Vunnit flest gånger!\n",
            'text4': "Modulen utvecklad av: ",
            'image': encoded_image,
        })
        return defaults

    name = fields.Char(string="Title", readonly=True , default="Choose your restaurant")

    def action_ok(self):
        # Here we may need some more functions...
        return {'type': 'ir.actions.act_window_close'}
