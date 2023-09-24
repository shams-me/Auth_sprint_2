from opentelemetry import trace


async def get_tracer() -> trace.Tracer:
    return trace.get_tracer(__name__)
