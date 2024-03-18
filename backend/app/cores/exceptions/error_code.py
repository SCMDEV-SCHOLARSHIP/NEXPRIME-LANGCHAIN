from enum import Enum


class ErrorCode(Enum):
    BAD_REQUEST = ("KMG_ERR_R_001", "Bad Request")
    NOT_EXIST = ("KMG_ERR_R_002", "Not exists")
    DUPLICATED_VALUE = ("KMG_ERR_R_003", "Dupllicated value")
    INVALID_FORMAT = ("KMG_ERR_R_004", "Invalid format")

    INTERNAL_SERVER_ERROR = ("KMG_ERR_S_001", "Internal Server Error")

    EXTERNAL_SERVICE_ERROR = ("KMG_ERR_E_001", "External Service Error")
