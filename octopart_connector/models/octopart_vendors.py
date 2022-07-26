# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.addons.octopart_connector.models.api_client import ApiClient
from odoo.addons.octopart_connector.models.octopart_client import demo_match_mpns, demo_search_mpn

_logger = logging.getLogger(__name__)

class OctoPartVendors(models.Model):
    _name = "octopart.parts.vendors"
    _description = "Retrieves Vendors from octopart"
    _order = "id desc"

    vendor_id = fields.Char(string="PartsBox ID", required=True)
    name = fields.Char(required=True)
    category_id = fields.Many2one('octopart.parts.vendors.category', string='Category')
    confirmed_vendor = fields.Boolean(string="Confirmed Vendor", default=False)
    contact_id = fields.Many2one('res.partner', string="Contact")
    description = fields.Text()


    _sql_constraints = [
        ('check_vendor_id', 'unique(vendor_id)',
         'vendor id has to be unique.')
    ]
# check if given part is exist, return it, otherwise create it
#TODO UNKNOWN bug, for some reason it still tries to create vender, which already existing
# might be problem with threads, since it happens when verdors are created in bulk
    def create(self, val):
        #_logger.info('%s creating new vendor', val)
        vendor_id = self.search([('vendor_id', '=' , val['vendor_id'])])
        if (vendor_id):
        #    _logger.info('%s existing vendor, returning vendor id', vendor_id)
            return vendor_id
        else:
        #    _logger.info('%s Vendor does not existing, creting new vendor', vendor_id)
            return super().create(val)

    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method
        #for record in self:
            #if (record.state == 'new'):
                #raise UserError('You can not delete property at new state')
        #    return True

        return super().unlink()

class OctoPartVendorsCategory(models.Model):
    _name = "octopart.parts.vendors.category"
    _description = "Category of different suppliers "
    _order = "id desc"

    vendors_ids = fields.One2many('octopart.parts.vendors', 'category_id')
    name = fields.Char(required=True)
    #TODO: desc is temp field to match values received from JS.
    #IF JS is changed so instead id was chosen from the select... then no need for this field.
    desc = fields.Char(help="Temp field for values received from JS")




    def unlink(self):
        # Do some business logic, modify vals...
        ...
        # Then call super to execute the parent method
        #for record in self:
            #if (record.state == 'new'):
                #raise UserError('You can not delete property at new state')
        #    return True

        return super().unlink()
