class SumUpException(Exception):
    pass

class SumUpNoAccessCode(SumUpException):
    pass

class SumUpAccessCodeExpired(SumUpException):
    pass

