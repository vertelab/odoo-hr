import json
import logging
import random
import string
from odoo.exceptions import Warning, AccessError

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

CIAM_STATUS_OK = 0
CIAM_STATUS_OBJECT_NOT_FOUND = '-3'


class CIAMUpdate(models.TransientModel):
    _name = "hr.employee.user.ciam"
    _description = "HR Employee User Ciam"

    employee_id = fields.Many2one(
        "hr.employee", default=lambda self: self.env.context.get("active_id")
    )

    def action_update_ciam(self):
        # validate that we have everything we need
        granted = False
        for group in (
                "base.group_system",
                "base_user_groups_dafa.group_dafa_org_admin_write",
                "base_user_groups_dafa.group_dafa_employees_write",
        ):
            if self.env.user.has_group(group):
                granted = True
                break
        if not granted:
            raise AccessError(_("You are not allowed to sync users to CIAM."))
        if not self.employee_id.user_id:
            raise Warning(
                _("The employee has no user information. Please assign user groups.")
            )
        if not self.employee_id.ssnid:
            raise Warning(_("The employee has no social security number."))
        legacy_no = self.env["ir.config_parameter"].sudo().get_param("dafa.legacy_no")
        if not legacy_no:
            raise Warning(_("No dafa.legacy_no in system parameters."))
        ciam_client = self.env["ciam.client.config"].sudo().search([], limit=1)
        if ciam_client:
            # search for user in CIAM
            user_get_data = {
                "username": self.employee_id.user_id.login,
            }
            user_get_response = ciam_client.user_get(user_get_data)
            user_get_res_dict = json.loads(user_get_response)
            user_get_response_code = user_get_res_dict.get("status", user_get_res_dict.get("cause", {})).get("code")
            if not user_get_response_code in (
                    CIAM_STATUS_OK,
                    CIAM_STATUS_OBJECT_NOT_FOUND,
            ):
                raise Warning(
                    _("Error in communication with CIAM. Answer: %s") % user_get_res_dict
                )

            user_data = {
                "personNr": self.employee_id.ssnid,
                "firstName": self.employee_id.firstname,
                "lastName": self.employee_id.lastname,
                "eMail": self.employee_id.user_id.email,
                "username": self.employee_id.user_id.login,
                "status": "1",
            }

            if not self.env["ir.config_parameter"].sudo().get_param("dafa.no_ciam_pw"):
                # Generate a password that will never be used..
                letters = string.ascii_lowercase
                temp_pass = "".join(random.choice(letters) for i in range(12))
                user_data["password"] = temp_pass + "21"

            # create or update user in CIAM
            user_error = ""
            if user_get_response_code == CIAM_STATUS_OK:
                # User already exists in CIAM, update it.
                user_get_data = user_get_res_dict.get("data")[0]
                user_id = user_get_data.get("userId")
                user_data["userId"] = user_id
                # read response from update
                response = ciam_client.user_update(user_data)
                res_dict = json.loads(response)
                status_code = res_dict.get("status", {}).get("code")
                if not status_code == 0:
                    if status_code:
                        user_error = "%s" % res_dict.get("status").get("message")
                    else:
                        user_error = _("Error, no status message available")
            else:  # user_get_response_code == CIAM_STATUS_OBJECT_NOT_FOUND
                # User does not exists in CIAM, create it.
                response = ciam_client.user_add(user_data)
                # read response from create
                res_dict = json.loads(response)
                data = res_dict.get("data")
                user_id = False
                user_error = ""
                if data:
                    user_id = data[0].get("userId")
                else:
                    status = res_dict.get("status")
                    if status:
                        user_error = "%s" % res_dict.get("status").get("message")
                    else:
                        user_error = _("Error, no status message available")

            # Log this change
            try:
                user = self.env.user
                groups = self.env["res.groups"].search([("users", "=", user.id)])
                data["password"] = "<removed>"  # hide password before logging
                data_additional = {
                    "user": user.login,
                    "groups": groups.mapped("display_name"),
                }
                _logger.info(json.dumps({**data, **data_additional}, default=str))
            except:
                pass

            # get customer from CIAM
            data = {
                "customerNr": legacy_no,
                "exactMatch": "true",  # do not search for partial matches
            }
            response = ciam_client.customer_get(data)
            res_dict = json.loads(response)
            data = res_dict.get("data")
            cust_id = False
            cust_error = ""
            if data:
                cust_id = data[0].get("custId")
            else:
                status = res_dict.get("status")
                if status:
                    cust_error = "%s" % res_dict.get("status").get("message")
                else:
                    cust_error = _("Error, no status message available")

            # assign roles in CIAM
            if cust_id and user_id:
                data = {"userId": user_id, "custId": cust_id, "roleName": "DAFA_COACH"}
                ciam_client.role_assign(data)
                # if user is Admin org (write), give them extra role in CIAM
                if self.employee_id.user_id.has_group(
                        "base_user_groups_dafa.group_dafa_org_admin_write"
                ):
                    data["roleName"] = "DAFA_SUPER_ADMIN"
                    ciam_client.role_assign(data)
            else:
                error = "%s %s" % (user_error, cust_error)
                raise Warning(error)
