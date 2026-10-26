"""
electoral_data_tool.py

Static structured retrieval tool for U.S. Senate Midterm data and
Voting-Eligible Population (VEP) benchmarks.
"""

from typing import Any, Dict, List, Optional

# --- Static Ground-Truth Dataset ---

SENATE_SUMMARY_DATA = {
    "election_cycle": 2026,
    "total_senate_seats": 100,
    "current_balance": {"republican": 53, "democratic_caucus": 47},
    "seats_contested": {
        "total": 35,
        "regular_class_ii": 33,
        "special_elections": 2,
        "democratic_held_up": 13,
        "republican_held_up": 22,
    },
    "special_elections_detail": [
        {"state": "Florida", "reason": "Seat formerly held by Marco Rubio"},
        {"state": "Ohio", "reason": "Seat formerly held by J.D. Vance"},
    ],
    "national_benchmark": {
        "total_us_vep_millions": 240.5,
        "avg_recent_midterm_national_turnout_pct": 52.2,
    },
}

BATTLEGROUND_STATES_DATA = {
    "Georgia": {
        "incumbent": "Jon Ossoff",
        "incumbent_party": "Democrat",
        "seat_class": "Class II",
        "consensus_rating": "Toss-up",
        "vep_millions": 7.85,
        "share_of_national_vep_pct": 3.26,
        "historical_midterm_vep_turnout_pct": 57.0,
        "key_factors": "High suburban growth in metro Atlanta, narrow 2020/2024 presidential margins, critical Democratic hold.",
    },
    "Michigan": {
        "incumbent": "Open Seat (Gary Peters retiring)",
        "incumbent_party": "Democrat",
        "seat_class": "Class II",
        "consensus_rating": "Toss-up / Lean Democratic",
        "vep_millions": 7.60,
        "share_of_national_vep_pct": 3.16,
        "historical_midterm_vep_turnout_pct": 58.5,
        "key_factors": "Rust Belt union turnout, suburban Macomb/Oakland swings, open-seat dynamics.",
    },
    "North Carolina": {
        "incumbent": "Thom Tillis",
        "incumbent_party": "Republican",
        "seat_class": "Class II",
        "consensus_rating": "Toss-up / Tilt Republican",
        "vep_millions": 7.95,
        "share_of_national_vep_pct": 3.31,
        "historical_midterm_vep_turnout_pct": 51.5,
        "key_factors": "Rapidly growing Research Triangle vs. rural baseline, top Democratic pickup target.",
    },
    "Maine": {
        "incumbent": "Susan Collins",
        "incumbent_party": "Republican",
        "seat_class": "Class II",
        "consensus_rating": "Lean Republican",
        "vep_millions": 1.10,
        "share_of_national_vep_pct": 0.46,
        "historical_midterm_vep_turnout_pct": 65.0,
        "key_factors": "Incumbent personal brand vs. blue federal lean, ranked-choice voting dynamics.",
    },
    "New Hampshire": {
        "incumbent": "Open Seat (Jeanne Shaheen retiring)",
        "incumbent_party": "Democrat",
        "seat_class": "Class II",
        "consensus_rating": "Lean Democratic",
        "vep_millions": 1.12,
        "share_of_national_vep_pct": 0.47,
        "historical_midterm_vep_turnout_pct": 55.4,
        "key_factors": "Historically volatile independent/swing electorate, open-seat race.",
    },
    "Ohio": {
        "incumbent": "Jon Husted (Appointee)",
        "incumbent_party": "Republican",
        "seat_class": "Special (Class III)",
        "consensus_rating": "Lean / Likely Republican",
        "vep_millions": 8.90,
        "share_of_national_vep_pct": 3.70,
        "historical_midterm_vep_turnout_pct": 52.3,
        "key_factors": "Special election fill-in for VP vacancy, tests working-class Midwest alignment.",
    },
    "Texas": {
        "incumbent": "John Cornyn",
        "incumbent_party": "Republican",
        "seat_class": "Class II",
        "consensus_rating": "Lean Republican",
        "vep_millions": 19.80,
        "share_of_national_vep_pct": 8.23,
        "historical_midterm_vep_turnout_pct": 45.7,
        "key_factors": "Urban turnout in Austin/Houston/Dallas vs. Republican South Texas/rural dominance.",
    },
}


# --- Tool Function ---

def get_election_dataset(
    category: str,
    state_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves structured electoral data for the U.S. Senate midterms.

    Args:
        category: Must be one of:
            - 'national_summary': Chamber arithmetic, seats up, balance of power.
            - 'battleground_list': List of all competitive battleground states.
            - 'state_detail': Specific electoral, VEP, and turnout data for a single state.
        state_name: Required if category is 'state_detail' (e.g., 'Georgia', 'Michigan').

    Returns:
        dict: Containing requested dataset records or an error message.
    """
    cat = category.strip().lower()

    if cat == "national_summary":
        return {"status": "success", "data": SENATE_SUMMARY_DATA}

    elif cat == "battleground_list":
        summaries = [
            {
                "state": state,
                "incumbent": info["incumbent"],
                "party": info["incumbent_party"],
                "consensus_rating": info["consensus_rating"],
            }
            for state, info in BATTLEGROUND_STATES_DATA.items()
        ]
        return {"status": "success", "battlegrounds": summaries}

    elif cat == "state_detail":
        if not state_name:
            return {
                "status": "error",
                "message": "state_name parameter is required when category is 'state_detail'.",
            }
        
        # Case-insensitive lookup
        matched_state = next(
            (s for s in BATTLEGROUND_STATES_DATA if s.lower() == state_name.strip().lower()),
            None,
        )
        if not matched_state:
            return {
                "status": "error",
                "message": f"State '{state_name}' not found in battleground dataset. Available states: {list(BATTLEGROUND_STATES_DATA.keys())}",
            }
        
        return {
            "status": "success",
            "state": matched_state,
            "data": BATTLEGROUND_STATES_DATA[matched_state],
        }

    return {
        "status": "error",
        "message": f"Unknown category '{category}'. Valid categories are: 'national_summary', 'battleground_list', 'state_detail'.",
    }