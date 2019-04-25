__all__ = ["HttpQueryError"]


class HttpQueryError(Exception):
    def __init__(self, status: int, message: str = None) -> None:
        self.status = status
        self.message = message

    def as_dict(self):
        return {"errors": [self.message]}
