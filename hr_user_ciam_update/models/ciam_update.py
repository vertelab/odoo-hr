import json
from odoo import models, fields, api, _
from odoo.exceptions import Warning
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
            response = ciam_id.user_add(data)
            res_dict = json.loads(response)
            data = res_dict.get('data')
            user_id = False
            user_error = ""
            if data:
                user_id = data[0].get('userId')
            else:
                user_error = "%s" % res_dict.get('status').get('message')
            data = {
                'customerNr': self.employee_id.address_id.legacy_no
            }
            response = ciam_id.customer_get(data)
            res_dict = json.loads(response)
            data = res_dict.get('data')
            cust_id = False
            cust_error = ""
            if data:
                cust_id = data[0].get('custId')
            else:
                cust_error = "%s" % res_dict.get('status').get('message')
            if cust_id and user_id:
                data = {
                    'userId': user_id,
                    'custId': cust_id,
                    'roleName': 'DAFA_COACH'
                }
                ciam_id.role_assign(data)    
            else:
                error = "%s %s" %(user_error, cust_error)
                raise Warning(error)
