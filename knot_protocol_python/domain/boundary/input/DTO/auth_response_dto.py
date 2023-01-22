class AuthResponseDTO:
    def __init__(self, id: str, error: str = None) -> None:
        self.id = id
        self.error = error
