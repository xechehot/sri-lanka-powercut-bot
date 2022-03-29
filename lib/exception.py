class PowercutBotException(Exception):
    pass


class PdfParseError(PowercutBotException):
    pass


class ExpiringCacheException(PowercutBotException):
    pass


class UpdateExpiredValueError(ExpiringCacheException):
    pass
