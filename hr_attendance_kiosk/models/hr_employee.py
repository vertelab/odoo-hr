from odoo import models, fields, api, exceptions, _

import traceback
import logging
import erppeek

_logger = logging.getLogger(__name__)

clients = {}
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
        
    @api.model
    def get_client(self):
        client = clients.get(self.env.cr.dbname)
        


        if client:
            # Checks if client can make a request. If not creates a new client. (Hopefully)
            try:
                client.model('hr.employee').search([('id', '=', 0)])
                return client
            except:
                pass 

        # Connecting to database with underlying parameters
        server_url = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.server_url1')
        database_name = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.database_name1')
        username = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.username1')
        password = self.env['ir.config_parameter'].sudo().get_param('hr_attendance.password1')
        try:
            client = erppeek.Client(server_url, database_name, username, password)
            clients[self.env.cr.dbname] = client
            return client
        except:
            _logger.error("Couldnt establish a network connection. \n %s"%traceback.format_exc())


    @api.model
    def attendance_scan(self, barcode):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding employee.
            Returns either an action or a warning.
        """
        match = None
        
        # Retrieves the information from RFID tag and matches the correct employee in database
        client = self.get_client()
        if client: 
            try:
                
                employee_id = client.search('hr.employee', [('barcode', '=', barcode)])
                match = client.model('hr.employee').browse(employee_id)
            except:
                _logger.warn("Something went wrong: \n %s"%traceback.format_exc())
                return {'warning': _("Connection to server unestablished.")}
        else:
            return {'warning': _("No config parameter found for either server_url or password.")}
        
        # Returns an action to either check in or out the employee, if none matches return error message 
        res = match and match.attendance_action('hr_attendance.hr_attendance_action_kiosk_mode') or \
            {'warning': _('No employee corresponding to barcode %(barcode)s') % {'barcode': barcode}}
        return res   
