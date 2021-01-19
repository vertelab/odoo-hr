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
                'personNr': self.employee_id.ssnid if self.employee_id.ssnid else "197001011234",
                'firstName': self.employee_id.firstname,
                'lastName': self.employee_id.lastname,
                'eMail': self.employee_id.user_id.email,
                'username': self.employee_id.user_id.login,
                #commented password in case we need it back for testing later
                #password is required for test environments
                #'password': self.employee_id.user_id.password if self.employee_id.user_id.password else "Acctest09",
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
                status = res_dict.get('status')
                if status:
                    user_error = "%s" % res_dict.get('status').get('message')
                else: 
                    user_error = "Error, no status message available"
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
                status = res_dict.get('status')
                if status:
                    cust_error = "%s" % res_dict.get('status').get('message')
                else: 
                    cust_error = "Error, no status message available"
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
