import random
from typing import List, Tuple, Dict

# ----------------------------------
# REAL-WORLD DOMAIN (SLA)
# ----------------------------------

# Facilitators
FACILITATORS = [
    "Lock", "Glen", "Banks", "Richards", "Shaw",
    "Singer", "Uther", "Tyler", "Numen", "Zeldin"
]
NUM_FACILITATORS = len(FACILITATORS)

# Times (we store the numeric hour to compute differences)
TIMES = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]
TIME_HOURS = [10, 11, 12, 13, 14, 15]  # maps TIMES[i] -> TIME_HOURS[i]
NUM_TIMES = len(TIMES)

# Rooms (with building and capacity — building matters for Roman/Beach)
ROOMS = [
    {"name": "Beach 201",  "capacity": 18,  "building": "Beach"},
    {"name": "Beach 301",  "capacity": 25,  "building": "Beach"},
    {"name": "Frank 119",  "capacity": 95,  "building": "Frank"},
    {"name": "Loft 206",   "capacity": 55,  "building": "Loft"},
    {"name": "Loft 310",   "capacity": 48,  "building": "Loft"},
    {"name": "James 325",  "capacity": 110, "building": "James"},
    {"name": "Roman 201",  "capacity": 40,  "building": "Roman"},
    {"name": "Roman 216",  "capacity": 80,  "building": "Roman"},
    {"name": "Slater 003", "capacity": 32,  "building": "Slater"},
]
NUM_ROOMS = len(ROOMS)

# Activities (11)
# Each activity: name, expected enrollment, preferred facilitators, other facilitators
ACTIVITIES = [
    {
        "name": "SLA101A",
        "enrollment": 40,
        "preferred": ["Glen", "Lock", "Banks"],
        "other": ["Numen", "Richards", "Shaw", "Singer"],
    },
    {
        "name": "SLA101B",
        "enrollment": 35,
        "preferred": ["Glen", "Lock", "Banks"],
        "other": ["Numen", "Richards", "Shaw", "Singer"],
    },
    {
        "name": "SLA191A",
        "enrollment": 45,
        "preferred": ["Glen", "Lock", "Banks"],
        "other": ["Numen", "Richards", "Shaw", "Singer"],
    },
    {
        "name": "SLA191B",
        "enrollment": 40,
        "preferred": ["Glen", "Lock", "Banks"],
        "other": ["Numen", "Richards", "Shaw", "Singer"],
    },
    {
        "name": "SLA201",
        "enrollment": 60,
        "preferred": ["Glen", "Banks", "Zeldin", "Lock", "Singer"],
        "other": ["Richards", "Uther", "Shaw"],
    },
    {
        "name": "SLA291",
        "enrollment": 50,
        "preferred": ["Glen", "Banks", "Zeldin", "Lock", "Singer"],
        "other": ["Richards", "Uther", "Shaw"],
    },
    {
        "name": "SLA303",
        "enrollment": 25,
        "preferred": ["Glen", "Zeldin"],
        "other": ["Banks"],
    },
    {
        "name": "SLA304",
        "enrollment": 20,
        "preferred": ["Singer", "Uther"],
        "other": ["Richards"],
    },
    {
        "name": "SLA394",
        "enrollment": 15,
        "preferred": ["Tyler", "Singer"],
        "other": ["Richards", "Zeldin"],
    },
    {
        "name": "SLA449",
        "enrollment": 30,
        "preferred": ["Tyler", "Zeldin", "Uther"],
        "other": ["Zeldin", "Shaw"],
    },
    {
        "name": "SLA451",
        "enrollment": 90,
        "preferred": ["Lock", "Banks", "Zeldin"],
        "other": ["Tyler", "Singer", "Shaw", "Glen"],
    },
]
NUM_ACTIVITIES = len(ACTIVITIES)

# Fast map: name -> index
ACTIVITY_INDEX: Dict[str, int] = {a["name"]: i for i, a in enumerate(ACTIVITIES)}

# Type of an individual:
# individual[activity_idx] = (room_idx, time_idx, facilitator_idx)
Individual = List[Tuple[int, int, int]]

# -------------------------------------------------
# CREATE A RANDOM INDIVIDUAL (A SCHEDULE)
# -------------------------------------------------

def create_random_individual() -> Individual:
    """
    For each activity (SLA101A, SLA101B, ... SLA451),
    randomly choose:
      - a room (room_idx)
      - a time (time_idx)
      - a facilitator (facilitator_idx)
    """
    individual: Individual = []
    for _ in range(NUM_ACTIVITIES):
        room_idx = random.randrange(NUM_ROOMS)
        time_idx = random.randrange(NUM_TIMES)
        fac_idx = random.randrange(NUM_FACILITATORS)
        individual.append((room_idx, time_idx, fac_idx))
    return individual

# -------------------------------------------------
# FITNESS FUNCTION (Appendix A)
# -------------------------------------------------

