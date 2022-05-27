from six.moves import urllib
import json
import os

# copy pasted from: https://github.com/prisma-labs/python-graphql-client/blob/master/graphqlclient/client.py
class OctoPartClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = None
        self.headername = None

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
         manufacturer {
           name
           id
         }
         sellers{
           company{
             id
             name
           }
           offers{
             id
             click_url
             inventory_level
             sku
             moq
            multipack_quantity
            order_multiple
             prices{
               quantity
               price
               converted_price
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
                manufacturer {
                    id
                    name
                }
                mpn
                manufacturer_url
                short_description
                octopart_url
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

def demo_match_mpns(client, mpn):
    print('\n---------------- demo_match_mpns')


    mpns = [
        str(mpn),
    ]

    matches = match_mpns(client, mpns)

    #for match in matches:
    #    for part in match['parts']:
    #        print(match['reference'], '\t', part['manufacturer']['name'], '\t', part['mpn'])

    return matches

def demo_search_mpn(client, mpn, currency):
    print('\n---------------- demo_search_mpn_____')

    matches = search_mpn(client, mpn, currency)
    #print(matches)
    return matches
