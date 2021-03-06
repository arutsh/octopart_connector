# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.addons.octopart_connector.models.octopart_client import OctoPartClient, demo_match_mpns, demo_search_mpn
from datetime import date, datetime, time, timedelta

_logger = logging.getLogger(__name__)

class OctoPartParts(models.Model):
    _name = "octopart.parts"
    _description = "Retrieves date from octopart by part name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    avail_ids = fields.One2many("octopart.parts.availability", "avail_id")
    part_id = fields.Char(string="PartsBox ID", required=True)
    name = fields.Char(required=True)
    date = fields.Date(default=(fields.Datetime.today()),string="Last updated", copy=False)
    manufacturer = fields.Many2one('octopart.parts.manufacturers',required=True)
    manufacturer_url = fields.Char()
    description = fields.Text()
    octopart_url = fields.Char()
    image = fields.Char()
    #TODO: default set to GBP manually, has to be match with company currency
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=147)
    linked_part_id = fields.Many2one('product.template', 'Link to Product')
    min_price = fields.Monetary(currency_field='currency_id', compute="_compute_min_price", readonly=True)
    max_price = fields.Monetary(currency_field='currency_id', compute="_compute_max_price", readonly=True)
    avg_price = fields.Monetary(currency_field='currency_id', compute="_compute_avg_price", readonly=True)
    #FIXME: Maybe this two fields can be implemented from controller. so we receive this dates from user and update min, max, avg price based on it
    start_date = fields.Date(default=(fields.Datetime.today()),string="Start date", copy=False)
    end_date = fields.Date(default=(fields.Datetime.today()),string="End date", copy=False)

    max_moq = fields.Integer(string="QTY", default=0)
    last_available_stock = fields.Many2one("octopart.parts.availability", "avail_id", compute="_compute_last_available_stock")

    last_available_stock_qty = fields.Integer(string="available qty", readonly=True, compute="_compute_last_available_stock")
    last_available_stock_url = fields.Char(string="offer url", readonly=True, compute="_compute_last_available_stock")

    seller_category_ids = fields.Many2many('octopart.parts.vendors.category', string="Category")

    #_sql_constraints = [
    #    ('check_selling_price', 'CHECK(selling_price >= 0)',
    #     'A property selling price must be positive.')
    #]



    def _update_category_ids(self, seller_category_ids):
        _logger.info("OCTPART PARTS: @api.onchange seller_category_ids")
        self.seller_category_ids = seller_category_ids
        self._compute_last_available_stock()


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

    # calculates last available stock to show in the Manufacturing order
    @api.depends("avail_ids.date")
    def _compute_last_available_stock(self):
        _logger.info("OCTPART PARTS: computing last available stock date")
        for record in self:
            #record.check_availability()
            if(record.avail_ids):
                domain = self.set_category_domain(record)

                item = record.avail_ids.filtered_domain(domain)
                _logger.info("OCTPART PARTS: computing last available stock domain %s", item)
                #item = item.filtered(lambda r: (r.stock_level > 0))
                #_logger.info("OCTPART PARTS: computing last available stock domain filtering out 0 stock %s", item)
                test = item.sorted(key = lambda r: (r.date, r.stock_level), reverse=True)
                _logger.info("OCTPART PARTS: computing last available stock domain sorting %s", test)
                #test = record.avail_ids.sorted(key = lambda r: (r.date, r.stock_level), reverse=True)
                if(test):
                    _logger.info("OCTPART PARTS: computing last available stock domain sorting %s", test[0].stock_level)
                    record.last_available_stock = test[0].id
                    record.last_available_stock_qty = record.last_available_stock.stock_level
                    if (record.last_available_stock_qty > 0):
                        record.last_available_stock_url = record.last_available_stock.offer_url
                    else:
                        record.last_available_stock_url = "<div>None</div>"
                else:
                    #TODO: Does not like same code twice :()
                    record.last_available_stock = None
                    record.last_available_stock_qty = None
                    record.last_available_stock_url = "<div>None</div>"

            else:
                record.last_available_stock = None
                record.last_available_stock_qty = None
                record.last_available_stock_url = "<div>None</div>"



    @api.depends("avail_ids.price", "max_moq", "start_date", "end_date", "seller_category_ids")
    def _compute_min_price(self):
        _logger.info("OCTPART PARTS: computing last available stock price")
        _logger.info("OCTPART PARTS: computing last available stock price -> seller_cat: %s", self.seller_category_ids)

        for record in self:
            domain = record.define_domain(record.max_moq, record.start_date, record.end_date, record.seller_category_ids)
            _logger.info("OCTPART PARTS: computing last available stock price -> Domain: %s", domain)
            if(record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                if(res):
                    record.min_price = min(res.mapped('price'))
                else:
                    record.min_price = 0
            else:
                record.min_price = 0

    def compute_min_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category = None):
        _logger.info("OCTOPART PARTS: compute min price BOM")

        domain = self.define_domain(moq_qty, start_date, end_date, seller_category)
        #_logger.info("OCTPART PARTS:compute_min_price_bom -> Domain: %s", domain)
        for record in self:
            if(record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                # record.min_price = min(record.avail_ids.mapped('price'))
                if(res):
                    min_price = min(res.mapped('price'))
                else:
                    min_price = 0
            else:
                min_price = 0
        return min_price

    def compute_max_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category = None):
        _logger.info("OCTOPART PARTS: compute max price BOM")
        domain = self.define_domain(moq_qty, start_date, end_date, seller_category)
        for record in self:
            if(record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                # record.min_price = min(record.avail_ids.mapped('price'))
                if(res):
                    max_price = max(res.mapped('price'))
                else:
                    max_price = 0
            else:
                max_price = 0
        return max_price


    def compute_min_price_button(self):
        _logger.info("OCTOPART PARTS: compute min price button")
        domain = [('date', '>=', self.start_date),('date', '<=', self.end_date)]

        if(self.max_moq):
             domain.append(('batch_qty', '<=', self.max_moq))
        #check if there is choosen categroy
        step = 0
        _logger.info("OCTOPART PARTS: compute min price button -> domain1: %s", domain)
        if(self.seller_category_ids):
            for i in self.seller_category_ids:
                if(len(self.seller_category_ids) > 1 and step < len(self.seller_category_ids)-1):
                    domain.append('|')
                domain.append(('seller_category_ids','in', i.id))
                step = step + 1


        for record in self:
            _logger.info("OCTOPART PARTS: compute min price button -> domain2: %s", domain)
            if(record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                _logger.info("OCTOPART PARTS: compute min price button filtered -> res: %s", res)
                # record.min_price = min(record.avail_ids.mapped('price'))
                if(res):
                    record.min_price = min(res.mapped('price'))
                else:
                    record.min_price = None

            else:
                record.min_price = None

    def define_domain(self, moq_qty=None, start_date=None, end_date=None, category=None):
        domain = []
        #if start and end dates are not givven, then by default domain will be for last 30 days
        if((start_date is None) or (start_date is False)):
            start_date = (date.today()- timedelta(days=30)).strftime('%Y-%m-%d')
        domain.append(('date', '>=', start_date))
        if((end_date is None) or (end_date is False)):
            end_date = date.today().strftime('%Y-%m-%d')
        domain.append(('date', '<=', end_date))
        if(moq_qty):
            domain.append(('batch_qty', '<=', moq_qty))
        step = 0
        if(category):
            for i in category:
                if(len(category) > 1 and step < len(category)-1):
                    domain.append('|')
                domain.append(('seller_category_ids','in', i.id))
                step = step + 1

        return domain


    @api.depends("avail_ids.price")
    def _compute_max_price(self):
        #testing config files

        for record in self:
            if(record.avail_ids):
                record.max_price = max(record.avail_ids.mapped('price'))
            else:
                record.max_price = None

    @api.depends("avail_ids.price")
    def _compute_avg_price(self):
        for record in self:
            if(record.avail_ids):
                s =  sum(record.avail_ids.mapped('price'))
                l =  len(record.avail_ids.mapped('price'))
                record.avg_price = s/l
            else:
                record.avg_price = None

    def _is_part_exist(self, part_id):
        if self.search([('part_id', '=' , part_id)]):
            raise UserError("part already exist")
            return True
        return False


    @api.onchange('name')
    def _match_parts(self):
        _logger.info("OCTOPART PARTS: ___selecting value")
        # client = OctoPartClient('https://octopart.com/api/v4/endpoint')
        # client.inject_token('10d26abe-cb84-476c-b2b7-a18b60ef3312')
        token = self.env['ir.config_parameter'].sudo().get_param('octopart_connector.api_token')
        endpoint = value = self.env['ir.config_parameter'].sudo().get_param('octopart_connector.client_url')
        client = OctoPartClient(endpoint)
        client.inject_token(token)
        mpn = self.name
        result = demo_match_mpns(client, str(mpn))
        for match in result:
            for part in match['parts']:
                if (self._is_part_exist(part['id'])):
                    self.name = ""
                else:
                    self.part_id = part['id']

                    self.manufacturer = self.env['octopart.parts.manufacturers'].create({
                    'manufacturer_id':part['manufacturer']['id'],
                    'name':part['manufacturer']['name']
                    }).id

                    #self.manufacturer = part['manufacturer']['name']
                    if part['manufacturer_url'] != None:
                        self.manufacturer_url = '<a href= "' + part['manufacturer_url']+'" target="_blank"> Manufacturer URL </a>'
                    self.description = part['short_description']
                    if part['octopart_url'] != None:
                        self.octopart_url = '<a href= "' + part['octopart_url'] +'" target="_blank">Octopart URL</a>'

                    if part['best_image'] != None:
                        self.image = '<img src = "' + part['best_image']['url'] + '" width="150px">'



    def check_availability(self):
        #get the latest update of available components
        if (self.avail_ids):
            dt = max(self.avail_ids.mapped('date'))
        else:
            dt = date.today()-timedelta(days=1)
        #if latest update is smaller then today then refresh data, otherwise do nothing
        #TODO: this is not the best solution, in case we want to check updates regularly, several times per day
        if(dt <  date.today()):
            _logger.info("OCTOPART PARTS: __adding values")
            # client = OctoPartClient('https://octopart.com/api/v4/endpoint')
            # client.inject_token('10d26abe-cb84-476c-b2b7-a18b60ef3312')
            token = self.env['ir.config_parameter'].sudo().get_param('octopart_connector.api_token')
            endpoint = value = self.env['ir.config_parameter'].sudo().get_param('octopart_connector.client_url')
            client = OctoPartClient(endpoint)
            client.inject_token(token)
            mpn = self.name
            curr = self.currency_id.name
            q = demo_search_mpn(client, mpn, curr)

            result = q['data']['search']['results']
            avail_ids = []
            for match in result:
                part_id = match['part']['id']
                if part_id != self.part_id:
                    continue
                name = match['part']['mpn']
                for sellers in match['part']['sellers']:
                    seller = self.env['octopart.parts.vendors'].create({
                    'vendor_id':sellers['company']['id'],
                    'name':sellers['company']['name']
                    }).id
                    #seller = sellers['company']['name']
                    for offers in sellers['offers']:
                        stock_level = offers['inventory_level']
                        stock_avail = 'false'
                        if stock_level > 0 :
                            stock_avail='true'
                        offer_url = '<a href= "' + offers['click_url'] +'" target="_blank">'+sellers['company']['name']+'</a>'
                        sku = offers['sku']
                        moq = offers['moq']
                        for p in offers['prices']:
                            price = p['converted_price']
                            currency = p['currency']
                            batch_qty = p['quantity']
                            _logger.info("OCTOPART PARTS: #create record for each seller and price groupe")

                            ret = self.env['octopart.parts.availability'].create({
                                'avail_id': self.id,
                                'currency_id': self.currency_id.id,
                                'part_id':part_id,
                                'name':name,
                                'seller':seller,
                                'stock_level': stock_level,
                                'stock_avail': stock_avail,
                                'sku': sku,
                                'moq': moq,
                                'price': price,
                                'currency': currency,
                                'batch_qty': batch_qty,
                                'offer_url': offer_url
                            })


    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method
        #for record in self:
            #if (record.state == 'new'):
                #raise UserError('You can not delete property at new state')
        #    return True
        for record in self:
            if (record.avail_ids):
                raise UserError('You can not delete Part, if there are availability parts associated with it. Please delete availability list first')
                return True
        return super().unlink()
