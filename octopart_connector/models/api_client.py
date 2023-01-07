from six.moves import urllib
import json
import os

#Parrent class for API clients
class ApiClient():

    def __init__(self, name, token, client_id, client_secret, endpoint, headername='token'):
        print(f"I am ApiCLient init {token} ")
        self.name = name
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
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
            print(f" can not get response from octopart: {e.read()}")
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
        return self.get_contact_data()

    def get_offers_data(self):
        return OfferData()
    def get_prices_data(self):
        return PriceData()


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

    def __str__(self):
        return (f'''Part_id =  {self.part_id} \n
                    name =  {self.name} \n
                    Manufacturer URL =  {self.manufacturer_url} \n
                    Desc =  {self.description} \n
                    Provider = {self.provider} \n
                    Provider_URL = {self.provider_url} \n
                    Image = {self.image_url} \n
                    Lead time = {self.factory_lead_time} \n
                    Median Price = {self.median_price} \n
                    Free sample = {self.free_sample_url} \n
                    Datasheet = {self.datasheet_url} \n
                    Manufacturer = {self.manufacturer} \n
                    Category = {self.category}\n
                    Total Avail = { self.total_avail} \n
                    Avg Avail = {self.avg_avail}''')

class PartAvailabilityData():
    def __init__(self):
        self.part_id = None
        self.mpn =  None
        self.sellers = [], # sellers is list of sellers defined by ContactData class

    def __str__(self):
        return f''' part_id  = {self.part_id}
                    mpn = {self.mpn}
                    sellers = {self.sellers}
        '''

class ContactData():
    def  __init__(self, manufacturer=False):

        self.id =  None #id provided by provider
        self.name = None #contact name
        self.is_verified = None
        self.is_authorized = None #boolean
        self.is_broker = None #Boolean
        self.homepage_url = None
        self.is_distributor_api = None
        if not manufacturer:
            self.offers = [] # offers is list of offers from each seller, defined OfferData class

    def __str__(self):
        return f''' id = {self.id}
                    name = {self.name}
                    is_verified = {self.is_verified}
                    is_authorized = {self.is_authorized}
                    is_broker = {self.is_broker}
                    is_distributor_api = {self.is_distributor_api}
                    homepage_url = {self.homepage_url}
            '''

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

    def __str__(self):
        return f''' id = {self.id}
                    stock_level = {self.stock_level}
                    offer_url = {self.offer_url}
                    sku = {self.sku}
                    moq = {self.moq}
                    packaging = {self.packaging}
                    updated = {self.updated}
                    multipack_quantity = {self.multipack_quantity}
                    order_multiple = {self.order_multiple}
                    prices = {self.prices}
        '''
class PriceData():
    def __init__(self):
       self.quantity = None
       self.price = None
       self.converted_price = None
       self.converted_currency = None
       self.conversion_rate = None
       self.currency = None


    def __str__(self):
        return f''' quantity = {self.quantity}
                    price = {self.price}
                    converted_price = {self.converted_price}
                    converted_currency = {self.converted_currency}
                    conversion_rate = {self.conversion_rate}
                    currency = {self.currency}
                '''
