from http import HTTPStatus
from typing import List

from db.tracer import get_tracer
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.oauth import Roles
from models.person import Person
from opentelemetry import trace
from services.person import get_person_service
from utils.oauth2 import allowed_user
from utils.tracer_utils import set_span_tag_request_id

from .service_protocol import ModelServiceProtocol

router = APIRouter()


@router.get(
    "/search",
    summary="Search throw persons according name.",
    description="Write full_name of person to field 'search' to get all persons with such name.",
    tags=["Search"],
    response_model=List[Person],
    dependencies=[Depends(allowed_user(roles=[Roles.SUPERUSER, Roles.ADMIN, Roles.MODERATOR]))],
)
async def person_details_list(
    request: Request,
    search: str = Query(None, description="Searching text"),
    page_size: int = Query(50, ge=1, le=100, description="Number of persons per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    model_service: ModelServiceProtocol[Person] = Depends(get_person_service),
    tracer: trace.Tracer = Depends(get_tracer),
) -> List[Person]:
    with tracer.start_as_current_span("person_details") as span:
        set_span_tag_request_id(request, span)
        persons = await model_service.get_many_by_parameters(
            search=search,
            page_number=page_number,
            page_size=page_size,
        )

        return persons


@router.get(
    "/{person_id}",
    tags=["Persons"],
    description="Returns information about person according uuid.",
    response_model=Person,
    dependencies=[Depends(allowed_user(roles=[Roles.SUPERUSER, Roles.ADMIN, Roles.MODERATOR]))],
)
async def person_details(
    person_id: str,
    model_service: ModelServiceProtocol[Person] = Depends(get_person_service),
) -> Person:
    person = await model_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return person
