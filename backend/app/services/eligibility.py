"""Applicant-type eligibility check for Grants.gov opportunities.

Grants.gov applicantTypes ids that can cover a for-profit startup:
  23  Small businesses
  22  For-profit organizations other than small businesses
  99  Unrestricted
  25  Others (free-text clarification — ambiguous, needs verification)
Everything else (nonprofits, universities, governments, tribes, individuals)
does not cover a for-profit company.
"""
from __future__ import annotations

STARTUP_OK = {"23", "22", "99"}
AMBIGUOUS = {"25"}


def evaluate(applicant_types: list[dict]) -> tuple[str, list[str]]:
    """Returns (flag, short_descriptions). flag: ok | verify | likely_ineligible."""
    if not applicant_types:
        return "verify", []
    ids = {str(t.get("id")) for t in applicant_types}
    descs = [_shorten(t.get("description") or "") for t in applicant_types]
    if ids & STARTUP_OK:
        return "ok", descs
    if ids & AMBIGUOUS:
        return "verify", descs
    return "likely_ineligible", descs


def _shorten(desc: str) -> str:
    cuts = {
        "Nonprofits having a 501(c)(3) status with the IRS, other than institutions of higher education": "501(c)(3) nonprofits",
        "Nonprofits that do not have a 501(c)(3) status with the IRS, other than institutions of higher education": "Other nonprofits",
        "Private institutions of higher education": "Private universities",
        "Public and State controlled institutions of higher education": "Public universities",
        "Native American tribal governments (Federally recognized)": "Tribal governments",
        "Native American tribal organizations (other than Federally recognized tribal governments)": "Tribal organizations",
        "Public housing authorities/Indian housing authorities": "Housing authorities",
        "State governments": "State governments",
        "County governments": "County governments",
        "City or township governments": "City governments",
        "Special district governments": "District governments",
        "Independent school districts": "School districts",
        "Small businesses": "Small businesses",
        "For-profit organizations other than small businesses": "For-profit organizations",
        "Individuals": "Individuals",
        "Unrestricted (i.e., open to any type of entity above), subject to any clarification in text field entitled \"Additional Information on Eligibility\"": "Unrestricted",
    }
    for k, v in cuts.items():
        if desc.startswith(k[:40]):
            return v
    return desc[:40]
