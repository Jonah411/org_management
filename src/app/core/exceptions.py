class UserNotFoundException(Exception):

    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsException(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidOTPException(Exception):

    def __init__(
        self,
        message: str = "Invalid or expired OTP"
    ):
        self.message = message
        super().__init__(self.message)

class AuthenticationException(Exception):

    def __init__(
        self,
        message: str = "Authentication failed"
    ):
        self.message = message
        super().__init__(self.message)

class AIServiceException(Exception):
    """Raised when an AI service operation fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class InvalidPasswordException(Exception):
    def __init__(self, message: str = "Invalid password"):
        self.message = message
        super().__init__(self.message)