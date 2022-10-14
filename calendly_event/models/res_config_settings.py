from odoo import fields, models, api, http
from calendly import Calendly
import logging
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    set_calendly = fields.Boolean(
        config_parameter='calendly_event.set_calendly')
    api_key = fields.Char(
        string="API Key",
        config_parameter='calendly_event.api_key')

    @api.constrains('api_key')
    def onchange_api_key(self):
        for rec in self:
            if rec.api_key:
                try:
                    current_url = http.request.env[
                                      'ir.config_parameter'].get_param(
                        'web.base.url') + '/create'
                    calendly = Calendly(rec.api_key)
                    _logger.info(
                        "----------calendly--------------------------%s",
                        calendly)
                    webhooks_exist = calendly.list_webhooks()
                    _logger.info(
                        "----------webhooks_exist--------------------------%s",
                        webhooks_exist)
                    if 'data' in webhooks_exist:
                        if webhooks_exist['data']:
                            _logger.info(
                                "----------wremove--------------------------%s",
                                webhooks_exist['data'][0].get('id'))
                            calendly.remove_webhook(
                                webhooks_exist['data'][0].get('id'))
                    calendly.create_webhook(current_url)
                    _logger.info(
                        "----------webhooks_exist--------------------------%s",
                        calendly.list_webhooks())
                except Exception as e:
                    print("e", e)
                    raise Warning(
                        "It will remove already existing calendly api,"
                        "And create new one with this api key")
