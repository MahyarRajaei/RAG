class QueryError(Exception):
    """Base class for query-related domain errors."""


class RetrievalError(QueryError):
    pass


class GenerationError(QueryError):
    pass
