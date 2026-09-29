"""
Indian Railways — History & Technology Content
================================================
Curated, hand-written reference content (no network calls, no third-party
API) summarising major trains introduced by Indian Railways over time and
the technology that has shaped the network. This is a general-knowledge
overview compiled from widely published public history, not an official
IR archival record — see DISCLAIMER below, also shown on the page itself.
Some rollout dates (electrification, gauge conversion, KAVACH, etc.) are
phased over many years; the year shown is when the effort was first
introduced/decided, not when every route was covered.
"""

from __future__ import annotations

DISCLAIMER = (
    "This is a general-knowledge overview of Indian Railways' history compiled from "
    "widely published public sources — not an official IR archival record. Some "
    "technology rollouts (electrification, gauge conversion, KAVACH, etc.) happened "
    "in phases over many years; the year shown is when the effort was introduced, "
    "not when it was completed everywhere."
)

# Each entry: year (sort key, int), year_label (display string), title, text
# (short summary shown by default), detail (longer paragraph shown on "Read
# more"), icon, tag. tag ∈ {"milestone", "train", "technology"} — used for
# the filter chips on the page.
TIMELINE: list[dict] = [
    {"year": 1853, "year_label": "1853", "month_day": "04-16", "tag": "milestone", "icon": "🚂",
     "title": "India's First Passenger Train",
     "text": "The Great Indian Peninsula Railway ran India's first passenger train, "
             "hauled by three steam locomotives (Sahib, Sindh & Sultan), 34 km from "
             "Bombay (Bori Bunder) to Thane.",
     "detail": "The Great Indian Peninsula Railway (GIPR) inaugurated India's first "
               "passenger railway on 16 April 1853, running 34 km from Bombay's Bori "
               "Bunder station to Thane. The train was hauled by three steam locomotives "
               "imported from Britain — nicknamed Sahib, Sindh and Sultan — and carried "
               "around 400 passengers in 14 carriages, escorted by a 21-gun salute. This "
               "one journey kicked off what would become one of the largest railway "
               "networks in the world, though a short freight-only line had actually run "
               "in Madras a few months earlier. Bori Bunder station was later rebuilt into "
               "what is now Chhatrapati Shivaji Maharaj Terminus (CSMT)."},
    {"year": 1854, "year_label": "1854", "month_day": "08-15", "tag": "milestone", "icon": "🚂",
     "title": "First Train in Eastern India",
     "text": "The East Indian Railway opened its first stretch, from Howrah to Hooghly, "
             "extending steam rail service to eastern India.",
     "detail": "The East Indian Railway Company opened its first section on 15 August "
               "1854, running roughly 24 miles from Howrah (opposite Kolkata) to Hooghly. "
               "It was built primarily to move coal from the Raniganj coalfields to "
               "Kolkata's docks, reflecting how early Indian railway construction was "
               "driven as much by resource extraction and colonial trade as by passenger "
               "travel. The Eastern network grew rapidly afterward, and Howrah station "
               "remains one of the busiest terminals in the world today."},
    {"year": 1925, "year_label": "1925", "month_day": "02-03", "tag": "technology", "icon": "⚡",
     "title": "First Electric Train",
     "text": "India's first electric passenger train ran on the Bombay VT–Kurla harbour "
             "line, marking the start of railway electrification.",
     "detail": "On 3 February 1925, the Great Indian Peninsula Railway ran India's first "
               "electric train service on the 1500V DC harbour branch line between "
               "Bombay's Victoria Terminus (now CSMT) and Kurla. Electrification was "
               "chosen for this stretch mainly because of the numerous tunnels and "
               "gradients on the line, where smoke from steam locomotives was a serious "
               "problem. This modest 16 km line proved the case for electrified suburban "
               "and later main-line traction, decades before electrification became a "
               "nationwide priority."},
    {"year": 1951, "year_label": "1951", "tag": "milestone", "icon": "🇮🇳",
     "title": "Nationalisation & Zonal Reorganisation",
     "text": "Dozens of privately-run regional railway companies were merged into a single "
             "national system, reorganised the following year into operating zones.",
     "detail": "Before independence, India's railways were a patchwork of roughly forty "
               "different companies and princely-state systems, each with its own rules, "
               "staff and often different track gauges. The government began nationalising "
               "these into a single unified system starting in 1951, and in 1952 the "
               "network was reorganised into operating zones (initially Southern, Central, "
               "Western, Northern and Eastern), each headed by a General Manager. This gave "
               "India, for the first time, one railway administration responsible for the "
               "whole country, setting the stage for later standardisation of gauge, "
               "signalling and rolling stock."},
    {"year": 1957, "year_label": "1957", "tag": "technology", "icon": "🔌",
     "title": "Electrification Drive Begins in Earnest",
     "text": "A national push to electrify main lines and standardise gauge began, "
             "gradually replacing steam traction over the following decades.",
     "detail": "Although the first electric train ran in 1925, electrification remained "
               "limited to a few suburban stretches for decades. From 1957 the government "
               "committed to a much larger electrification programme covering trunk "
               "routes, driven by the need to move heavier freight (especially coal) "
               "faster and more efficiently than steam allowed. Electrification proceeded "
               "corridor by corridor over the following decades — the Delhi–Howrah and "
               "Delhi–Mumbai trunk routes were electrified through the 1970s–90s — and by "
               "the 2020s the large majority of India's broad-gauge network had been "
               "electrified, with a target of near-total broad-gauge electrification "
               "completed around 2023–24."},
    {"year": 1969, "year_label": "1969", "month_day": "03-01", "tag": "train", "icon": "🚄",
     "title": "Rajdhani Express",
     "text": "India's first fully air-conditioned, superfast train launched between New "
             "Delhi and Howrah, linking the capital directly with state capitals.",
     "detail": "The first Rajdhani Express began service on 1 March 1969 between New "
               "Delhi and Howrah, introduced specifically to give India's state capitals "
               "a fast, fully air-conditioned overnight link to the national capital "
               "(the name means 'capital'). It ran with lighter, higher-priority coaches "
               "and reached speeds around 120 km/h — exceptional for Indian Railways at "
               "the time. The Rajdhani concept was later extended to dozens of routes "
               "connecting New Delhi with state capitals across the country, and for many "
               "years it was considered the network's most prestigious train service."},
    {"year": 1984, "year_label": "1984", "month_day": "10-24", "tag": "train", "icon": "🚇",
     "title": "Kolkata Metro",
     "text": "South Asia's first metro rail system opened in Kolkata, bringing urban "
             "rapid transit to Indian Railways for the first time.",
     "detail": "Kolkata Metro's first stretch, between Esplanade and Bhowanipore (Netaji "
               "Bhavan), opened on 24 October 1984, making it the first metro rail system "
               "not just in India but in the whole of South Asia. Planning had begun back "
               "in the 1970s, and construction faced major delays due to the city's "
               "congested streets and difficult underground conditions. It was built and "
               "is still operated directly by Indian Railways — a unique arrangement, "
               "since India's other metros are run by separate state/city metro "
               "corporations — and its success influenced the decision to build the Delhi "
               "Metro roughly two decades later."},
    {"year": 1986, "year_label": "1986", "tag": "technology", "icon": "🖥️",
     "title": "Computerised Passenger Reservation",
     "text": "The Passenger Reservation System (PRS) digitised ticket booking, replacing "
             "manual ledger-based reservations nationwide.",
     "detail": "Before computerisation, reserving a train ticket meant a clerk manually "
               "checking paper charts and ledgers for available berths — slow, "
               "error-prone and effectively impossible to check for trains departing from "
               "a different city. The Passenger Reservation System (PRS), rolled out from "
               "1986 starting in New Delhi and expanding to other major cities over the "
               "following years, let clerks check and book seats electronically across a "
               "networked database. It was developed with support from CRIS (Centre for "
               "Railway Information Systems, formed around the same period) and laid the "
               "technical foundation for everything that followed — including IRCTC's "
               "online booking system launched in 2002."},
    {"year": 1988, "year_label": "1988", "tag": "train", "icon": "🚄",
     "title": "Shatabdi Express",
     "text": "A same-day, chair-car intercity service launched — the fastest train of its "
             "era for day trips between major cities.",
     "detail": "The first Shatabdi Express ran between New Delhi and Jhansi/Gwalior in "
               "1988 (named to mark the railways' upcoming 150th anniversary), designed "
               "as a same-day return service rather than an overnight train like the "
               "Rajdhani. It offered fully air-conditioned chair-car seating, onboard "
               "catering and higher average speeds for business travellers who needed to "
               "reach a city and return within a day. Shatabdi services were subsequently "
               "launched on dozens of routes radiating from major state capitals, and for "
               "a long time the Bhopal Shatabdi held the record as India's fastest train, "
               "briefly touching 150 km/h in trials."},
    {"year": 1992, "year_label": "1990s", "tag": "technology", "icon": "🛤️",
     "title": "Project Unigauge",
     "text": "A long-running programme to convert metre-gauge and narrow-gauge lines to "
             "broad gauge, unifying the network onto a single standard gauge.",
     "detail": "India inherited three different track gauges from the colonial era — "
               "broad gauge (1,676 mm), metre gauge and narrow gauge — which meant goods "
               "and passengers often had to change trains at gauge-break junctions. "
               "Project Unigauge, launched to convert metre-gauge and narrow-gauge lines "
               "to broad gauge, ran for roughly three decades from the 1990s onward and "
               "converted tens of thousands of route-kilometres. A small number of "
               "narrow-gauge heritage lines — like the Darjeeling Himalayan Railway and "
               "the Nilgiri Mountain Railway — were deliberately preserved for their "
               "UNESCO World Heritage status rather than converted."},
    {"year": 1998, "year_label": "1998", "tag": "milestone", "icon": "⛰️",
     "title": "Konkan Railway Completed",
     "text": "A major engineering achievement — tunnels and bridges carved through "
             "difficult coastal terrain to link Maharashtra, Goa and coastal Karnataka.",
     "detail": "The Konkan Railway, running roughly 740 km along India's western coast "
               "from Roha (Maharashtra) to Thokur (near Mangalore, Karnataka), was one of "
               "the most challenging railway projects ever undertaken in the country. "
               "Engineers had to cut through the Western Ghats' unstable, water-logged "
               "terrain, building over 2,000 bridges and around 90 tunnels — including the "
               "Karbude tunnel, one of India's longest at the time. Built by the Konkan "
               "Railway Corporation (a special-purpose entity, not a regular zone) and "
               "completed in 1998, it dramatically shortened travel between Mumbai and "
               "coastal Karnataka/Goa/Kerala compared with the older inland route."},
    {"year": 2002, "year_label": "2002", "tag": "technology", "icon": "💻",
     "title": "IRCTC Online Ticketing",
     "text": "IRCTC launched online train ticket booking, later followed by mobile apps, "
             "letting passengers book without visiting a counter.",
     "detail": "The Indian Railway Catering and Tourism Corporation (IRCTC), formed in "
               "1999, launched online train ticket booking at irctc.co.in in 2002 — one "
               "of the earliest large-scale e-commerce systems in India. It let passengers "
               "book, pay for and print tickets from home instead of queueing at a "
               "reservation counter, and it later expanded into e-catering, tourism "
               "packages and, from the mid-2010s, mobile apps like IRCTC Rail Connect and "
               "the UTS app for unreserved tickets. The platform now handles a very large "
               "share of all reserved-ticket bookings on Indian Railways."},
    {"year": 2002, "year_label": "2002", "month_day": "12-24", "tag": "train", "icon": "🚇",
     "title": "Delhi Metro Opens",
     "text": "Delhi's first metro line began service, kicking off rapid urban-rail "
             "expansion that later spread to many other Indian cities.",
     "detail": "Delhi Metro's first line, between Shahdara and Tis Hazari, opened on 24 "
               "December 2002, built by the Delhi Metro Rail Corporation under the "
               "leadership of E. Sreedharan, often called the 'Metro Man of India'. "
               "Unlike Kolkata Metro, it was built as a separate state-backed corporation "
               "rather than run directly by Indian Railways — a model later copied by "
               "nearly every other Indian city that built a metro. Delhi Metro's rapid, "
               "largely on-time construction became a widely cited example of large "
               "infrastructure delivery in India, and the network has since grown into "
               "one of the largest metro systems in the world by route length."},
    {"year": 2009, "year_label": "2009", "tag": "train", "icon": "🚄",
     "title": "Duronto Express",
     "text": "India's first point-to-point, non-stop long-distance train — running "
             "between origin and destination without scheduled intermediate halts.",
     "detail": "The first Duronto Express services were flagged off in September 2009, "
               "built around a simple idea: a long-distance train that runs non-stop "
               "between its origin and destination, with no scheduled passenger halts in "
               "between (only technical stops for crew change or watering). 'Duronto' "
               "means 'restless' or 'unstoppable' in Bengali, reflecting the concept. "
               "Because they skip intermediate commercial stops, Duronto trains could "
               "offer meaningfully shorter journey times than an equivalent Rajdhani or "
               "ordinary express service on the same route."},
    {"year": 2016, "year_label": "2016", "tag": "train", "icon": "🚄",
     "title": "Gatimaan Express",
     "text": "Running at up to 160 km/h between Delhi and Agra, it became India's fastest "
             "conventional train at the time of launch.",
     "detail": "The Gatimaan Express, launched in April 2016 between Hazrat Nizamuddin "
               "(Delhi) and Agra Cantonment, was designed to run at up to 160 km/h — "
               "making it India's fastest conventional train at the time, cutting the "
               "roughly 200 km journey to under two hours. It used upgraded track, "
               "signalling and Linke Hofmann Busch (LHB) coaches capable of the higher "
               "speed, effectively serving as a testbed for what would later become the "
               "Vande Bharat programme's higher-speed ambitions. 'Gatimaan' means "
               "'speedy' or 'swift' in Hindi."},
    {"year": 2017, "year_label": "2017", "tag": "train", "icon": "🎬",
     "title": "Tejas Express",
     "text": "A premium chair-car service with onboard infotainment, better catering and "
             "modern passenger amenities.",
     "detail": "Tejas Express, first launched in 2017 on the Mumbai–Goa route, was "
               "positioned as a premium, fully air-conditioned chair-car service with "
               "amenities uncommon on Indian trains at the time — onboard infotainment "
               "screens, automatic doors, CCTV, better catering and dedicated "
               "attendants. It was also notable as one of the first Indian Railways "
               "trains to trial private-style service standards, and a Lucknow–Delhi "
               "Tejas run directly by IRCTC (rather than the zonal railway) became one "
               "of the earliest examples of private operation of a train on the IR "
               "network."},
    {"year": 2019, "year_label": "2019", "month_day": "02-15", "tag": "train", "icon": "🚅",
     "title": "Vande Bharat Express",
     "text": "India's first indigenously designed and manufactured semi-high-speed train "
             "(originally \"Train 18\"), built at the Integral Coach Factory, Chennai.",
     "detail": "Vande Bharat Express, originally called 'Train 18', was flagged off in "
               "February 2019 on the New Delhi–Varanasi route. It was India's first "
               "indigenously designed and manufactured semi-high-speed train, built at "
               "the Integral Coach Factory (ICF), Chennai, using a self-propelled "
               "'distributed traction' design (motors spread across the train, like a "
               "metro) rather than a separate locomotive — letting it accelerate and "
               "brake faster than a conventional loco-hauled train. It's designed for "
               "speeds up to 180 km/h (though it typically runs slower depending on "
               "track conditions) and became the flagship of India's push toward "
               "faster, domestically built rolling stock."},
    {"year": 2022, "year_label": "2022", "tag": "technology", "icon": "🛡️",
     "title": "KAVACH — Indigenous Train Collision Avoidance",
     "text": "After years of trials, KAVACH — India's own Automatic Train Protection "
             "system — began wider rollout to automatically prevent train collisions.",
     "detail": "KAVACH ('armour' in Hindi) is India's indigenous Automatic Train "
               "Protection (ATP) system, developed by Indian Railways with domestic "
               "industry partners after earlier attempts at a similar system stalled. It "
               "uses onboard and trackside radio-frequency identification and GPS to "
               "automatically apply brakes if a driver overshoots a signal or a "
               "collision risk is detected, and it can also help trains run safely in "
               "low-visibility conditions like dense fog. After extensive trials on "
               "South Central Railway from around 2016 onward, wider rollout across "
               "high-traffic and high-speed corridors accelerated from 2022, though as "
               "of the mid-2020s it still covers only a fraction of India's total route "
               "network."},
    {"year": 2022, "year_label": "2022–24", "tag": "milestone", "icon": "🚛",
     "title": "Dedicated Freight Corridors",
     "text": "The Eastern and Western Dedicated Freight Corridors were progressively "
             "commissioned, separating freight traffic from passenger lines.",
     "detail": "The Eastern Dedicated Freight Corridor (roughly Ludhiana to Dankuni, "
               "mainly for coal and general goods) and Western Dedicated Freight "
               "Corridor (roughly Dadri to Jawaharlal Nehru Port near Mumbai, mainly for "
               "container traffic) were built to give freight trains their own "
               "double-stack-capable tracks, separate from the busy passenger main "
               "lines. Construction, run by the Dedicated Freight Corridor Corporation "
               "of India (DFCCIL), progressed in sections through the early 2020s, with "
               "most of both corridors commissioned by 2022–2024. By moving slow freight "
               "traffic off shared lines, the DFCs free up capacity and punctuality for "
               "passenger trains on the original routes."},
    {"year": 2023, "year_label": "2023", "tag": "train", "icon": "🚆",
     "title": "Vande Bharat Expansion & Namo Bharat",
     "text": "The Vande Bharat network expanded to dozens of routes; Namo Bharat (RRTS) "
             "introduced regional rapid transit on the Delhi–Meerut corridor.",
     "detail": "By 2023 the Vande Bharat network had grown from its single original "
               "route to dozens of pairs connecting major cities across almost every "
               "state, making it Indian Railways' fastest-growing train brand. The same "
               "year also saw the debut of Namo Bharat (the RRTS — Regional Rapid "
               "Transit System) on the Delhi–Ghaziabad–Meerut corridor, India's first "
               "purpose-built regional rapid rail service designed to run at higher "
               "speed and frequency than a metro but over longer, more spread-out "
               "distances than a typical city metro line."},
    {"year": 2024, "year_label": "2024", "tag": "train", "icon": "🚋",
     "title": "Amrit Bharat Express",
     "text": "A push-pull long-distance express aimed at non-AC classes, pairing modern "
             "LHB-based coaches with a more affordable fare segment.",
     "detail": "Amrit Bharat Express, first flagged off in December 2023/January 2024, "
               "was designed to bring modern LHB-based push-pull coaches (with "
               "locomotives at both ends, for faster acceleration and braking without "
               "reversing) to the large number of passengers who travel in non-AC "
               "sleeper and general classes — a segment the fully air-conditioned Vande "
               "Bharat and Tejas trains don't serve. It aimed to combine better ride "
               "quality and safety features with an affordable fare structure for "
               "long-distance travel."},
    {"year": 2030, "year_label": "Under construction", "tag": "technology", "icon": "🚄",
     "title": "Mumbai–Ahmedabad Bullet Train",
     "text": "India's first true high-speed rail line, being built with Japanese Shinkansen "
             "technology on a dedicated corridor between Mumbai and Ahmedabad.",
     "detail": "The Mumbai–Ahmedabad High Speed Rail corridor, roughly 508 km long, is "
               "being built with Japanese Shinkansen technology and financing support "
               "from Japan, targeting operating speeds around 320 km/h — several times "
               "faster than any conventional Indian train. It is India's first dedicated "
               "high-speed rail line, fully separate from the existing broad-gauge "
               "network and built to standard gauge instead, and includes India's first "
               "underwater rail tunnel, running beneath Thane Creek near Mumbai. "
               "Construction has faced land-acquisition delays, particularly in "
               "Maharashtra, and various target completion dates have been announced "
               "and revised since the project began in 2017."},
]
TIMELINE.sort(key=lambda e: e["year"])

