from flask import request, current_app
from functools import wraps


def paginated(f):

    @wraps(f)
    def paginated_wrapper(*args, **kwargs):
        def_size = current_app.config['DEFAULT_PAGE_SIZE']
        max_size = current_app.config['MAX_PAGE_SIZE']
        limit = min(request.args.get('size', def_size, type=int), max_size)
        page = request.args.get('page', 1, type=int)
        return f(*args, **kwargs, limit=limit, page=page)

    return paginated_wrapper
