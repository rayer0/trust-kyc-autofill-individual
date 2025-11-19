"""Pydantic models shared across the backend."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class IdentificationDocument(BaseModel):
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    country_of_issue: Optional[str] = None
    date_of_issue: Optional[date] = None
    date_of_expiry: Optional[date] = None


class EmploymentInfo(BaseModel):
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    employer_address: Optional[Address] = None
    source_of_wealth: Optional[str] = None
    annual_income: Optional[str] = None


class TaxResidency(BaseModel):
    country: Optional[str] = None
    tin: Optional[str] = None
    reason_no_tin: Optional[str] = None


class ClientProfile(BaseModel):
    full_name_en: Optional[str] = Field(None, description="English full name")
    full_name_native: Optional[str] = Field(None, description="Native language name")
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    residential_address: Optional[Address] = None
    mailing_address: Optional[Address] = None
    identification: Optional[IdentificationDocument] = None
    employment: Optional[EmploymentInfo] = None
    tax_residencies: List[TaxResidency] = Field(default_factory=list)
    source_of_funds: Optional[str] = None
    pep_status: Optional[str] = None
    sanctions_disclosures: Optional[str] = None


class DocumentText(BaseModel):
    source_name: str
    text: str


class GenerationRequest(BaseModel):
    text: str
    hints: Optional[Dict[str, str]] = None


class QAItem(BaseModel):
    question: str
    answer: Optional[str]
    reference_field: Optional[str] = None


class FormAnswer(BaseModel):
    form_id: str
    form_title: str
    answers: List[QAItem]


class GenerationResponse(BaseModel):
    profile: ClientProfile
    forms: List[FormAnswer]


__all__ = [
    "Address",
    "ClientProfile",
    "DocumentText",
    "EmploymentInfo",
    "FormAnswer",
    "GenerationRequest",
    "GenerationResponse",
    "IdentificationDocument",
    "QAItem",
    "TaxResidency",
]