def evaluate_fitness(individual: Individual) -> float:
    """
    Computes the total fitness of a schedule.

    - Adds fitness for each activity, considering:
        * room/time conflicts
        * room size vs expected enrollment
        * facilitator type (preferred / other / unrelated)
        * facilitator load (same time, total activities)
    - Also includes special SLA101 / SLA191 adjustments.
    """
    assert len(individual) == NUM_ACTIVITIES

    # Helper dictionaries
    room_time_to_acts: Dict[Tuple[int, int], List[int]] = {}
    fac_time_to_acts: Dict[Tuple[int, int], List[int]] = {}
    fac_to_acts: Dict[int, List[int]] = {}

    for act_idx, (room_idx, time_idx, fac_idx) in enumerate(individual):
        room_time_to_acts.setdefault((room_idx, time_idx), []).append(act_idx)
        fac_time_to_acts.setdefault((fac_idx, time_idx), []).append(act_idx)
        fac_to_acts.setdefault(fac_idx, []).append(act_idx)

    per_activity_score = [0.0 for _ in range(NUM_ACTIVITIES)]

    # ---- Part 1: base score per activity ----
    for act_idx, (room_idx, time_idx, fac_idx) in enumerate(individual):
        activity = ACTIVITIES[act_idx]
        room = ROOMS[room_idx]
        fac_name = FACILITATORS[fac_idx]
        expected = activity["enrollment"]
        capacity = room["capacity"]

        score = 0.0

        # a) Room + time conflict
        if len(room_time_to_acts[(room_idx, time_idx)]) > 1:
            score -= 0.5

        # b) Room size vs enrollment
        if capacity < expected:
            score -= 0.5
        else:
            ratio = capacity / expected
            if ratio > 3.0:
                score -= 0.4
            elif ratio > 1.5:
                score -= 0.2
            else:
                score += 0.3

        # c) Facilitator type
        if fac_name in activity["preferred"]:
            score += 0.5
        elif fac_name in activity["other"]:
            score += 0.2
        else:
            score -= 0.1

        # d) Facilitator load at the SAME time
        same_time_acts = fac_time_to_acts[(fac_idx, time_idx)]
        if len(same_time_acts) > 1:
            score -= 0.2
        else:
            score += 0.2

        per_activity_score[act_idx] = score

    # ---- Part 2: total facilitator load ----
    for fac_idx, acts in fac_to_acts.items():
        total = len(acts)
        fac_name = FACILITATORS[fac_idx]

        if total > 4:
            for a in acts:
                per_activity_score[a] -= 0.5
        elif total < 3:
            if fac_name == "Tyler" and total < 2:
                continue
            else:
                for a in acts:
                    per_activity_score[a] -= 0.4

    total_fitness = sum(per_activity_score)

    # ---- Part 3: SLA101 / SLA191 specific adjustments ----

    def time_hour(time_idx: int) -> int:
        return TIME_HOURS[time_idx]

    # special indices
    idx_101A = ACTIVITY_INDEX["SLA101A"]
    idx_101B = ACTIVITY_INDEX["SLA101B"]
    idx_191A = ACTIVITY_INDEX["SLA191A"]
    idx_191B = ACTIVITY_INDEX["SLA191B"]

    # get times
    t101A = individual[idx_101A][1]
    t101B = individual[idx_101B][1]
    t191A = individual[idx_191A][1]
    t191B = individual[idx_191B][1]

    # SLA101 A/B
    diff101 = abs(time_hour(t101A) - time_hour(t101B))
    if t101A == t101B:
        total_fitness -= 0.5
    elif diff101 > 4:
        total_fitness += 0.5

    # SLA191 A/B
    diff191 = abs(time_hour(t191A) - time_hour(t191B))
    if t191A == t191B:
        total_fitness -= 0.5
    elif diff191 > 4:
        total_fitness += 0.5

    # Relations between SLA101 and SLA191 (all A/B combinations)
    pair_101 = [idx_101A, idx_101B]
    pair_191 = [idx_191A, idx_191B]

    for i101 in pair_101:
        for i191 in pair_191:
            t101 = individual[i101][1]
            t191 = individual[i191][1]
            hdiff = abs(time_hour(t101) - time_hour(t191))

            if t101 == t191:
                total_fitness -= 0.25
            elif hdiff == 1:
                total_fitness += 0.5

                r101 = ROOMS[individual[i101][0]]
                r191 = ROOMS[individual[i191][0]]

                is_rb_101 = r101["building"] in ("Roman", "Beach")
                is_rb_191 = r191["building"] in ("Roman", "Beach")

                if is_rb_101 != is_rb_191:
                    total_fitness -= 0.4

            elif hdiff == 2:
                total_fitness += 0.25

    return float(total_fitness)

# -------------------------------------------------
# FORMAT SCHEDULE FOR PRINTING/FILE
# -------------------------------------------------

def format_schedule(individual: Individual) -> str:
    """
    Converts an individual schedule into readable text:

    Activity   Room        Time   Facilitator
    SLA101A    Beach 201   10 AM  Glen
    ...
    """
    lines = []
    header = f"{'Activity':<8}  {'Room':<10}  {'Time':<5}  {'Facilitator'}"
    lines.append(header)
    lines.append("-" * len(header))

    for act_idx, (room_idx, time_idx, fac_idx) in enumerate(individual):
        act_name = ACTIVITIES[act_idx]["name"]
        room_name = ROOMS[room_idx]["name"]
        time_name = TIMES[time_idx]
        fac_name = FACILITATORS[fac_idx]

        lines.append(
            f"{act_name:<8}  {room_name:<10}  {time_name:<5}  {fac_name}"
        )

    return "\n".join(lines)
