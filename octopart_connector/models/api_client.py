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
    #new API client has to request this and return dict according to defined struct
    def get_dict_data(self):
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
            'avg_avai': None
        }
        return d
