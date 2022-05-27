# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.addons.octopart_api.models.octopart_client  import OctoPartClient, demo_search_mpn

#TODO: check if it appeares in the project list
#TODO: testing something else
class OctoPartAvailability(models.Model):
    _name = "octopart.parts.availability"
    _description = "Retrieves availability from octopart by part name"
    _order = "id desc"

    avail_id = fields.Many2one("octopart.parts", string="Part name")
    part_id = fields.Integer(readonly=True)
    name = fields.Char(required=True, readonly=True)
    date = fields.Date(default=(fields.Datetime.today()),string="Last updated", copy=False)
    seller = fields.Many2one('octopart.parts.vendors',required=True)
    offer_url = fields.Char(readonly=True)
    stock_level = fields.Integer(readonly=True)
    stock_avail = fields.Selection([
                                    ('true', 'Available'),
                                    ('false', 'Non-Stock'),
                                    ])
    sku = fields.Char(readonly=True)
    moq = fields.Integer(string="MOQ", readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)
    price = fields.Monetary(currency_field='currency_id', string="Price", readonly=True)
    currency = fields.Char(string="Vendor Currency", readonly=True)
    batch_qty = fields.Integer(string="Min QTY", readonly=True)
    seller_category_ids = fields.Many2one('octopart.parts.vendors.category', related="seller.category_id")

    @api.onchange("stock_level")
    def _update_stock_avail(self):
        if self.stock_level > 0:
            self.stock_avail = 'true'
        else:
            self.stock_avail = 'false'

    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method
        #for record in self:
            #if (record.state == 'new'):
                #raise UserError('You can not delete property at new state')
        #    return True

        return super().unlink()
