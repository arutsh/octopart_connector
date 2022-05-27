# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from pathlib import Path

from datetime import timedelta
from odoo import api, fields, models
from odoo.tools.float_utils import float_round, float_is_zero
from datetime import date, datetime, time, timedelta

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    linked_part_ids = fields.One2many('octopart.parts', 'linked_part_id')
    manufacturers_ids = fields.Many2many('octopart.parts.manufacturers', 'manufacturer_id')

    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    min_price = fields.Monetary(currency_field='currency_id', string="Min Price", compute="_compute_min_price")
    max_price = fields.Monetary(currency_field='currency_id', string="Max Price", compute="_compute_max_price")
    avg_price = fields.Monetary(currency_field='currency_id', compute="_compute_avg_price", string = "Avg Price")
    octopart_linked = fields.Boolean(default=False, string="Link to Octopart", compute="_compute_link_status")
    last_available_stock = fields.Many2one("octopart.parts.availability", "avail_id", compute="_compute_last_available_stock")

    last_available_stock_qty = fields.Integer(string="available qty", readonly=True, compute="_compute_last_available_stock")
    last_available_stock_url = fields.Char(string="offer url", readonly=True, compute="_compute_last_available_stock")

    seller_category_ids = fields.Many2many('octopart.parts.vendors.category', string="Category")

    def set_category_domain(self, record):
        domain = []
        #check if there is choosen categroy
        step = 0
        if(record.seller_category_ids):
            for i in record.seller_category_ids:
                if(len(record.seller_category_ids) > 1 and step < len(record.seller_category_ids)-1):
                    domain.append('|')
                domain.append(('seller_category_ids','in', i.id))
                step = step + 1

        return domain

    # def _update_category_ids(self):
    #     _logger.info("OCTPART PRODUCTs: _update_category_ids")
    #     for record in self:
    #         if(record.linked_part_ids):
    #             for i in record.linked_part_ids:
    #                 i.seller_category_ids = self.seller_category_ids
    #                 _logger.info("OCTPART PRODUCTs: _onchange_category_ids %s", i.seller_category_ids)

    @api.depends("linked_part_ids.last_available_stock")
    def _compute_last_available_stock(self):
        _logger.info("OCTPART PRODUCTs: _compute_last_available_stock")
        dt = date(1,1,1)
        qty = 0
        for record in self:
            if(record.linked_part_ids):
                for i in record.linked_part_ids:
                    #TODO: check if there is availability of the linked part
                    i._update_category_ids(self.seller_category_ids)
                    if (i.last_available_stock.date == False):
                        record.last_available_stock = None
                        record.last_available_stock_qty = 0
                        record.last_available_stock_url = "<div>None</div>"

                    elif(i.last_available_stock.date >= dt and i.last_available_stock.stock_level >= qty):
                        record.last_available_stock = i.last_available_stock
                        dt = record.last_available_stock.date
                        qty = record.last_available_stock_qty

                        record.last_available_stock_qty = i.last_available_stock_qty
                        record.last_available_stock_url = i.last_available_stock_url
            else:
                #TODO: very messsy code, has to be completly rewritten
                record.last_available_stock = None
                record.last_available_stock_qty = 0
                record.last_available_stock_url = "<div>Not linked</div>"


    @api.depends("linked_part_ids")
    def _compute_link_status(self):
        for record in self:
            if(record.linked_part_ids):
                record.octopart_linked = True
            else:
                record.octopart_linked = False

    @api.depends("linked_part_ids.min_price")
    def _compute_min_price(self):
        for record in self:
            if (record.linked_part_ids):
                record.min_price = min(record.linked_part_ids.mapped('min_price'))
            else:
                record.min_price = None

    @api.depends("linked_part_ids.max_price")
    def _compute_max_price(self):
        for record in self:
            if (record.linked_part_ids):
                record.max_price = max(record.linked_part_ids.mapped('max_price'))
            else:
                record.max_price = None


    @api.depends("linked_part_ids.avg_price")
    def _compute_avg_price(self):
        for record in self:
            if(record.linked_part_ids):
                s =  sum(record.linked_part_ids.mapped('avg_price'))
                l =  len(record.linked_part_ids.mapped('avg_price'))
                record.avg_price = s/l
            else:
                record.avg_price = None

    def _compute_min_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category = None):
        _logger.warning("OCTOPART Product Inhehtery: _compute_min_price_bom product template %s, %s", seller_category, self.name)
        #TODO: Min price has to first value
        min_price = 1000
        for record in self:
            try:
                if (record.linked_part_ids):
                    for item in record.linked_part_ids:
                        if(item.compute_min_price_bom(moq_qty=moq_qty, start_date=start_date, end_date=end_date, seller_category=seller_category) <= min_price):
                            _logger.warning("OCTOPART Product Inhehtery: _compute_min_price_bom product template")
                            min_price = item.compute_min_price_bom(moq_qty=mor_qty, start_date=start_date, end_date=end_date, seller_category=seller_category)
                        else:
                            min_price = None
            except:
                _logger.error("OCTOPART Product Inhehtery: _compute_min_price_bom exceptions")
        return min_price

    def check_availability(self):
        for record in self:
            if(record.linked_part_ids):
                for item in record.linked_part_ids:
                    item.check_availability()
