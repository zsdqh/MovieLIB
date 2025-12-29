from starlette.responses import Response


def custom_redirect(response: Response, location: str) -> Response:
    """
    Редирект с реальным переходом по страницам
    нужен для того, чтобы браузер сам выставлял куки между редиректами
    стандартные редиректы fastapi сразу отдают ссылку на нужную страницу,
    не давая браузеру успеть выставить токены
    """
    response.status_code = 303
    response.headers["Location"] = location
    return response
