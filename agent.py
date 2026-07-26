# agent.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from config import model
from mcp_client import FileSystemMCP
from langchain_core.runnables import RunnableConfig
from prompts import ROUTING_PROMPT_TEMPLATE, MCP_ANALYSIS_PROMPT, MCP_RESPONSE_PROMPT
from dotenv import load_dotenv

load_dotenv(override=True)


class AgentState(TypedDict):
    question: str
    decision: Literal["MCP", "RAG"]
    response: str
    source_used: str
class LLMDecision(BaseModel):
    decision:Literal["MCP", "RAG"] = Field(description="Action that should taken")

class MCPAction(BaseModel):
    action_type: Literal["tree", "file"] = Field(description="Should bee 'tree' if user request directory tree, or 'file' if user request content of a file")
    file_path: Optional[str] = Field(default=None, description="Relative path of the requested file (ex: 'src/test.py'). Set it None if it is tree that is requested")

decision_llm = ChatOpenAI(model=model, temperature=0).with_structured_output(LLMDecision)
decision_chain = ROUTING_PROMPT_TEMPLATE | decision_llm

mcp_llm = ChatOpenAI(model=model, temperature=0).with_structured_output(MCPAction)
mcp_chain = MCP_ANALYSIS_PROMPT | mcp_llm

response_llm = ChatOpenAI(model=model, temperature=0)
response_chain = MCP_RESPONSE_PROMPT | response_llm

def routing_node(state: AgentState) :
    response: LLMDecision = decision_chain.invoke({"question": state["question"]})
    decision = response.decision
    return {"decision": decision}

def rag_node(state: AgentState, config:RunnableConfig):
    rag_instance = config["configurable"]["rag_instance"]
    result = rag_instance.query(state["question"])

    sources_str = ", ".join(result["sources"]) if result["sources"] else "Base Vectorielle"
    badge = f"🔍 Source : RAG ({sources_str})" 

    return {
        "response": result["answer"], 
        "source_used": badge,
        }

def mcp_node(state: AgentState, config: RunnableConfig):

    mcp_instance: FileSystemMCP = config["configurable"]["mcp_instance"]
    analysis: MCPAction = mcp_chain.invoke({"question": state["question"]})
    source = "📁 Source : MCP"

    if analysis.action_type == "tree":
        context_data = mcp_instance.get_tree()
        source = "📁 Source : MCP (Arborescence)"

    elif analysis.action_type == "file":
        if analysis.file_path:
            try:
                raw_content = mcp_instance.get_file_content(analysis.file_path)
                context_data = f"Fichier demandé : {analysis.file_path}\n\nContenu :\n{raw_content}\n"
                source = f"📁 Source : MCP (Fichier : {analysis.file_path})"
            except Exception as e:
                context_data = f"Erreur lors de la lecture du fichier '{analysis.file_path}' : {e}"
        else:
            context_data = "Aucun chemin de fichier n'a été spécifié par l'utilisateur."
    else:
        context_data = "Aucune information n'a pu être extraite."


    response = response_chain.invoke({
        "context": context_data, 
        "question": state["question"]
    })
    return {"response": response.content, "source_used": source }

def router_decision(state:AgentState):
    return state["decision"].lower()

workflow = StateGraph(AgentState)
workflow.add_node("router_node", routing_node)
workflow.add_node("rag", rag_node)
workflow.add_node("mcp", mcp_node)

workflow.add_edge(START, "router_node")
workflow.add_conditional_edges(
    "router_node", 
    router_decision, 
    {
        "rag" : "rag",
        "mcp" : "mcp"
    })

workflow.add_edge("rag", END)
workflow.add_edge("mcp", END)

app = workflow.compile()




