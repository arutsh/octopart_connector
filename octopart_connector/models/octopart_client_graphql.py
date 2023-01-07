from six.moves import urllib
import json
import os
from odoo.addons.octopart_connector.models.api_client import ApiClient

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


class OctopartGraphQL():

    """
    Partial Graphql Query for getting manufacturers data
    """
    @classmethod
    def get_manufacturer(self):
        return '''manufacturer {
                    id
                    is_verified
                    homepage_url
                    name
                }'''

    """
    Partial Graphql Query for getting part data for pro subscribtion
    @:param 
    @:returns grapqhql query
    """

    @classmethod
    def get_pro_parts(self):
        return '''best_image {
        			url
        		  }
                  estimated_factory_lead_days'''

    """
    Partial Graphql query for getting company details 
    """

    @classmethod
    def get_contact_data(self):
        return '''company {
                      id
                      homepage_url
                      is_verified
                      name
                      is_distributorapi
                    } '''

    """
    Partial Graphql Query for getting part data
    if subscribtion is PRO, when relevant data is added to query to
    """

    @classmethod
    def get_part(self, subscription):
        part = '''
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

			category {
				name
                id
			}
            ''' + self.get_manufacturer()

        closing = '''}'''
        if subscription == "pro":
            part = part + self.get_pro_parts() + closing
        else:
            part = part + closing

        return part

    """
    
    @:param mpn - manufacturer part number
    @:param [currency='GBP'] - Currency which is by default GPB
    @:returns graphql query to search given mpn for the given currency
    """

    @classmethod
    def search_mpn(self, subscription, mpn, currency='GBP'):

        query = '''
        query Match_part($q: String, $curr: String!, $country: String!, $limit: Int){
        search_mpn(q: $q, currency: $curr, country: $country, limit: $limit) {
         hits
         results { ''' + self.get_part(subscription) + '''

             }
           }
        }
        '''
        var = {
            "q": mpn,
            "curr": currency,
            "country": "GB",
        }
        # resp = self.execute(query, var)
        # ret = json.loads(resp)
        ret_data = {
            'query_body': query,
            'variables': var,
            'nested_data': ['data', 'search_mpn', 'results']
        }
        # return ret['data']['search_mpn']['results']
        return ret_data

    """
    Graphql request for quering mpn availability
    """
    @classmethod
    def search_mpn_availability(self, mpn, currency='GBP'):
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
        # resp = self.execute(query, var)
        # ret = json.loads(resp)

        ret_data = {
            'query_body': query,
            'variables': var,
            'nested_data': ['data', 'search_mpn', 'results']
        }

        return ret_data
