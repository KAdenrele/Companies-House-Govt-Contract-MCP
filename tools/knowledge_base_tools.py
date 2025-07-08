from utils.mcp_instance import mcp
from utils.retreival_augmented_generation import KnowledgeBaseTool
from pathlib import Path

vector_dir = Path(__file__).resolve().parent.parent 
vector_name = "faiss_index"

kb_tool = KnowledgeBaseTool(index_directory=vector_dir, index_file=vector_name)

@mcp.tool(name="retrieve_from_knowledge_base")
def knowledge_base_search(query: str) -> dict:
    """
    Searches the internal knowledge base for information relevant to the user's query.
    Use this to answer questions about specific internal documents.
    """

    query_result = kb_tool.search(query)
    result ={"result": query_result}
    return result



