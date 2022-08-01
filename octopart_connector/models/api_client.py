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


    def match_mpns(self, mpn, currency='GBP'):
        pass

    def search_mpns(self, mpn, currency='GBP'):
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
        return PartData()

    def get_availability_data(self):
        return PartAvailabilityData()

    def get_contact_data(self, manufacturer=False):
        return ContactData(manufacturer)

    def get_seller_data(self):
        return get_contact_data()

    def get_offers_data(self):
        return OfferData
    def get_prices_data(self):
        return PriceData


class PartData():
    def __init__(self):
        self.part_id = None
        self.name = None
        self.manufacturer_url = None
        self.description = None
        self.provider =  None
        self.provider_url = None
        self.image_url = None
        self.factory_lead_time = None
        self.median_price = None
        self.free_sample_url = None
        self.datasheet_url = None
        self.manufacturer = ContactData(True) #definees ContactData with manufacturer = true
        self.category = None
        self.total_avail =  None
        self.avg_avail = None

class OctoPartAvailabilityData():
    def __init__(self):
        self.part_id = None
        self.mpn =  None
        self.sellers = [], # sellers is list of sellers defined by ContactData class

class ContactData():
    def  __init__(self, manufacturer=False):

        self.id =  None #id provided by provider
        self.name = None #contact name
        self.is_verified = None
        self.is_authorized = None #boolean
        self.is_broker = None #Boolean
        self.homepage_url = None
        if not manufacturer:
            self.offers = [] # offers is list of offers from each seller, defined OfferData class

class OfferData():
    def __init__(self):
        self.id = None
        self.stock_level = None
        self.offer_url = None
        self.sku = None
        self.moq = None
        self.packaging = None
        self.updated = None
        self.multipack_quantity = None
        self.order_multiple = None
        self.prices = []  # is list of prices defined by PriceData classs

class PriceData():
    def __init__(self):
       self.quantity = None
       self.price = None
       self.converted_price = None
       self.converted_currency = None
       self.conversion_rate = None
       self.currency = None
