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

class OctoPartParts(models.Model):
    _name = "octopart.parts"
    _description = "Retrieves date from octopart by part name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    avail_ids = fields.One2many("octopart.parts.availability", "avail_id")
    part_id = fields.Char(string="Provider's part ID", required=True)
    part_history_ids = fields.One2many("octopart.parts.history", "part_id")
    provider = fields.Char(string="Provider", help="part information was retrie from this provider")
    name = fields.Char(required=True)
    date = fields.Date(default=get_default_date_today(), string="Last updated", copy=False)
    manufacturer_id = fields.Many2one('res.partner', string="Manufacturer")

    manufacturer_url = fields.Char()
    description = fields.Text()
    octopart_url = fields.Char()
    image = fields.Char()
    est_factory_lead_time = fields.Integer(string="Lead time", default=0, help="Available only for pro subscription")
    # Returns already converted price for requested currency
    median_price_1000_converted_currency = fields.Monetary(string="Median Price", default=0,
                                                           help="Median price for 1000qty")
    free_sample_url = fields.Char(string="Free sample")
    datasheet_url = fields.Char(string="Datasheet", help="Available only for pro subscribtion")

    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=_get_default_currency_id)
    linked_part_id = fields.Many2many('product.template', column1='product_template_id', column2='octopart_parts_id')
    # linked_part_customer = fields.Many2one(related='linked_part_id.customer_id')
    avg_avail = fields.Integer(string="Avg Available", help="Average avail of the part", default=None)
    total_avail = fields.Integer(string="Total Available", help="Total Availability in the market", default=None)

    # All fields below has to be reviewed and optimised
    min_price = fields.Monetary(currency_field='currency_id', compute="_compute_min_price", readonly=True)
    max_price = fields.Monetary(currency_field='currency_id', compute="_compute_max_price", readonly=True)
    # avg_price set same as median_price_1000_converted_currency, used in products for now.
    avg_price = fields.Monetary(currency_field='currency_id', compute="_compute_avg_price", readonly=True)
    # FIXME: Maybe this two fields can be implemented from controller. so we receive this dates from user and update min, max, avg price based on it
    start_date = fields.Date(default=(fields.Datetime.today()), string="Start date", copy=False)
    end_date = fields.Date(default=(fields.Datetime.today()), string="End date", copy=False)

    max_moq = fields.Integer(string="QTY", default=0)
    last_available_stock = fields.Many2one("octopart.parts.availability", "avail_id",
                                           compute="_compute_last_available_stock")

    last_available_stock_qty = fields.Integer(string="available qty", readonly=True,
                                              compute="_compute_last_available_stock")
    last_available_stock_url = fields.Char(string="offer url", readonly=True, compute="_compute_last_available_stock")

    seller_category_ids = fields.Many2many('octopart.parts.vendors.category', string="Category")

    _sql_constraints = [
        ('check_product_id', 'unique(part_id, provider)',
         'part_id and provider has to be unique.')
    ]

    def _set_default_date(self):
        for record in self:
            record.date = date.today(),
    def create_parts_by_matching_mpn(self, mpn, curr='GBP'):
        '''receives new mpn and creates all patching parts received from client'''
        print("i am test function called from query:", mpn)
        _logger.info("OCTOPART PARTS: ___searching value ")
        client = self.get_api_client()
        matches = client.search_mpns(str(mpn), curr)
        newParts = []
        for match in matches:
            part = self.search([('part_id', '=', match.part_id), ('provider', '=', match.provider)])
            if (part):
                newParts.append(part)
            else:
                p = self.create(self.convertClientPartToComponent(match))
                p.manufacturer_id = p.add_contact(match.manufacturer, True)
                newParts.append(p)
        return newParts

    # receives list of mpns and returns list of matching components
    def create_parts_by_matching_mpns(self, mpns, curr='GBP'):
        '''receives new mpn and creates all matching parts received from client'''
        # print("i am test function called from query:")
        _logger.info("OCTOPART PARTS: ___searching value mpns")
        client = self.get_api_client()
        newParts = []
        for mpn in mpns:

            matches = client.search_mpns(str(mpn).upper(), curr)
            print("searching part , ", str(mpn).upper(), matches)
            # newParts = []
            #if error was raised
            if matches:
                for match in matches:
                    # print("match part is", match)
                    part = self.search([('part_id', '=', match.part_id), ('provider', '=', match.provider)])
                    print(match, "searched part is: ", part)
                    if part:
                        # print("part exist = ", match)
                        part.update_part_history(match)
                        newParts.append(part)

                    elif len(mpn) >= 4:
                        # check with 3rd party only if len of the mpn is bigger than 3 symbols
                        # TODO this can be defined in configuration
                        p = self.create(self.convertClientPartToComponent(match))
                        p.manufacturer_id = p.add_contact(match.manufacturer, True)
                        newParts.append(p)


        return newParts

    def update_part_history(self, part):

        if self.part_history_ids:
            dt = max(self.part_history_ids.mapped('date'))
            #print("update_part_history -1 ", dt)
        else:
            dt = date.today() - timedelta(days=1)
            #print("update_part_history -2 ", dt, "today is ", date.today())

        # if latest update is smaller then today then refresh data, otherwise do nothing
        #print("Update part history, ", dt,  date.today())
        if dt < date.today():
            self.create_history_record(part)

    def create_history_record(self, part):
        self.write({
            'part_history_ids': [(0, 0, {
                'avg_price': part.median_price,
                'est_factory_lead_time': part.factory_lead_time,
                'avg_avail': part.avg_avail,
                'total_avail': part.total_avail,
                'date': get_default_date_today()
            })],
            'median_price_1000_converted_currency': part.median_price,
            'est_factory_lead_time': part.factory_lead_time,
            'avg_avail': part.avg_avail,
            'total_avail': part.total_avail,
            'date': get_default_date_today()
        })
    def convertClientPartToComponent(self, part):
        '''Converts part received from Client to json for selfcreate function'''
        return {
            'name': part.name,
            'part_id': part.part_id,
            'provider': part.provider,
            'manufacturer_url': part.manufacturer_url,
            'description': part.description,
            'octopart_url': part.provider_url,
            'image': part.image_url,
            'est_factory_lead_time': part.factory_lead_time,
            'median_price_1000_converted_currency': part.median_price,
            'free_sample_url': part.free_sample_url,
            'datasheet_url': part.datasheet_url,
        }

    def _update_category_ids(self, seller_category_ids):
        _logger.info("OCTPART PARTS: @api.onchange seller_category_ids")
        self.seller_category_ids = seller_category_ids
        self._compute_last_available_stock()

    def set_category_domain(self, record):
        domain = []
        # check if there is choosen categroy
        step = 0
        if (record.seller_category_ids):
            for i in record.seller_category_ids:
                if (len(record.seller_category_ids) > 1 and step < len(record.seller_category_ids) - 1):
                    domain.append('|')
                domain.append(('seller_category_ids', 'in', i.id))
                step = step + 1

        return domain

    # calculates last available stock to show in the Manufacturing order
    @api.depends("avail_ids.date")
    def _compute_last_available_stock(self):
        _logger.info("OCTPART PARTS: computing last available stock date")

        for record in self:
            # record.check_availability()
            record.last_available_stock = None
            record.last_available_stock_qty = None
            record.last_available_stock_url = None
            if (record.avail_ids):
                domain = self.set_category_domain(record)

                item = record.avail_ids.filtered_domain(domain)
                _logger.info("OCTPART PARTS: computing last available stock domain %s", item)
                test = item.sorted(key=lambda r: (r.date, r.stock_level), reverse=True)
                _logger.info("OCTPART PARTS: computing last available stock domain sorting %s", test)
                if (test):
                    _logger.info("OCTPART PARTS: computing last available stock domain sorting %s", test[0].stock_level)
                    record.last_available_stock = test[0].id
                    record.last_available_stock_qty = record.last_available_stock.stock_level
                    if record.last_available_stock_qty > 0:
                        record.last_available_stock_url = record.last_available_stock.offer_url

    @api.depends("avail_ids.price", "max_moq", "start_date", "end_date", "seller_category_ids")
    def _compute_min_price(self):
        _logger.info("OCTPART PARTS: _compute_min_price")
        for record in self:
            record.min_price = 0
            domain = record.define_domain(record.max_moq, record.start_date, datetime.today(),
                                          record.seller_category_ids)
            # _logger.info("OCTPART PARTS: computing last available stock price -> Domain: %s", domain)
            if (record.avail_ids):
                res = record.avail_ids.filtered_domain(domain).filtered(lambda i: i.price > 0)
                if (res):
                    record.min_price = min(res.mapped('price'))
                    # _logger.info("OCTPART PARTS: _compute_min_price minprice %s", record.min_price)

    def compute_min_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category=None):
        _logger.info("OCTOPART PARTS: compute min price BOM")

        domain = self.define_domain(moq_qty, start_date, end_date, seller_category)
        # _logger.info("OCTPART PARTS:compute_min_price_bom -> Domain: %s", domain)
        for record in self:
            if (record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                # record.min_price = min(record.avail_ids.mapped('price'))
                if (res):
                    min_price = min(res.mapped('price'))
                else:
                    min_price = 0
            else:
                min_price = 0
        return min_price

    def compute_max_price_bom(self, moq_qty=None, start_date=None, end_date=None, seller_category=None):
        _logger.info("OCTOPART PARTS: compute max price BOM")
        domain = self.define_domain(moq_qty, start_date, end_date, seller_category)
        for record in self:
            if (record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                # record.min_price = min(record.avail_ids.mapped('price'))
                if (res):
                    max_price = max(res.mapped('price'))
                else:
                    max_price = 0
            else:
                max_price = 0
        return max_price

    def compute_min_price_button(self):
        _logger.info("OCTOPART PARTS: compute min price button")
        domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]

        if (self.max_moq):
            domain.append(('batch_qty', '<=', self.max_moq))
        # check if there is choosen categroy
        step = 0
        _logger.info("OCTOPART PARTS: compute min price button -> domain1: %s", domain)
        if (self.seller_category_ids):
            for i in self.seller_category_ids:
                if (len(self.seller_category_ids) > 1 and step < len(self.seller_category_ids) - 1):
                    domain.append('|')
                domain.append(('seller_category_ids', 'in', i.id))
                step = step + 1

        for record in self:
            _logger.info("OCTOPART PARTS: compute min price button -> domain2: %s", domain)
            if (record.avail_ids):
                res = record.avail_ids.filtered_domain(domain)
                _logger.info("OCTOPART PARTS: compute min price button filtered -> res: %s", res)
                # record.min_price = min(record.avail_ids.mapped('price'))
                if (res):
                    record.min_price = min(res.mapped('price'))
                else:
                    record.min_price = None

            else:
                record.min_price = None

    def define_domain(self, moq_qty=None, start_date=None, end_date=None, category=None):
        domain = []
        # if start and end dates are not givven, then by default domain will be for last 30 days
        if ((start_date is None) or (start_date is False)):
            start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        domain.append(('date', '>=', start_date))
        if ((end_date is None) or (end_date is False)):
            end_date = date.today().strftime('%Y-%m-%d')
        domain.append(('date', '<=', end_date))
        if (moq_qty):
            domain.append(('batch_qty', '<=', moq_qty))
        step = 0
        if (category):
            for i in category:
                if (len(category) > 1 and step < len(category) - 1):
                    domain.append('|')
                domain.append(('seller_category_ids', 'in', i.id))
                step = step + 1

        return domain

    @api.depends("avail_ids.price")
    def _compute_max_price(self):
        # testing config files

        for record in self:
            record.max_price = None
            if (record.avail_ids):
                record.max_price = max(record.avail_ids.mapped('price'))

    @api.depends("avail_ids.price")
    def _compute_avg_price(self):
        for record in self:
            record.avg_price = record.median_price_1000_converted_currency

    def _is_part_exist(self, part_id, provider):
        ## TODO: add provider name for filtering after provider is created
        part = self.search([('part_id', '=', part_id), ('provider', '=', provider)])
        if part:
            raise UserError(f"{part.name} from {provider}  already exist!")
            return True
        return False

    # get api token from ApiClient object
    def get_api_client(self):
        client = ApiClientSettings(self.env['ir.config_parameter'])
        client = client.getProvider()

        return client

    def add_contact(self, contact, manufacturer=False):

        '''
        1. create supplier attribute
        :param contact:
        :param manufacturer:
        :return:
        '''
        category = None
        #1. find correct vendor category id
        if manufacturer:
            category = 'manufacturer'
        elif contact.is_authorized:
            category = 'authorised'
        elif contact.is_broker:
            category = 'broker'




        vendor_attr_id = self.env['vendors.attributes'].create({
            'name': contact.name,
            'is_verified': contact.is_verified or None,
            'vendor_category': category
        }).id


        return self.env['res.partner'].create({
            'contact_id': contact.id,
            'name': contact.name,
            # 'is_verified': contact.is_verified or None,
            # 'is_authorized': contact.is_authorized or None,
            # 'is_broker': contact.is_broker or None,
            'is_distributor_api': contact.is_distributor_api or None,
            'website': contact.homepage_url or None,
            'provider': self.provider,
            # 'is_manufacturer': manufacturer,
            'company_type': 'company',
            'is_supplier': True,
            'vendor_attribute_id': vendor_attr_id
        }).id

    # new module parts category has to be created
    def add_category(self, category):
        pass

    # receive value from API search and updates record
    def update_record(self, part):
        print(f"update record, received part = {type(part)}")
        if (self._is_part_exist(part.part_id, part.provider)):
            # self.name = ""
            pass
        else:
            self.name = part.name
            self.part_id = part.part_id
            self.provider = part.provider
            self.manufacturer_id = self.add_contact(part.manufacturer, True)  # adds contact with mfr =true

            self.manufacturer_url = part.manufacturer_url
            self.description = part.description
            self.octopart_url = part.provider_url
            if part.image_url:
                self.image = '<img src = "' + part.image_url + '" width="150px">'

            self.est_factory_lead_time = part.factory_lead_time

            self.median_price_1000_converted_currency = part.median_price

            self.free_sample_url = part.free_sample_url

            self.datasheet_url = part.datasheet_url

    # the function create val dict for create function based on the given part name
    def get_val_to_create(self, mpn, curr='GBP'):
        _logger.warning("****getValueToCreate received %s", mpn)
        part = self._match_parts(mpn, curr)
        val = {}
        history = {}
        val['name'] = mpn
        val['part_id'] = part.part_id
        val['provider'] = part.provider
        val['manufacturer_id'] = self.add_contact(part.manufacturer, True)  # adds contact with mfr =true
        val['manufacturer_url'] = part.manufacturer_url
        val['description'] = part.description
        val['octopart_url'] = part.provider_url
        if part.image_url:
            val['image'] = '<img src = "' + part.image_url + '" width="150px">'

        val['est_factory_lead_time'] = part.factory_lead_time
        history['est_factory_lead_time'] = part.factory_lead_time

        val['median_price_1000_converted_currency'] = part.median_price
        history['avg_price'] = part.median_price

        val['free_sample_url'] = part.free_sample_url

        val['avg_avail'] = part.avg_avail
        history['avg_avail'] = part.avg_avail

        val['total_avail'] = part.total_avail
        history['total_avail'] = part.total_avail

        val['datasheet_url'] = part.datasheet_url

        return (val, history)

    @api.model
    def create(self, val):
        # if part id is not set, then try to fetch from provider.
        if not val.get('part_id'):
            val, history = self.get_val_to_create(str(val.get('name').upper()))
            val['part_history_ids'] = [(0, 0, history)]
            _logger.info(" *** after matching val is %s", val, history)

        # return None
        return super().create(val)

    @api.onchange('name')
    def getPartDetails(self):
        if self.name:
            self.name = str(self.name).upper()
            result = self._match_parts(self.name, self.currency_id.name)
            self.update_record(result)

    def _match_parts(self, mpn, curr='GBP'):
        _logger.info("OCTOPART PARTS: ___selecting value")
        client = self.get_api_client()
        return client.match_mpns(str(mpn), curr)

    # update availability with given query result
    def update_availability(self, result):
        avail_ids = []
        part_id = result.part_id
        name = result.mpn
        for s in result.sellers:

            seller_id = self.add_contact(s)

            for offer in s.offers:
                stock_level = offer.stock_level
                stock_avail = 'false'
                if stock_level > 0:
                    stock_avail = 'true'
                offer_url = offer.offer_url
                sku = offer.sku
                moq = offer.moq
                updated = offer.updated
                for p in offer.prices:
                    price = p.converted_price
                    currency = p.converted_currency
                    batch_qty = p.quantity
                    _logger.info("OCTOPART PARTS: #create record for each seller and price group")

                    ret = self.env['octopart.parts.availability'].create({
                        'avail_id': self.id,
                        'currency_id': self.currency_id.id,
                        'part_id': part_id,
                        'name': name,
                        'seller_id': seller_id,
                        'stock_level': stock_level,
                        'stock_avail': stock_avail,
                        'update_from_vendor': updated,
                        'sku': sku,
                        'moq': moq,
                        'price': price,
                        'currency': currency,
                        'batch_qty': batch_qty,
                        'offer_url': offer_url
                    })
                    # print(f"creating new record = {ret}")

    def check_availability(self):
        # get the latest update of available components
        if (self.avail_ids):
            dt = max(self.avail_ids.mapped('date'))
        else:
            dt = date.today() - timedelta(days=1)
        _logger.info("check_availability: latest date is: %s", dt)
        # if latest update is smaller then today then refresh data, otherwise do nothing
        # TODO: this is not the best solution, in case we want to check updates regularly, several times per day
        if (dt < date.today()):
            _logger.info("API: __adding values")

            client = self.get_api_client()
            q = client.match_mpn_availability(self.name, self.part_id, self.currency_id.name)
            self.update_availability(q)
            self.fetch_new_history_record()

    def fetch_new_history_record(self):
        # TODO can be modified and run as a part of schedule if user choose....
        # gets new data from provider to match new stock availability and median price
        dt = date.today() - timedelta(days=1)
        if (self.part_history_ids):
            dt = max(self.part_history_ids.mapped('date'))

        _logger.info("Fetch History: latest date is: %s", dt)
        # if latest update is smaller then today then refresh data, otherwise do nothing
        if (dt < date.today()):
            _logger.info("API: __adding  history record %s", self.name)

            history = self._match_parts(self.name, 'GBP')
            self.create_history_record(history)

        return True




    def unlink(self):

        for record in self:
            if (record.avail_ids):
                raise UserError(
                    'You can not delete Part, if there are availability parts associated with it. Please delete availability list first')
                return True
        return super().unlink()
