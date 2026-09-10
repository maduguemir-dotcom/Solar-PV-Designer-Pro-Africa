"""Session-state initialization for Solar PV Designer Pro Africa™."""

from copy import deepcopy
import streamlit as st

DEFAULT_STATE = {
    "location_ready": False,
    "location_description": None,
    "latitude": None,
    "longitude": None,
    "sun_hours": None,
    "temperature": None,
    "solar_data": None,
    "solar_summary": None,
    "location_summary": None,
    "location_source": None,
    "location_search_results": [],
    "selected_map_location": None,
    "design_results": None,
    "appliance_loads": [],
    "use_appliance_demand": False,
    "cost_diary": [],
    "energy_source": None,
    "ai_recommendation": None,
}

def initialize_session_state() -> None:
    """Create missing application state without overwriting user work."""
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(value)
