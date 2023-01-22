class AuthenticationRequestDTO:
    def __init__(self, id: str, token: str) -> None:
        self.id = id
        self.token = token
