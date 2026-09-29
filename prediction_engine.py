# -*- coding: utf-8 -*-
"""
Rule-based Vedic astrology prediction engine for Gujarat Vedic Kundali.

DROP-IN REPLACEMENT VERSION
Compatible with the existing:
    generate_rule_based_predictions(rows, asc, dasha_df, birth_dt=None)

Important:
This is a traditional rule-based Jyotish interpretation engine.
It is not a scientifically validated prediction system.
"""

from datetime import datetime
import pandas as pd
import swisseph as swe


# ============================================================
# SWISS EPHEMERIS SETTINGS
# ============================================================

swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANET_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}


# ============================================================
# RASHI DATA
# ============================================================

RASHIS = [
    ("Mesha", "Aries"),
    ("Vrishabha", "Taurus"),
    ("Mithuna", "Gemini"),
    ("Karka", "Cancer"),
    ("Simha", "Leo"),
    ("Kanya", "Virgo"),
    ("Tula", "Libra"),
    ("Vrishchika", "Scorpio"),
    ("Dhanu", "Sagittarius"),
    ("Makara", "Capricorn"),
    ("Kumbha", "Aquarius"),
    ("Meena", "Pisces")
]


def get_rashi(longitude):
    longitude = longitude % 360
    index = int(longitude // 30)

    return (
        index,
        RASHIS[index][0],
        RASHIS[index][1],
        longitude % 30
    )


# ============================================================
# SIGN LORDS
# ============================================================

SIGN_LORDS = {
    "Mesha": "Mars",
    "Vrishabha": "Venus",
    "Mithuna": "Mercury",
    "Karka": "Moon",
    "Simha": "Sun",
    "Kanya": "Mercury",
    "Tula": "Venus",
    "Vrishchika": "Mars",
    "Dhanu": "Jupiter",
    "Makara": "Saturn",
    "Kumbha": "Saturn",
    "Meena": "Jupiter"
}

SIGN_INDEX_BY_NAME = {
    name: i for i, (name, _) in enumerate(RASHIS)
}


# ============================================================
# PLANETARY DIGNITIES
# ============================================================

OWN_SIGNS = {
    "Sun": ["Simha"],
    "Moon": ["Karka"],
    "Mars": ["Mesha", "Vrishchika"],
    "Mercury": ["Mithuna", "Kanya"],
    "Jupiter": ["Dhanu", "Meena"],
    "Venus": ["Vrishabha", "Tula"],
    "Saturn": ["Makara", "Kumbha"],
}

EXALTATION_SIGNS = {
    "Sun": "Mesha",
    "Moon": "Vrishabha",
    "Mars": "Makara",
    "Mercury": "Kanya",
    "Jupiter": "Karka",
    "Venus": "Meena",
    "Saturn": "Tula"
}

DEBILITATION_SIGNS = {
    "Sun": "Tula",
    "Moon": "Vrishchika",
    "Mars": "Karka",
    "Mercury": "Meena",
    "Jupiter": "Makara",
    "Venus": "Kanya",
    "Saturn": "Mesha"
}


# ============================================================
# NATURAL PLANETARY NATURE
# ============================================================

NATURAL_BENEFICS = {
    "Jupiter",
    "Venus",
    "Mercury",
    "Moon"
}

NATURAL_MALEFICS = {
    "Sun",
    "Mars",
    "Saturn",
    "Rahu",
    "Ketu"
}


# ============================================================
# CORRECTED HOUSE THEMES
# ============================================================

HOUSE_THEMES = {
    1: "self, body, personality, appearance, vitality, health, character and overall life",

    2: "wealth, family, speech, food, values, accumulated resources and family lineage",

    3: "siblings, courage, communication, skills, efforts, initiative, writing and short journeys",

    4: "mother, home, property, education, vehicles, emotional happiness and domestic peace",

    5: "intelligence, creativity, education, children, romance, mantra, speculation and past-life merit",

    6: "disease, debts, enemies, competition, service, disputes, obstacles and daily routines",

    7: "marriage, spouse, partnerships, contracts, business relationships, sexuality and public dealings",

    8: "longevity, sudden events, transformation, inheritance, joint assets, secrets, occult knowledge and research",

    9: "fortune, dharma, father, guru, higher learning, spirituality, pilgrimage and long journeys",

    10: "career, profession, karma, authority, reputation, leadership, status and public life",

    11: "income, gains, fulfilment of desires, elder siblings, friendships, networks and achievements",

    12: "expenses, losses, foreign residence, isolation, sleep, confinement, spirituality and liberation"
}


# ============================================================
# HOUSE GROUPS
# ============================================================

HOUSE_GROUPS = {
    "kendra": {1, 4, 7, 10},
    "trikona": {1, 5, 9},
    "dusthana": {6, 8, 12},
    "upachaya": {3, 6, 10, 11},

    "wealth": {2, 5, 9, 11},
    "dharma": {1, 5, 9},
    "artha": {2, 6, 10},
    "kama": {3, 7, 11},
    "moksha": {4, 8, 12},

    "panaphara": {2, 5, 8, 11},
    "apoklima": {3, 6, 9, 12}
}


# ============================================================
# PLANETARY TRAITS
# ============================================================

PLANET_TRAITS = {

    "Sun": [
        "leadership",
        "authority",
        "confidence",
        "administration",
        "self-expression"
    ],

    "Moon": [
        "emotional intelligence",
        "adaptability",
        "public connection",
        "intuition",
        "sensitivity"
    ],

    "Mars": [
        "initiative",
        "courage",
        "technical drive",
        "competition",
        "action orientation"
    ],

    "Mercury": [
        "analysis",
        "communication",
        "technology",
        "commerce",
        "logical thinking"
    ],

    "Jupiter": [
        "wisdom",
        "teaching",
        "research",
        "guidance",
        "higher learning"
    ],

    "Venus": [
        "creativity",
        "relationships",
        "design",
        "diplomacy",
        "aesthetic sense"
    ],

    "Saturn": [
        "discipline",
        "persistence",
        "structure",
        "responsibility",
        "long-term work"
    ],

    "Rahu": [
        "ambition",
        "innovation",
        "unconventional thinking",
        "foreign links",
        "technology"
    ],

    "Ketu": [
        "research",
        "detachment",
        "specialization",
        "introspection",
        "spiritual inquiry"
    ]
}


# ============================================================
# CAREER DOMAINS
# ============================================================

CAREER_DOMAINS = {

    "Sun": [
        "administration",
        "government/public institutions",
        "leadership",
        "management"
    ],

    "Moon": [
        "public relations",
        "hospitality",
        "healthcare support",
        "travel/service"
    ],

    "Mars": [
        "engineering",
        "technology",
        "defence",
        "operations",
        "sports"
    ],

    "Mercury": [
        "IT/software",
        "data analysis",
        "communication",
        "commerce",
        "business"
    ],

    "Jupiter": [
        "teaching",
        "research",
        "law",
        "finance",
        "consulting"
    ],

    "Venus": [
        "design",
        "media",
        "arts",
        "fashion",
        "public-facing creative work"
    ],

    "Saturn": [
        "engineering",
        "infrastructure",
        "manufacturing",
        "administration",
        "large organizations"
    ],

    "Rahu": [
        "technology",
        "digital media",
        "foreign organizations",
        "emerging industries"
    ],

    "Ketu": [
        "research",
        "analytics",
        "specialized technical work",
        "spiritual/academic study"
    ]
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def _clamp(value, low=0, high=100):
    return max(low, min(high, float(value)))


def _add_reason(bucket, text, weight=0):
    bucket.append({
        "text": text,
        "weight": weight
    })


def _planet_map(rows):
    return {
        r["Planet"]: r
        for r in rows
        if r.get("Planet")
    }


def _house_of(planet_map, planet):
    return planet_map.get(planet, {}).get("House")


def _sign_of(planet_map, planet):
    return planet_map.get(planet, {}).get("Rashi")


def _lord_of_sign(sign):
    return SIGN_LORDS.get(sign)


# ============================================================
# HOUSE LORDS
# ============================================================

def _house_lords(asc_index):
    result = {}

    for house in range(1, 13):

        sign_index = (asc_index + house - 1) % 12
        sign = RASHIS[sign_index][0]

        result[house] = SIGN_LORDS[sign]

    return result


def _planet_house_from_lord(planet_map, lord):
    return _house_of(planet_map, lord)


def _lord_house_for_house(
    house_lords,
    planet_map,
    house
):
    lord = house_lords[house]

    return (
        lord,
        _planet_house_from_lord(
            planet_map,
            lord
        )
    )


# ============================================================
# HOUSE RELATION
# ============================================================

def _house_relation(h1, h2):

    if h1 is None or h2 is None:
        return None

    return ((h2 - h1) % 12) + 1


# ============================================================
# CORRECTED PARASHARI PLANETARY ASPECTS
# ============================================================

def _planet_aspects(planet, source_house):
    """
    Commonly used Parashari Graha Drishti.

    Every planet:
        7th aspect

    Mars:
        4th, 7th, 8th

    Jupiter:
        5th, 7th, 9th

    Saturn:
        3rd, 7th, 10th

    Rahu/Ketu:
        Node aspects vary among Jyotish traditions.
        This implementation uses 5th, 7th and 9th as
        the existing application's chosen convention.
    """

    if source_house is None:
        return set()

    def target(offset):
        return ((source_house - 1 + offset) % 12) + 1

    # Universal 7th aspect.
    aspects = {
        target(6)
    }

    if planet == "Mars":

        aspects |= {
            target(3),   # 4th
            target(7)    # 8th
        }

    elif planet == "Jupiter":

        aspects |= {
            target(4),   # 5th
            target(8)    # 9th
        }

    elif planet == "Saturn":

        aspects |= {
            target(2),   # 3rd
            target(9)    # 10th
        }

    elif planet in {"Rahu", "Ketu"}:

        aspects |= {
            target(4),   # 5th
            target(8)    # 9th
        }

    return aspects


# ============================================================
# PLANETS IN HOUSE
# ============================================================

def _planets_in_house(planet_map, house):

    return [
        p
        for p, row in planet_map.items()
        if row.get("House") == house
    ]


# ============================================================
# PLANETS ASPECTING HOUSE
# ============================================================

def _aspects_house(planet_map, house):

    result = []

    for planet, row in planet_map.items():

        if house in _planet_aspects(
            planet,
            row.get("House")
        ):
            result.append(planet)

    return result


# ============================================================
# PLANET CONNECTION
# ============================================================

def _is_connected(planet_map, p1, p2):

    h1 = _house_of(planet_map, p1)
    h2 = _house_of(planet_map, p2)

    if h1 is None or h2 is None:
        return False

    # Conjunction.
    if h1 == h2:
        return True

    # Mutual 7th-house relationship.
    if _house_relation(h1, h2) == 7:
        return True

    # Graha Drishti connection.
    if h2 in _planet_aspects(p1, h1):
        return True

    if h1 in _planet_aspects(p2, h2):
        return True

    return False


# ============================================================
# DIGNITY
# ============================================================

def _dignity(planet, sign):

    if not sign:
        return "unknown", 0

    if (
        planet in EXALTATION_SIGNS
        and sign == EXALTATION_SIGNS[planet]
    ):
        return "exalted", 25

    if (
        planet in DEBILITATION_SIGNS
        and sign == DEBILITATION_SIGNS[planet]
    ):
        return "debilitated", -25

    if sign in OWN_SIGNS.get(planet, []):
        return "own sign", 18

    if planet in {"Rahu", "Ketu"}:
        return "node", 0

    return "neutral", 0


# ============================================================
# FUNCTIONAL NATURE
# ============================================================

def _functional_nature(planet, house_lords):

    owned = [
        h
        for h, lord in house_lords.items()
        if lord == planet
    ]

    if not owned:
        return None

    # Lagna lord is fundamentally supportive.
    if 1 in owned:
        return True

    has_trikona = bool(
        set(owned) & {5, 9}
    )

    has_dusthana = bool(
        set(owned) & {6, 8, 12}
    )

    # Yogakaraka / strong Trikona influence.
    if has_trikona and not has_dusthana:
        return True

    # Dusthana ownership without Trikona ownership.
    if has_dusthana and not has_trikona:
        return False

    # Strong Kendra-only ownership.
    if set(owned) & {4, 7, 10}:
        return None

    return None


# ============================================================
# YOGAKARAKA DETECTION
# ============================================================

def _yogakaraka_planets(house_lords):

    result = []

    for planet in set(house_lords.values()):

        owned = {
            h
            for h, lord in house_lords.items()
            if lord == planet
        }

        if (
            owned & {4, 7, 10}
            and owned & {5, 9}
        ):
            result.append(planet)

    return sorted(result)


# ============================================================
# PLANET STRENGTH
# ============================================================

def _planet_strength(
    planet,
    row,
    functional_benefic=None
):

    score = 50.0
    reasons = []

    sign = row.get("Rashi")
    house = row.get("House")

    dignity, delta = _dignity(
        planet,
        sign
    )

    score += delta

    if delta:
        reasons.append(
            f"{planet} is {dignity} in {sign}"
        )

    if house in HOUSE_GROUPS["kendra"]:
        score += 5

    if house in HOUSE_GROUPS["trikona"]:
        score += 7

    if house in HOUSE_GROUPS["dusthana"]:
        score -= 6

    if house in HOUSE_GROUPS["upachaya"]:
        score += 3

    if (
        row.get("Retrograde")
        and planet in {
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn"
        }
    ):
        score += 2

        reasons.append(
            f"{planet} is retrograde"
        )

    if row.get("Combust"):
        score -= 4

        reasons.append(
            f"{planet} is combust"
        )

    if functional_benefic is True:
        score += 5

    elif functional_benefic is False:
        score -= 4

    return _clamp(score), reasons


# ============================================================
# COMBUSTION
# ============================================================

def _combustion_threshold(planet):

    return {
        "Moon": 12,
        "Mars": 17,
        "Mercury": 14,
        "Jupiter": 11,
        "Venus": 10,
        "Saturn": 15
    }.get(planet, 0)


def _angular_distance(a, b):

    d = abs((a - b) % 360.0)

    return min(
        d,
        360.0 - d
    )


def _combust_status(planet_map, planet):

    if planet not in planet_map:
        return False

    if "Sun" not in planet_map:
        return False

    threshold = _combustion_threshold(planet)

    if not threshold:
        return False

    return (
        _angular_distance(
            float(planet_map[planet]["Longitude"]),
            float(planet_map["Sun"]["Longitude"])
        )
        <= threshold
    )


# ============================================================
# HOUSE SCORE
# ============================================================

def _house_score(
    planet_map,
    house,
    house_lords,
    category
):

    score = 50.0
    reasons = []

    occupants = _planets_in_house(
        planet_map,
        house
    )

    lord = house_lords[house]

    lord_house = _house_of(
        planet_map,
        lord
    )

    # House lord placement.
    if lord_house in {
        1, 4, 5, 7, 9, 10, 11
    }:

        score += 10

        reasons.append(
            f"Lord of house {house} occupies a supportive house ({lord_house})"
        )

    elif lord_house in {
        6, 8, 12
    }:

        score -= 8

        reasons.append(
            f"Lord of house {house} occupies a dusthana ({lord_house})"
        )

    # Occupying planets.
    for p in occupants:

        if p in NATURAL_BENEFICS:

            score += 6

            reasons.append(
                f"{p} occupies house {house}"
            )

        elif p in NATURAL_MALEFICS:

            score -= 4

            reasons.append(
                f"{p} influences house {house}"
            )

    # Aspecting planets.
    for p in _aspects_house(
        planet_map,
        house
    ):

        if p in NATURAL_BENEFICS:

            score += 5

            reasons.append(
                f"{p} aspects house {house}"
            )

        elif p in NATURAL_MALEFICS:

            score -= 3

            reasons.append(
                f"{p} aspects house {house}"
            )

    # Career.
    if category == "career" and house == 10:

        if any(
            p in occupants
            for p in [
                "Sun",
                "Saturn",
                "Mercury",
                "Jupiter"
            ]
        ):
            score += 8

    # Wealth.
    if category == "wealth" and house == 11:

        if any(
            p in occupants
            for p in [
                "Jupiter",
                "Venus",
                "Mercury"
            ]
        ):
            score += 8

    return _clamp(score), reasons


# ============================================================
# BEST PLANETS FOR AREA
# ============================================================

def _best_planet_for_area(
    planet_map,
    area_houses
):

    candidates = []

    for planet, row in planet_map.items():

        if row.get("House") in area_houses:

            candidates.append(
                (
                    planet,
                    row.get("House")
                )
            )

    return candidates


# ============================================================
# PERSONALITY ANALYSIS
# ============================================================

def _trait_analysis(
    planet_map,
    asc,
    house_lords
):

    score = 50.0
    reasons = []
    traits = []

    lagna_lord = house_lords[1]

    lagna_lord_house = _house_of(
        planet_map,
        lagna_lord
    )

    if lagna_lord_house in {
        1, 4, 5, 9, 10, 11
    }:

        score += 15

        reasons.append(
            f"Lagna lord {lagna_lord} is in supportive house {lagna_lord_house}"
        )

    elif lagna_lord_house in {
        6, 8, 12
    }:

        score -= 7

        reasons.append(
            f"Lagna lord {lagna_lord} is in house {lagna_lord_house}"
        )

    # Planets in Lagna.
    for p in _planets_in_house(
        planet_map,
        1
    ):

        traits.extend(
            PLANET_TRAITS.get(
                p,
                []
            )
        )

        if p in NATURAL_BENEFICS:
            score += 8
        else:
            score += 3

        reasons.append(
            f"{p} occupies the Ascendant"
        )

    # Planets aspecting Lagna.
    for p in _aspects_house(
        planet_map,
        1
    ):

        traits.extend(
            PLANET_TRAITS.get(
                p,
                []
            )
        )

        if p in NATURAL_BENEFICS:
            score += 4
        else:
            score += 2

        reasons.append(
            f"{p} aspects the Ascendant"
        )

    # Moon.
    moon_house = _house_of(
        planet_map,
        "Moon"
    )

    if moon_house in {
        1, 4, 5, 9, 10, 11
    }:

        score += 5

        reasons.append(
            f"Moon occupies supportive house {moon_house}"
        )

    elif moon_house in {
        6, 8, 12
    }:

        score -= 3

    # Sun.
    sun_house = _house_of(
        planet_map,
        "Sun"
    )

    if sun_house in {
        1, 5, 9, 10
    }:

        traits.append(
            "leadership orientation"
        )

        score += 4

    traits = list(
        dict.fromkeys(traits)
    )[:10]

    return {
        "score": _clamp(score),
        "traits": traits,
        "reasons": reasons[:10]
    }


# ============================================================
# INTELLIGENCE
# ============================================================

def _intelligence_analysis(
    planet_map,
    house_lords
):

    score = 50.0
    reasons = []

    for house in [5, 9]:

        hs, rs = _house_score(
            planet_map,
            house,
            house_lords,
            "education"
        )

        score += (
            hs - 50
        ) * 0.45

        reasons.extend(
            rs[:3]
        )

    for p in [
        "Mercury",
        "Jupiter",
        "Moon"
    ]:

        h = _house_of(
            planet_map,
            p
        )

        if h in {
            1, 4, 5, 9, 10, 11
        }:

            score += 5

            reasons.append(
                f"{p} supports learning through house {h}"
            )

    return (
        _clamp(score),
        reasons[:10]
    )


# ============================================================
# EDUCATION
# ============================================================

def _education_analysis(
    planet_map,
    house_lords
):

    score = 50.0
    reasons = []

    for house in [4, 5, 9]:

        hs, rs = _house_score(
            planet_map,
            house,
            house_lords,
            "education"
        )

        score += (
            hs - 50
        ) * 0.55

        reasons.extend(
            rs[:3]
        )

    for p in [
        "Mercury",
        "Jupiter"
    ]:

        if _house_of(
            planet_map,
            p
        ) in {
            4, 5, 9, 10, 11
        }:

            score += 7

            reasons.append(
                f"{p} is connected with education"
            )

    return (
        _clamp(score),
        reasons[:10]
    )


# ============================================================
# CAREER
# ============================================================

def _career_analysis(
    planet_map,
    house_lords,
    d9_rows=None
):

    score = 50.0
    reasons = []

    domain_scores = {
        d: 0.0
        for p in CAREER_DOMAINS
        for d in CAREER_DOMAINS[p]
    }

    for house in [6, 10, 11]:

        hs, rs = _house_score(
            planet_map,
            house,
            house_lords,
            "career"
        )

        score += (
            hs - 50
        ) * 0.75

        reasons.extend(
            rs[:4]
        )

    # Planets connected with career houses.
    for p, row in planet_map.items():

        h = row.get("House")

        if h in {
            2, 6, 10, 11
        }:

            for domain in CAREER_DOMAINS.get(
                p,
                []
            ):

                domain_scores[domain] += 2.0

    # 10th lord.
    tenth_lord = house_lords[10]

    if tenth_lord in CAREER_DOMAINS:

        for domain in CAREER_DOMAINS[tenth_lord]:

            domain_scores[domain] += 8.0

        reasons.append(
            f"10th lord is {tenth_lord}, highlighting its career themes"
        )

    # Planets in 10th.
    for p in _planets_in_house(
        planet_map,
        10
    ):

        for domain in CAREER_DOMAINS.get(
            p,
            []
        ):

            domain_scores[domain] += 6.0

        reasons.append(
            f"{p} occupies the 10th house"
        )

    # D9 secondary confirmation.
    if d9_rows:

        d9_map = _planet_map(
            d9_rows
        )

        for p in [
            "Sun",
            "Mercury",
            "Jupiter",
            "Saturn"
        ]:

            if p not in d9_map:
                continue

            d9_sign = d9_map[p].get(
                "Rashi"
            )

            if not d9_sign:
                continue

            dignity, delta = _dignity(
                p,
                d9_sign
            )

            if delta > 0:

                score += 1

                reasons.append(
                    f"D9 gives additional dignity support to {p}"
                )

    top_domains = [
        x[0]
        for x in sorted(
            domain_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:6]
    ]

    return (
        _clamp(score),
        reasons[:12],
        top_domains
    )


# ============================================================
# WEALTH
# ============================================================

def _wealth_analysis(
    planet_map,
    house_lords
):

    score = 50.0
    reasons = []

    for house in [
        2,
        5,
        9,
        11
    ]:

        hs, rs = _house_score(
            planet_map,
            house,
            house_lords,
            "wealth"
        )

        score += (
            hs - 50
        ) * 0.60

        reasons.extend(
            rs[:3]
        )

    wealth_pairs = [
        (2, 11),
        (5, 11),
        (9, 11),
        (2, 9),
        (2, 5)
    ]

    for h1, h2 in wealth_pairs:

        l1 = house_lords[h1]
        l2 = house_lords[h2]

        if _is_connected(
            planet_map,
            l1,
            l2
        ):

            score += 10

            reasons.append(
                f"Connection between lords of houses {h1} and {h2}"
            )

    return (
        _clamp(score),
        reasons[:12]
    )


# ============================================================
# MARRIAGE / RELATIONSHIPS
# ============================================================

def _marriage_analysis(
    planet_map,
    house_lords,
    d9_rows=None
):

    score = 50.0
    reasons = []

    for house in [
        2,
        7,
        8,
        11
    ]:

        hs, rs = _house_score(
            planet_map,
            house,
            house_lords,
            "marriage"
        )

        score += (
            hs - 50
        ) * 0.55

        reasons.extend(
            rs[:2]
        )

    venus_h = _house_of(
        planet_map,
        "Venus"
    )

    jup_h = _house_of(
        planet_map,
        "Jupiter"
    )

    if venus_h in {
        1, 5, 7, 9, 11
    }:

        score += 8

        reasons.append(
            "Venus is in a traditionally supportive relationship house"
        )

    if jup_h in {
        1, 5, 7, 9, 11
    }:

        score += 6

        reasons.append(
            "Jupiter supports partnership through a favorable house"
        )

    for p in _planets_in_house(
        planet_map,
        7
    ):

        if p == "Saturn":

            score -= 5

            reasons.append(
                "Saturn in the 7th can emphasize responsibility or delay"
            )

        elif p == "Jupiter":

            score += 8

            reasons.append(
                "Jupiter in the 7th supports partnership themes"
            )

        elif p == "Venus":

            score += 8

            reasons.append(
                "Venus in the 7th strongly emphasizes relationship themes"
            )

    # D9 relationship confirmation.
    if d9_rows:

        d9_map = _planet_map(
            d9_rows
        )

        d9_7 = _planets_in_house(
            d9_map,
            7
        )

        if "Venus" in d9_7:

            score += 5

            reasons.append(
                "D9 Venus in the 7th provides relationship support"
            )

        if "Jupiter" in d9_7:

            score += 5

            reasons.append(
                "D9 Jupiter in the 7th provides relationship support"
            )

        if "Saturn" in d9_7:

            score -= 3

            reasons.append(
                "D9 Saturn emphasizes maturity and responsibility in partnership"
            )

    return (
        _clamp(score),
        reasons[:12]
    )


# ============================================================
# FOREIGN / RELOCATION
# ============================================================

def _foreign_analysis(
    planet_map,
    house_lords
):

    score = 40.0
    reasons = []

    for h in [
        3,
        9,
        12
    ]:

        hs, rs = _house_score(
            planet_map,
            h,
            house_lords,
            "foreign"
        )

        score += (
            hs - 50
        ) * 0.45

        reasons.extend(
            rs[:2]
        )

    if _is_connected(
        planet_map,
        house_lords[9],
        house_lords[12]
    ):

        score += 15

        reasons.append(
            "9th and 12th lords are connected"
        )

    if _is_connected(
        planet_map,
        house_lords[4],
        house_lords[12]
    ):

        score += 10

        reasons.append(
            "4th and 12th lords are connected, suggesting relocation or foreign themes"
        )

    for p in [
        "Rahu",
        "Saturn"
    ]:

        if _house_of(
            planet_map,
            p
        ) in {
            9,
            12
        }:

            score += 8

            reasons.append(
                f"{p} occupies a foreign/travel-related house"
            )

    return (
        _clamp(score),
        reasons[:12]
    )


# ============================================================
# VITALITY / ROUTINE
# ============================================================

def _health_routine_analysis(
    planet_map,
    house_lords
):

    score = 55.0
    reasons = []

    h1, r1 = _house_score(
        planet_map,
        1,
        house_lords,
        "health"
    )

    h6, r6 = _house_score(
        planet_map,
        6,
        house_lords,
        "health"
    )

    score += (
        h1 - 50
    ) * 0.35

    score += (
        h6 - 50
    ) * 0.25

    reasons.extend(
        r1[:4]
    )

    reasons.extend(
        r6[:4]
    )

    return (
        _clamp(score),
        reasons[:10]
    )


# ============================================================
# YOGA DETECTION
# ============================================================

def _yoga_detection(
    planet_map,
    house_lords
):

    yogas = []

    # --------------------------------------------------------
    # Raja Yoga
    # --------------------------------------------------------

    kendra_lords = [
        house_lords[h]
        for h in [1, 4, 7, 10]
    ]

    trikona_lords = [
        house_lords[h]
        for h in [1, 5, 9]
    ]

    raja_pairs = []

    for kp in set(kendra_lords):

        for tp in set(trikona_lords):

            if kp == tp:
                continue

            if _is_connected(
                planet_map,
                kp,
                tp
            ):

                raja_pairs.append(
                    (kp, tp)
                )

    if raja_pairs:

        yogas.append({
            "name": "Raja Yoga connection",
            "strength": "Moderate",
            "reason": (
                "Kendra and Trikona lords have a conjunction, "
                "mutual 7th relationship or graha-drishṭi connection."
            )
        })

    # --------------------------------------------------------
    # Dharma-Karmadhipati
    # --------------------------------------------------------

    if _is_connected(
        planet_map,
        house_lords[9],
        house_lords[10]
    ):

        yogas.append({
            "name": "Dharma-Karmadhipati Yoga",
            "strength": "Strong",
            "reason": (
                "The 9th and 10th lords are connected."
            )
        })

    # --------------------------------------------------------
    # Dhana Yoga
    # --------------------------------------------------------

    wealth_pairs = [
        (2, 11),
        (5, 11),
        (9, 11),
        (2, 5),
        (2, 9)
    ]

    wealth_hits = []

    for a, b in wealth_pairs:

        if _is_connected(
            planet_map,
            house_lords[a],
            house_lords[b]
        ):

            wealth_hits.append(
                (a, b)
            )

    if wealth_hits:

        yogas.append({
            "name": "Dhana Yoga connection",
            "strength": "Moderate",
            "reason": (
                "Wealth-related house lords have supportive connections."
            )
        })

    # --------------------------------------------------------
    # Gaja Kesari
    # --------------------------------------------------------

    moon_h = _house_of(
        planet_map,
        "Moon"
    )

    jup_h = _house_of(
        planet_map,
        "Jupiter"
    )

    if (
        moon_h is not None
        and jup_h is not None
        and _house_relation(
            moon_h,
            jup_h
        ) in {1, 4, 7, 10}
    ):

        yogas.append({
            "name": "Gaja Kesari Yoga",
            "strength": "Context-dependent",
            "reason": (
                "Jupiter is in a Kendra from the Moon. "
                "Actual strength depends on dignity, affliction, "
                "house placement and other chart factors."
            )
        })

    # --------------------------------------------------------
    # Budha-Aditya
    # --------------------------------------------------------

    sun_sign = _sign_of(
        planet_map,
        "Sun"
    )

    mercury_sign = _sign_of(
        planet_map,
        "Mercury"
    )

    if (
        sun_sign
        and mercury_sign
        and sun_sign == mercury_sign
    ):

        yogas.append({
            "name": "Budha-Aditya Yoga",
            "strength": "Context-dependent",
            "reason": (
                "Sun and Mercury occupy the same sign. "
                "Final strength depends on dignity, combustion "
                "and other planetary influences."
            )
        })

    # --------------------------------------------------------
    # Vipareeta Raja Yoga
    # --------------------------------------------------------

    vip_hits = []

    for source in [
        6,
        8,
        12
    ]:

        lord = house_lords[source]

        lord_h = _house_of(
            planet_map,
            lord
        )

        if lord_h in {
            6,
            8,
            12
        }:

            vip_hits.append(
                (
                    source,
                    lord,
                    lord_h
                )
            )

    if vip_hits:

        yogas.append({
            "name": "Vipareeta Raja Yoga indication",
            "strength": "Context-dependent",
            "reason": (
                "A dusthana lord is placed in another dusthana. "
                "The exact yoga requires examination of the "
                "6th, 8th and 12th lords and their associations."
            )
        })

    # --------------------------------------------------------
    # Neecha
    # --------------------------------------------------------

    debilitated = []

    for p, r in planet_map.items():

        if (
            p in DEBILITATION_SIGNS
            and r.get("Rashi")
            == DEBILITATION_SIGNS[p]
        ):

            debilitated.append(
                p
            )

    if debilitated:

        yogas.append({
            "name": "Neecha placement",
            "strength": "Requires cancellation analysis",
            "reason": (
                ", ".join(debilitated)
                + " is in debilitation. "
                  "Neecha Bhanga should be checked before making "
                  "a final judgment."
            )
        })

    return yogas


# ============================================================
# MANGLIK ANALYSIS
# ============================================================

def _manglik_analysis(planet_map):

    mars_house = _house_of(
        planet_map,
        "Mars"
    )

    moon_house = _house_of(
        planet_map,
        "Moon"
    )

    venus_house = _house_of(
        planet_map,
        "Venus"
    )

    def house_from(
        reference_house,
        target_house
    ):

        if (
            reference_house is None
            or target_house is None
        ):
            return None

        return (
            (target_house - reference_house) % 12
        ) + 1

    mars_from_lagna = mars_house

    mars_from_moon = house_from(
        moon_house,
        mars_house
    )

    mars_from_venus = house_from(
        venus_house,
        mars_house
    )

    manglik_houses = {
        1,
        4,
        7,
        8,
        12
    }

    lagna_manglik = (
        mars_from_lagna
        in manglik_houses
    )

    moon_manglik = (
        mars_from_moon
        in manglik_houses
    )

    venus_manglik = (
        mars_from_venus
        in manglik_houses
    )

    present = (
        lagna_manglik
        or moon_manglik
        or venus_manglik
    )

    reasons = []

    if lagna_manglik:

        reasons.append(
            "Mars is in a Manglik house from Lagna."
        )

    if moon_manglik:

        reasons.append(
            "Mars is in a Manglik house from Moon."
        )

    if venus_manglik:

        reasons.append(
            "Mars is in a Manglik house from Venus."
        )

    if not reasons:

        reason = (
            "No Manglik indication was detected from "
            "Lagna, Moon or Venus under the implemented rule."
        )

    else:

        reason = " ".join(
            reasons
        )

    return (
        present,
        mars_house,
        reason
    )


# ============================================================
# SADE SATI
# ============================================================

def _sade_sati_status(
    natal_moon_sign_index,
    transit_saturn_sign_index
):

    previous_sign = (
        natal_moon_sign_index - 1
    ) % 12

    current_sign = natal_moon_sign_index

    next_sign = (
        natal_moon_sign_index + 1
    ) % 12

    if transit_saturn_sign_index == previous_sign:
        return "Phase 1"

    if transit_saturn_sign_index == current_sign:
        return "Phase 2"

    if transit_saturn_sign_index == next_sign:
        return "Phase 3"

    return None


# ============================================================
# DASHA DATE CONVERSION
# ============================================================

def _dasha_rows_to_datetimes(dasha_df):

    rows = []

    if (
        dasha_df is None
        or len(dasha_df) == 0
    ):
        return rows

    for _, r in dasha_df.iterrows():

        try:

            start = datetime.strptime(
                str(r["Start"]),
                "%d-%m-%Y"
            )

            end = datetime.strptime(
                str(r["End"]),
                "%d-%m-%Y"
            )

            rows.append({
                "Mahadasha": r["Mahadasha"],
                "Antardasha": r["Antardasha"],
                "Start": start,
                "End": end
            })

        except Exception:

            continue

    return rows


# ============================================================
# ACTIVE DASHA
# ============================================================

def _active_dasha(
    dasha_df,
    when=None
):

    """
    Return Dasha active on supplied date.

    Dasha table uses day-level dates.
    Therefore calendar-date comparison is used.
    """

    when = when or datetime.now()

    rows = _dasha_rows_to_datetimes(
        dasha_df
    )

    if not rows:
        return None

    if isinstance(
        when,
        datetime
    ):

        when_date = when.date()

    else:

        try:

            when_date = (
                when.to_pydatetime()
                .date()
            )

        except AttributeError:

            when_date = when

    for r in rows:

        if (
            r["Start"].date()
            <= when_date
            <= r["End"].date()
        ):

            return r

    # Outside generated range:
    if when_date < rows[0]["Start"].date():

        return rows[0]

    return rows[-1]


# ============================================================
# DASHA MODIFIER
# ============================================================

def _dasha_area_modifier(
    md,
    ad,
    planet_map,
    house_lords
):

    if not md or not ad:

        return 0, []

    score = 0
    reasons = []

    for label, p in [
        ("Mahadasha", md),
        ("Antardasha", ad)
    ]:

        h = _house_of(
            planet_map,
            p
        )

        if h in {
            1,
            5,
            9,
            10,
            11
        }:

            score += (
                8
                if label == "Mahadasha"
                else 5
            )

            reasons.append(
                f"{label} planet {p} activates supportive house {h}"
            )

        elif h in {
            6,
            8,
            12
        }:

            score -= (
                4
                if label == "Mahadasha"
                else 2
            )

            reasons.append(
                f"{label} planet {p} activates house {h}"
            )

    return (
        score,
        reasons
    )


# ============================================================
# TRANSIT CALCULATION
# ============================================================

def _transit_planet_row(
    jd_ut,
    planet_name
):

    planet_id = PLANETS.get(
        planet_name
    )

    if planet_id is None:
        return None

    values, _ = swe.calc_ut(
        jd_ut,
        planet_id,
        PLANET_FLAGS
    )

    lon = values[0] % 360

    (
        rashi_index,
        rashi,
        english,
        degree
    ) = get_rashi(lon)

    return {
        "Planet": planet_name,
        "Longitude": lon,
        "Rashi_Index": rashi_index,
        "Rashi": rashi,
        "Sign": english,
        "Degree_in_Rashi": degree
    }


# ============================================================
# JULIAN DATE
# ============================================================

def _jd_for_date(dt):

    return swe.julday(
        dt.year,
        dt.month,
        dt.day,
        dt.hour + dt.minute / 60.0,
        swe.GREG_CAL
    )


# ============================================================
# ANNUAL TRANSIT PROFILE
# ============================================================

def _annual_transit_profile(
    natal_asc_index,
    natal_moon_index,
    year
):

    # Stable annual reference.
    dt = datetime(
        year,
        7,
        1,
        12,
        0
    )

    jd = _jd_for_date(dt)

    j = _transit_planet_row(
        jd,
        "Jupiter"
    )

    s = _transit_planet_row(
        jd,
        "Saturn"
    )

    result = {
        "year": year
    }

    for label, row in [
        ("Jupiter", j),
        ("Saturn", s)
    ]:

        if row:

            sign_index = row[
                "Rashi_Index"
            ]

            result[label] = {

                "sign_index": sign_index,

                "house_from_lagna":
                    ((sign_index - natal_asc_index) % 12) + 1,

                "house_from_moon":
                    ((sign_index - natal_moon_index) % 12) + 1
            }

    result["sade_sati"] = (
        _sade_sati_status(
            natal_moon_index,
            s["Rashi_Index"]
        )
        if s
        else None
    )

    return result


# ============================================================
# ANNUAL PREDICTION
# ============================================================

def _annual_prediction(
    year,
    base_scores,
    transit_profile,
    dasha_df,
    planet_map,
    house_lords
):

    scores = dict(
        base_scores
    )

    reasons = []

    jt = transit_profile.get(
        "Jupiter",
        {}
    )

    st = transit_profile.get(
        "Saturn",
        {}
    )

    jh = jt.get(
        "house_from_lagna"
    )

    sh = st.get(
        "house_from_lagna"
    )

    # Jupiter.
    if jh in {
        1,
        2,
        5,
        7,
        9,
        10,
        11
    }:

        scores["career"] += 5
        scores["education"] += 4
        scores["wealth"] += 4

        reasons.append(
            f"Jupiter transit is supportive from Lagna (house {jh})"
        )

    elif jh in {
        6,
        8,
        12
    }:

        scores["career"] -= 3

        reasons.append(
            f"Jupiter transit is more reflective from Lagna (house {jh})"
        )

    # Saturn.
    if sh in {
        3,
        6,
        10,
        11
    }:

        scores["career"] += 5
        scores["discipline"] += 4

        reasons.append(
            f"Saturn transit emphasizes effort/results through house {sh}"
        )

    elif sh in {
        8,
        12
    }:

        scores["career"] -= 3
        scores["discipline"] -= 2

        reasons.append(
            f"Saturn transit emphasizes restructuring through house {sh}"
        )

    # Sade Sati.
    if transit_profile.get(
        "sade_sati"
    ):

        scores["discipline"] -= 4

        reasons.append(
            "Saturn is in Sade Sati "
            + transit_profile["sade_sati"]
            + " relative to natal Moon"
        )

    # Dasha at 1 July.
    active = _active_dasha(
        dasha_df,
        datetime(
            year,
            7,
            1
        )
    )

    if active:

        mod, rs = _dasha_area_modifier(
            active["Mahadasha"],
            active["Antardasha"],
            planet_map,
            house_lords
        )

        scores["career"] += (
            mod * 0.45
        )

        scores["wealth"] += (
            mod * 0.35
        )

        scores["education"] += (
            mod * 0.25
        )

        scores["relationships"] += (
            mod * 0.25
        )

        reasons.extend(
            rs
        )

    for k in scores:

        scores[k] = round(
            _clamp(
                scores[k]
            ),
            1
        )

    return (
        scores,
        reasons[:6],
        active
    )


# ============================================================
# STATUS
# ============================================================

def _status(score):

    if score >= 80:
        return "Highly supportive"

    if score >= 65:
        return "Favorable"

    if score >= 50:
        return "Mixed / manageable"

    if score >= 35:
        return "Needs caution"

    return "Challenging"


# ============================================================
# PREDICTION DATAFRAME
# ============================================================

def _make_prediction_dataframe(
    pred
):

    rows = []

    labels = {

        "personality":
            "Personality",

        "intelligence":
            "Intelligence / Learning",

        "education":
            "Education",

        "career":
            "Career",

        "wealth":
            "Wealth / Income",

        "relationships":
            "Marriage / Relationships",

        "foreign":
            "Foreign / Relocation",

        "vitality":
            "Vitality / Routine"
    }

    for key, label in labels.items():

        item = pred[
            "areas"
        ].get(
            key,
            {}
        )

        rows.append({

            "Area": label,

            "Score": round(
                item.get(
                    "score",
                    0
                ),
                1
            ),

            "Assessment":
                _status(
                    item.get(
                        "score",
                        0
                    )
                )
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# PREDICTION REPORT
# ============================================================

def _prediction_report(
    pred,
    name=""
):

    areas = pred["areas"]

    lines = []

    lines.append(
        "\n---\n"
    )

    lines.append(
        "# 🔮 Rule-Based Vedic Astrology Interpretation"
    )

    lines.append("")

    lines.append(
        "> **Note:** This is a traditional Jyotish interpretation generated from explicit rules and planetary relationships. It is not a scientifically validated prediction system and should not be used as a substitute for professional medical, legal or financial advice."
    )

    lines.append("")

    # Overall.
    lines.append(
        "## 🌟 Overall Interpretation"
    )

    lines.append(
        f"**Overall Rule-Based Support Score:** "
        f"{pred['overall_score']:.1f}/100 — "
        f"**{_status(pred['overall_score'])}**"
    )

    lines.append("")

    # Areas.
    for key, label in [

        (
            "personality",
            "Personality & Nature"
        ),

        (
            "intelligence",
            "Intelligence & Learning"
        ),

        (
            "education",
            "Education"
        ),

        (
            "career",
            "Career & Profession"
        ),

        (
            "wealth",
            "Wealth & Income"
        ),

        (
            "relationships",
            "Marriage & Relationships"
        ),

        (
            "foreign",
            "Foreign Connection / Relocation"
        ),

        (
            "vitality",
            "Vitality & Lifestyle Themes"
        )
    ]:

        item = areas[key]

        lines.append(
            f"### {label} — "
            f"{item['score']:.1f}/100 "
            f"({_status(item['score'])})"
        )

        if item.get(
            "traits"
        ):

            lines.append(
                "**Traits:** "
                + ", ".join(
                    item["traits"]
                )
            )

        if item.get(
            "domains"
        ):

            lines.append(
                "**Career domains:** "
                + ", ".join(
                    item["domains"]
                )
            )

        if item.get(
            "reasons"
        ):

            lines.append(
                "**Rules supporting this assessment:**"
            )

            for reason in item[
                "reasons"
            ][:6]:

                text = (
                    reason["text"]
                    if isinstance(
                        reason,
                        dict
                    )
                    else str(reason)
                )

                lines.append(
                    f"- {text}"
                )

        lines.append("")

    # Yogas.
    lines.append(
        "## 🧿 Important Yogas / Conditions"
    )

    if pred["yogas"]:

        for y in pred["yogas"]:

            lines.append(
                f"- **{y['name']}** — "
                f"{y['strength']}: "
                f"{y['reason']}"
            )

    else:

        lines.append(
            "No major rule-defined yoga was detected by the current engine."
        )

    lines.append("")

    # Yogakaraka.
    if pred.get(
        "yogakaraka"
    ):

        lines.append(
            "### ⭐ Yogakaraka Planet(s)"
        )

        lines.append(
            ", ".join(
                pred["yogakaraka"]
            )
        )

        lines.append("")

    # Manglik.
    lines.append(
        "## 🔥 Manglik Check"
    )

    m = pred["manglik"]

    lines.append(
        f"**{m['status']}** — "
        f"{m['reason']}"
    )

    lines.append("")

    # Current Dasha.
    lines.append(
        "## 🕉️ Current Vimshottari Period"
    )

    if pred.get(
        "active_dasha"
    ):

        d = pred[
            "active_dasha"
        ]

        lines.append(
            f"**Mahadasha:** "
            f"{d['Mahadasha']}  "
        )

        lines.append(
            f"**Antardasha:** "
            f"{d['Antardasha']}  "
        )

        lines.append(
            f"**Period:** "
            f"{d['Start'].strftime('%d-%m-%Y')} "
            f"to "
            f"{d['End'].strftime('%d-%m-%Y')}"
        )

        lines.append("")

        for r in pred.get(
            "dasha_reasons",
            []
        )[:8]:

            lines.append(
                f"- {r}"
            )

    else:

        lines.append(
            "Current Dasha could not be identified from the generated Dasha table."
        )

    lines.append("")

    # Annual.
    lines.append(
        "## 📅 Year-wise Trend"
    )

    lines.append(
        "The following is a rule-based trend using Vimshottari periods plus Jupiter/Saturn transit positions around 1 July of each year. It is not an event guarantee."
    )

    lines.append("")

    for yr in pred[
        "annual"
    ]:

        s = yr["scores"]

        lines.append(
            f"### {yr['year']} — "
            f"Career {s['career']:.0f} | "
            f"Wealth {s['wealth']:.0f} | "
            f"Education {s['education']:.0f} | "
            f"Relationships {s['relationships']:.0f}"
        )

        for r in yr[
            "reasons"
        ][:3]:

            lines.append(
                f"- {r}"
            )

        if yr.get(
            "active_dasha"
        ):

            lines.append(
                f"- Dasha reference: "
                f"{yr['active_dasha']['Mahadasha']}/"
                f"{yr['active_dasha']['Antardasha']}"
            )

        lines.append("")

    # Interpretation.
    lines.append(
        "## 🧭 How to Read the Result"
    )

    lines.append(
        "- **65+** indicates comparatively supportive rule combinations."
    )

    lines.append(
        "- **50–64** indicates mixed factors requiring contextual interpretation."
    )

    lines.append(
        "- **Below 50** indicates more challenging or effort-oriented combinations."
    )

    lines.append(
        "- A high score does **not** guarantee an event; it indicates stronger rule support within this software model."
    )

    return "\n".join(
        lines
    )


# ============================================================
# MAIN PUBLIC API
# ============================================================

def generate_rule_based_predictions(
    rows,
    asc,
    dasha_df,
    birth_dt=None
):
    """
    Main public API for the prediction engine.

    Existing application can continue calling:

        generate_rule_based_predictions(
            rows,
            asc,
            dasha_df,
            birth_dt
        )
    """

    # --------------------------------------------------------
    # Planet map.
    # --------------------------------------------------------

    planet_map = _planet_map(
        rows
    )

    # --------------------------------------------------------
    # Add Ketu automatically from Rahu if Ketu is absent.
    # --------------------------------------------------------

    if (
        "Rahu" in planet_map
        and "Ketu" not in planet_map
    ):

        rahu = planet_map["Rahu"]

        try:

            ketu_lon = (
                float(
                    rahu["Longitude"]
                ) + 180.0
            ) % 360.0

            (
                rashi_index,
                rashi,
                english,
                degree
            ) = get_rashi(
                ketu_lon
            )

            ketu_house = None

            if asc is not None:

                asc_index_temp = int(
                    asc["Rashi_Index"]
                )

                ketu_house = (
                    (rashi_index - asc_index_temp)
                    % 12
                ) + 1

            planet_map["Ketu"] = {

                "Planet": "Ketu",

                "Longitude":
                    ketu_lon,

                "Rashi_Index":
                    rashi_index,

                "Rashi":
                    rashi,

                "Sign":
                    english,

                "Degree_in_Rashi":
                    degree,

                "House":
                    ketu_house,

                "Retrograde":
                    True
            }

        except Exception:
            pass

    # --------------------------------------------------------
    # Ascendant.
    # --------------------------------------------------------

    asc_index = int(
        asc["Rashi_Index"]
    )

    # --------------------------------------------------------
    # House lords.
    # --------------------------------------------------------

    house_lords = _house_lords(
        asc_index
    )

    # --------------------------------------------------------
    # Combustion.
    # --------------------------------------------------------

    for p, row in planet_map.items():

        row["Combust"] = _combust_status(
            planet_map,
            p
        )

    # --------------------------------------------------------
    # Main analyses.
    # --------------------------------------------------------

    personality = _trait_analysis(
        planet_map,
        asc,
        house_lords
    )

    (
        intelligence_score,
        intelligence_reasons
    ) = _intelligence_analysis(
        planet_map,
        house_lords
    )

    (
        education_score,
        education_reasons
    ) = _education_analysis(
        planet_map,
        house_lords
    )

    (
        career_score,
        career_reasons,
        career_domains
    ) = _career_analysis(
        planet_map,
        house_lords,
        rows
    )

    (
        wealth_score,
        wealth_reasons
    ) = _wealth_analysis(
        planet_map,
        house_lords
    )

    (
        marriage_score,
        marriage_reasons
    ) = _marriage_analysis(
        planet_map,
        house_lords,
        rows
    )

    (
        foreign_score,
        foreign_reasons
    ) = _foreign_analysis(
        planet_map,
        house_lords
    )

    (
        vitality_score,
        vitality_reasons
    ) = _health_routine_analysis(
        planet_map,
        house_lords
    )

    # --------------------------------------------------------
    # Areas.
    # --------------------------------------------------------

    areas = {

        "personality": {
            "score":
                personality["score"],

            "traits":
                personality["traits"],

            "reasons":
                personality["reasons"]
        },

        "intelligence": {
            "score":
                intelligence_score,

            "reasons":
                intelligence_reasons
        },

        "education": {
            "score":
                education_score,

            "reasons":
                education_reasons
        },

        "career": {
            "score":
                career_score,

            "reasons":
                career_reasons,

            "domains":
                career_domains
        },

        "wealth": {
            "score":
                wealth_score,

            "reasons":
                wealth_reasons
        },

        "relationships": {
            "score":
                marriage_score,

            "reasons":
                marriage_reasons
        },

        "foreign": {
            "score":
                foreign_score,

            "reasons":
                foreign_reasons
        },

        "vitality": {
            "score":
                vitality_score,

            "reasons":
                vitality_reasons
        }
    }

    # --------------------------------------------------------
    # Yogas.
    # --------------------------------------------------------

    yogas = _yoga_detection(
        planet_map,
        house_lords
    )

    # --------------------------------------------------------
    # Yogakaraka.
    # --------------------------------------------------------

    yogakaraka = _yogakaraka_planets(
        house_lords
    )

    # Give Yogakaraka a modest interpretive boost.
    for p in yogakaraka:

        h = _house_of(
            planet_map,
            p
        )

        if h in {
            1,
            4,
            5,
            7,
            9,
            10,
            11
        }:

            areas["career"]["score"] += 2
            areas["wealth"]["score"] += 2

    # --------------------------------------------------------
    # Manglik.
    # --------------------------------------------------------

    (
        manglik,
        mars_house,
        manglik_reason
    ) = _manglik_analysis(
        planet_map
    )

    # --------------------------------------------------------
    # CURRENT DASHA.
    #
    # IMPORTANT:
    # Use today's date, NOT birth date.
    # --------------------------------------------------------

    now = datetime.now()

    active = _active_dasha(
        dasha_df,
        now
    )

    dasha_reasons = []

    if active:

        md = active["Mahadasha"]
        ad = active["Antardasha"]

        mod, rs = _dasha_area_modifier(
            md,
            ad,
            planet_map,
            house_lords
        )

        dasha_reasons.extend(
            rs
        )

        # Timing modifier only.
        for key in [
            "career",
            "wealth",
            "education",
            "relationships"
        ]:

            areas[key]["score"] = _clamp(
                areas[key]["score"]
                + mod * 0.35
            )

    # --------------------------------------------------------
    # Overall score.
    # --------------------------------------------------------

    weights = {

        "personality": 1.2,

        "intelligence": 0.8,

        "education": 0.8,

        "career": 1.2,

        "wealth": 1.0,

        "relationships": 1.0,

        "foreign": 0.7,

        "vitality": 0.8
    }

    total = sum(
        areas[k]["score"]
        * weights[k]
        for k in areas
    )

    overall = (
        total
        / sum(
            weights.values()
        )
    )

    # --------------------------------------------------------
    # Annual trend.
    # --------------------------------------------------------

    annual = []

    if "Moon" in planet_map:

        natal_moon_index = int(
            planet_map["Moon"][
                "Rashi_Index"
            ]
        )

    else:

        natal_moon_index = 0

    start_year = datetime.now().year

    base_scores = {

        "career":
            career_score,

        "wealth":
            wealth_score,

        "education":
            education_score,

        "relationships":
            marriage_score,

        "discipline":
            60.0
    }

    for year in range(
        start_year,
        start_year + 11
    ):

        tp = _annual_transit_profile(
            asc_index,
            natal_moon_index,
            year
        )

        (
            scores,
            reasons,
            ad
        ) = _annual_prediction(
            year,
            base_scores,
            tp,
            dasha_df,
            planet_map,
            house_lords
        )

        annual.append({

            "year":
                year,

            "scores":
                scores,

            "reasons":
                reasons,

            "active_dasha":
                ad,

            "transits":
                tp
        })

    # --------------------------------------------------------
    # Planet strength.
    # --------------------------------------------------------

    strength_rows = []

    for p, row in planet_map.items():

        fb = _functional_nature(
            p,
            house_lords
        )

        score, rs = _planet_strength(
            p,
            row,
            fb
        )

        strength_rows.append({

            "Planet":
                p,

            "Strength":
                round(
                    score,
                    1
                ),

            "Dignity":
                _dignity(
                    p,
                    row.get(
                        "Rashi"
                    )
                )[0],

            "House":
                row.get(
                    "House"
                ),

            "Functional":
                (
                    "Supportive"
                    if fb is True
                    else
                    (
                        "Challenging"
                        if fb is False
                        else "Mixed"
                    )
                ),

            "Combust":
                (
                    "Yes"
                    if row.get(
                        "Combust"
                    )
                    else "No"
                ),

            "Notes":
                "; ".join(
                    rs[:2]
                )
        })

    # --------------------------------------------------------
    # Final result.
    # --------------------------------------------------------

    return {

        "overall_score":
            _clamp(
                overall
            ),

        "areas":
            areas,

        "yogas":
            yogas,

        "yogakaraka":
            yogakaraka,

        "manglik": {

            "present":
                manglik,

            "mars_house":
                mars_house,

            "status":
                (
                    "Manglik indication present"
                    if manglik
                    else
                    "No Manglik indication"
                ),

            "reason":
                manglik_reason
        },

        "active_dasha":
            active,

        "dasha_reasons":
            dasha_reasons,

        "annual":
            annual,

        "planet_strengths":
            strength_rows,

        "house_lords":
            house_lords,

        "house_themes":
            HOUSE_THEMES
    }


# ============================================================
# FINAL LOAD MESSAGE
# ============================================================

print(
    "✅ Corrected rule-based Vedic prediction engine loaded successfully."
)
print(
    "✅ Parashari planetary aspects corrected."
)
print(
    "✅ Current Dasha uses today's date."
)
print(
    "✅ Ketu derivation supported."
)
print(
    "✅ Manglik checked from Lagna, Moon and Venus."
)
print(
    "✅ Yogakaraka detection added."
)
print(
    "✅ House themes and house groups updated."
)
