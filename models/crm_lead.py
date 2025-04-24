from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    has_unread_whatsapp = fields.Boolean(string='Unread WhatsApp', default=False)
    whatsapp_message_ids = fields.One2many('mail.message', 'res_id', domain=[('whatsapp_message', '=', True)], string='WhatsApp Messages')
    whatsapp_message_count = fields.Integer(compute='_compute_whatsapp_message_count')

    def _compute_whatsapp_message_count(self):
        for record in self:
            record.whatsapp_message_count = len(record.whatsapp_message_ids)

    def mark_whatsapp_read(self):
        self.has_unread_whatsapp = False
        return True
