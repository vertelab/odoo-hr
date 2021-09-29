# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class AboutUsController(http.Controller):

    @http.route('/about-us/', auth='public', type='http', website=True)
    def about_us(self, **kw):
        is_publisher = request.env.user.has_group('website.group_website_publisher')
        employees_domain = [] if is_publisher else [('website_published', '=', True)]

        values={
            'employee_ids' : request.env['hr.employee'].sudo().search(employees_domain),
        }
        return request.render("hr_website_about-us.about-us", values)

