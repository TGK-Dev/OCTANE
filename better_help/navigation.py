__all__ = ["Navigation"]

from re import search


class Navigation:
    def __init__(self, pg_left="◀", pg_right="▶", cancel="⏹", start="⏮", end="⏭"):
        self.pg_left = self.__get_match(pg_left)
        self.pg_right = self.__get_match(pg_right)
        self.cancel = self.__get_match(cancel)
        self.start = self.__get_match(start)
        self.end = self.__get_match(end)

    @property
    def _dict(self) -> dict:
        return {
            self.start: -2,
            self.pg_left: -1,
            self.cancel: 0,
            self.pg_right: 1,
            self.end: 2,
        }

    @staticmethod
    def custom(emoji):
        return f":{emoji.name}:{emoji.id}"

    def get(self, emoji):
        if isinstance(emoji, str):
            return self._dict.get(emoji)
        else:
            return self._dict.get(self.custom(emoji))

    def __contains__(self, emoji):
        if isinstance(emoji, str):
            return emoji in self._dict
        else:
            return self.custom(emoji) in self._dict

    @staticmethod
    def __get_match(emoji: str):
        try:
            return search(r":[a-zA-Z0-9]+:[0-9]+", emoji)[0]
        except TypeError:
            return emoji

    def __iter__(self):
        return self._dict.__iter__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} pg_left:{self.pg_left} pg_right:{self.pg_right} cancel:{self.cancel} start:{self.start} end:{self.end}>"
