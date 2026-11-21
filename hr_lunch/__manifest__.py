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
    # Version = <Odoo series>.<module version>. The series must match the branch
    # (pfiles-check gate 3 fails otherwise). Bump the module version in ALL
    # branches when the code changes.
    'version': '18.0.3.0',
    'summary': 'Choose where to eat!',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'description': """
    Choose where to eat!
    Manage your dining with your friends! Let the most popular lunch win!
    Programmed by:
        - Emma Jarlvi Skog,
        - Dmitri Iselund,
        - Jimmie Hinke,
        - Ruben Riddarhaage,
        - Andreas Kuylenstierna
    """,
    'sequence': 1,
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-hr/hr_lunch',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-hr',
    # Any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    'data': [
        'wizard/message_wizard_view.xml',
        'wizard/take_away_view.xml',
        'views/assets.xml',
        'views/restaurant_choice_tag.xml',
        'views/restaurant_choice.xml',
        # After restaurant_choice.xml: the discovery menu hangs under
        # options_menu, which that file defines. A forward reference fails on
        # a clean install (it only worked in a database where the menu already
        # existed from an earlier install).
        'wizard/lunch_discovery_view.xml',
        'views/restaurant_choice_order.xml',
        'views/winner_history.xml',
        'views/res_config_settings.xml',
        'security/ir.model.access.csv',
        'security/lunch_security.xml',
        'data/ir_cron.xml',
        'data/ir_cron_menus.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
