from typing import Any


def success_response(data: Any = None, message: str = "") -> dict[str, Any]:
    return {
        "success": True,
        "code": "0000",
        "data": {} if data is None else data,
        "msg": message,
        "message": message,
    }


def error_response(error_code: str, message: str) -> dict[str, Any]:
    return {
        "success": False,
        "code": error_code,
        "errorCode": error_code,
        "data": None,
        "msg": message,
        "message": message,
    }
