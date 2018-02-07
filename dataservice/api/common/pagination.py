from flask import request, current_app
from functools import wraps


def paginated(f):

    @wraps(f)
    def paginated_wrapper(*args, **kwargs):
        def_limit = current_app.config['DEFAULT_PAGE_LIMIT']
        max_limit = current_app.config['MAX_PAGE_LIMIT']
        limit = min(request.args.get('limit', def_limit, type=int), max_limit)
        page = request.args.get('page', 1, type=int)
        return f(*args, **kwargs, limit=limit, page=page)

    return paginated_wrapper
