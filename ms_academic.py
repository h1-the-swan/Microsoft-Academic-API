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
        self.attributes = kwargs.get('attributes')
        if not self.attributes:
            self.attributes = "Id"
        self.query_threshold = kwargs.get('query_threshold')
        if not self.query_threshold:
            self.query_threshold = 1000
        self._number_of_queries = 0

    @property
    def number_of_queries(self):
        return self._number_of_queries

    @number_of_queries.setter
    def number_of_queries(self, value):
        if value > self.query_threshold:
            # too many queries
            raise RuntimeError("This instance has made {} queries. No more queries allowed".format(self.query_threshold))
        else:
            self._number_of_queries = value


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
        self.number_of_queries += 1
        r = requests.get(self.interpret_url, params=params, headers=self.header)
        return r.json()

    def get_evaluate_query_from_interpret_resp(self, resp_dict, interpret_idx=0):
        """From a response (dictionary) from the interpret method, get a query to feed to the evaluate method.

        :resp_dict: response from the interpret method (can use get_interpret_response() )
        :interpret_idx: Since the interpret method can return multiple interpretations, interpret_idx is the zero-based index to select (default: 0 (the first one))
        :returns: query to use with the API's evaluate method (string)

        """
        if not resp_dict['interpretations']:
            return ''
        q = resp_dict['interpretations'][interpret_idx]
        q = q['rules'][0]
        q = q['output']['value']
        return q

    def get_evaluate_response(self, expr, attributes='Id', count=10, offset=0):
        """Make a request to the evaluate API and return a response

        :expr: query expression
        :attributes: (comma-separated) attributes to include in the response (https://www.microsoft.com/cognitive-services/en-us/Academic-Knowledge-API/documentation/EntityAttributes) (default: 'Id')
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
        self.number_of_queries += 1
        r = requests.get(self.evaluate_url, params=params, headers=self.header)
        return r.json()

    def interpret_and_evaluate(self, query, attributes=None, count=10, return_expr=False):
        """TODO: Docstring for interpret_and_evaluate.

        :query: text query to be passed to the requests module
        :attributes: (comma-separated) attributes to include in the response (https://www.microsoft.com/cognitive-services/en-us/Academic-Knowledge-API/documentation/EntityAttributes) (default: 'Id')
        :count: number of entities to return (default: 10)
        :return_expr: if True, return a dictionary with keys: 'expr' which has the expression used for the evaluate method, and 'entities' which is a list of entities. Otherwise just return the list of entities (default: False)
        :returns: list of entities

        """
        if attributes is None:
            attributes = self.attributes

        j = self.get_interpret_response(query)
        expr = self.get_evaluate_query_from_interpret_resp(j)
        if not expr:
            return []
        r = self.get_evaluate_response(expr, attributes=attributes, count=count)
        self. attributes = attributes
        self.current_expr = r['expr']
        self.current_offset = len(r['entities'])
        if return_expr is True:
            return r
        else:
            return r['entities']

    def paginate(self, expr="", offset=None, count=10):
        """Returns a new page of results for an expression (from the evaluate method)

        :expr: query expression for the evaluate method
        :offset: offset value (should equal the number of entities already retrieved previously)
        :returns: list of entities

        """
        if not expr:
            expr = self.current_expr
        if offset is None:
            offset = self.current_offset
        r = self.get_evaluate_response(expr, attributes=self.attributes, offset=offset, count=count)
        if 'entities' in r:
            entities = r['entities']
            self.current_offset += len(r['entities'])
            return r['entities']
        else:
            # something went wrong
            print(r)

    def get_paperids(self, entities_list):
        """Takes a list of entities as returned by the evaluate API and returns a list of paper IDs as strings.

        :entities_list: list of entities (dictionaries). should have 'Id' as a key
        :returns: list of paper IDs as strings

        """
        return [str(entity['Id']) for entity in entities_list]
