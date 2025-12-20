from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core.llm.prompts.sql_generator import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE
)
from core.llm.client import (
    load_schema_context,
    load_business_rules_context
)

# You will plug in the actual LLM later
def create_text_to_sql_chain(llm):
    schema_context = load_schema_context()
    business_rules = load_business_rules_context()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_PROMPT_TEMPLATE)
    ])

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    def run(question: str) -> str:
        return chain.invoke({
            "schema_context": schema_context,
            "business_rules": business_rules,
            "question": question
        }).strip()

    return run