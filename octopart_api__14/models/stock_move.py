# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from collections import defaultdict
from datetime import datetime
from itertools import groupby
from operator import itemgetter
from re import findall as regex_findall
from re import split as regex_split

from dateutil import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
from odoo.tools.misc import clean_context, format_date, OrderedSet

PROCUREMENT_PRIORITIES = [('0', 'Normal'), ('1', 'Urgent')]


class StockMove(models.Model):
    _inherit = "stock.move"
    _description = "Stock Move octopart linked"

    octopart_linked = fields.Boolean(related='product_tmpl_id.octopart_linked', readonly=True)
    last_available_stock_qty = fields.Integer(related='product_tmpl_id.last_available_stock_qty', readonly=True)
    last_available_stock_url = fields.Char(related='product_tmpl_id.last_available_stock_url', readonly=True)

    #octopart_avail = fields.Char(string="Octopart Availability", compute="_compute_availability")

    #@api.depends("product_tmpl_id.price")
    #def _compute_availability(self):
