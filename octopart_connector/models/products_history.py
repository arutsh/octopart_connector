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


def get_default_date_today():
    return date.today()


class ProductsHistory(models.Model):
    _name = "products.template.history"
    _description = "Keeps products' update history for price, availability, etc"
    _order = "id desc"
    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    product_id = fields.Many2one("product.template")
    name = fields.Char(related='product_id.name')
    date = fields.Date(string="Last updated", copy=False, default=get_default_date_today())
    min_est_factory_lead_time = fields.Integer(string="Min Lead time", default=0, help="Min Lead time of all linked components")
    # Returns already converted price for requested currency
    min_avg_price = fields.Monetary(string="Min Median Price", currency_field='currency_id', default=0,
                                help="Min of Median price for 1000qty of all linked components")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=_get_default_currency_id)
    max_avg_avail = fields.Integer(string="max Avg Available", help="max Average avail of all linked components", default=None)
    max_total_avail = fields.Integer(string="Total Available", help="max Total Availability of all linked components", default=None)



    @api.model
    def create(self, val):
        # if part id is not set, then try to fetch from provider.
        return super().create(val)

    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method

        return super().unlink()
