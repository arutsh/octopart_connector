# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.addons.octopart_connector.models.api_client_settings import ApiClientSettings
# from odoo.addons.octopart_connector.models.octopart_client import demo_match_mpns, demo_search_mpn
from datetime import date, datetime, time, timedelta

_logger = logging.getLogger(__name__)

class OctoPartPartsHistory(models.Model):
    _name = "octopart.parts.history"
    _description = "Keeps part update history for price, availability, etc"
    _order = "id desc"

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    part_id = fields.Many2one("octopart.parts")
    name = fields.Char(related='part_id.name')
    date = fields.Date(default=(fields.Datetime.today()),string="Last updated", copy=False)
    est_factory_lead_time = fields.Integer(string="Lead time", default=0, help="Available only for pro subscription")
    #Returns already converted price for requested currency
    avg_price = fields.Monetary(string="Median Price", currency_field='currency_id', default=0, help="Median price for 1000qty")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=_get_default_currency_id)
    avg_avail = fields.Integer(string="Avg Available", help="Average avail of the part", default=None)
    total_avail = fields.Integer(string="Total Available", help="Total Availability in the market", default=None)


    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.model
    def create(self, val):

        # if part id is not set, then try to fetch from provider.
        return super().create(val)


    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method

        return super().unlink()
