from six.moves import urllib
import json
import os
from odoo.addons.octopart_connector.models.api_client import ApiClient

class OctopartApiClient(ApiClient):
    def __init__(self, provider, token, endpoint, subscription=None, headername='token'):
        print("I am octopart client")
        super().__init__(provider, token, endpoint, headername='token')
        if subscription:
            self.subscription = subscription
    def search_mpns(self, mpn, currency):
        if self.subscription == 'basic':
            return self._search_mpn_basic(mpn, currency)
        if self.subscription == 'pro':
            return self._search_mpn_pro(mpn, currency)

    def match_mpns(self, mpn):

        mpns = [
            str(mpn),
        ]
        if self.subscription == 'pro':
            matches = self._match_mpns_pro(mpns)
        elif self.subscription == 'basic':
            matches = self._match_mpns_basic(mpns)

        return matches


    def _search_mpn_pro(self, mpn, currency="GBP"):

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
          "country": "GB"
        }
        resp = self.execute(query, var)
        return json.loads(resp)

    def _search_mpn_basic(self, mpn, currency="GBP"):

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
