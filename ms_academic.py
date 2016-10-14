import sys, os, warnings, requests

MICROSOFT_ACADEMIC_KEY = os.environ.get('MICROSOFT_ACADEMIC_KEY') or ''
if not MICROSOFT_ACADEMIC_KEY:
    warnings.warn('MICROSOFT_ACADEMIC_KEY not set in environment')

api_request_header = {
        'Ocp-Apim-Subscription-Key': MICROSOFT_ACADEMIC_KEY
        }

interpret_url = 'https://api.projectoxford.ai/academic/v1.0/interpret'

class MicrosoftAcademic(object):

    """Interact with Microsoft Academic API"""

    def __init__(self, **kwargs):
        """TODO: to be defined1. """
        self.header = api_request_header
        self.interpret_url = interpret_url

    def get_interpret_response(self, query='', count=1, offset=0):
        """Make a request to the interpret API and return a response

        :query: text query to be passed to the requests module
        :count: number of responses to return (default: 1)
        :offset: offset value for pagination of responses (default: 0)
        :returns: response dictionary (from requests.json())

        """
        params = {
                    'query': query,
                    'count': count,
                    'offset': offset,
                    'complete': 0
                }
        r = requests.get(self.interpret_url, params=params, headers=self.header)
        return r.json()

    def get_evaluate_query_from_interpret_resp(self, resp_dict, interpret_idx=0):
        """From a response (dictionary) from the interpret method, get a query to feed to the evaluate method.

        :resp_dict: response from the interpret method (can use get_interpret_response() )
        :interpret_idx: Since the interpret method can return multiple interpretations, interpret_idx is the zero-based index to select (default: 0 (the first one))
        :returns: query to use with the API's evaluate method (string)

        """
        q = resp_dict['interpretations'][interpret_idx]
        q = q['rules'][0]
        q = q['output']['value']
        return q

    def get_evaluate_response(self, expr, attributes='Id', count=10, offset=0):
        """Make a request to the evaluate API and return a response

        :expr: query expression
        :attributes: attributes to include in the response (https://www.microsoft.com/cognitive-services/en-us/Academic-Knowledge-API/documentation/EntityAttributes) (default: 'Id')
        :count: number of entities to return (default: 10)
        :offset: offset value for pagination (default: 0)
        :returns: response dictionary (from requests.json())

        """
        params = {
                    'expr': expr,
                    'attributes': attributes,
                    'count': count,
                    'offset': offset
                }
        r = requests.get(self.interpret_url, params=params, headers=self.header)
        return r.json()

        