# Technology grouped by theme (not strictly chronological — shown as reference cards).
TECHNOLOGY: list[dict] = [
    {"icon": "🚂", "title": "Traction: Steam → Diesel → Electric",
     "text": "Steam locomotives ran India's railways for over a century before diesel "
             "traction arrived in the 1950s and electrification accelerated from 1957. "
             "The great majority of broad-gauge route-km is now electrified.",
     "detail": "Steam locomotives were the backbone of Indian Railways from 1853 until "
               "the 1990s–2000s, when the last broad-gauge steam services in regular use "
               "were phased out (steam continued a little longer on some narrow-gauge "
               "heritage lines, which still run steam trains today for tourism). "
               "Diesel-electric locomotives, using engines like the WDM series built at "
               "Diesel Locomotive Works, Varanasi, began arriving from the 1950s and "
               "took over most non-electrified routes. Electrification, restarted in "
               "earnest from 1957, has now reached the large majority of broad-gauge "
               "route-kilometres, and Indian Railways has set targets to electrify "
               "essentially all remaining broad-gauge lines, both to cut fuel costs and "
               "reduce emissions."},
    {"icon": "🚃", "title": "Coach Design: ICF → LHB",
     "text": "Conventional ICF (Integral Coach Factory) coaches, built since 1955, are "
             "being progressively replaced by German-designed LHB (Linke-Hofmann-Busch) "
             "coaches, which are lighter, ride at higher speeds and resist telescoping "
             "in a collision.",
     "detail": "The Integral Coach Factory (ICF) in Chennai, established in 1955, "
               "designed and built the standard steel coach that equipped the vast "
               "majority of Indian trains for decades. From around 2000, Indian Railways "
               "began inducting LHB (Linke-Hofmann-Busch) coaches — a design licensed "
               "from Germany and now built domestically — which are lighter, ride more "
               "smoothly at higher speeds, and are built with anti-climbing features "
               "that make them far less likely to override each other and telescope in "
               "a collision. LHB coaches are now the standard for new mail/express and "
               "premium trains, with older ICF coaches being progressively phased out "
               "of long-distance service."},
    {"icon": "🛡️", "title": "Signalling & Safety: KAVACH",
     "text": "Signalling evolved from mechanical interlocking to Solid State Interlocking, "
             "and now KAVACH — an indigenous Automatic Train Protection system — is being "
             "rolled out to automatically apply brakes and prevent collisions.",
     "detail": "Early Indian Railways signalling relied on mechanical semaphore signals "
               "and manually operated interlocking, requiring a signaller to physically "
               "ensure conflicting routes couldn't be set at once. This was progressively "
               "replaced by Solid State Interlocking (electronic logic replacing "
               "mechanical relays) and centralised traffic control at busier stations "
               "and yards. The latest layer is KAVACH, an automatic train protection "
               "system that can independently apply brakes if it detects a signal "
               "overshoot or collision risk, adding a safety net on top of — rather than "
               "replacing — the driver's own signal-following."},
    {"icon": "🛤️", "title": "Gauge Unification & Freight Corridors",
     "text": "Project Unigauge converted most metre/narrow-gauge lines to broad gauge. "
             "More recently, Dedicated Freight Corridors give freight trains their own "
             "high-capacity tracks, freeing capacity for faster passenger services.",
     "detail": "India's early railways were built to a mix of gauges by different "
               "companies, which meant reloading goods (or changing trains) at "
               "gauge-break junctions — a major inefficiency. Project Unigauge, running "
               "for roughly three decades from the 1990s, converted most of the network "
               "to a single broad gauge. More recently, the Eastern and Western "
               "Dedicated Freight Corridors have given freight its own double-stack- "
               "capable tracks separate from passenger lines, addressing a different "
               "bottleneck — shared track capacity — by physically separating fast "
               "passenger and slow freight traffic."},
    {"icon": "📱", "title": "Passenger-Facing Technology",
     "text": "From the 1986 computerised Passenger Reservation System to IRCTC's online "
             "and mobile booking, the National Train Enquiry System (NTES) for running "
             "status, and free WiFi rolled out at thousands of stations.",
     "detail": "Ticketing evolved from manual ledgers, to the 1986 computerised "
               "Passenger Reservation System, to IRCTC's 2002 website and later mobile "
               "apps for both reserved (IRCTC Rail Connect) and unreserved (UTS) "
               "tickets. The National Train Enquiry System (NTES) gives passengers real "
               "running-status information for any train, sourced from signalling and "
               "control-office updates rather than GPS. Free public WiFi, rolled out at "
               "thousands of stations from around 2016 in partnership with RailTel and "
               "Google Station, brought high-speed internet access to stations that "
               "often had none before."},
    {"icon": "🌞", "title": "Green Initiatives",
     "text": "Solar panels at stations, bio-toilets on coaches to eliminate direct track "
             "discharge, and a near-complete broad-gauge electrification push to cut "
             "diesel dependence and emissions.",
     "detail": "Bio-toilets, developed with DRDO and installed across the coach fleet "
               "from the early 2010s, replaced the older design that discharged waste "
               "directly onto the tracks. Solar panels have been installed on station "
               "roofs and some coaches to offset electricity use, and Indian Railways "
               "has set a target of net-zero carbon emissions, with electrification of "
               "nearly all broad-gauge routes — rather than continued diesel use — "
               "forming the largest single piece of that plan."},
]

