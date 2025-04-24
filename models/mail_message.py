from odoo import models, fields

class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    whatsapp_message = fields.Boolean('WhatsApp Message', default=False)
