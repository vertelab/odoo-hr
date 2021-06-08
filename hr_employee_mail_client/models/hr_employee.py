from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    mail_message_id = fields.One2many('mail.message', 'employee_id', string="Message", compute='_get_partners_message')
    show_messages = fields.Boolean(string="Show Messages", compute='_show_message')

    @api.depends('name')
    def _get_partners_message(self):
        for rec in self:
            messages_ids = self.env['mail.message'].search([('model', '=', 'hr.employee')])
            for record in messages_ids:
                if (record.author_id.id == self.user_id.partner_id.id) or \
                        (self.user_id.partner_id.id in record.partner_ids.ids):
                    rec.mail_message_id = [(4, record.id)]

    @api.depends('mail_message_id')
    def _show_message(self):
        for rec in self:
            if (len(rec.mail_message_id) > 0) and (self.user_id.partner_id.id == self.env.user.partner_id.id):
                rec.show_messages = True
            else:
                rec.show_messages = False


class MailMessage(models.Model):
    _inherit = 'mail.message'

    employee_id = fields.Many2one('hr.employee', string="Employee")
