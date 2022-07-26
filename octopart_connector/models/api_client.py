from six.moves import urllib
import json
import os

#Parrent class for API clients
class ApiClient():

    def __init__(self, name, token, endpoint, headername='token'):
        print(f"I am ApiCLient init {token} ")
        self.name = name
        self.token = token
        self.endpoint = endpoint
        self.headername = headername


    def match_mpns(self):
        pass

    def search_mpns(self):
        pass

    def execute(self, query, variables=None):
        return self._send(query, variables)

    def inject_token(self, token, headername='token'):
        self.token = token
        self.headername = headername

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        req = urllib.request.Request(self.endpoint, json.dumps(data).encode('utf-8'), headers)

        try:
            response = urllib.request.urlopen(req)
            return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e
    #new API client has to request this  for each part and return dict according to defined struct
    def get_part_data(self):
        d = {
            'part_id':None,
            'name':None,
            'manufacturer_url': None,
            'description': None,
            'provider': None,
            'provider_url': None,
            'image_url': None,
            'factory_lead_time': None,
            'median_price': None,
            'free_sample_url': None,
            'datasheet_url': None,
            'manufacturer': None,
            'category': None,
            'total_avail': None,
            'avg_avai': None
        }
        return d

    def get_availability_data(self):
        d = {
            'part_id':None,
            'mpn': None,
            'sellers':[], # sellers is list of sellers defined in get_seller_data()
        }
        return d

    def get_seller_data(self):
        d = {
            'id': None,
            'name' : None, #SELLER name
            'is_verified':None,
            'is_authorized':None, #boolean
            'is_broker':None, #Boolean
            'is_rfq':None, #Boolean
            'homepage_url' : None,
            'offers': [], # offers is list of offers from each seller, defined get_offers_data
            }

        return d

    def get_offers_data(self):
        d={
            'id' : None,
            'stock_level' : None,
            'offer_url' : None,
            'sku' : None,
            'moq' : None,
            'packaging' : None,
            'updated' : None,
            'multipack_quantity': None,
            'order_multiple' : None,
            'prices' : [], # is list of prices defined get_prices_data
        }

        return d
    def get_prices_data(self):
        d = {
               'quantity' : None,
               'price' : None,
               'converted_price' : None,
               'converted_currency' : None,
               'conversion_rate': None,
               'currency': None
        }
        return d
