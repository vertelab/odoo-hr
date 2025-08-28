from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class HrResumeLine(models.Model):

    _inherit = 'hr.resume.line'

    linkedin_cert_url = fields.Char(compute="_compute_linkedin_cert_url")
    url_to_cert = fields.Char()

    def _compute_linkedin_cert_url(self):
        for cert in self:
            if cert.display_type == "certification":
                issueYear = cert.date_start.year 
                issueMonth = cert.date_start.month 
                expirationYear = cert.date_end.year
                expirationMonth = cert.date_end.month
                linkedin_url = "https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME&" \
                "name={name}&organizationName={organizationName}&issueYear={issueYear}&issueMonth={issueMonth}&" \
                "expirationYear={expirationYear}&expirationMonth={expirationMonth}&certUrl={certUrl}&certId={certId}"
                url = linkedin_url.format(
                    name=cert.name, 
                    organizationName=cert.employee_id.company_id.name,
                    issueYear=issueYear, 
                    issueMonth=issueMonth, 
                    expirationYear=expirationYear, 
                    expirationMonth=expirationMonth,
                    certUrl= cert.url_to_cert if cert.url_to_cert else self.env['ir.config_parameter'].get_param('web.base.url'),
                    certId=cert.id)
                cert.linkedin_cert_url = url
            else:
                cert.linkedin_cert_url = False

    def action_add_cert_to_linkedin(self):
        if self.linkedin_cert_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.linkedin_cert_url, 
                'target': 'new',
            }