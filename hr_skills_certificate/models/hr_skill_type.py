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


class HrSkillType(models.Model):
    """Mark a skill type as a certification type.

    Odoo treats certifications as CV lines with display_type=certification,
    but a company that tracks certifications as skills needs to know which
    skill types carry expiry dates. Without the flag, every skill would be
    checked for expiry and the overview would be noise.

    The flag lives here rather than in a customer module because it is
    generic: any industry bridge that seeds certifications needs it.
    """

    _inherit = 'hr.skill.type'

    is_certification = fields.Boolean(
        string='Is Certification Type',
        help='Marks this skill type as certifications with expiry dates. '
             'Only types with this flag are checked for expiry and shown '
             'in the certification overview.',
    )
