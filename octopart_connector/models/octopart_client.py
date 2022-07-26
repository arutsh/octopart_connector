from six.moves import urllib
import json
import os
from odoo.addons.octopart_connector.models.api_client import ApiClient

STRING = [{'part': {'id': '446330', 'mpn': 'AD5160BRJZ10-RL7', 'manufacturer_url': 'https://octopart.com/opatz8j6/b1?t=EcFOO8GgbxJ6c5lOwQ0iKuFidHlHHHCCfIq-wBVIliFLhD3XMcceyjVfDE8jmhU9lex79sPg-XpmPLpYutcjk4XiyVvzH1Xi8w0uS8QG4DLehzJysSCIqrKbzXmhdg6b54DtFcLE9o6boaiFW4DEVMLswN6yTFQTyfdOuzm0Myi8uH3lJK8TJhB44C4jnoLTix4JsOR53VR8LmLdIHt7iAUXB_gKcK0x0oi55NbcF6Oq-70STzNlase40FbuPA', 'short_description': 'Digital Potentiometer 10kOhm 256POS Volatile Linear Automotive 8-Pin SOT-23 T/R', 'estimated_factory_lead_days': 546, 'descriptions': [{'credit_string': 'Verical', 'text': 'Digital Potentiometer 10kOhm 256POS Volatile Linear Automotive 8-Pin SOT-23 T/R'}, {'credit_string': 'element14 APAC', 'text': 'DIGITAL POTENTIOMETER 10KOHM 256, SIGNAL, SOT23-8, FULL REEL'}, {'credit_string': 'Analog Devices', 'text': 'The AD5160 provides a compact 2.9 mm × 3 mm packaged solution for 256-position adjustment applications. These devices perform the same electronic adjustment function as mechanical potentiometers1 or variable resistors but with enhanced resolution, solid-state reliability, and superior low temperature coefficient performance. The wiper settings are controllable through an SPI-compatible digital interface. The resistance between the wiper and either end point of the fixed resistor varies linearly with respect to the digital code transferred into the RDAC latch. Operating from a 2.7 V to 5.5 V power supply and consuming less than 5 μA allows for usage in portable battery-operated applications.'}], 'total_avail': 1849210, 'avg_avail': 16221, 'best_datasheet': {'name': 'Datasheet', 'url': 'http://datasheet.octopart.com/AD5160BRJZ10-RL7-Analog-Devices-datasheet-8541704.pdf'}, 'free_sample_url': None, 'median_price_1000': {'converted_currency': 'GBP', 'converted_price': 0.9396639299999999}, 'octopart_url': 'https://octopart.com/ad5160brjz10-rl7-analog+devices-446330', 'best_image': {'url': 'https://sigma.octopart.com/10048060/image/Analog-Devices-AD5160BRJZ10-RL7.jpg'}, 'category': {'name': 'Digital Potentiometers', 'id':'1'}, 'manufacturer': {'name': 'Analog Devices', 'id': '26'}}}]

