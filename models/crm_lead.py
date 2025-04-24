from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    has_unread_whatsapp = fields.Boolean(string='Unread WhatsApp', default=False)
    show_whatsapp_indicator = fields.Boolean(compute='_compute_show_whatsapp_indicator')

    @api.depends('has_unread_whatsapp')
    def _compute_show_whatsapp_indicator(self):
        for record in self:
            record.show_whatsapp_indicator = record.has_unread_whatsapp
