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

from odoo import fields, models


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
