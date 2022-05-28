# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.addons.octopart_connector.models.octopart_client import OctoPartClient, demo_match_mpns, demo_search_mpn


class OctoPartManufacturers(models.Model):
    _name = "octopart.parts.manufacturers"
    _description = "Retrieves manufacturers from octopart "
    _order = "id desc"

    manufacturer_id = fields.Char(string="PartsBox ID", required=True)
    name = fields.Char(required=True)

    def _is_manufacurer_exist(self, m_id):
        if self.search([('manufacturer_id', '=' , m_id)]):
            #raise UserError("Manufacturer already exist")
            print(self.search([('manufacturer_id', '=' , m_id)]))
            return True
        return False

    def create(self, val):
        if self.search([('manufacturer_id', '=' , val['manufacturer_id'])]):
            return self.search([('manufacturer_id', '=' , val['manufacturer_id'])])
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
