from typing import Optional, Tuple
from uuid import UUID
from flask import request, current_app
from functools import wraps
from dateutil import parser
from datetime import datetime
from sqlalchemy import and_, or_


After = Tuple[Optional[datetime], Optional[str]]


def paginated(f):

    @wraps(f)
    def paginated_wrapper(*args, **kwargs):
        """
        Parses details about a page being requested by its urls parameters
        and injects them into the wrapped function's kwargs

        Handles parameters of the form:
        ?after=1529089066.003078&after_uuid=e29fba44-6d39-4719-b600-97aadbe876a0&limit=10

        Where the ?after parameter is a either a timestamp or parseable
        datetime (as determined by the dateutil module).
        The ?after_uuid parameter is the uuid used to resolve any conflicts
        between rows with the same created_at datetime.
        The ?limit parameter specifies how many results to return on a page
        that occur after the specified ?after and ?after_uuid parameters
        """
        def_limit = current_app.config['DEFAULT_PAGE_LIMIT']
        max_limit = current_app.config['MAX_PAGE_LIMIT']
        limit = min(request.args.get('limit', def_limit, type=int), max_limit)
        after_date = request.args.get('after', '')
        after_uuid = request.args.get('after_uuid', None)

        # Assume timestamp if ?after is a number
        if after_date.replace('.', '').isdigit():
            after_date = float(after_date)
            after_date = datetime.fromtimestamp(after_date)
        # Otherwise, try to extract a datetime with dateutil parser
        else:
            try:
                after_date = parser.parse(after_date)
            # Parser couldn't derive a datetime from the string
            except ValueError:
                # Fallback to begining of the epoch if we can't parse
                after_date = datetime.fromtimestamp(0)

        # Try to parse a valid UUID, if there is one
        if after_uuid is not None:
            try:
                after_uuid = str(UUID(after_uuid))
            except ValueError:
                after_uuid = None

        # Default the uuid to the zero uuid if none is specified
        if after_uuid is None:
            after_uuid = str(UUID(int=0))

        after = (after_date, after_uuid)
        return f(*args, **kwargs, after=after, limit=limit)

    return paginated_wrapper


class Pagination(object):
    """
    Object to help paginate through endpoints using the created_at field and
    uuid fields
    """

    def __init__(self, query: str, after: After, limit: int):
        self.query = query
        self.after = after
        self.limit = limit
        self.total = query.count()
        # Assumes that we only provide queries for one entity
        # This is safe as pagination only accesses one entity at a time
        model = query._entities[0].mapper.entity

        after_date, after_uuid = after

        query = query.order_by(model.created_at.asc(), model.uuid.asc())
        # Resolve any rows that have the same created_at time by their uuid,
        # return all other rows that were created later
        query = query.filter(
            or_(
                and_(model.created_at == after_date, model.uuid > after_uuid),
                model.created_at > after_date,
            )
        )
        query = query.limit(limit)

        self.items = query.all()

    @property
    def prev_num(self) -> After:
        """ Returns the (datetime, uuid) tuple of the first item """
        if len(self.items) > 0:
            return (self.items[0].created_at, str(self.items[0].uuid))
        return (datetime.fromtimestamp(0), str(UUID(int=0)))

    @property
    def curr_num(self) -> Optional[After]:
        """ Returns the after index of the current page """
        return self.after

    @property
    def next_num(self) -> Optional[After]:
        """ Returns the timestamp, uuid of the last item"""
        if self.has_next:
            return (self.items[-1].created_at, str(self.items[-1].uuid))

    @property
    def has_next(self):
        """ True if there are more than `limit` results """
        return len(self.items) >= self.limit


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
    pager = Pagination(q, after, limit)
    keep = []
    refresh = True
    next_after = None
    # Continue updating the page until we get a page with no deleted files
    while (pager.total > 0 and refresh):
        refresh = False
        # Move the cursor ahead to the last valid file
        next_after = keep[-1].created_at if len(keep) > 0 else after
        # Number of results needed to fulfill the original limit
        remain = limit - len(keep)
        pager = Pagination(q, next_after, remain)

        for st in pager.items:
            if hasattr(st, 'was_deleted') and st.was_deleted:
                refresh = True
            else:
                keep.append(st)

    # Replace original page's items with new list of valid files
    pager.items = keep
    pager.after = next_after if next_after else after

    return pager
