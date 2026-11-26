=== To Run=Not Very Good ==============>
cd /media/user/dsk64/monowork/trip-planner-crew

# Set the venv path on your primary Linux drive
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/trip-planner-crew"

uv --version 
    uv 0.12.17

# Add your dependencies
uv add crewai langchain langchain-google-genai google-generativeai python-dotenv litellm unstructured
uv sync --upgrade-package crewai

# Run your script run Чтобы запустить проект c uv достаточно выполнить:
uv run python src/trip_planner_crew/main.py

create requirements.txt: crewai langchain langchain-google-genai google-generativeai python-dotenv litellm unstructured

----------------------------------------------
cd /media/user/dsk64/monowork/trip-planner-crew
uv python pin 3.13
source ~/.bashrc
uv add --python 3.13 -r requirements.txt
rm -rf /media/user/dsk64/monowork/trip-planner-crew/.venv
uv run python src/trip_planner_crew/main.py

rm -rf /media/user/dsk64/monowork/.venv /media/user/dsk64/monowork/trip-planner-crew/.venv
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/trip-planner-crew"
uv venv --clear --python 3.13


=========================================================================================================================================

Welcome to Trip Planner Crew
From where will you be traveling from? Tbilisi What are the cities options you are interested in visiting? Madrid What is the date range you are interested in traveling? 1.09.2026 What are some of your high level interests and hobbies? Study in Madrid universiti

[System] Verifying connection and checking location: Madrid... [System] API Verified. Landmark found: The Royal Palace of Madrid.

[System] Starting the Trip Planning Crew. This may take a minute...

########################

Here is you Trip Plan
########################

Fallback Trip Plan
Real-time AI planning is currently unavailable. Reason: LLM provider is not configured.

This fallback plan is a static itinerary based on your inputs and does not include live pricing, live weather, or API-fetched places.

Trip Summary
Origin: Tbilisi
Destination: Madrid
Date Range: 1.09.2026
Interests: Study in Madrid universiti
Suggested 7-Day Outline
Day 1: Arrival, settle near the city center, and take an evening walk around the main historic district. Day 2: Visit the main university area, identify campus buildings, admissions offices, and nearby study-friendly cafes. Day 3: Explore major academic neighborhoods, libraries, and public transport routes between housing and university zones. Day 4: Review accommodation options, estimate commute times, and shortlist affordable food spots near the university. Day 5: Spend the day in museums, public plazas, and cultural landmarks to understand the city beyond academics. Day 6: Compare student services, co-working or library spaces, and practical essentials such as supermarkets and pharmacies. Day 7: Keep a flexible day for follow-up campus visits, paperwork, or meeting student support offices before departure.

Packing Suggestions
Passport and study documents
Printed and digital copies of university paperwork
Comfortable walking shoes
Weather-appropriate layers
Charger, adapter, and backup battery
Notebook or laptop for campus visits
Budget Guidance
Accommodation: check student-friendly hotels, hostels, or short-stay rentals near the university area
Transport: plan for airport transfer plus 7 days of metro or bus use
Food: budget for a mix of groceries, cafes, and one or two restaurant visits
Miscellaneous: include museum tickets, local SIM or data, and emergency cash buffer
Next Step
Re-run the app once your LLM/API access is available to generate a live researched itinerary with actual places, weather, and costs.
