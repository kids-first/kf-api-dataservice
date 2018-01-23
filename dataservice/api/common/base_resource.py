from flask_restplus import Resource


class BaseResource(Resource):
    """
    Formats resource responses into a standard format:
    ```
    {
      "_links": {
        ...
      },
      "_status": {
        "code": 200,
        "message": "Success"
      },
      "results": [
        ...
      ]
    }
    ```

    Any resource that extends `BaseResource` should return tuples of the form:
    ```
    body, [[[status_code], [message]], [links]]
    ```
    """
    def __init__(self, api, *args, **kwargs):
        self.api = api
        super(BaseResource, self).__init__(api, *args, **kwargs)

    def dispatch_request(self, *args, **kwargs):
        r = super(BaseResource, self).dispatch_request(*args, **kwargs)
        results = r[0]
        code = r[1] if len(r) > 1 else 200
        message = r[2] if len(r) > 2 else 'Success'
        resp = {
             '_status': {
                 'code': code,
                 'message': message
             }
        }
        resp['results'] = results

        # Generic flask response: body, code
        return resp, code
