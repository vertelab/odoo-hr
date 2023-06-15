# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate

import logging
import json
#import pyotp
try: 
    import qrcode
except ImportError:
    qrcode = None
try:
   import base64
except ImportError:
   base64 = None
from io import BytesIO

#import io
# ~ _logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'website.seo.metadata', 'website.published.multi.mixin']
    qr_code = fields.Binary('QRcode', compute="_generate_qr")
    #vcard = fields.Binary('QRcode', compute="generate_vcard")
    def _generate_qr(self):
        "method to generate QR code"
        for employee in self:
            street          = employee.company_id.street
            city            = employee.company_id.city
            state     		= employee.company_id.state_id
            postal_code     = employee.company_id.zip
            country     	= employee.company_id.country_id
            
            vcard_data = f"BEGIN:VCARD\r\nVERSION:3.0\r\nN:{employee.name}\r\nORG:{employee.company_id.name}\r\nTITLE:{employee.job_title}\r\nEMAIL;PREF;INTERNET:{employee.work_email}\r\nTEL;WORK;VOICE:{employee.work_phone}\r\nADR;WORK;PREF:;;{street};{city};;{postal_code}\r\nEND:VCARD"
            
            if qrcode and base64:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=5,
                    border=4,
                )                
                qr.add_data(vcard_data)                
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                employee.update({'qr_code':qr_image}) 