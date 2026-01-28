import os
import sys
import time
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated
from typing import List
from colorama import Fore, Style, init
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# --------------------------------------------------
# COLORAMA INIT
# --------------------------------------------------
init()

# --------------------------------------------------
# STATE DEFINITION
# --------------------------------------------------
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_input: str
    error: str
    solver: str
    output: str
    summary: str

# --------------------------------------------------
# TOOLS (Example)
# --------------------------------------------------
@tool(description="Search documentation for error solutions")
def doc_search_tool(query: str) -> str:
    """Search documentation for error solutions"""

tools = [doc_search_tool]
tool_node = ToolNode(tools)

# --------------------------------------------------
# LLM
# --------------------------------------------------
llm = ChatGroq(model="qwen/qwen3-32b")
llm_with_tools = llm.bind_tools(tools)

# --------------------------------------------------
# NODE FUNCTIONS
# --------------------------------------------------
def user_input_node(state: State):
    if state["user_input"]:
        msg = HumanMessage(content=state["user_input"])
        return {"messages": [msg]}
    return {"messages": []}

def solver_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def output_node(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, "content"):
        output = last_message.content
    elif hasattr(last_message, "tool_calls"):
        output = "Tool calls were made. Check tool outputs."
    else:
        output = str(last_message)
    return {"output": output}

# --------------------------------------------------
# BUILD GRAPH
# --------------------------------------------------
builder = StateGraph(State)
builder.add_node("user_input", user_input_node)
builder.add_node("solver", solver_node)
builder.add_node("tools", tool_node)
builder.add_node("output", output_node)

builder.add_edge(START, "user_input")
builder.add_edge("user_input", "solver")

builder.add_conditional_edges(
    "solver",
    tools_condition,
    {
        "tools": "tools",
        END: "output",
    },
)

builder.add_edge("tools", "solver")
builder.add_edge("output", END)
graph = builder.compile()

# --------------------------------------------------
# OUTPUT FORMATTING & ANIMATION
# --------------------------------------------------
def type_print(text: str, delay: float = 0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

spinner = ["|", "/", "-", "\\"]

def thinking_animation(duration: float = 0.1):
    for sym in spinner:
        sys.stdout.write(f"\r{Fore.YELLOW}Thinking {sym}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(duration)
    sys.stdout.write("\r")

def print_colored_message(msg):
    """Print each message with color & typing effect."""
    sender = msg.type
    content = msg.content

    if sender == "human":
        print(Fore.BLUE + "\nHuman: " + Style.RESET_ALL, end="")
        type_print(content)

    elif sender == "system":
        print(Fore.MAGENTA + "\nSystem: " + Style.RESET_ALL, end="")
        type_print(content)

    elif sender == "assistant":
        print(Fore.GREEN + "\nAI: " + Style.RESET_ALL, end="")
        type_print(content)

    elif sender == "tool":
        print(Fore.CYAN + "\nTool: " + Style.RESET_ALL, end="")
        type_print(content)

    else:
        # fallback
        print("\n" + sender + ": ", end="")
        type_print(content)

# --------------------------------------------------
# MAIN RUN
# --------------------------------------------------
if __name__ == "__main__":
    user_error = input("Paste your error/problem:\n> ")

    print("\n")
    # Live spinner while waiting for LLM
    start = time.time()
    while time.time() - start < 1.5:  # spinner for ~1.5s
        thinking_animation(0.1)

    result = graph.invoke(
        {
            "user_input": user_error,
            "messages": [
                SystemMessage(content="You are a programming expert assistant. Analyze errors and provide solutions. Use tools when needed."),
            ],
            "error": "",
            "solver": "",
            "output": "",
            "summary": "",
        }
    )

    print("\n" + "="*60)
    print(f"{Fore.CYAN}🧠 AI Solver Response:{Style.RESET_ALL}")
    print("="*60)

    final_output = result.get("output", "No output generated")
    print(Fore.GREEN, end="")
    type_print(final_output)
    print(Style.RESET_ALL)

    print("\n" + "="*60)
    print(f"{Fore.YELLOW}FULL CONVERSATION LOG:{Style.RESET_ALL}")
    print("="*60)

    for i, msg in enumerate(result["messages"]):
        print_colored_message(msg)
