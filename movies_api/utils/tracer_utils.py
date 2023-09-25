from fastapi import Request
from opentelemetry.trace import Span


def set_span_tag_request_id(request: Request, span: Span):
    request_id = request.headers.get("X-Request-Id")
    span.set_attribute("http.request_id", request_id)
