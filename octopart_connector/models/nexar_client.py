from six.moves import urllib
import json
import os
import requests
import base64
import json
import time
from typing import Dict
from copy import deepcopy
from odoo.addons.octopart_connector.models.api_client import ApiClient
import logging

_logger = logging.getLogger(__name__)
NEXAR_URL = "https://api.nexar.com/graphql"
PROD_TOKEN_URL = "https://identity.nexar.com/connect/token"

STRING = [{'part': {'id': '446330', 'mpn': 'AD5160BRJZ10-RL7', 'manufacturer_url': 'https://octopart.com/opatz8j6/b1?t=EcFOO8GgbxJ6c5lOwQ0iKuFidHlHHHCCfIq-wBVIliFLhD3XMcceyjVfDE8jmhU9lex79sPg-XpmPLpYutcjk4XiyVvzH1Xi8w0uS8QG4DLehzJysSCIqrKbzXmhdg6b54DtFcLE9o6boaiFW4DEVMLswN6yTFQTyfdOuzm0Myi8uH3lJK8TJhB44C4jnoLTix4JsOR53VR8LmLdIHt7iAUXB_gKcK0x0oi55NbcF6Oq-70STzNlase40FbuPA', 'short_description': 'Digital Potentiometer 10kOhm 256POS Volatile Linear Automotive 8-Pin SOT-23 T/R', 'estimated_factory_lead_days': 546, 'descriptions': [{'credit_string': 'Verical', 'text': 'Digital Potentiometer 10kOhm 256POS Volatile Linear Automotive 8-Pin SOT-23 T/R'}, {'credit_string': 'element14 APAC', 'text': 'DIGITAL POTENTIOMETER 10KOHM 256, SIGNAL, SOT23-8, FULL REEL'}, {'credit_string': 'Analog Devices', 'text': 'The AD5160 provides a compact 2.9 mm × 3 mm packaged solution for 256-position adjustment applications. These devices perform the same electronic adjustment function as mechanical potentiometers1 or variable resistors but with enhanced resolution, solid-state reliability, and superior low temperature coefficient performance. The wiper settings are controllable through an SPI-compatible digital interface. The resistance between the wiper and either end point of the fixed resistor varies linearly with respect to the digital code transferred into the RDAC latch. Operating from a 2.7 V to 5.5 V power supply and consuming less than 5 μA allows for usage in portable battery-operated applications.'}], 'total_avail': 1849210, 'avg_avail': 16221, 'best_datasheet': {'name': 'Datasheet', 'url': 'http://datasheet.octopart.com/AD5160BRJZ10-RL7-Analog-Devices-datasheet-8541704.pdf'}, 'free_sample_url': None, 'median_price_1000': {'converted_currency': 'GBP', 'converted_price': 0.9396639299999999}, 'octopart_url': 'https://octopart.com/ad5160brjz10-rl7-analog+devices-446330', 'best_image': {'url': 'https://sigma.octopart.com/10048060/image/Analog-Devices-AD5160BRJZ10-RL7.jpg'}, 'category': {'name': 'Digital Potentiometers', 'id':'1'}, 'manufacturer': {'name': 'Analog Devices', 'id': '26'}}}]


PROD_TOKEN_URL = "https://identity.nexar.com/connect/token"
NEXAR_URL = "https://api.nexar.com/graphql"

