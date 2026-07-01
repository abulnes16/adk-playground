from google.adk.agents import Agent
from google.adk.agents import LoopAgent
from google.adk.tools import google_search, AgentTool
from utils import load_instruction_from_file

script_writter_agent = Agent(
    model="gemini-2.5-flash",
    name='ShortsScriptWriter',
    description='A helpful assistant for user questions.',
    instruction=load_instruction_from_file("instructions/scriptwiter_instructions.txt"),
    tools=[google_search],
    output_key="generated_script"
)


visualizer_agent = Agent(
    name="ShortsVisualizer",
    model="gemini-2.5-flash",
    instruction=load_instruction_from_file("instructions/visualizer_instructions.txt"),
    description='Visual content generator for YouTube Shorts',
    output_key="visual_concepts"
)

formatter_agent = Agent(
    name="ContentFormatter",
    model="gemini-2.5-flash",
    instruction=load_instruction_from_file("instructions/formatter_instructions.txt"),
    description="Formats the final Short concept in Markdown",
    output_key="final_short_concept"
)

youtube_shorts_agent = LoopAgent(   
    name="youtube_shorts_agent",
    max_iterations=3,
    sub_agents=[
        script_writter_agent, 
        visualizer_agent, 
        formatter_agent
    ],
)

root_agent = youtube_shorts_agent