"""Startup-language → government-language translation table.

Used directly by the mock provider and as grounding context for the LLM
query planner. Keys are lowercase substrings matched against the profile text.
"""

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "health": ["health information technology", "clinical informatics", "hospital operations", "digital health"],
    "nurse": ["nursing workforce", "clinical workflow", "health workforce"],
    "hospital": ["hospital operations", "health care delivery", "patient safety"],
    "ai": ["artificial intelligence", "machine learning"],
    "machine learning": ["artificial intelligence", "machine learning"],
    "software": ["software", "information technology"],
    "manufactur": ["advanced manufacturing", "manufacturing technology"],
    "aerospace": ["aerospace", "aeronautics", "space technology"],
    "lightweight": ["lightweight materials", "advanced materials", "composites"],
    "defense": ["defense", "dual use technology"],
    "water": ["water resources", "water infrastructure", "water treatment"],
    "municipal": ["municipal utilities", "public infrastructure"],
    "sensor": ["sensors", "monitoring systems", "internet of things"],
    "climate": ["climate resilience", "environmental technology", "clean energy"],
    "cyber": ["cybersecurity", "information security", "critical infrastructure protection"],
    "threat detection": ["cybersecurity", "threat intelligence"],
    "education": ["education technology", "STEM education"],
    "youth": ["youth development", "out-of-school programs", "community programs"],
    "parent": ["family engagement", "community services"],
    "marketplace": ["small business", "technology commercialization"],
    "workforce": ["workforce development", "labor productivity"],
}

# Agency hints per domain (used for context/filters, not hard requirements)
DOMAIN_AGENCIES: dict[str, list[str]] = {
    "health": ["HHS", "NIH", "NSF", "AHRQ"],
    "nurse": ["HHS", "HRSA", "NIH"],
    "ai": ["NSF", "DOD", "DOE"],
    "manufactur": ["DOD", "NASA", "DOE", "NIST"],
    "aerospace": ["DOD", "NASA", "AFRL"],
    "water": ["EPA", "DOE", "USBR", "USDA"],
    "climate": ["DOE", "EPA", "NOAA"],
    "cyber": ["DHS", "DOD", "NSA", "NSF"],
    "education": ["ED", "NSF"],
    "youth": ["HHS", "ED", "DOL"],
    "workforce": ["DOL", "ED", "EDA"],
}

# Rough NAICS hints for USAspending recipient search
DOMAIN_NAICS: dict[str, list[str]] = {
    "software": ["513210", "541511", "541512"],
    "ai": ["541511", "541715"],
    "manufactur": ["3364", "332", "336"],
    "aerospace": ["336411", "336413", "541715"],
    "water": ["221310", "541330", "334512"],
    "cyber": ["541512", "541519", "541690"],
    "health": ["621", "513210", "541511"],
}


def translate(text: str) -> tuple[list[str], list[str], list[str]]:
    """Return (keywords, agencies, naics) for any profile text. Deterministic."""
    t = text.lower()
    kws: list[str] = []
    agencies: list[str] = []
    naics: list[str] = []
    for needle, words in DOMAIN_KEYWORDS.items():
        if needle in t:
            kws.extend(w for w in words if w not in kws)
    for needle, ags in DOMAIN_AGENCIES.items():
        if needle in t:
            agencies.extend(a for a in ags if a not in agencies)
    for needle, codes in DOMAIN_NAICS.items():
        if needle in t:
            naics.extend(c for c in codes if c not in naics)
    if not kws:
        kws = ["small business technology", "technology commercialization"]
    return kws[:8], agencies[:6], naics[:6]
