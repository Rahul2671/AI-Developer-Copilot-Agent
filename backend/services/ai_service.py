from agents.code_agent import ask_codebase



def chat_with_agent(
    project_id,
    question
):

    response = ask_codebase(
        project_id,
        question
    )

    return response