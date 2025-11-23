class DomainException(Exception):
    pass


class UserNotFoundException(DomainException):
    pass


class UserAlreadyExistsException(DomainException):
    pass


class InvalidEmailException(DomainException):
    pass


class InvalidUsernameException(DomainException):
    pass

