import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class EventCalendarInheritCalendly(models.Model):
    _inherit = 'calendar.event'

    calendly_id = fields.Char()