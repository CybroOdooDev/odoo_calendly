# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from datetime import datetime
from odoo.tools import safe_eval
import logging

_logger = logging.getLogger(__name__)


class WebHook(http.Controller):
    @http.route(['/create'], type='json', auth='public', methods=['GET', 'POST'], csrf=False)
    def get_calendly_webhook_url(self, *args, **kwargs):
        if request.jsonrequest.get('event') == 'invitee.created':
            _logger.info(
                "----------request.jsonrequest--------------------------%s",
                request.jsonrequest)
            event_type = request.jsonrequest.get('payload').get(
                'event_type')
            event = request.jsonrequest.get('payload').get('event')
            invitee = request.jsonrequest.get('payload').get('invitee')
            start = event.get('start_time')
            end = event.get('end_time')
            start_time = datetime.fromisoformat(start).replace(
                tzinfo=None)
            end_time = datetime.fromisoformat(end).replace(tzinfo=None)
            partner = request.env['res.partner'].sudo().search(
                [('email', '=', invitee.get('email'))],
                limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create(
                    {'name': invitee.get('name'),
                     'email': invitee.get('email')})
            user_partner = request.env['res.partner'].sudo().search(
                [('email', '=',
                  event.get('extended_assigned_to')[0].get('email'))],
                limit=1)
            partner_ids = []
            attendee_ids = []
            if partner:
                new_event = request.env['calendar.event'].sudo().create({
                        'name': event_type.get('name'),
                        'start': start_time,
                        'stop': end_time,
                        'calendly_id': event.get('uuid'),
                        'duration': event_type.get('duration'),
                    })
                partner_ids.append(partner[0].id)
                odoo_attendee = request.env[
                    'calendar.attendee'].sudo().create({
                    'partner_id': partner.id,
                    'event_id': new_event.id,
                    'email': partner.email,
                    'common_name': partner.name,

                    })
                attendee_ids.append(odoo_attendee.id)
                if user_partner:
                    partner_ids.append(user_partner[0].id)
                    odoo_attendee = request.env[
                        'calendar.attendee'].sudo().create({
                        'partner_id': user_partner.id,
                        'event_id': new_event.id,
                        'email': user_partner.email,
                        'common_name': user_partner.name,
                        'state': 'accepted'
                        })
                    attendee_ids.append(odoo_attendee.id)
                new_event.write({
                    'attendee_ids': [[6, 0, attendee_ids]],
                    'partner_ids': [[6, 0, partner_ids]]
                })
        if request.jsonrequest.get('event') == 'invitee.canceled':
            event = request.jsonrequest.get('payload').get('event')
            search_event = request.env['calendar.event'].sudo().search(
                [('calendly_id', '=', event.get('uuid'))], limit=1)
            if search_event:
                search_event.unlink()
