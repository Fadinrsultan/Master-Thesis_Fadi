import asyncio
from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    ContextPrecision,
    ContextRecall,
    ResponseGroundedness,
    AnswerAccuracy,
    ExactMatch,
)

# Ollama exposes an OpenAI-compatible API at /v1
# so we point the OpenAI client to Ollama's base_url.
client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)

# Ragas LLM wrapper using the OpenAI-compatible client (Ollama)
llm = llm_factory("ministral-3:3b-cloud", provider="openai", client=client)

# Metrics (LLM-based)
faithfulness = Faithfulness(llm=llm)
context_precision = ContextPrecision(llm=llm)      # needs reference
context_recall = ContextRecall(llm=llm)            # needs reference
groundedness = ResponseGroundedness(llm=llm)
answer_accuracy = AnswerAccuracy(llm=llm)          # needs reference

# Metric (non-LLM)
exact_match = ExactMatch()

async def evaluate():
    user_input = "When was the first Super Bowl?"
    response = "The first Super Bowl was held on Jan 15, 1967."
    reference = "The first Super Bowl was played on January 15, 1967."
    retrieved_contexts = [
        "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
    ]

    results = await asyncio.gather(
        faithfulness.ascore(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts,
        ),
        context_precision.ascore(
            user_input=user_input,
            reference=reference,
            retrieved_contexts=retrieved_contexts,
        ),
        context_recall.ascore(
            user_input=user_input,
            reference=reference,
            retrieved_contexts=retrieved_contexts,
        ),
        groundedness.ascore(
            response=response,
            retrieved_contexts=retrieved_contexts,
        ),
        answer_accuracy.ascore(
            user_input=user_input,
            response=response,
            reference=reference,
        ),
        exact_match.ascore(
            reference=reference,
            response=response,
        ),
    )

    names = [
        "Faithfulness",
        "ContextPrecision",
        "ContextRecall",
        "ResponseGroundedness",
        "AnswerAccuracy",
        "ExactMatch",
    ]

    for name, r in zip(names, results):
        print(f"{name}: {r.value}")

if __name__ == "__main__":
    asyncio.run(evaluate())
