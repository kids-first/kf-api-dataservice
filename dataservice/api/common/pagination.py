from flask import request, current_app
from functools import wraps
from dateutil import parser
from datetime import datetime
from dataservice.extensions import db, indexd


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

        return f(*args, **kwargs,
                 after=after,
                 limit=limit)

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
            return self._to_timestamp(self.items[0].created_at) - 1 / 100000
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


def indexd_pagination(q, after, limit):
    """
    Special logic to paginate through indexd objects.
    Whenever an indexd object is encountered that has been deleted in indexd,
    the file is then deleted in the dataservice, thus making it necesarry to
    re-fetch new files to return the desired amount of objects per page

    :param q: The base query to perform
    :param after: The earliest datetime to return objects from
    :param limit: The maximum number of objects to return in a page

    :returns: A Pagination object
    """
    def prefetch_indexd(after):
        """ Compute dids for the page and have indexd fetch them in bulk """
        model = q._entities[0].mapper.entity
        gfs = (q.order_by(model.created_at.asc())
                .filter(model.created_at > after)
                .with_entities(model.latest_did)
                .limit(limit).all())
        dids = [gf[0] for gf in gfs]
        indexd.prefetch(dids)

    indexd.clear_cache()
    prefetch_indexd(after)
    pager = Pagination(q, after, limit)
    keep = []
    refresh = True
    next_after = None
    # Continue updating the page until we get a page with no deleted files
    while (pager.total > 0 and refresh):
        refresh = False
        for st in pager.items:
            if hasattr(st, 'was_deleted') and st.was_deleted:
                refresh = True
            else:
                keep.append(st)

        # Only fetch more if we saw there were some items that were deleted
        if refresh:
            # Move the cursor ahead to the last valid file
            next_after = keep[-1].created_at if len(keep) > 0 else after
            # Number of results needed to fulfill the original limit
            remain = limit - len(keep)

            prefetch_indexd(next_after)
            pager = Pagination(q, next_after, remain)

    # Replace original page's items with new list of valid files
    pager.items = keep
    pager.after = next_after if next_after else after

    return pager