class NexarApiClient(ApiClient):

    def __init__(self, provider, client_id, client_secret, endpoint, subscription=None, headername='token'):
        print("I am Nexar client")
        token = None
        self.s = requests.session()
        self.s.keep_alive = False
        super().__init__(provider, token, client_id, client_secret, endpoint, headername='token')
        if subscription:
            self.subscription = subscription

        self.token = self.get_token()
        self.s.headers.update({"token": self.token.get('access_token')})
        self.exp = self.decodeJWT(self.token.get('access_token')).get('exp')

    def get_token(self):
        """Return the Nexar token from the client_id and client_secret provided."""

        if not self.client_id or not self.client_secret:
            raise Exception("client_id and/or client_secret are empty")

        token = {}
        try:
            token = requests.post(
                url=PROD_TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                allow_redirects=False,
            ).json()

        except Exception:
            raise

        return token

    def decodeJWT(self,token):
        return json.loads(
            (base64.urlsafe_b64decode(token.split(".")[1] + "==")).decode("utf-8")
        )

    def check_exp(self):
        if (self.exp < time.time() + 300):
            self.token = get_token(self.id, self.secret)
            self.s.headers.update({"token": self.token.get('access_token')})
            self.exp = decodeJWT(self.token.get('access_token')).get('exp')


    def execute(self, query: str, variables: Dict) -> dict:
        """Return Nexar response for the query."""
        try:
            self.check_exp()
            r = self.s.post(
                NEXAR_URL,
                json={"query": query, "variables": variables},
            )

        except Exception as e:
            print(e)
            raise Exception("Error while getting Nexar response")

        response = r.json()
        if ("errors" in response):
            for error in response["errors"]: print(error["message"])
            raise SystemExit


        return response["data"]

    def _get_manufacturer(self):
        return '''manufacturer {
                    id
                    isVerified
                    homepageUrl
                    name
                }'''

    def _get_contact_data(self):
        return '''company {
                    id
                    name
                    homepageUrl
                    isVerified
                    isDistributorApi
                } '''
    def _get_extra_data_parts(self):
        return '''bestImage {
        			url
        		  }
                  estimatedFactoryLeadDays'''


    def _get_prices_data(self):
        return '''prices{
                    quantity
                    price
                    convertedPrice
                    convertedCurrency
                    conversionRate
                    currency
                }'''
    def _get_offer_data(self):
        return '''offers{
                    id
                    clickUrl
                    inventoryLevel
                    sku
                    moq
                    packaging
                    updated
                    multipackQuantity
                    orderMultiple
                    '''+self._get_prices_data()+'''
                }
                '''

    def _get_part(self):
        part = '''
        part {
			id
			mpn
			manufacturerUrl
			shortDescription

			descriptions {
				creditString
				text
			}
			totalAvail
			avgAvail
			bestDatasheet{
				name
				url
			}
			freeSampleUrl
			manufacturerUrl
			medianPrice1000 {
				convertedCurrency
				convertedPrice
			}
			octopartUrl

			category {
				name
                id
			}
            '''+ self._get_manufacturer()

        closing = '''}'''

        part = part + self._get_extra_data_parts()+closing


        return part

    def _get_part_availability_data(self):
        return '''part {
                    id
                    mpn
                    sellers{
                        '''+self._get_contact_data()+'''

                        isAuthorized
                        isBroker
                        isRfq
                        '''+self._get_offer_data()+'''
                    }
                }
                '''
    #
    # def search_mpns(self, mpn, currency="GBP"):
    #     if self.subscription == 'basic':
    #         return self._search_basic(mpn, currency)
    #     if self.subscription == 'pro':
    #         return self._search_pro(mpn, currency)

    def match_mpns(self, mpn, currency='GBP'):
        _logger.info("nexar client match mpn, received: %s", mpn)
        matches = self._search_mpn(mpn, currency)
        _logger.info("nexar client matches: %s", matches)

        # ## TODO:  Remove after # DEBUG:
        # matches = STRING
        return self.filter_part_matches(matches, mpn)

    def search_mpn_availability(self, mpn, pid, currency='GBP'):

        matches = self._search_mpn_availability(mpn)

        #matches = [{'part': {'id': '88318820', 'mpn': 'LTC3026EMSE#PBF', 'sellers': [{'company': {'id': '12899', 'homepage_url': 'https://extremecomponents.com', 'is_verified': False, 'name': 'Extreme Components', 'slug': 'extreme-components'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '663797666', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=29167&sig=0e5a5b7&vpid=663797666', 'inventory_level': 135, 'sku': 'LTC3026EMSE#PBF', 'moq': None, 'packaging': None, 'updated': '2022-04-23T07:52:45Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}, {'company': {'id': '12079', 'homepage_url': 'http://www.sourceability.com', 'is_verified': False, 'name': 'Sourceability', 'slug': 'sourceability'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '662606679', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=28281&sig=0a37f74&vpid=662606679', 'inventory_level': 43, 'sku': 'LTC3026EMSE#PBF', 'moq': None, 'packaging': None, 'updated': '2022-06-29T15:13:15Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}, {'company': {'id': '10079', 'homepage_url': 'http://www.abacuselect.com/', 'is_verified': False, 'name': 'Abacus Technologies', 'slug': 'abacus-technologies'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '462282693', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=25917&sig=0a9b3d3&vpid=462282693', 'inventory_level': 0, 'sku': 'LTC3026EMSEPBF', 'moq': None, 'packaging': None, 'updated': '2022-07-16T00:02:43Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}, {'company': {'id': '10643', 'homepage_url': 'http://iodparts.com', 'is_verified': False, 'name': 'iodParts', 'slug': 'iodparts'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '671948368', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=26822&sig=065aa5d&vpid=671948368', 'inventory_level': 78, 'sku': 'LTC3026EMSE#PBF', 'moq': None, 'packaging': None, 'updated': '2022-07-15T11:22:57Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}]}}]

        return self.filter_availability_matches(matches, mpn, pid)

    def filter_availability_matches(self, matches, mpn, pid):
        # d =  self.get_availability_data()
        d = self.get_availability_data()
        #print(f"mpn = {mpn}, id = {pid}")
        # print(f"matches = {matches}")
        for match in matches:
            if (match['part']['mpn']).lower() == mpn.lower() and match['part']['id'] ==  pid:
                s_d  = self.get_seller_data()

                d.part_id =  pid
                d.mpn = mpn
                d.sellers = []
                sellers = match['part']['sellers']
                # print(f"sellers ")
                # print(f"new s_d = {s_d}")
                for s in sellers:
                    #print(f"s = {s}")
                    s_d.id = s['company']['id']
                    s_d.name = s['company']['name']
                    s_d.is_verified = s['company']['isVerified']
                    s_d.homepage_url = s['company']['homepageUrl']
                    s_d.is_distributor_api = s['company']['isDistributorApi']
                    s_d.is_authorized = s['isAuthorized']
                    s_d.is_broker = s['isBroker']
                    s_d.is_rfq = s['isRfq']

                    s_d.offers = []

                    offers = s['offers']

                    o_d = self.get_offers_data()
                    # print(f"s_d = {s_d}")
                    # print(f"new o_d = {o_d}")
                    for offer in  offers:
                        o_d.id =  offer['id']
                        o_d.stock_level =  offer['inventoryLevel']
                        o_d.offer_url =  offer['clickUrl']
                        o_d.sku =  offer['sku']
                        o_d.moq =  offer['moq']
                        o_d.packaging = offer['packaging']
                        o_d.updated = offer['updated']
                        o_d.multipack_quantity = offer['multipackQuantity']
                        o_d.order_multiple = offer['orderMultiple']
                        o_d.prices = []
                        prices = offer['prices']
                        p_d = self.get_prices_data()
                        # print(f"o_d = {o_d}")
                        # print(f"new p_d = {p_d}")
                        for p in prices:
                            p_d.quantity = p['quantity']
                            p_d.price = p['price']
                            p_d.converted_price = p['convertedPrice']
                            p_d.converted_currency = p['convertedCurrency']
                            p_d.conversion_rate = p['conversionRate']
                            p_d.currency = p['currency']
                            # print(f"p_d = {p_d}")
                            o_d.prices.append(deepcopy(p_d))
                            # print(f"added to o_d = {o_d}")
                        s_d.offers.append(deepcopy(o_d))
                    # print(f"s_d = {s_d}")
                    d.sellers.append(deepcopy(s_d))
            # print(f"d = {d}")

        return d

    def filter_part_matches(self, matches, mpn):
        d = self.get_part_data()

        for match in matches:
            if (match['part']['mpn']).upper() == mpn.upper():

                d.part_id = match['part']['id']
                d.name = mpn.upper()
                d.manufacturer_url = match['part']['manufacturerUrl']
                d.description = match['part']['shortDescription']
                d.provider = self.name
                d.provider_url =  match['part']['octopartUrl']
                if match['part']['bestImage']:
                    d.image_url = match['part']['bestImage']['url']
                if match['part']['estimatedFactoryLeadDays']:
                    d.factory_lead_time = int(match['part']['estimatedFactoryLeadDays'])
                if match['part']['medianPrice1000']:
                    d.median_price = float(match['part']['medianPrice1000']['convertedPrice'])
                d.free_sample_url = match['part']['freeSampleUrl']
                if match['part']['bestDatasheet']:
                    d.datasheet_url =  match['part']['bestDatasheet']['url']
                if match['part']['category']:
                    d.category = match['part']['category']
                if match['part']['manufacturer']:
                    print(match['part']['manufacturer'])
                    d.manufacturer.id = match['part']['manufacturer']['id']
                    d.manufacturer.name = match['part']['manufacturer']['name']
                    d.manufacturer.is_verified = match['part']['manufacturer']['isVerified']
                    d.manufacturer.homepage_url = match['part']['manufacturer']['homepageUrl']
                d.avg_avail = match['part']['avgAvail']
                d.total_avail = match['part']['totalAvail']

        return(d)


    def _search_mpn(self, mpn, currency='GBP'):

        query = '''
        query Match_part($q: String, $curr: String!, $country: String!, $limit: Int){
        supSearchMpn(q: $q, currency: $curr, country: $country, limit: $limit) {
         hits
         results { ''' +self._get_part()+ '''

             }
           }
        }
        '''
        var = {
          "q": mpn,
          "curr": currency,
          "country": "GB",
          "limit":1,

        }

        _logger.info("VAR IS %s", var)
        resp = self.execute(query, var)


        return resp['supSearchMpn']['results']



    def _search_mpn_availability(self, mpn, currency='GBP'):
        print(f"_search_mpn_availability mpn = {mpn}")
        query = '''
        query supSearchMpn($q: String, $curr: String!, $country: String!){
        supSearchMpn(q: $q, currency: $curr, country: $country) {
            hits
            results {
                    '''+self._get_part_availability_data()+'''
                }
            }
        }
        '''

        var = {
          "q": mpn,
          "curr": currency,
          "country": "GB",
        }
        resp = self.execute(query, var)


        return resp['supSearchMpn']['results']