class OctopartApiClient(ApiClient):
    def __init__(self, provider, token, endpoint, subscription=None, headername='token'):
        print("I am octopart client")
        super().__init__(provider, token, endpoint, headername='token')
        if subscription:
            self.subscription = subscription
    def search_mpns(self, mpn, currency):
        if self.subscription == 'basic':
            return self._search_basic(mpn, currency)
        if self.subscription == 'pro':
            return self._search_pro(mpn, currency)

    def match_mpns(self, mpn):

        if self.subscription == 'pro':
            matches = self._search_mpn_pro(mpn)
        elif self.subscription == 'basic':
            matches = self._search_mpn_basic(mpn)

        # ## TODO:  Remove after # DEBUG:
        # matches = STRING
        return self.filter_part_matches(matches, mpn)

    def search_mpn_availability(self, mpn, pid, currency='GBP'):

        matches = self._search_mpn_availability(mpn)

        #matches = [{'part': {'id': '88318820', 'mpn': 'LTC3026EMSE#PBF', 'sellers': [{'company': {'id': '12899', 'homepage_url': 'https://extremecomponents.com', 'is_verified': False, 'name': 'Extreme Components', 'slug': 'extreme-components'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '663797666', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=29167&sig=0e5a5b7&vpid=663797666', 'inventory_level': 135, 'sku': 'LTC3026EMSE#PBF', 'moq': None, 'packaging': None, 'updated': '2022-04-23T07:52:45Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}, {'company': {'id': '12079', 'homepage_url': 'http://www.sourceability.com', 'is_verified': False, 'name': 'Sourceability', 'slug': 'sourceability'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '662606679', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=28281&sig=0a37f74&vpid=662606679', 'inventory_level': 43, 'sku': 'LTC3026EMSE#PBF', 'moq': None, 'packaging': None, 'updated': '2022-06-29T15:13:15Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}, {'company': {'id': '10079', 'homepage_url': 'http://www.abacuselect.com/', 'is_verified': False, 'name': 'Abacus Technologies', 'slug': 'abacus-technologies'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '462282693', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=25917&sig=0a9b3d3&vpid=462282693', 'inventory_level': 0, 'sku': 'LTC3026EMSEPBF', 'moq': None, 'packaging': None, 'updated': '2022-07-16T00:02:43Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}, {'company': {'id': '10643', 'homepage_url': 'http://iodparts.com', 'is_verified': False, 'name': 'iodParts', 'slug': 'iodparts'}, 'is_authorized': False, 'is_broker': False, 'is_rfq': False, 'offers': [{'id': '671948368', 'click_url': 'https://octopart.com/click/track?ai4=134978&country=GB&ct=offers&ppid=88318820&sid=26822&sig=065aa5d&vpid=671948368', 'inventory_level': 78, 'sku': 'LTC3026EMSE#PBF', 'moq': None, 'packaging': None, 'updated': '2022-07-15T11:22:57Z', 'multipack_quantity': None, 'order_multiple': None, 'prices': []}]}]}}]

        return self.filter_availability_matches(matches, mpn, pid)

    def filter_availability_matches(self, matches, mpn, pid):
        d =  self.get_availability_data()
        #print(f"mpn = {mpn}, id = {pid}")
        # print(f"matches = {matches}")
        for match in matches:
            if (match['part']['mpn']).lower() == mpn.lower() and match['part']['id'] ==  pid:
                s_d  = self.get_seller_data()
                d['part_id'] =  pid
                d['mpn'] = mpn
                d['seller'] = []
                sellers = match['part']['sellers']
                #print(f"sellers ")
                for s in sellers:
                    #print(f"s = {s}")
                    s_d['id'] = s['company']['id']
                    s_d['name'] = s['company']['name']
                    s_d['is_verified'] = s['company']['name']
                    s_d['homepage_url'] = s['company']['homepage_url']
                    s_d['is_authorized'] = s['is_authorized']
                    s_d['is_broker'] = s['is_broker']
                    s_d['is_rfq'] = s['is_rfq']
                    s_d['offers'] = []

                    offers = s['offers']
                    o_d = self.get_offers_data()
                    for offer in  offers:
                        o_d['id'] =  offer['id']
                        o_d['stock_level'] =  offer['inventory_level']
                        o_d['offer_url'] =  offer['click_url']
                        o_d['sku'] =  offer['sku']
                        o_d['moq'] =  offer['moq']
                        o_d['packaging'] = offer['packaging']
                        o_d['updated'] = offer['updated']
                        o_d['multipack_quantity'] = offer['multipack_quantity']
                        o_d['order_multiple'] = offer['order_multiple']
                        o_d['prices'] = []
                        prices = offer['prices']
                        p_d = self.get_prices_data()

                        for p in prices:
                            p_d['quantity'] = p['quantity']
                            p_d['price'] = p['price']
                            p_d['converted_price'] = p['converted_price']
                            p_d['converted_currency'] = p['converted_currency']
                            p_d['conversion_rate'] = p['conversion_rate']
                            p_d['currency'] = p['currency']
                            #print(f"p_d = {p_d}")
                            o_d['prices'].append(dict(p_d))
                        s_d['offers'].append(dict(o_d))
                    # print(f"s_d = {s_d}")
                    d['sellers'].append(dict(s_d))
            print(f"d = {d}")

        return d








    def filter_part_matches(self, matches, mpn):
        d = self.get_part_data()

        for match in matches:
            if (match['part']['mpn']).lower() == mpn.lower():

                d['part_id'] = match['part']['id']
                d['name'] = mpn
                d['manufacturer_url'] = match['part']['manufacturer_url']
                d['description'] = match['part']['short_description']
                d['provider'] = self.name
                d['provider_url'] =  match['part']['octopart_url']
                if match['part']['best_image']:
                    d['image_url'] = match['part']['best_image']['url']
                d['factory_lead_time'] = int(match['part']['estimated_factory_lead_days'])
                if match['part']['median_price_1000']:
                    d['median_price'] = float(match['part']['median_price_1000']['converted_price'])
                d['free_sample_url'] = match['part']['free_sample_url']
                if match['part']['best_datasheet']:
                    d['datasheet_url'] =  match['part']['best_datasheet']['url']
                if match['part']['category']:
                    d['category'] = match['part']['category']
                if match['part']['manufacturer']:
                    d['manufacturer'] = match['part']['manufacturer']
                d['avg_avail'] = match['part']['avg_avail']
                d['total_avail'] = match['part']['total_avail']
        return(d)


    def _search_mpn_pro(self, mpn, currency='GBP'):

        query = '''
        query Match_part($q: String, $curr: String!, $country: String!, $limit: Int){
        search_mpn(q: $q, currency: $curr, country: $country, limit: $limit) {
         hits
         results {
		part {
			id
			mpn
			manufacturer_url
			short_description
			estimated_factory_lead_days
			descriptions {
				credit_string
				text
			}
			total_avail
			avg_avail
			best_datasheet{
				name
				url
			}
			free_sample_url
			manufacturer_url
			median_price_1000 {
				converted_currency
				converted_price
			}
			octopart_url
			best_image {
			 	url
			}
			category {
				name
                id
			}
			manufacturer {
				name
				id

			}
		}
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
        resp = self.execute(query, var)
        ret = json.loads(resp)

        return ret['data']['search_mpn']['results']

    def _search_mpns_basic(self, mpns):
        dsl = '''
        query match_mpns($queries: [PartMatchQuery!]!) {
            multi_match(queries: $queries) {
                hits
                reference
                parts {
                    id
                    mpn
                    manufacturer_url
                    short_description
                    octopart_url
                    free_sample_url
                    total_avail
                    avg_avail
                    median_price_1000 {
                      converted_currency
                      converted_price
                    }
                    manufacturer {
                        id
                        name
                    }

                    best_image {
                        url
                    }
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
        resp = self.execute(query, var)
        ret = json.loads(resp)

        return ret['data']['search_mpn']['results']

    def _search_mpn_availability(self, mpn, currency='GBP'):
        print(f"_search_mpn_availability mpn = {mpn}")
        query = '''
        query Match_part($q: String, $curr: String!, $country: String!){
        search_mpn(q: $q, currency: $curr, country: $country) {
            hits
            results {
                part {
                    id
                    mpn
                    sellers{
                        company{
                            id
                            homepage_url
                            is_verified
                            name
                            slug
                        }
                        is_authorized
                        is_broker
                        is_rfq
                        offers{
                            id
                            click_url
                            inventory_level
                            sku
                            moq
                            packaging
                            updated
                            multipack_quantity
                            order_multiple
                            prices{
                                quantity
                                price
                                converted_price
                                converted_currency
                                conversion_rate
                                currency
                            }
                        }
                    }
                }
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
        ret = json.loads(resp)

        return ret['data']['search_mpn']['results']


    def _search_pro(self, mpn, currency="GBP"):

        query = '''
        query MyPartSearch ($q: String!, $curr: String!, $country: String!, $limit: int){
        search(q: $q, currency: $curr, country: $country, limit: $limit) {
         hits
         results {
           part {
             id
             mpn
             manufacturer_url
             short_description
             estimated_factory_lead_days
             descriptions {
              credit_string
              text
            }
            total_avail
            avg_avail
            best_datasheet{
              name
              url
            }
            free_sample_url
            manufacturer_url
            median_price_1000 {
              converted_currency
              converted_price
            }
             octopart_url
             best_image {
                 url
             }
            category {
              name
            }
             manufacturer {
               name
               id

             }
             sellers{
               company{
                  id
                  homepage_url
                  is_verified
                  name
                  slug
                }
                is_authorized
                is_broker
                is_rfq
               offers{
                 id
                 click_url
                 inventory_level
                 sku
                 moq
                 packaging
                 updated
                multipack_quantity
                order_multiple
                 prices{
                   quantity
                   price
                   converted_price
                   converted_currency
                   conversion_rate
                   currency
                     }
                   }
                 }
               }
             }
           }
        }'''
        var = {
          "q": mpn,
          "curr": currency,
          "country": "GB",
          "limit":1
        }
        resp = self.execute(query, var)
        return json.loads(resp)

    def _search_basic(self, mpn, currency="GBP"):

        query = '''
        query MyPartSearch ($q: String!, $curr: String!, $country: String!){
        search(q: $q, currency: $curr, country: $country) {
         hits
         results {
           part {
             id
             mpn
             manufacturer_url
             short_description
             descriptions {
              credit_string
              text
            }
            total_avail
            avg_avail

            free_sample_url
            manufacturer_url
            median_price_1000 {
              converted_currency
              converted_price
            }
             octopart_url
             best_image {
                 url
             }
            category {
              name
            }
             manufacturer {
               name
               id

             }
             sellers{
               company{
                  id
                  homepage_url
                  is_verified
                  name
                  slug
                }
                is_authorized
                is_broker
                is_rfq
               offers{
                 id
                 click_url
                 inventory_level
                 sku
                 moq
                 packaging
                 updated
                multipack_quantity
                order_multiple
                 prices{
                   quantity
                   price
                   converted_price
                   converted_currency
                   conversion_rate
                   currency
                 }
               }
             }
           }
         }
       }
    }'''
        var = {
          "q": mpn,
          "curr": currency,
          "country": "GB"
        }
        resp = self.execute(query, var)
        return json.loads(resp)

    def _match_mpns_pro(self, mpns):
        dsl = '''
        query match_mpns($queries: [PartMatchQuery!]!) {
            multi_match(queries: $queries) {
                hits
                reference
                parts {
                    id
                    mpn
                    manufacturer_url
                    short_description
                    estimated_factory_lead_days
                    octopart_url
                    free_sample_url
                    total_avail
                    avg_avail
                    best_datasheet{
                      name
                      url
                    }
                    median_price_1000 {
                      converted_currency
                      converted_price
                    }
                    manufacturer {
                        id
                        name
                    }

                    best_image {
                        url
                    }
                }
            }
        }
        '''
        #TODO number of parts limits to 1, for enhancemenet this has to be changed
        queries = []
        for mpn in mpns:
            queries.append({
                'mpn_or_sku': mpn,
                'start': 0,
                'limit': 1,
                'reference': mpn,
            })
        resp = self.execute(dsl, {'queries': queries})

        return json.loads(resp)['data']['multi_match']

    def _match_mpns_basic(self, mpns):
        dsl = '''
        query match_mpns($queries: [PartMatchQuery!]!) {
            multi_match(queries: $queries) {
                hits
                reference
                parts {
                    id
                    mpn
                    manufacturer_url
                    short_description
                    octopart_url
                    free_sample_url
                    total_avail
                    avg_avail
                    median_price_1000 {
                      converted_currency
                      converted_price
                    }
                    manufacturer {
                        id
                        name
                    }

                    best_image {
                        url
                    }
                }
            }
        }
        '''
        #TODO number of parts limits to 1, for enhancemenet this has to be changed
        queries = []
        for mpn in mpns:
            queries.append({
                'mpn_or_sku': mpn,
                'start': 0,
                'limit': 1,
                'reference': mpn,
            })
        resp = self.execute(dsl, {'queries': queries})

        return json.loads(resp)['data']['multi_match']

def demo_match_mpns(client, mpn, subscription='basic'):

    mpns = [
        str(mpn),
    ]
    if subscription == 'pro':
        matches = match_mpns(client, mpns)
    elif subscription == 'basic':
        matches = match_mpns_basic(client, mpns)

    #for match in matches:
    #    for part in match['parts']:
    #        print(match['reference'], '\t', part['manufacturer']['name'], '\t', part['mpn'])

    return matches

def demo_search_mpn(client, mpn, currency, subscription='basic'):

    if subscription == 'pro':
        matches = search_mpn(client, mpn, currency)
    elif subscription == 'basic':
        matches = search_mpn_basic(client, mpn, currency)

    #print(matches)
    return matches
