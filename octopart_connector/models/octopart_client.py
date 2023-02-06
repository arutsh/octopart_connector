from six.moves import urllib
import json
from copy import deepcopy

from odoo.addons.octopart_connector.models.api_client import ApiClient
from odoo.addons.octopart_connector.models.octopart_client_graphql import OctopartGraphQL

STRING = [{'part': {'id': '446330', 'mpn': 'AD5160BRJZ10-RL7',
                    'manufacturer_url': 'https://octopart.com/opatz8j6/b1?t=EcFOO8GgbxJ6c5lOwQ0iKuFidHlHHHCCfIq-wBVIliFLhD3XMcceyjVfDE8jmhU9lex79sPg-XpmPLpYutcjk4XiyVvzH1Xi8w0uS8QG4DLehzJysSCIqrKbzXmhdg6b54DtFcLE9o6boaiFW4DEVMLswN6yTFQTyfdOuzm0Myi8uH3lJK8TJhB44C4jnoLTix4JsOR53VR8LmLdIHt7iAUXB_gKcK0x0oi55NbcF6Oq-70STzNlase40FbuPA',
                    'short_description': 'Digital Potentiometer 10kOhm 256POS Volatile Linear Automotive 8-Pin SOT-23 T/R',
                    'estimated_factory_lead_days': 546, 'descriptions': [{'credit_string': 'Verical',
                                                                          'text': 'Digital Potentiometer 10kOhm 256POS Volatile Linear Automotive 8-Pin SOT-23 T/R'},
                                                                         {'credit_string': 'element14 APAC',
                                                                          'text': 'DIGITAL POTENTIOMETER 10KOHM 256, SIGNAL, SOT23-8, FULL REEL'},
                                                                         {'credit_string': 'Analog Devices',
                                                                          'text': 'The AD5160 provides a compact 2.9 mm × 3 mm packaged solution for 256-position adjustment applications. These devices perform the same electronic adjustment function as mechanical potentiometers1 or variable resistors but with enhanced resolution, solid-state reliability, and superior low temperature coefficient performance. The wiper settings are controllable through an SPI-compatible digital interface. The resistance between the wiper and either end point of the fixed resistor varies linearly with respect to the digital code transferred into the RDAC latch. Operating from a 2.7 V to 5.5 V power supply and consuming less than 5 μA allows for usage in portable battery-operated applications.'}],
                    'total_avail': 1849210, 'avg_avail': 16221, 'best_datasheet': {'name': 'Datasheet',
                                                                                   'url': 'http://datasheet.octopart.com/AD5160BRJZ10-RL7-Analog-Devices-datasheet-8541704.pdf'},
                    'free_sample_url': None,
                    'median_price_1000': {'converted_currency': 'GBP', 'converted_price': 0.9396639299999999},
                    'octopart_url': 'https://octopart.com/ad5160brjz10-rl7-analog+devices-446330', 'best_image': {
        'url': 'https://sigma.octopart.com/10048060/image/Analog-Devices-AD5160BRJZ10-RL7.jpg'},
                    'category': {'name': 'Digital Potentiometers', 'id': '1'},
                    'manufacturer': {'name': 'Analog Devices', 'id': '26'}}}]


