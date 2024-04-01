from enum import Enum


class ErrorCode(Enum):
    BAD_REQUEST = ("KMG_ERR_R_001", "Bad Request")
    NOT_EXIST = ("KMG_ERR_R_002", "Not exists")
    DUPLICATED_VALUE = ("KMG_ERR_R_003", "Dupllicated value")
    INVALID_FORMAT = ("KMG_ERR_R_004", "Invalid format")
    NOT_MATCHED_VALUE = ("KMG_ERR_R_005", "Not matched value")
    FORBIDDEN_ACCESS = ("KMG_ERR_R_006", "Forbidden access")
    EXPIRED = ("KMG_ERR_R_007", "Expired")
    NOT_EXPIRED = ("KMG_ERR_R_008", "Not expired yet")
    INCORRECT_PASSWORD = ("KMG_ERR_R_009", "Incorrect password value")

    INTERNAL_SERVER_ERROR = ("KMG_ERR_S_001", "Internal Server Error")

    EXTERNAL_SERVICE_ERROR = ("KMG_ERR_E_001", "External Service Error")
