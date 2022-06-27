from six.moves import urllib
import json
import os

# copied from: https://github.com/prisma-labs/python-graphql-client/blob/master/graphqlclient/client.py
class OctoPartClient:
    def __init__(self, endpoint, token, headername='token'):
        self.endpoint = endpoint
        self.token = token
        self.headername = headername

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




def search_mpn(client, mpn, currency):

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
    resp = client.execute(query, var)
    return json.loads(resp)

def search_mpn_basic(client, mpn, currency):

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
    resp = client.execute(query, var)
    return json.loads(resp)


def match_mpns(client, mpns):
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
    resp = client.execute(dsl, {'queries': queries})

    return json.loads(resp)['data']['multi_match']

def match_mpns_basic(client, mpns):
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
    resp = client.execute(dsl, {'queries': queries})

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
