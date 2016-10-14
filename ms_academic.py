import sys, os, warnings, requests

MICROSOFT_ACADEMIC_KEY = os.environ.get('MICROSOFT_ACADEMIC_KEY') or ''
if not MICROSOFT_ACADEMIC_KEY:
    warnings.warn('MICROSOFT_ACADEMIC_KEY not set in environment')

api_request_header = {
        'Ocp-Apim-Subscription-Key': MICROSOFT_ACADEMIC_KEY
        }

interpret_url = 'https://api.projectoxford.ai/academic/v1.0/interpret'
evaluate_url = 'https://api.projectoxford.ai/academic/v1.0/evaluate'

class MicrosoftAcademic(object):

    """Interact with Microsoft Academic API"""

    def __init__(self, **kwargs):
        """TODO: to be defined1. """
        self.header = api_request_header
        self.interpret_url = interpret_url
        self.evaluate_url = evaluate_url
        self.current_expr = ""
        self.current_offset = 0

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
        r = requests.get(self.evaluate_url, params=params, headers=self.header)
        return r.json()

    def interpret_and_evaluate(self, query, count=10):
        """TODO: Docstring for interpret_and_evaluate.

        :query: TODO
        :returns: dictionary with keys: 'expr' which has the expression used for the evaluate method, and 'entities' which is a list of entities

        """
        j = self.get_interpret_response(query)
        expr = self.get_evaluate_query_from_interpret_resp(j)
        r = self.get_evaluate_response(expr, attributes='Id,Ti', count=count)
        self.current_expr = r['expr']
        self.current_offset = len(r['entities'])
        return r

    def paginate(self, expr="", offset=None):
        """Returns a new page of results for an expression (from the evaluate method)

        :expr: query expression for the evaluate method
        :offset: offset value (should equal the number of entities already retrieved previously)
        :returns: list of entities

        """
        if not expr:
            expr = self.current_expr
        if offset is None:
            offset = self.current_offset
        r = self.get_evaluate_response(expr, offset=offset)
        if 'entities' in r:
            entities = r['entities']
            self.current_offset += len(r['entities'])
            return r['entities']
        else:
            print(r)

        

