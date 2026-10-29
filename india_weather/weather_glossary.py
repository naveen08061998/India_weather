"""
India Weather — Terminology Glossary
=======================================
Curated, static reference data (no live API — plain meteorological facts,
same pattern as other agents' GLOSSARY lists e.g. gov_updates/sources.py,
indian_railways/history_content.py). Explains the terminology a reader
needs to actually understand a weather bulletin: pressure systems/cyclone
classification (the real IMD wind-speed scale), observation instruments
like Doppler radar, common measurements, and wind/air-movement concepts.
"""

from __future__ import annotations

CATEGORIES = [
    "Pressure Systems & Cyclones",
    "Instruments & Observation",
    "Measurements & Scales",
    "Wind & Air Movement",
    "Fronts & Clouds",
]

TERMS: list[dict] = [
    # ── Pressure Systems & Cyclones (IMD's real classification scale) ──────
    {"term": "Low Pressure Area", "category": "Pressure Systems & Cyclones",
     "definition": "A region where atmospheric pressure is lower than its surroundings — the starting point from which a cyclone may develop. Winds are below 31 km/h."},
    {"term": "Depression", "category": "Pressure Systems & Cyclones",
     "definition": "A low-pressure system with sustained winds of 31-49 km/h — the first stage the India Meteorological Department (IMD) formally tracks on its way to becoming a cyclone."},
    {"term": "Deep Depression", "category": "Pressure Systems & Cyclones",
     "definition": "The next stage up from a Depression, with sustained winds of 50-61 km/h."},
    {"term": "Cyclonic Storm", "category": "Pressure Systems & Cyclones",
     "definition": "Winds of 62-88 km/h. This is the stage at which IMD officially names the storm (e.g. 'Cyclone Biparjoy')."},
    {"term": "Severe Cyclonic Storm", "category": "Pressure Systems & Cyclones",
     "definition": "Winds of 89-117 km/h, strong enough to cause structural damage and significant storm surge."},
    {"term": "Very Severe Cyclonic Storm", "category": "Pressure Systems & Cyclones",
     "definition": "Winds of 118-165 km/h — equivalent in strength to a major hurricane."},
    {"term": "Extremely Severe Cyclonic Storm", "category": "Pressure Systems & Cyclones",
     "definition": "Winds of 166-221 km/h, capable of catastrophic damage near landfall."},
    {"term": "Super Cyclonic Storm", "category": "Pressure Systems & Cyclones",
     "definition": "The most intense category — sustained winds of 222 km/h or more. Rare; the 1999 Odisha cyclone was a Super Cyclonic Storm."},
    {"term": "Eye of the Storm", "category": "Pressure Systems & Cyclones",
     "definition": "The calm, roughly circular region at the centre of a mature cyclone, often with clear skies, surrounded by the storm's strongest winds."},
    {"term": "Eyewall", "category": "Pressure Systems & Cyclones",
     "definition": "The ring of intense thunderstorms immediately surrounding the eye — where a cyclone's strongest winds and heaviest rain occur."},
    {"term": "Storm Surge", "category": "Pressure Systems & Cyclones",
     "definition": "An abnormal rise of sea level pushed ashore by a cyclone's winds — historically the single deadliest hazard in major Indian cyclones (e.g. 1999 Odisha, Bhola 1970)."},
    {"term": "Anticyclone", "category": "Pressure Systems & Cyclones",
     "definition": "A high-pressure system with winds spiralling outward — generally brings clear skies and calm, settled weather (the opposite of a cyclone)."},
    {"term": "Trough", "category": "Pressure Systems & Cyclones",
     "definition": "An elongated area of relatively low pressure extending from a larger low-pressure system, often associated with cloudy or unsettled weather."},
    {"term": "Ridge", "category": "Pressure Systems & Cyclones",
     "definition": "An elongated area of relatively high pressure, usually bringing clear and stable weather along its length."},

    # ── Instruments & Observation ──────────────────────────────────────────
    {"term": "Doppler Weather Radar (DWR)", "category": "Instruments & Observation",
     "definition": "A radar that uses the Doppler effect to measure both the intensity and the speed/direction of precipitation moving toward or away from it — IMD operates a network of DWRs across India's coast to track cyclones in real time."},
    {"term": "Weather Satellite (INSAT)", "category": "Instruments & Observation",
     "definition": "India's geostationary INSAT/INSAT-3D series satellites continuously image cloud cover, helping forecasters spot and track developing storm systems from space."},
    {"term": "Anemometer", "category": "Instruments & Observation",
     "definition": "An instrument that measures wind speed, typically using spinning cups or a propeller."},
    {"term": "Wind Vane", "category": "Instruments & Observation",
     "definition": "A simple instrument that shows the direction the wind is blowing FROM, usually paired with an anemometer at a weather station."},
    {"term": "Barometer", "category": "Instruments & Observation",
     "definition": "An instrument that measures atmospheric pressure — a rapidly falling reading often signals an approaching storm."},
    {"term": "Radiosonde", "category": "Instruments & Observation",
     "definition": "A small instrument package carried by a weather balloon to measure temperature, humidity and pressure as it rises through the atmosphere, transmitting data back by radio."},
    {"term": "Automatic Weather Station (AWS)", "category": "Instruments & Observation",
     "definition": "An unmanned station that automatically records and transmits weather data (temperature, rainfall, wind, humidity) at regular intervals, widely deployed by IMD for dense ground coverage."},

    # ── Measurements & Scales ───────────────────────────────────────────────
    {"term": "Atmospheric Pressure", "category": "Measurements & Scales",
     "definition": "The weight of the air above a point on Earth's surface, measured in hectopascals (hPa) or millibars — average sea-level pressure is about 1013 hPa."},
    {"term": "Relative Humidity", "category": "Measurements & Scales",
     "definition": "The amount of water vapour in the air expressed as a percentage of the maximum the air could hold at that temperature."},
    {"term": "Dew Point", "category": "Measurements & Scales",
     "definition": "The temperature at which air becomes saturated and water vapour starts condensing into dew/fog — a higher dew point means muggier, stickier air."},
    {"term": "Beaufort Scale", "category": "Measurements & Scales",
     "definition": "A 0-12 scale describing wind force from 'Calm' (0) to 'Hurricane' (12), based on observed effects on sea/land rather than instrument readings."},
    {"term": "Visibility", "category": "Measurements & Scales",
     "definition": "The greatest distance at which an object can be clearly seen, reduced by fog, haze, heavy rain or dust."},
    {"term": "UV Index", "category": "Measurements & Scales",
     "definition": "A scale (typically 0-11+) indicating the strength of sunburn-causing ultraviolet radiation expected at solar noon."},
    {"term": "Heat Index", "category": "Measurements & Scales",
     "definition": "A 'feels like' temperature combining actual air temperature with humidity, since high humidity reduces the body's ability to cool itself by sweating."},

    # ── Wind & Air Movement ─────────────────────────────────────────────────
    {"term": "Wind Direction", "category": "Wind & Air Movement",
     "definition": "By meteorological convention, named for where the wind is blowing FROM — a 'westerly' wind blows from the west toward the east."},
    {"term": "Jet Stream", "category": "Wind & Air Movement",
     "definition": "A narrow band of very strong winds high in the atmosphere (around 9-16 km up) that steers weather systems and strongly influences the timing of India's monsoon."},
    {"term": "Monsoon", "category": "Wind & Air Movement",
     "definition": "A seasonal reversal of prevailing winds — India's Southwest Monsoon (June-September) brings most of its annual rainfall; the Northeast Monsoon (Oct-Dec) brings rain mainly to Tamil Nadu and the southeast coast."},
    {"term": "Sea Breeze", "category": "Wind & Air Movement",
     "definition": "A local wind that blows from the (cooler) sea toward the (warmer) land during the day, common along India's coastline in the afternoon."},
    {"term": "Land Breeze", "category": "Wind & Air Movement",
     "definition": "The nighttime reverse of a sea breeze — land cools faster than the sea after sunset, so the wind flows from land out to sea."},
    {"term": "Squall", "category": "Wind & Air Movement",
     "definition": "A sudden, sharp increase in wind speed, usually accompanying a thunderstorm, that ends almost as abruptly as it began."},

    # ── Fronts & Clouds ──────────────────────────────────────────────────────
    {"term": "Cold Front", "category": "Fronts & Clouds",
     "definition": "The leading edge of an advancing cold air mass, often triggering a sharp, short burst of rain or thunderstorms as it passes."},
    {"term": "Warm Front", "category": "Fronts & Clouds",
     "definition": "The leading edge of an advancing warm air mass, typically bringing a longer period of lighter, steadier rain ahead of it."},
    {"term": "Occluded Front", "category": "Fronts & Clouds",
     "definition": "Formed when a fast-moving cold front catches up to a warm front, lifting the warm air mass entirely off the ground."},
    {"term": "Cumulonimbus", "category": "Fronts & Clouds",
     "definition": "A towering, anvil-shaped cloud associated with thunderstorms, heavy rain, hail and lightning."},
    {"term": "Cirrus", "category": "Fronts & Clouds",
     "definition": "Thin, wispy, high-altitude ice-crystal clouds, often an early sign that weather may change within a day or two."},
    {"term": "Stratus", "category": "Fronts & Clouds",
     "definition": "A flat, featureless, low-lying cloud layer that often covers the whole sky in grey, associated with overcast drizzly days."},
    {"term": "Fog", "category": "Fronts & Clouds",
     "definition": "A cloud at ground level that reduces visibility below 1 km, formed when moist air cools and water vapour condenses near the surface."},
]
