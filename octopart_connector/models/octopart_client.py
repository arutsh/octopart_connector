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

        # if self.subscription == 'pro':
        #     matches = self._search_mpn_pro(mpn)
        # elif self.subscription == 'basic':
        #     matches = self._search_mpn_pro(mpn)

            ## TODO:  Remove after # DEBUG:
        matches = STRING
        return self.filter_matches(matches, mpn)

    def filter_matches(self, matches, mpn):
        d = self.get_dict_data()

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
