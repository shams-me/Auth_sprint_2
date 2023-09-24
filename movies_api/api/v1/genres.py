from http import HTTPStatus
from typing import List

from db.tracer import get_tracer
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.genre import Genre
from opentelemetry import trace
from services.genre import get_genre_service
from utils.tracer_utils import set_span_tag_request_id

from .service_protocol import ModelServiceProtocol

router = APIRouter()


@router.get(
    "/search",
    summary="Search throw genres",
    description="Write genre name to field search to retrieve all genres with this name.",
    tags=["Search"],
    response_model=List[Genre],
)
async def genre_details_list(
    request: Request,
    search: str = Query(None, description="Searching text"),
    page_size: int = Query(50, ge=1, le=100, description="Number of genres per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    model_service: ModelServiceProtocol[Genre] = Depends(get_genre_service),
    tracer: trace.Tracer = Depends(get_tracer),
) -> List[Genre]:
    with tracer.start_as_current_span("genre_details") as span:
        set_span_tag_request_id(request=request, span=span)
        genres = await model_service.get_many_by_parameters(
            search=search,
            page_number=page_number,
            page_size=page_size,
        )

        return genres


@router.get(
    "/{genre_id}",
    tags=["Genres"],
    description="Returns information about genre according uuid.",
    response_model=Genre,
)
async def genre_details(
    genre_id: str,
    request: Request,
    model_service: ModelServiceProtocol[Genre] = Depends(get_genre_service),
    tracer: trace.Tracer = Depends(get_tracer),
) -> Genre:
    with tracer.start_as_current_span("genre_details") as span:
        set_span_tag_request_id(request=request, span=span)
        genre = await model_service.get_by_id(genre_id)
        if not genre:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

        return genre
