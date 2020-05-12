# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class HrTimesheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def button_confirm(self):
        res = super(HrTimesheet, self).button_confirm()
        for sheet in self:
            message_id = sheet.message_post(body=_('Approve time report'), subject="%s %s" % (sheet.employee_id.name, sheet.display_name), type='comment',subtype="mail.mt_comment")
            message = self.env["mail.message"].browse(message_id)
            message.sudo(sheet.employee_id.parent_id.user_id.id).set_message_starred(True)
        return res