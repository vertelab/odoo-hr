# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request

# ~ import logging
# ~ _logger = logging.getLogger(__name__)
# ~ raise Warning(_('Start period should precede then end period.'))
# ~ _logger.debug('Create a %s with vals %s', self._name, vals)

class AboutUsController(http.Controller):

    @http.route('/aboutus/', auth='public', type='http', website=True)
    def about_us(self, **kw):
        
        # ~ _logger.debug('n\n\n\n\is_publisher = request.env.user.has_group %s' , request.env.user.has_group('website.group_website_publisher') )
        is_publisher = request.env.user.has_group('website.group_website_publisher')
        employees_domain = [] if is_publisher else [('website_published', '=', True)]

        values={
            'employee_ids' : request.env['hr.employee'].sudo().search(employees_domain),
            # ~ 'employee_ids' : request.env['hr.employee'].search([]),
        }
        return request.render("hr_website_about_us.aboutus", values)

