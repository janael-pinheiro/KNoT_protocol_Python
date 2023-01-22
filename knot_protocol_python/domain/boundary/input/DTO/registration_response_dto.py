class RegistrationResponseDTO:
    def __init__(self, id: str, name: str, token: str, error: str = None) -> None:
        self.id = id
        self.name = name
        self.token = token
        self.error = error
