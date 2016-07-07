"""    Briefy HTTP error with status codes   """
import json

from webob import exc
from webob import Response

# WebOb is usd by cornice - but it's HTTPError classes
# can't handle a json response body.

class HTTPErrorJSONPayload(exc.HTTPError):
    code = 500
    default_msg = "Internal server error"

    def __init__(self, msg=None):
        super().__init__()
        if msg is None:
            msg = self.default_msg
        body = {'status': self.status_code, 'message': msg}
        Response.__init__(self, json.dumps(body))
        self.status = self.code
        self.content_type = 'application/json'

# TODO: Add other errors if agreeded this is the best way.


class HTTPConflict(BriefyHTTPError):
    code = 409
    default_msg = "Conflicting data"
