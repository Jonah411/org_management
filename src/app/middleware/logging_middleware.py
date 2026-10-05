import time
import uuid

from fastapi import Request


async def logging_middleware(request: Request, call_next):

    start_time = time.perf_counter()

    request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    print(
        f"➡️ [{request_id}] "
        f"{request.method} {request.url.path}"
    )

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id

    print(
        f"⬅️ [{request_id}] "
        f"{response.status_code} "
        f"| {process_time:.4f}s"
    )

    return response