class OctopartApiClient(ApiClient):

    def __init__(self, provider, token, endpoint, subscription=None, headername='token'):
        print("I am octopart client", subscription, "is sub")
        # super().__init__(provider, token, client_id, client_secret, endpoint, headername)
        self.name = provider
        self.token = token
        self.endpoint = endpoint
        self.headername = headername
        if subscription:
            self.subscription = subscription

    """
    search mpn
    :param mpn - manufacturing part number
    :param currency=GPB 
    :todo     
    """

    # TODO: seems name better to have match mpn, not mpns
    def match_mpns(self, mpn, currency='GBP'):
        query = OctopartGraphQL.search_mpn(self.subscription, mpn, currency)
        matches = json.loads(self.execute(query['query_body'], query['variables']))

        for i in query['nested_data']:
            matches = matches[i]



        return self.filter_part_matches(matches, mpn)

    """
    search mpn
    :param mpn - manufacturing part number
    :param currency=GPB 
    :todo     
    """

    # TODO: seems name better to have match mpn, not mpns
    def search_mpns(self, mpn, currency='GBP'):

        query = OctopartGraphQL.search_mpn(self.subscription, mpn, currency)
        # print("octopart search mpn", mpn)
        matches = json.loads(self.execute(query['query_body'], query['variables']))
        print("octopart search mpn matches", matches)

        for i in query['nested_data']:
            matches = matches[i]

        if matches:
            return self.filter_parts_searches(matches)

        return []


    """
    search availability for the mpn
    :param mpn - manufacturing part number
    :param currency=GPB 
    :todo     
    """
    def match_mpn_availability(self, mpn, pid, currency='GBP'):
        query = OctopartGraphQL.search_mpn_availability(mpn, currency)
        matches = json.loads(self.execute(query['query_body'], query['variables']))
        for i in query['nested_data']:
            matches = matches[i]

        return self.filter_availability_matches(matches, mpn, pid)

    """
    translates received data to PartAvailabilityData class
    """
    def filter_availability_matches(self, matches, mpn, pid):
        d = self.get_availability_data()
        # print(f"mpn = {mpn}, id = {pid}")
        # print(f"matches = {matches}")
        for match in matches:
            if (match['part']['mpn']).lower() == mpn.lower() and match['part']['id'] == pid:
                s_d = self.get_seller_data()
                d.part_id = pid
                d.mpn = mpn
                d.sellers = []
                sellers = match['part']['sellers']
                # print(f"sellers ")
                for s in sellers:
                    # print(f"s = {s}")
                    s_d.id = s['company']['id']
                    s_d.name = s['company']['name']
                    s_d.is_verified= s['company']['name']
                    s_d.homepage_url = s['company']['homepage_url']
                    s_d.is_authorized = s['is_authorized']
                    s_d.is_broker = s['is_broker']
                    s_d.is_rfq = s['is_rfq']
                    s_d.offers = []

                    offers = s['offers']
                    o_d = self.get_offers_data()
                    for offer in offers:
                        o_d.id = offer['id']
                        o_d.stock_level = offer['inventory_level']
                        o_d.offer_url = offer['click_url']
                        o_d.sku = offer['sku']
                        o_d.moq = offer['moq']
                        o_d.packaging = offer['packaging']
                        o_d.updated = offer['updated']
                        o_d.multipack_quantity = offer['multipack_quantity']
                        o_d.order_multiple = offer['order_multiple']
                        o_d.prices = []
                        prices = offer['prices']
                        p_d = self.get_prices_data()

                        for p in prices:
                            p_d.quantity = p['quantity']
                            p_d.price = p['price']
                            p_d.converted_price = p['converted_price']
                            p_d.converted_currency = p['converted_currency']
                            p_d.conversion_rate = p['conversion_rate']
                            p_d.currency = p['currency']
                            # print(f"p_d = {p_d}")
                            o_d.prices.append(deepcopy(p_d))
                        s_d.offers.append(deepcopy(o_d))
                    # print(f"s_d = {s_d}")
                    d.sellers.append(deepcopy(s_d))
            # print(f"d = {d}")

        return d

    """
    translates received data to PartData class
    """

    def filter_part_matches(self, matches, mpn):
        d = self.get_part_data()

        # for match in matches:
        #     if (match['part']['mpn']).lower() == mpn.lower():
        #
        #         d.part_id = match['part']['id']
        #         d.name = mpn
        #         d.manufacturer_url = match['part']['manufacturer_url']
        #         d.description = match['part']['short_description']
        #         d.provider = self.name
        #         d.provider_url = match['part']['octopart_url']
        #         if match['part']['best_image']:
        #             d.image_url = match['part']['best_image']['url']
        #         d.factory_lead_time = int(match['part']['estimated_factory_lead_days'])
        #         if match['part']['median_price_1000']:
        #             d.median_price = float(match['part']['median_price_1000']['converted_price'])
        #         d.free_sample_url = match['part']['free_sample_url']
        #         if match['part']['best_datasheet']:
        #             d.datasheet_url = match['part']['best_datasheet']['url']
        #         if match['part']['category']:
        #             d.category = match['part']['category']
        #         if match['part']['manufacturer']:
        #             print(match['part']['manufacturer'])
        #             d.manufacturer.id = match['part']['manufacturer']['id']
        #             d.manufacturer.name = match['part']['manufacturer']['name']
        #             d.is_verified = match['part']['manufacturer']['is_verified']
        #             d.homepage_url = match['part']['manufacturer']['homepage_url']
        #         d.avg_avail = match['part']['avg_avail']
        #         d.total_avail = match['part']['total_avail']

        for match in matches:
            if (match['part']['mpn']).upper() == mpn.upper():
                d = self.translateToPartData(match)

        print("filter matched data is ", d)
        return (d)


    def filter_parts_searches(self, matches):
        d = self.get_part_data()
        d_list = []
        # print("filter part matches", matches)
        for match in matches:
            d_list.append(self.translateToPartData(match))

        # print("filter part searches" , d_list)
        return d_list

    def translateToPartData(self, match):
        d = self.get_part_data()
        d.part_id = match['part']['id']
        d.name = match['part']['mpn'].upper()
        d.manufacturer_url = match['part']['manufacturer_url']
        d.description = match['part']['short_description']
        d.provider = self.name
        d.provider_url = match['part']['octopart_url']
        if match['part']['best_image']:
            d.image_url = match['part']['best_image']['url']
        if match['part']['estimated_factory_lead_days']:
            d.factory_lead_time = int(match['part']['estimated_factory_lead_days'])
        if match['part']['median_price_1000']:
            d.median_price = float(match['part']['median_price_1000']['converted_price'])
        d.free_sample_url = match['part']['free_sample_url']
        if match['part']['best_datasheet']:
            d.datasheet_url = match['part']['best_datasheet']['url']
        if match['part']['category']:
            d.category = match['part']['category']
        if match['part']['manufacturer']:
            print(match['part']['manufacturer'])
            d.manufacturer.id = match['part']['manufacturer']['id']
            d.manufacturer.name = match['part']['manufacturer']['name']
            d.manufacturer.is_verified = match['part']['manufacturer']['is_verified']
            d.manufacturer.homepage_url = match['part']['manufacturer']['homepage_url']
        d.avg_avail = match['part']['avg_avail']
        d.total_avail = match['part']['total_avail']

        return d