class Definitions:
    def __init__(self) -> None:
        self._date_format = "%Y-%m-%d"

    @property
    def date_format(self) -> str:
        return self._date_format

