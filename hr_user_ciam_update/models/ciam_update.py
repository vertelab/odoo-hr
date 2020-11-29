from odoo import models, fields, api, _
import json


class CIAMUpdate(models.TransientModel):
    _name = 'hr.employee.user.ciam'

    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('active_id'))

    def action_update_ciam(self):
        ciam_id = self.env['ciam.client.config'].search([], limit=1)
        if ciam_id:
            headers = ciam_id.get_headers()
            print(headers)

            # Add User
            querystring = {"client_secret": ciam_id.client_secret,
                           "client_id": ciam_id.client_id}
            payload = {'personNr': 1955010127777,
                       'firstName': 'Pelle',
                       'lastName': 'Svensson',
                       'eMail': 'pelle.svensson@bolaget.se',
                       'orgId': 'c4c0b8c2-dccc-4580-b2f9-88b4aeb9bc06',
                       'username': 'pelle.svensson.14',
                       'password': '123',
                       'customerNr': '444', 'status': "1"}

            url = ciam_id.get_url('v1/user/add')
            response = self.request_call(method="POST",
                                         url=url,
                                         payload=json.dumps(payload),
                                         headers=ciam_id.get_headers(),
                                         params=querystring)
            print(response.text)
