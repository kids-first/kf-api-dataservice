from flask import request, current_app
from functools import wraps
from dateutil import parser
from datetime import datetime


def paginated(f):

    @wraps(f)
    def paginated_wrapper(*args, **kwargs):
        def_limit = current_app.config['DEFAULT_PAGE_LIMIT']
        max_limit = current_app.config['MAX_PAGE_LIMIT']
        limit = min(request.args.get('limit', def_limit, type=int), max_limit)
        after = request.args.get('after', None)

        if type(after) is str:
            # Parser won't recognize the timestamp with fractional seconds
            if after.replace('.', '').isdigit():
                after = float(after)
                after = datetime.fromtimestamp(after)
            else:
                try:
                    after = parser.parse(after)
                # Parser couldn't derive a datetime from the string
                except ValueError:
                    after = None

        # Default to the unix epoch
        if after is None:
            after = datetime.fromtimestamp(0)

        return f(*args, **kwargs, after=after, limit=limit)

    return paginated_wrapper


class Pagination(object):
    """
    Object to help paginate through endpoints using the created_at field
    """

    def __init__(self, query, after, limit):
        assert type(after) is datetime
        self.query = query
        self.after = after
        self.limit = limit
        self.total = query.count()
        # Assumes that we only provide queries for one entity
        # This is safe as pagination only accesses one entity at a time
        model = query._entities[0].mapper.entity
        assert hasattr(model, 'created_at')
        self.items = (query.order_by(model.created_at.asc())
                           .filter(model.created_at > after)
                           .limit(limit).all())

    @property
    def prev_num(self):
        """ Returns the timestamp of the first item """
        if len(self.items) > 0:
            return self._to_timestamp(self.items[0].created_at)
        return datetime.fromtimestamp(0)

    @property
    def curr_num(self):
        """
        Returns the timestamp of the first item minus some epsilon
        so that the current timestamp will be included in the range
        """
        if len(self.items) > 0:
            return self._to_timestamp(self.items[0].created_at) - 1/1000
        return self._to_timestamp(datetime.utcnow())

    @property
    def next_num(self):
        """ Returns the timestamp of the last item"""
        if self.has_next:
            return self._to_timestamp(self.items[-1].created_at)

    @property
    def has_next(self):
        """ True if there are more than `limit` results """
        return len(self.items) >= self.limit

    def _to_timestamp(self, dt):
        """ Converts a datetime object to milliseconds since epoch """
        return dt.timestamp()
