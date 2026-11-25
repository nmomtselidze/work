import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()

gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)

planner = Agent(
    role="Trip Planner",
    goal="Create a concise, practical travel itinerary for {destination}",
    backstory="You are an experienced travel consultant who builds realistic day-by-day itineraries.",
    llm=gemini_llm,
    verbose=True,
)

plan_task = Task(
    description="Build a 3-day travel itinerary for {destination}, including top sights, food spots, and logistics.",
    expected_output="A structured 3-day itinerary in Markdown.",
    agent=planner,
)

def run():
    crew = Crew(agents=[planner], tasks=[plan_task], verbose=True)
    result = crew.kickoff(inputs={"destination": "Tbilisi, Georgia"})
    print(result)

if __name__ == "__main__":
    run()
