from odoo import models, fields, api, _


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False,
                                          ondelete='set null',
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                          check_company=True,
                                          help="Analytic account to which this department, its employees and its "
                                               "timesheets are linked. \n"
                                               "Track the costs and revenues of your project by setting this analytic "
                                               "account on your related documents (e.g. sales orders, invoices, "
                                               "purchase orders, vendor bills, expenses etc.).\n"
                                               "This analytic account can be changed on each task individually "
                                               "if necessary.\n"
                                          )
    analytic_account_balance = fields.Monetary(related="analytic_account_id.balance")