# Reference glossary of terms/abbreviations used across this app (train
# "type" values shown on cards, and general railway/technology terms).
# category: "train_type" | "term" — used for the filter chips on the page.
GLOSSARY: list[dict] = [
    {"term": "Rajdhani Express", "category": "train_type",
     "definition": "A fully air-conditioned, superfast overnight train connecting New "
                   "Delhi directly with a state capital."},
    {"term": "Shatabdi Express", "category": "train_type",
     "definition": "A same-day, fully air-conditioned chair-car intercity service — "
                   "out and back within a single day rather than overnight."},
    {"term": "Duronto Express", "category": "train_type",
     "definition": "A point-to-point long-distance train that runs non-stop between "
                   "origin and destination, with no scheduled passenger halts."},
    {"term": "Vande Bharat Express", "category": "train_type",
     "definition": "India's indigenously designed, self-propelled semi-high-speed "
                   "train (distributed traction, no separate locomotive)."},
    {"term": "Garib Rath", "category": "train_type",
     "definition": "A budget fully air-conditioned (3-tier) service aimed at making AC "
                   "travel affordable."},
    {"term": "Superfast", "category": "train_type",
     "definition": "Any train classified as running above a minimum average speed "
                   "threshold — attracts a small superfast surcharge on the fare."},
    {"term": "Sampark Kranti Express", "category": "train_type",
     "definition": "An express service linking a state capital directly with New Delhi, "
                   "similar in spirit to Rajdhani but without full-AC-only classes."},
    {"term": "Jan Shatabdi Express", "category": "train_type",
     "definition": "A budget counterpart to the Shatabdi, offering both AC chair-car "
                   "and ordinary non-AC classes on the same day-trip concept."},
    {"term": "Mail / Mail-Express", "category": "train_type",
     "definition": "Long-distance services historically carrying mail alongside "
                   "passengers; 'Mail-Express' covers trains with both mail and express "
                   "stop patterns."},
    {"term": "Tejas Express", "category": "train_type",
     "definition": "A premium chair-car service with onboard infotainment, better "
                   "catering and private-style amenities."},
    {"term": "Amrit Bharat Express", "category": "train_type",
     "definition": "A push-pull (locomotive at both ends) long-distance express aimed "
                   "at affordable non-AC sleeper/general classes."},
    {"term": "Gatimaan Express", "category": "train_type",
     "definition": "A high-speed conventional intercity service running at up to "
                   "160 km/h — India's fastest conventional train at launch."},
    {"term": "Humsafar Express", "category": "train_type",
     "definition": "A fully 3AC-only long-distance service with modern amenities like "
                   "reading lights, charging points and CCTV."},
    {"term": "Antyodaya Express", "category": "train_type",
     "definition": "A fully unreserved, long-distance service aimed at budget travellers "
                   "on high-demand routes."},
    {"term": "Namo Bharat (RRTS)", "category": "train_type",
     "definition": "Regional Rapid Transit System service — faster and less frequent-stop "
                   "than a metro, for longer inter-city commuter distances (e.g. "
                   "Delhi–Meerut)."},
    {"term": "LHB Coach", "category": "term",
     "definition": "Linke-Hofmann-Busch — a German-designed coach, lighter and safer at "
                   "higher speed than older ICF coaches, now standard on new trains."},
    {"term": "ICF Coach", "category": "term",
     "definition": "Integral Coach Factory (Chennai) — designed the conventional steel "
                   "coach that equipped most Indian trains for decades, now being "
                   "phased out in favour of LHB."},
    {"term": "KAVACH", "category": "term",
     "definition": "India's indigenous Automatic Train Protection system — automatically "
                   "applies brakes to prevent signal-overshoot collisions."},
    {"term": "DFC / DFCCIL", "category": "term",
     "definition": "Dedicated Freight Corridor (Corporation of India) — separate "
                   "high-capacity tracks built exclusively for freight trains."},
    {"term": "PRS", "category": "term",
     "definition": "Passenger Reservation System — the 1986 computerised system that "
                   "replaced manual ledger-based ticket booking."},
    {"term": "UTS", "category": "term",
     "definition": "Unreserved Ticketing System — lets passengers buy unreserved "
                   "(general-class) tickets via a mobile app instead of a counter queue."},
    {"term": "IRCTC", "category": "term",
     "definition": "Indian Railway Catering and Tourism Corporation — runs online "
                   "ticket booking, e-catering and tourism packages."},
    {"term": "NTES", "category": "term",
     "definition": "National Train Enquiry System — the official source for a train's "
                   "real running status, sourced from signalling/control-office updates."},
    {"term": "CRIS", "category": "term",
     "definition": "Centre for Railway Information Systems — builds and runs IR's core "
                   "IT systems, including PRS and freight information systems."},
    {"term": "PNR", "category": "term",
     "definition": "Passenger Name Record — the unique 10-digit number identifying a "
                   "reserved ticket booking."},
    {"term": "RAC", "category": "term",
     "definition": "Reservation Against Cancellation — a shared-berth status one step "
                   "above waitlisted, confirmed to travel but sharing a berth."},
    {"term": "Tatkal", "category": "term",
     "definition": "A premium last-minute booking scheme that opens a small quota of "
                   "seats one day before departure, at a higher fare."},
    {"term": "Waitlist (WL)", "category": "term",
     "definition": "A booking status meaning all confirmed/RAC berths are full — "
                   "confirmed only if enough passengers ahead cancel."},
    {"term": "Zone / Zonal Railway", "category": "term",
     "definition": "Indian Railways is organised into operating zones (e.g. Northern, "
                   "Southern, Western), each responsible for a region's day-to-day "
                   "operations."},
    {"term": "EMU / MEMU / DEMU", "category": "term",
     "definition": "Electric/Mainline-Electric/Diesel Multiple Unit — self-propelled "
                   "commuter train sets (no separate locomotive), used for suburban and "
                   "short-distance services."},
    {"term": "Gauge (Broad / Metre / Narrow)", "category": "term",
     "definition": "The distance between rails. India standardised mostly on broad "
                   "gauge (1,676 mm) via Project Unigauge; a few narrow-gauge heritage "
                   "lines remain."},
    {"term": "OHE", "category": "term",
     "definition": "Overhead Equipment — the overhead wiring that supplies power to "
                   "electric locomotives and EMUs via a pantograph."},
    {"term": "Junction (Jn)", "category": "term",
     "definition": "A station where two or more different railway lines meet, letting "
                   "trains change routes — shown as \"Jn\" in station names."},
]

