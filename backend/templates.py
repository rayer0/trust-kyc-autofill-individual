"""Mapping helpers to turn a ClientProfile into form-specific question/answers."""
from __future__ import annotations

from typing import Callable, Iterable, List

from .models import ClientProfile, FormAnswer, QAItem


class FormTemplate:
    def __init__(self, form_id: str, title: str, mappings: Iterable[tuple[str, str, Callable[[ClientProfile], str | None]]]):
        self.form_id = form_id
        self.title = title
        self.mappings = list(mappings)

    def render(self, profile: ClientProfile) -> FormAnswer:
        answers = [
            QAItem(question=question, answer=value(profile), reference_field=reference)
            for reference, question, value in self.mappings
        ]
        return FormAnswer(form_id=self.form_id, form_title=self.title, answers=answers)


def _attr_getter(path: str) -> Callable[[ClientProfile], str | None]:
    def getter(profile: ClientProfile) -> str | None:
        current = profile
        for segment in path.split("."):
            current = getattr(current, segment, None)
            if current is None:
                return None
        if isinstance(current, list):
            return "; ".join(filter(None, (str(item) for item in current))) or None
        return str(current) if current is not None else None

    return getter


def _first_tax_country(profile: ClientProfile) -> str | None:
    return profile.tax_residencies[0].country if profile.tax_residencies else None


def _first_tax_tin(profile: ClientProfile) -> str | None:
    return profile.tax_residencies[0].tin if profile.tax_residencies else None


FORMS: List[FormTemplate] = [
    FormTemplate(
        "1.3",
        "客户开户申请表（个人）",
        [
            ("full_name_en", "English Full Name", _attr_getter("full_name_en")),
            ("full_name_native", "Chinese Name", _attr_getter("full_name_native")),
            ("date_of_birth", "Date of Birth", _attr_getter("date_of_birth")),
            ("nationality", "Nationality", _attr_getter("nationality")),
            ("residential_address", "Residential Address", _attr_getter("residential_address.line1")),
            ("phone", "Contact Phone", _attr_getter("phone")),
            ("email", "Email", _attr_getter("email")),
        ],
    ),
    FormTemplate(
        "1.4",
        "Declaration on Source of Wealth – Individual",
        [
            ("employment.occupation", "Occupation", _attr_getter("employment.occupation")),
            ("employment.employer_name", "Employer Name", _attr_getter("employment.employer_name")),
            ("employment.source_of_wealth", "Source of Wealth", _attr_getter("employment.source_of_wealth")),
            ("source_of_funds", "Source of Funds", _attr_getter("source_of_funds")),
        ],
    ),
    FormTemplate(
        "1.5",
        "无犯罪、监管、制裁或罚款声明（个人）",
        [
            ("pep_status", "Are you a PEP?", _attr_getter("pep_status")),
            (
                "sanctions_disclosures",
                "Any criminal / regulatory / sanction disclosures",
                _attr_getter("sanctions_disclosures"),
            ),
        ],
    ),
    FormTemplate(
        "1.2",
        "CRS Individual Self Certification Form",
        [
            ("full_name_en", "Name", _attr_getter("full_name_en")),
            ("tax_residencies.country", "Tax Residency Country", _first_tax_country),
            ("tax_residencies.tin", "Tax Identification Number", _first_tax_tin),
        ],
    ),
    FormTemplate(
        "1.1",
        "Form W-8BEN (individual)",
        [
            ("full_name_en", "Name of individual", _attr_getter("full_name_en")),
            ("residential_address", "Permanent residence address", _attr_getter("residential_address.line1")),
            ("tax_residencies", "U.S. TIN (if any)", _first_tax_tin),
        ],
    ),
]


def build_form_answers(profile: ClientProfile) -> List[FormAnswer]:
    return [template.render(profile) for template in FORMS]


__all__ = ["build_form_answers"]
