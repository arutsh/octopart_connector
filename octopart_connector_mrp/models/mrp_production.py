# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import operator as py_operator
import re

import logging
from pathlib import Path

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    _description = 'Production Order with octopart inhancement'

    seller_category_ids = fields.Many2many('octopart.parts.vendors.category', string="Category")

    @api.onchange("seller_category_ids")
    def _onchange_category_id(self):
        for record in self:
                for raw in record.move_raw_ids:
                    _logger.info('%s category search changed product', raw.product_id.name)
                    raw.product_id.seller_category_ids = record.seller_category_ids
                    raw.product_id._compute_last_available_stock()

    def check_availability(self):
        _logger.info('MRP Production, check availability')
        for record in self:
            for raw in record.move_raw_ids:
                _logger.info('%s check availability for product', raw.product_id.name)
                raw.product_id.check_availability()
