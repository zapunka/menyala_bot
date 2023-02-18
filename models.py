class ExchangeResponse:
    error: str
    result: str
    status: int
    headers: dict

    def __init__(self, error, result, status, headers):
        self.error = error
        self.result = result
        self.status = status
        self.headers = headers