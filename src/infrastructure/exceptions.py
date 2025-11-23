class DatabaseException(Exception):
    pass


class DatabaseConnectionException(DatabaseException):
    pass


class DatabaseTransactionException(DatabaseException):
    pass

