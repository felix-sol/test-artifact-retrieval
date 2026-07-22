from fastapi import Request


def get_retrieval_service(request: Request):
    return request.app.state.retrieval_service
