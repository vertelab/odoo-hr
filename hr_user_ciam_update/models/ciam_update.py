import json
from odoo import models, fields, api, _
from odoo.exceptions import Warning, AccessError
import logging

_logger = logging.getLogger(__name__)


class CIAMUpdate(models.TransientModel):
    _name = 'hr.employee.user.ciam'

    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('active_id'))

    def action_update_ciam(self):
        granted = False
        for group in ('base.group_system',
                      'base_user_groups_dafa.group_dafa_org_admin_write',
                      'base_user_groups_dafa.group_dafa_employees_write'):
            if self.env.user.has_group(group):
                granted = True
                break
        if not granted:
            raise AccessError(_("You are not allowed to sync users to CIAM."))
        if not self.employee_id.user_id:
            raise Warning(_("The employee has no user information. Please assign user groups."))
        ciam_id = self.env['ciam.client.config'].sudo().search([], limit=1)
        if ciam_id:
            data = {
                'personNr': self.employee_id.ssnid,
                'firstName': self.employee_id.firstname,
                'lastName': self.employee_id.lastname,
                'eMail': self.employee_id.user_id.email,
                'username': self.employee_id.user_id.login,
                'status': '1'
            }
            response = ciam_id.user_add(data)

            # Log this change
            try:
                user = self.env.user
                groups = self.env['res.groups'].search([('users', '=', user.id)])

                data['password'] = "<removed>" # hide password before logging

                data_additional = {
                    "user": user.login,
                    "groups": groups.mapped('display_name'),
                }

                _logger.info(json.dumps({**data, **data_additional}, default=str))
            except:
                pass

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

            legacy_no = self.env['ir.config_parameter'].sudo().get_param('dafa.legacy_no')
            if not legacy_no:
                raise Warning("No dafa.legacy_no in system parameters.")
            data = {
                'customerNr': legacy_no,
                'exactMatch': 'true', #do not search for partial matches
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
