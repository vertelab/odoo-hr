from odoo import models, fields, api, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    sale_partner_ids = fields.One2many("res.partner", 'employee_id', "My Customers", compute='get_partners')

    def get_partners(self):
        sale_obj = self.env['sale.order']
        for employee in self:
            if employee.user_id:
                sales = sale_obj.search([('user_id', '=', employee.user_id.id)])
                partners = sales.mapped('partner_id')
                employee.sale_partner_ids = [(4, partner.id) for partner in partners]


class SalePartner(models.Model):
    _inherit = 'res.partner'

    employee_id = fields.Many2one('hr.employee')
