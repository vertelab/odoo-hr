# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrResumeLine(models.Model):
    """The certificate itself, on the CV line.

    Odoo already knows the certification type, the dates and whether it is
    still valid. What it lacks is the identifier that lets someone else
    verify the claim — the number on the physical certificate and the body
    that issued it.

    The fields are not restricted to certification lines. An experience or
    education line simply leaves them empty, which is how Odoo treats
    date_end already.
    """

    _inherit = 'hr.resume.line'

    certificate_number = fields.Char(
        string='Certificate Number',
        help='The number printed on the certificate. Needed to verify an '
             'external certification against the issuer.',
    )
    certificate_issuer = fields.Char(
        string='Issued By',
        help='The body that issued the certificate — a training company, '
             'an authority, an industry scheme.',
    )
    certificate_url = fields.Char(
        string='Verification URL',
        help='Where the certificate can be checked, if the issuer offers '
             'an online register.',
    )
    expiration_status = fields.Selection(
        selection=[
            ('valid', 'Valid'),
            ('expiring', 'Expiring Soon'),
            ('expired', 'Expired'),
            ('no_date', 'No Expiry'),
        ],
        string='Status',
        compute='_compute_expiration_status',
        store=True,
        help='Derived from the end date. hr_skills_survey adds its own '
             'three-value version when installed; this one adds no_date so '
             'a certification without an expiry is not reported as valid '
             'forever.',
    )

    @api.depends('date_end')
    def _compute_expiration_status(self):
        today = fields.Date.context_today(self)
        soon = today + relativedelta(days=60)
        for line in self:
            if not line.date_end:
                line.expiration_status = 'no_date'
            elif line.date_end < today:
                line.expiration_status = 'expired'
            elif line.date_end <= soon:
                line.expiration_status = 'expiring'
            else:
                line.expiration_status = 'valid'


class HrSkillType(models.Model):
    """Mark which skill types are certifications.

    A certification is a skill with a proof and an expiry: a licence, a
    course certificate, an authorisation. A plain skill — "speaks German",
    "drives a forklift" — has neither, and treating them the same means
    either every skill gets an expiry field it does not need, or no skill
    gets one.

    The flag lives on the type rather than on the skill so a customer marks
    "Certifications" once and every skill under it inherits the behaviour.
    """

    _inherit = 'hr.skill.type'

    is_certification = fields.Boolean(
        string='Is Certification Type',
        help='Skills of this type are certifications: they have a '
             'certificate number and an expiry date.',
    )
