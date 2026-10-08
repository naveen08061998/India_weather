"""
Indian Railways — Typical Coach / Rake Composition (curated reference data)
============================================================================
Hand-written, general-knowledge facts about the TYPICAL rake makeup for
each train category (Rajdhani, Shatabdi, Vande Bharat, ...) — no network
calls, no third-party API. Keyed by the same "type" string already stored
on each train in train_data.py (see ir_client._TIER_BY_TYPE for the full
set of values in use).

NOT an exact, per-train, per-date coach list — actual rake composition
varies by route length, demand, and coach availability on a given day.
See DISCLAIMER, also shown on the page.
"""

from __future__ import annotations

DISCLAIMER = (
    "Typical/illustrative rake composition for this train category, not an exact "
    "per-train or per-date coach list — actual composition varies by route, demand "
    "and coach availability."
)

# composition: ordered list of {code, name, count} — common coach classes,
# counts are an illustrative typical total (not official allocation rules).
# total_coaches: approximate overall rake length including power/luggage cars.
COACH_COMPOSITION: dict[str, dict] = {
    "Rajdhani": {
        "rake": "LHB (loco-hauled, fully air-conditioned)",
        "composition": [
            {"code": "1A", "name": "AC First Class", "count": 1},
            {"code": "2A", "name": "AC 2-Tier", "count": 3},
            {"code": "3A", "name": "AC 3-Tier", "count": 11},
            {"code": "PC", "name": "Pantry Car", "count": 1},
            {"code": "EOG", "name": "Generator/Power Car", "count": 2},
        ],
        "total_coaches": 18,
        "note": "India's flagship fully air-conditioned long-distance service, with onboard catering "
                "included in the fare and the highest priority in signalling precedence.",
    },
    "Shatabdi": {
        "rake": "LHB (loco-hauled, fully air-conditioned, day service)",
        "composition": [
            {"code": "EC", "name": "AC Executive Chair Car", "count": 1},
            {"code": "CC", "name": "AC Chair Car", "count": 9},
            {"code": "PC", "name": "Pantry Car", "count": 1},
            {"code": "EOG", "name": "Generator/Power Car", "count": 2},
        ],
        "total_coaches": 13,
        "note": "Same-day return intercity service with at-seat catering included in the fare.",
    },
    "Duronto": {
        "rake": "LHB (loco-hauled, fully air-conditioned, non-stop)",
        "composition": [
            {"code": "1A", "name": "AC First Class", "count": 1},
            {"code": "2A", "name": "AC 2-Tier", "count": 2},
            {"code": "3A", "name": "AC 3-Tier", "count": 10},
            {"code": "PC", "name": "Pantry Car", "count": 1},
            {"code": "EOG", "name": "Generator/Power Car", "count": 2},
        ],
        "total_coaches": 16,
        "note": "Point-to-point service with no scheduled commercial halts between origin and destination.",
    },
    "Vande Bharat": {
        "rake": "EMU train-set (self-propelled, distributed power, fully air-conditioned)",
        "composition": [
            {"code": "EC", "name": "AC Executive Chair Car", "count": 2},
            {"code": "CC", "name": "AC Chair Car", "count": 14},
        ],
        "total_coaches": 16,
        "note": "India's first indigenously designed semi-high-speed train-set — no separate locomotive "
                "or pantry car; catering is served at-seat from an integrated modular pantry, and the "
                "rake has automatic plug doors, GPS-based passenger info screens and regenerative braking.",
    },
    "Tejas": {
        "rake": "LHB-based, fully air-conditioned, onboard amenities",
        "composition": [
            {"code": "EC", "name": "AC Executive Chair Car", "count": 1},
            {"code": "CC", "name": "AC Chair Car", "count": 7},
            {"code": "EOG", "name": "Generator/Power Car", "count": 2},
        ],
        "total_coaches": 10,
        "note": "Premium chair-car service with onboard infotainment, automatic doors and attendant "
                "service; catering is served at-seat rather than from a dedicated pantry car.",
    },
    "Garib Rath": {
        "rake": "LHB (loco-hauled, fully air-conditioned, budget 3-tier only)",
        "composition": [
            {"code": "3A", "name": "AC 3-Tier (higher-density seating)", "count": 17},
            {"code": "EOG", "name": "Generator/Power Car", "count": 2},
        ],
        "total_coaches": 19,
        "note": "Budget fully-AC service — all-3AC rake with higher berth density than a standard 3AC "
                "coach; bedrolls and catering are chargeable extras, not included in the base fare.",
    },
    "Humsafar": {
        "rake": "LHB (loco-hauled, fully air-conditioned 3-tier, fully reserved)",
        "composition": [
            {"code": "3A", "name": "AC 3-Tier", "count": 16},
            {"code": "EOG", "name": "Generator/Power Car", "count": 2},
        ],
        "total_coaches": 18,
        "note": "All-3AC, fully reserved rake fitted with fire/smoke detectors, LED passenger displays, "
                "mobile-charging points and CCTV; no unreserved or pantry coaches, catering is on-demand.",
    },
    "Sampark Kranti": {
        "rake": "ICF/LHB mixed, reserved + unreserved classes",
        "composition": [
            {"code": "2A", "name": "AC 2-Tier", "count": 1},
            {"code": "3A", "name": "AC 3-Tier", "count": 4},
            {"code": "SL", "name": "Sleeper Class", "count": 10},
            {"code": "GEN", "name": "General/Unreserved", "count": 3},
            {"code": "SLR", "name": "Seating-cum-Luggage Rake (guard coach)", "count": 1},
        ],
        "total_coaches": 19,
        "note": "Superfast service designed to connect state capitals to Delhi without needing a separate "
                "reservation quota at every intermediate stop.",
    },
    "Jan Shatabdi": {
        "rake": "ICF/LHB mixed, budget day service",
        "composition": [
            {"code": "CC", "name": "AC Chair Car", "count": 2},
            {"code": "2S", "name": "Second Sitting (non-AC chair car)", "count": 8},
            {"code": "GEN", "name": "General/Unreserved", "count": 2},
            {"code": "SLR", "name": "Seating-cum-Luggage Rake (guard coach)", "count": 1},
        ],
        "total_coaches": 13,
        "note": "Budget counterpart to Shatabdi — mostly non-AC chair car seating, catering available at "
                "stops rather than an included onboard pantry.",
    },
    "Superfast": {
        "rake": "ICF/LHB mixed, mail/express with a speed surcharge",
        "composition": [
            {"code": "2A", "name": "AC 2-Tier", "count": 1},
            {"code": "3A", "name": "AC 3-Tier", "count": 4},
            {"code": "SL", "name": "Sleeper Class", "count": 11},
            {"code": "GEN", "name": "General/Unreserved", "count": 4},
            {"code": "SLR", "name": "Seating-cum-Luggage Rake (guard coach)", "count": 2},
        ],
        "total_coaches": 22,
        "note": "Classified \"superfast\" (average speed above IR's threshold), which attracts a small "
                "fare surcharge versus an ordinary Mail/Express of the same route.",
    },
    "Mail-Express": {
        "rake": "ICF/LHB mixed, general long-distance service",
        "composition": [
            {"code": "2A", "name": "AC 2-Tier", "count": 1},
            {"code": "3A", "name": "AC 3-Tier", "count": 3},
            {"code": "SL", "name": "Sleeper Class", "count": 12},
            {"code": "GEN", "name": "General/Unreserved", "count": 4},
            {"code": "SLR", "name": "Seating-cum-Luggage Rake (guard coach)", "count": 2},
        ],
        "total_coaches": 22,
        "note": "The most common long-distance rake makeup — majority Sleeper Class with a handful of "
                "AC coaches and unreserved coaches at both ends for walk-up passengers.",
    },
    "Express": {
        "rake": "ICF/LHB mixed, general service",
        "composition": [
            {"code": "3A", "name": "AC 3-Tier", "count": 2},
            {"code": "SL", "name": "Sleeper Class", "count": 10},
            {"code": "GEN", "name": "General/Unreserved", "count": 5},
            {"code": "SLR", "name": "Seating-cum-Luggage Rake (guard coach)", "count": 2},
        ],
        "total_coaches": 19,
        "note": "Shorter/medium-distance service, with a larger share of unreserved coaches than a "
                "Mail/Express or Superfast covering a longer trunk route.",
    },
    "Mail": {
        "rake": "ICF/LHB mixed, general service (historically carried mail)",
        "composition": [
            {"code": "2A", "name": "AC 2-Tier", "count": 1},
            {"code": "3A", "name": "AC 3-Tier", "count": 2},
            {"code": "SL", "name": "Sleeper Class", "count": 12},
            {"code": "GEN", "name": "General/Unreserved", "count": 5},
            {"code": "SLR", "name": "Seating-cum-Luggage Rake (guard coach)", "count": 2},
        ],
        "total_coaches": 22,
        "note": "\"Mail\" trains historically carried railway mail vans alongside passengers; the name "
                "is now largely a legacy classification rather than a functional difference from Express.",
    },
}
