from odoo import http, SUPERUSER_ID
from odoo.http import request
import logging
import json
import traceback
_logger = logging.getLogger("TelinfyDebug")
SOURCE_ID_WHATSAPP = 81
import random

class TelinfyApi(http.Controller):

    # Event 1: Incoming call landed on server
    @http.route('/telinfy/whatsapp/webhook', type='json', auth='none', methods=["POST"], csrf=False)
    def incoming_landed(self, *args, **post):
        post_data: dict = request.httprequest.json
        _logger.error(f'Webhook Data: {post_data}')
        if post_data.get('messages'):
            messages = post_data.get('messages')
            for message in messages:
                if message.get('type','')=='text':
                    superuser = request.env['res.users'].sudo().browse(SUPERUSER_ID)
                    from_number = message['from']
                    lead_name = post_data.get('contacts')[0]['profile']['name']
                    lead = request.env['crm.lead'].sudo().search([('phone','like',from_number), ('phone','!=',False)], limit=1)
                    if lead:
                        _logger.info(f'Lead already exists for this whatsapp contact {lead_name}, {from_number}.')
                    else:
                        sales_team = False
                        sales_teams = request.env['crm.team'].sudo().search([])
                        if sales_teams:
                            random_choice = random.choice(range(len(sales_teams)))
                            sales_team = sales_teams[random_choice]
                        sales_team = sales_teams[0] #comment this line to bypass team assignment
                        lead = request.env['crm.lead'].with_user(superuser).create({
                        'name': f'[WhatsApp] {lead_name}',
                        'partner_id': request.env['res.partner'].sudo().create({'name': lead_name, 'company_type': 'person', 'phone': from_number}).id,
                        'phone': from_number,
                        'user_id': False,
                        'team_id': sales_team.id,
                        'description': f"<p>{message['text']['body']}</p>",
                        'type': 'lead',
                        'source_id': SOURCE_ID_WHATSAPP,
                        })
                        _logger.info(f'Lead {lead_name}, {from_number} created successfully!')
                    # Add message to chatter
                    lead.write({'has_unread_whatsapp': True})
                    lead.message_post(body=f"WhatsApp Message: {message['text']['body']}")
                    
                    # Send notification to assigned salesperson
                    if lead.user_id:
                        lead.message_subscribe([lead.user_id.partner_id.id])
                        notification = {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': 'New WhatsApp Message',
                                'message': f'New message from {lead_name}',
                                'type': 'info',
                                'sticky': False,
                            }
                        }
                        lead.env['bus.bus']._sendone(lead.user_id.partner_id, 'notification', notification)
                else:
                    # Add message to chatter for non-text messages
                    lead.message_post(body=f"WhatsApp Message: {message}")
        return json.dumps({'status': 'success',})