#    @api.onchange("linked_part_ids")
    #def _update_manufacturers_list(self):


class ProductProduct(models.Model):
    _inherit = "product.product"

    def check_availability(self):
        for record in self:
            if(record.linked_part_ids):
                for item in record.linked_part_ids:
                    item.check_availability()

    def _compute_min_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category = None):
        #TODO: Min price has to first value
        _logger.warning("OCTOPART Product Inhehtery: _compute_min_price_bom product product %s %s", seller_category, self.name)
        min_price = 0
        for record in self:
            if (record.linked_part_ids):
                for item in record.linked_part_ids:
                    tmp = item.compute_min_price_bom(moq_qty=moq_qty, start_date=start_date, end_date=end_date, seller_category=seller_category)
                    if(min_price == 0):
                        min_price = tmp
                    elif(tmp <= min_price):
                        min_price = tmp
        return min_price


    def _compute_max_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category = None):
        #TODO: Max price has to first value
        max_price = 0
        for record in self:
            if (record.linked_part_ids):
                for item in record.linked_part_ids:
                    tmp = item.compute_max_price_bom(moq_qty=moq_qty, start_date=start_date, end_date=end_date, seller_category=seller_category)
                    if(max_price == 0):
                        max_price = tmp
                    elif(tmp >= max_price):
                        max_price = tmp
        return max_price

    @api.depends("linked_part_ids.last_available_stock")
    def _compute_last_available_stock(self):
        _logger.info("OCTPART PRODUCTs: _compute_last_available_stock")
        dt = date(1,1,1)
        qty = 0
        for record in self:
            if(record.linked_part_ids):
                for i in record.linked_part_ids:
                    #TODO: check if there is availability of the linked part
                    i._update_category_ids(self.seller_category_ids)
                    if (i.last_available_stock.date == False):
                        record.last_available_stock = None
                        record.last_available_stock_qty = 0
                        record.last_available_stock_url = "<div>None</div>"

                    elif(i.last_available_stock.date >= dt and i.last_available_stock.stock_level >= qty):
                        record.last_available_stock = i.last_available_stock
                        dt = record.last_available_stock.date
                        qty = record.last_available_stock_qty

                        record.last_available_stock_qty = i.last_available_stock_qty
                        record.last_available_stock_url = i.last_available_stock_url
            else:
                #TODO: very messsy code, has to be completly rewritten
                record.last_available_stock = None
                record.last_available_stock_qty = 0
                record.last_available_stock_url = "<div>Not linked</div>"