# Major rail disasters, presented factually and respectfully for historical
# and public-safety context — not for sensationalism. These events are why
# safety technology like KAVACH, ACDs and modern signalling matter; several
# entries note the safety response that followed. Death tolls for older
# disasters vary across sources/inquiries; figures here are the commonly
# cited approximate ranges from public reporting, not an official verified
# record. See SAFETY_DISCLAIMER, also shown on the page itself.
SAFETY_DISCLAIMER = (
    "Presented factually and respectfully for historical and public-safety awareness, "
    "not for sensationalism — these events are part of why safety technology like KAVACH "
    "exists today. Death tolls, especially for older disasters, vary across sources and "
    "official inquiries; figures shown are commonly cited approximate ranges from public "
    "reporting, not a verified official record."
)

SAFETY_HISTORY: list[dict] = [
    {"year": 1981, "year_label": "1981", "title": "Bihar Train Disaster (Bagmati River)",
     "deaths_approx": "estimates vary widely, from the low hundreds officially counted to over 800 by some accounts",
     "text": "A passenger train crossing a bridge over the Bagmati river near Mansi, Bihar "
             "derailed and several coaches plunged into the water — believed to be one of "
             "the deadliest rail disasters in world history. A sudden brake application, "
             "possibly triggered by a cyclonic storm or an animal on the track, was "
             "suspected, but the exact cause was never conclusively established, and many "
             "victims were never recovered from the river."},
    {"year": 1995, "year_label": "1995", "title": "Firozabad Train Collision (Uttar Pradesh)",
     "deaths_approx": "over 300",
     "text": "The Kalindi Express ploughed into the derailed wreckage of the Purushottam "
             "Express near Firozabad, Uttar Pradesh, after the first train had already "
             "derailed on the same stretch of track."},
    {"year": 1998, "year_label": "1998", "title": "Khanna Rail Disaster (Punjab)",
     "deaths_approx": "around 212",
     "text": "The Frontier Mail collided with the derailed wreckage of the Golden Temple "
             "Mail at Khanna, Punjab, in dense winter fog that had already caused the "
             "first derailment."},
    {"year": 1999, "year_label": "1999", "title": "Gaisal Train Disaster (Assam)",
     "deaths_approx": "close to 290",
     "text": "The Brahmaputra Mail and the Awadh-Assam Express collided head-on near "
             "Gaisal, Assam, after a signalling error routed both trains onto the same "
             "track.",
     "note": "The disaster accelerated trials of India's first Anti-Collision Device "
             "(ACD) — an early precursor to today's KAVACH system."},
    {"year": 2010, "year_label": "2010", "title": "Sainthia Rail Disaster (West Bengal)",
     "deaths_approx": "around 66",
     "text": "The Uttar Banga Express rear-ended the stationary Vananchal Express at "
             "Sainthia station, West Bengal, in early morning fog."},
    {"year": 2010, "year_label": "2010", "title": "Jnaneswari Express Derailment (West Bengal)",
     "deaths_approx": "around 150",
     "text": "Sabotage — attributed to Maoist rebels tampering with the track — caused the "
             "Jnaneswari Super Deluxe Express to derail, after which some of its coaches "
             "were struck by an oncoming goods train."},
    {"year": 2016, "year_label": "2016", "title": "Indore-Patna Express Derailment (Pukhrayan, UP)",
     "deaths_approx": "around 150",
     "text": "Multiple coaches of the Indore-Patna Express derailed near Pukhrayan, Kanpur "
             "Dehat district; a fractured rail was identified as the likely cause."},
    {"year": 2023, "year_label": "2023", "title": "Odisha Train Collision (Bahanaga Bazar, Balasore)",
     "deaths_approx": "close to 290",
     "text": "A signalling error routed the Coromandel Express onto a loop line where it "
             "collided with a stationary goods train; derailed coaches then struck the "
             "passing Yesvantpur-Howrah Superfast Express — a three-train collision and "
             "one of India's deadliest rail disasters in decades.",
     "note": "Renewed national urgency around accelerating KAVACH's rollout across the "
             "full network."},
]

