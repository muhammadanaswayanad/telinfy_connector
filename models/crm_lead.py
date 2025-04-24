from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    has_unread_whatsapp = fields.Boolean(string='Unread WhatsApp', default=False)
