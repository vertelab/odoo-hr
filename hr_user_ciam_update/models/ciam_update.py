import json
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class CIAMUpdate(models.TransientModel):
    _name = 'hr.employee.user.ciam'

    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('active_id'))

    def action_update_ciam(self):
        ciam_id = self.env['ciam.client.config'].search([], limit=1)
        if ciam_id:
            data = {
                'personNr': self.employee_id.ssnid,
                'firstName': self.employee_id.firstname,
                'lastName': self.employee_id.lastname,
                'eMail': self.employee_id.user_id.email,
                'username': self.employee_id.user_id.login,
                'password': self.employee_id.user_id.password,
                #'customerNr': self.employee_id., #not implemented yet
                'status': '1'
                }
            _logger.info("Sending data: %s" % data)
            response = ciam_id.user_add(data)
            res_dict = json.loads(response)
            user_id = res_dict.get('data').get('userId')
            data = {
                'customerNr': self.some_variable_idk #711
            }
            response = ciam_id.organization_get(data)
            res_dict = json.loads(response)
            org_id = res_dict.get('data').get('orgId')
            data = {
                'userId': user_id,
                'orgId': org_id,
                'roleName': 'DAFA Coach'
            }
