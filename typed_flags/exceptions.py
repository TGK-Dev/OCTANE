from discord import DiscordException


class BaseFlagException(DiscordException):
    """A base exception handler for flags."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message


class ReservedKeyword(BaseFlagException):
    """This keyword is reserved internally and cannot be a flag. (argless)"""
