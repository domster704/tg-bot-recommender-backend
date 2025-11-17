from starlette.requests import Request


def get_recommender(request: Request):
    return request.app.state.recommender
