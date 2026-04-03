def is_attendance_response(
    url: str,
    method: str,
    attendance_path: str = "/web/v1/game/endfield/attendance",
) -> bool:
    from urllib.parse import urlparse

    path = urlparse(url).path.rstrip("/")
    return path == attendance_path.rstrip("/") and method.upper() == "GET"


