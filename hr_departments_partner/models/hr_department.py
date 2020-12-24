from odoo import models, api, fields, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    address_id = fields.Many2many('res.partner', string="Address")

    @api.depends('address_id')
    def _address_details(self):
        for rec in self:
            if rec.address_id:
                if len(rec.address_id) > 1:
                    rec.show_address_details = True
                else:
                    rec.show_address_details = False
                address_list = []
                for record in rec.address_id:
                    address = ''
                    address += record.zip if record.zip else ''
                    address += ' ' + record.street if record.street else ''
                    address += ' ' + record.city if record.city else ''
                    address += ' ' + record.state_id.name if record.state_id else ''
                    address += ' ' + record.country_id.name if record.country_id else ''
                    address_list.append(address)
                rec.address_details = '\n'.join(address_list)

    address_details = fields.Text(string="Address Details", compute=_address_details)
    show_address_details = fields.Boolean(string="Show Address Details", compute=_address_details)

    @api.depends('address_id')
    def _single_address_details(self):
        for rec in self:
            if rec.address_id and len(rec.address_id) == 1:
                for record in rec.address_id:
                    address = ''
                    address += 'Zip: ' + record.zip if record.zip else ''
                    address += '\nStreet: ' + record.street if record.street else ''
                    address += '\nCity: ' + record.city if record.city else ''
                    address += '\nState: ' + record.state_id.name if record.state_id else ''
                    address += '\nCountry: ' + record.country_id.name if record.country_id else ''
                    rec.one_address_detail = address

    one_address_detail = fields.Text(string="Address Details", compute=_single_address_details)
    # street = fields.Char()
    # zip = fields.Char(change_default=True)
    # city = fields.Char()
    # state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
    #                            domain="[('country_id', '=?', country_id)]")
    # country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
