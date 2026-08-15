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


import re

# Phrases in a synopsis that mean "institutions only" even when the applicant-type
# codes are the vague "Others". The codes are structured but coarse; the prose is
# the ground truth the program officer actually wrote.
_INSTITUTION_ONLY = re.compile(
    r"\b(invites?|open to|limited to|eligible|restricted to|only)\b[^.]{0,80}?"
    r"\b(academic|research institutions?|institutions? of higher education|universities|"
    r"colleges|nonprofit organizations? only|state and local governments? only|hospitals? and universities)\b",
    re.I,
)
_SMALL_BIZ_OK = re.compile(
    r"\b(small business(es)?|for-profit|for profit|commercial (entities|organizations)|"
    r"sbir|sttr|companies|firms|industry partners?)\b",
    re.I,
)


def evaluate(applicant_types: list[dict], synopsis: str = "") -> tuple[str, list[str]]:
    """Returns (flag, short_descriptions). flag: ok | verify | likely_ineligible.
    Structured applicant-type codes first; the synopsis prose can only tighten
    the verdict (never loosen it) when it names institutions and not businesses."""
    if not applicant_types:
        flag, descs = "verify", []
    else:
        ids = {str(t.get("id")) for t in applicant_types}
        descs = [_shorten(t.get("description") or "") for t in applicant_types]
        if ids & STARTUP_OK:
            flag = "ok"
        elif ids & AMBIGUOUS:
            flag = "verify"
        else:
            flag = "likely_ineligible"

    if synopsis and flag != "likely_ineligible":
        head = synopsis[:1500]
        if _INSTITUTION_ONLY.search(head) and not _SMALL_BIZ_OK.search(head):
            flag = "likely_ineligible"
            if "Institutions (per synopsis)" not in descs:
                descs = ["Institutions (per synopsis)"] + descs
    return flag, descs


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
