# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.addons.octopart_connector.models.api_client import ApiClient
from odoo.addons.octopart_connector.models.octopart_client import demo_search_mpn

#TODO: check if it appeares in the project list
#TODO: testing something else
class OctoPartAvailability(models.Model):
    _name = "octopart.parts.availability"
    _description = "Retrieves availability from octopart by part name"
    _order = "id desc"

    avail_id = fields.Many2one("octopart.parts", string="Part name")
    part_id = fields.Char(readonly=True)
    name = fields.Char(required=True, readonly=True)
    date = fields.Date(default=(fields.Datetime.today()),string="Last updated", copy=False)
    seller = fields.Many2one('octopart.parts.vendors')
    seller_id = fields.Many2one('res.partner', string="Contact")
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
    # seller_category_ids = fields.Many2one('octopart.parts.vendors.category', related="seller.category_id")
    seller_category_ids = fields.Many2many('res.partner.category', related="seller_id.category_id")
    seller_status = fields.Boolean(related="seller.confirmed_vendor")
    update_from_vendor = fields.Date(default=(fields.Datetime.today()),string="Updated with Vendor", copy=False)

    @api.onchange("stock_level")
    def _update_stock_avail(self):
        if self.stock_level > 0:
            self.stock_avail = 'true'
        else:
            self.stock_avail = 'false'


    def add_to_supplier_info(self):
        try:
            ret = self.env['product.supplierinfo'].create({
                'name' : self.seller_id.id,
                'product_name' : self.name,
                'product_code' : self.sku,
                'min_qty':self.batch_qty,
                'price' : self.price,
                'date_start' : fields.Datetime.today(),
                'date_end' : fields.Datetime.today(),
                'product_tmpl_id' : self.avail_id.linked_part_id.id
            })
        except Exception as e:
            raise UserError(e)
        return True

    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method
        #for record in self:
            #if (record.state == 'new'):
                #raise UserError('You can not delete property at new state')
        #    return True

        return super().unlink()
