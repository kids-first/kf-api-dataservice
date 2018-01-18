def kf_response(results=None, code=200, message='Success', links=None):
    """
    Quick formatter for an API response of the form:

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
    """
    resp = {
         '_status': {
             'code': code,
             'message': message
         }
    }
    if results:
        resp['results'] = results,
    if links:
        resp['_links'] = links

    return resp, code
