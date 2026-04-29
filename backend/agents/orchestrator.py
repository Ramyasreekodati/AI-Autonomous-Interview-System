from langgraph.graph import StateGraph, END
from .state import InterviewState
from .interviewer import interviewer_node
from .coach import coach_node
from .evaluator_hierarchy import (
    technical_specialist_node,
    soft_skills_specialist_node,
    internal_review_node,
    senior_manager_node
)

# 1. Initialize the Graph
workflow = StateGraph(InterviewState)

# 2. Add Nodes
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("coach", coach_node)
workflow.add_node("tech_specialist", technical_specialist_node)
workflow.add_node("soft_skills_specialist", soft_skills_specialist_node)
workflow.add_node("internal_review", internal_review_node)
workflow.add_node("senior_manager", senior_manager_node)

# 3. Define Routing Logic
def entry_router(state: InterviewState):
    transcript = state.get("transcript", [])
    if not transcript:
        return "interviewer"
    
    if transcript[-1]["role"] == "human":
        # Start the Hierarchical Evaluation Chain
        # First: Run specialists in parallel
        return ["tech_specialist", "soft_skills_specialist", "coach"]
    
    return "interviewer"

def after_interviewer_router(state: InterviewState):
    return END

# 4. Define the Flow (The Hierarchy)

workflow.set_conditional_entry_point(
    entry_router,
    {
        "interviewer": "interviewer",
        "tech_specialist": "tech_specialist",
        "soft_skills_specialist": "soft_skills_specialist",
        "coach": "coach"
    }
)

# After specialists run, they all point to the Medium-Level Consolidator
workflow.add_edge("tech_specialist", "internal_review")
workflow.add_edge("soft_skills_specialist", "internal_review")
workflow.add_edge("coach", "internal_review")

# Medium-Level Review leads to Higher-Level Senior Manager
workflow.add_edge("internal_review", "senior_manager")

# Senior Manager decides next steps (Back to Interviewer or END)
workflow.add_edge("senior_manager", "interviewer")

# Interviewer always leads to a wait state
workflow.add_conditional_edges("interviewer", after_interviewer_router)

# Compile the graph
app = workflow.compile()
