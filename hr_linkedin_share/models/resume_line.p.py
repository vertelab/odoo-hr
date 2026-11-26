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
            # display_type is gone from hr.resume.line in 19.0: the selection
            # that carried 'certification' was replaced by line_type_id, and
            # hr_skills_survey now sets resume_type_certification there.
            # #if VERSION >= "19.0"
            if cert.line_type_id == self.env.ref('hr_skills_survey.resume_type_certification', raise_if_not_found=False):
            # #else
            if cert.display_type == "certification":
            # #endif
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
                    # #if VERSION >= "20.0"
                    certUrl= cert.url_to_cert if cert.url_to_cert else self.env['ir.config_parameter'].get_str('web.base.url'),
                    # #else
                    certUrl= cert.url_to_cert if cert.url_to_cert else self.env['ir.config_parameter'].get_param('web.base.url'),
                    # #endif
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