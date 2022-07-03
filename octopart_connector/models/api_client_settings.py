from six.moves import urllib
import json
import os
from odoo.addons.octopart_connector.models.octopart_client import OctopartApiClient

# copied from: https://github.com/prisma-labs/python-graphql-client/blob/master/graphqlclient/client.py
class ApiClientSettings():
    def __init__(self, val,headername='token'):

        self.token = val.sudo().get_param('octopart_connector.api_token')
        self.endpoint = val.sudo().get_param('octopart_connector.client_url')
        self.subscription = val.sudo().get_param('octopart_connector.subscription')
        self.provider = val.sudo().get_param('octopart_connector.provider')
        self.headername = headername

    def getProvider(self):
        if self.provider == "octopart":
            return OctopartApiClient(self.provider, self.token, self.endpoint, self.subscription)
