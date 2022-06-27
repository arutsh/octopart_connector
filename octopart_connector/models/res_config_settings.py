# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_token = fields.Char(string="Octopart API token")
    client_url = fields.Char(string="Octopart Client URL")
    #TODO: add field for Basic and PRO subscribtion
    #based on subscription level some values might be available some not



    def set_values(self):
       """Octopart API setting field values"""
       res = super(ResConfigSettings, self).set_values()
       self.env['ir.config_parameter'].set_param('octopart_connector.api_token', self.api_token)
       self.env['ir.config_parameter'].set_param('octopart_connector.client_url', self.client_url)
       return res

    def get_values(self):
       """Octopart API getting field values"""
       res = super(ResConfigSettings, self).get_values()
       token = self.env['ir.config_parameter'].sudo().get_param('octopart_connector.api_token')
       client = self.env['ir.config_parameter'].sudo().get_param('octopart_connector.client_url')
       res.update(
           api_token=token,
           client_url=client
       )
       return res
