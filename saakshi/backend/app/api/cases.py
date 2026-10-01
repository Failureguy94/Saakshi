"""Saakshi Case Management API.

Purpose: Endpoints to initialize, register, and query forensic investigation cases.
Inputs: Case registration payloads and query parameters.
Outputs: Created and retrieved case entities backed by persistent database storage.
Status: Implemented
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import CaseModel

router = APIRouter(prefix="/cases", tags=["Cases"])


class CaseCreateRequest(BaseModel):
    """Payload to register a new forensic case."""

    case_number: str = Field(description="Unique official case number (e.g. FIR-124/2026)")
    title: str = Field(description="Descriptive case title")
    description: str | None = Field(default=None, description="Detailed case notes")
    investigator_name: str = Field(description="Name and rank of examining forensic officer")
    agency: str = Field(default="Forensic Science Laboratory", description="Agency or department")


class CaseResponse(BaseModel):
    """Forensic case response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    case_number: str
    title: str
    description: str | None
    investigator_name: str
    agency: str
    status: str
    created_at: datetime
    updated_at: datetime


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreateRequest, db: Session = Depends(get_db)) -> CaseResponse:
    """Register a new forensic investigation case."""
    existing = db.query(CaseModel).filter(CaseModel.case_number == payload.case_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case number '{payload.case_number}' is already registered.",
        )

    new_case = CaseModel(
        case_number=payload.case_number,
        title=payload.title,
        description=payload.description,
        investigator_name=payload.investigator_name,
        agency=payload.agency,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return CaseResponse.model_validate(new_case)


@router.get("", response_model=list[CaseResponse])
def list_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[CaseResponse]:
    """Retrieve all registered forensic cases."""
    cases = db.query(CaseModel).offset(skip).limit(limit).all()
    return [CaseResponse.model_validate(c) for c in cases]


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)) -> CaseResponse:
    """Retrieve a single forensic case by ID."""
    case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID '{case_id}' not found.",
        )
    return CaseResponse.model_validate(case)
