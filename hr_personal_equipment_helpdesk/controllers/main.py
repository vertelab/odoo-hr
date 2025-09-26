import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskTicketControllerTypes(HelpdeskTicketController):

    def _get_personal_equipment_ids(self):
        personal_equipment_ids = http.request.env["hr.personal.equipment"].with_user(
            request.env.user.id
        ).with_company(
            request.env.company.id
        ).search([
            ("state", "=", "valid"),
            ("employee_id", "=", request.env.user.employee_id.id),
        ])

        return personal_equipment_ids

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        response = super().create_new_ticket(**kw)
        response.qcontext["personal_equipment_ids"] = self._get_personal_equipment_ids()
        return response

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        personal_equipment_id = http.request.env["hr.personal.equipment"].sudo().browse(
            int(kw.get("personal_equipment"))
        ).exists()
        vals["hr_personal_equipment_id"] = personal_equipment_id.id
        return vals


