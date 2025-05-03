from odoo import http, SUPERUSER_ID
from odoo.http import request
import logging
import json
import traceback

_logger = logging.getLogger("TelinfyDebug")

class TelinfyApi(http.Controller):

    @http.route('/telinfy/whatsapp/webhook', type='json', auth='none', methods=["POST"], csrf=False)
    def incoming_landed(self, *args, **post):
        return self._process_whatsapp_webhook("WhatsApp API", *args, **post)

    @http.route('/telinfy/whatsapp2/webhook', type='json', auth='none', methods=["POST"], csrf=False)
    def incoming_landed_whatsapp2(self, *args, **post):
        return self._process_whatsapp_webhook("WhatsApp API 2", *args, **post)
    
    def _process_whatsapp_webhook(self, source_name, *args, **post):
        try:
            post_data: dict = request.httprequest.json
            _logger.error(f'Webhook Data: {post_data}')
            
            if post_data.get('messages'):
                messages = post_data.get('messages')
                for message in messages:
                    if message.get('type','')=='text':
                        superuser = request.env['res.users'].sudo().browse(SUPERUSER_ID)
                        from_number = message['from']
                        lead_name = post_data.get('contacts')[0]['profile']['name']
                        
                        # Get or create source
                        source = self._get_or_create_source(source_name)
                        
                        # Search for lead with proper sudo
                        lead = request.env['crm.lead'].sudo().search([('phone','like',from_number), ('phone','!=',False)], limit=1)
                        
                        if not lead:
                            # Create new lead if not found
                            sales_team = request.env['crm.team'].sudo().search([], limit=1)
                            lead = request.env['crm.lead'].with_user(superuser).create({
                                'name': f'[{source_name}] {lead_name}',
                                'partner_id': request.env['res.partner'].sudo().create({
                                    'name': lead_name, 
                                    'company_type': 'person', 
                                    'phone': from_number
                                }).id,
                                'phone': from_number,
                                'user_id': False,
                                'team_id': sales_team.id if sales_team else False,
                                'description': f"<p>{message['text']['body']}</p>",
                                'type': 'lead',
                                'source_id': source.id,
                            })
                            _logger.info(f'Lead {lead_name}, {from_number} created successfully!')
                        
                        # Post message with proper user context
                        if lead:
                            with request.env.cr.savepoint():
                                # Post message without whatsapp flag first
                                msg = lead.with_user(superuser).message_post(
                                    body=f"{source_name} Message: {message['text']['body']}",
                                    message_type='comment'
                                )
                                # Update message with whatsapp flag
                                request.env['mail.message'].sudo().browse(msg.id).write({
                                    'whatsapp_message': True
                                })
                                lead.has_unread_whatsapp = True
                                _logger.info(f'Message posted to lead {lead_name}')
                    else:
                        _logger.warning(f'Non-text message received: {message}')
                        
            return json.dumps({'status': 'success'})
        except Exception as e:
            _logger.error(f'Error in webhook: {str(e)}\n{traceback.format_exc()}')
            return json.dumps({'status': 'error', 'message': str(e)})
            
    def _get_or_create_source(self, name):
        """Get a source by name or create it if it doesn't exist"""
        source = request.env['utm.source'].sudo().search([('name', '=', name)], limit=1)
        if not source:
            source = request.env['utm.source'].sudo().create({'name': name})
        return source
