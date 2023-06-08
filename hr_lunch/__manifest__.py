# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2023- Vertel AB (<https://vertel.se>).
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

{
    'name': 'HR: Vote For Lunch',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Choose where to eat!',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'description': """
    Choose where to eat!<br>
    Manage your dining with your friends! Let the most popular lunch win!
    Programmed by:
        - Emma Jarlvi Skog,
        - Dmitri Iselund,
        - Jimmie Hinke,
        - Ruben Riddarhaage,
        - Andreas Kuylenstierna
    """,
    'sequence': 1,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_lunch',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    # Any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    'data': [
        'wizard/message_wizard_view.xml',
        'wizard/take_away_view.xml',
        'views/assets.xml',
        'views/restaurant_choice_tag.xml',
        'views/restaurant_choice.xml',
        'views/restaurant_choice_order.xml',
        'views/winner_history.xml',
        "security/ir.model.access.csv"
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
