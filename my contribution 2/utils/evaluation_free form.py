import pandas as pd
from utils.load_data import wrap_input_for_demo
from utils.helper import *
from utils.evaluate import *
from utils.chain import *
from operations import *
from utils.LLAMA import Ollama

gpt_llm = Ollama(model_name="deepseek-v3.1:671b-cloud")  # or "llama3.2:1b", "qwen2.5:3b",,gemma3,gemma3:4b,:1b etc.,gpt-oss:120b-cloud
import pandas as pd
from collections import Counter
import asyncio
import pandas as pd

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

# OPTIONAL: If you have table2string available, it makes contexts nicer.
try:
    from utils.helper import table2string
except Exception:
    table2string = None


# ----------------------------------------------------
# 0) YOU MUST PROVIDE THESE (from your project)
# ----------------------------------------------------
# from your_project import (
#     wrap_input_for_demo,
#     dynamic_chain_exec_one_sample,
#     qa_query,
#     get_table_info,
#     gpt_llm,
# )
#
# NOTE:
# - gpt_llm is your generation model used by Chain-of-Table to answer
# - RAGAS judge LLM is Ollama (below)


# ----------------------------------------------------
# 1) Setup RAGAS judge LLM (Ollama)
# ----------------------------------------------------
judge_client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)

judge_llm = llm_factory(
    "deepseek-v3.1:671b-cloud",
    provider="openai",
    client=judge_client,
)

faithfulness = Faithfulness(llm=judge_llm)
context_precision = ContextPrecision(llm=judge_llm)     # needs reference
context_recall = ContextRecall(llm=judge_llm)           # needs reference
groundedness = ResponseGroundedness(llm=judge_llm)
answer_accuracy = AnswerAccuracy(llm=judge_llm)         # needs reference
exact_match = ExactMatch()                               # non-LLM exact match :contentReference[oaicite:2]{index=2}


# ----------------------------------------------------
# 2) Helpers
# ----------------------------------------------------
def normalize_reference(ref) -> str:
    """RAGAS expects reference as a string for these metrics."""
    if ref is None:
        return ""
    if isinstance(ref, list):
        # if you ever store multiple gold answers, join them
        return " | ".join(str(x) for x in ref)
    return str(ref).strip()


def table_as_context(row_dict) -> list[str]:
    """
    RAGAS expects retrieved_contexts: list[str].
    We'll treat the TABLE itself as the "retrieved context".
    """
    table_text = row_dict.get("table_text", "")
    caption = row_dict.get("table_caption", "")

    if isinstance(table_text, str):
        return [table_text]

    # If table_text is structured (list-of-lists), convert it.
    if table2string is not None:
        try:
            return [table2string(table_text, caption=caption)]
        except Exception:
            pass

    # Fallback stringify
    return [f"caption: {caption}\n{str(table_text)}"]


def extract_pred_answer_from_qa_query(output_sample) -> str:
    """
    Your qa_query() stores an operation:
      operation_name: "qa_query"
      parameter_and_conf: [(text, prob), ...]
    We take the top-1 text.
    """
    chain = output_sample.get("chain", [])
    qa_ops = [op for op in chain if op.get("operation_name") == "qa_query"]
    if not qa_ops:
        # fallback: return empty
        return ""
    last = qa_ops[-1]
    pac = last.get("parameter_and_conf", [])
    if not pac:
        return ""
    return str(pac[0][0]).strip()


async def ragas_score_one(user_input: str, response: str, reference: str, contexts: list[str]) -> dict:
    """
    Same 6 metrics as your earlier Ollama/RAGAS script, but now for QA.
    Uses keyword args as in RAGAS docs. :contentReference[oaicite:3]{index=3}
    """
    results = await asyncio.gather(
        faithfulness.ascore(
            user_input=user_input,
            response=response,
            retrieved_contexts=contexts,
        ),
        context_precision.ascore(
            user_input=user_input,
            reference=reference,
            retrieved_contexts=contexts,
        ),
        context_recall.ascore(
            user_input=user_input,
            reference=reference,
            retrieved_contexts=contexts,
        ),
        groundedness.ascore(
            response=response,
            retrieved_contexts=contexts,
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
    return {n: r.value for n, r in zip(names, results)}


# ----------------------------------------------------
# 3) Main evaluation (for your converted JSONL)
# ----------------------------------------------------
async def main():
    file_path = "/Users/fadisultan/PycharmProjects/my contribution 2/data/tabfact/846 all_free_form.jsonl"
    df = pd.read_json(file_path, lines=True)

    n_eval = min(1, len(df))
    print(f"Evaluating on  {(n_eval)} examples...")

    rows = []

    for idx in range(n_eval):
        row = df.iloc[idx].to_dict()

        # New schema:
        question = row["statement"]
        reference = normalize_reference(row["label"])  # label holds the gold ANSWER string now

        table_caption = row.get("table_caption", "")
        table_text = row.get("table_text", "")

        try:
            # --- Wrap input for Chain-of-Table ---
            demo_sample = wrap_input_for_demo(
                statement=question,          # your wrap function expects "statement"; we pass question text
                table_caption=table_caption,
                table_text=table_text,
            )

            # --- Run dynamic chain (your model that selects ops etc.) ---
            proc_sample, dynamic_chain_log = dynamic_chain_exec_one_sample(
                sample=demo_sample,
                llm=gpt_llm,statement=question,
            )

            # --- Final QA query (free-form answer) ---
            output_sample = qa_query(
                sample=proc_sample,
                table_info=get_table_info(proc_sample),
                llm=gpt_llm,
                use_demo=True,
                llm_options=gpt_llm.get_model_options(
                    temperature=1,
                    per_example_max_decode_steps=400,
                    per_example_top_p=1.0,
                ),
            )

            pred_answer = extract_pred_answer_from_qa_query(output_sample)

            # --- RAGAS contexts (table as evidence) ---
            contexts = table_as_context(row)

            # --- RAGAS scoring (Ollama judge) ---
            scores = await ragas_score_one(
                user_input=question,
                response=pred_answer,
                reference=reference,
                contexts=contexts,
            )

            rows.append(
                {
                    "idx": idx,
                    "question": question,
                    "reference": reference,
                    "pred_answer": pred_answer,
                    "item_type": row.get("item_type", ""),
                    "label_original": row.get("label_original", None),
                    **scores,
                }
            )

            #print(f"[{idx}] ExactMatch={scores['ExactMatch']} | pred='{pred_answer}' | #gold='{reference}'")

        except Exception as e:
            print(f"[ERROR] index {idx}: {e}")
            continue

    if not rows:
        print("No rows evaluated successfully.")
        return

    out_df = pd.DataFrame(rows)

    metric_cols = [
        "Faithfulness",
        "ContextPrecision",
        "ContextRecall",
        "ResponseGroundedness",
        "AnswerAccuracy",
        "ExactMatch",
    ]

    print("\n========== MEAN METRICS ==========")
    print(out_df[metric_cols].mean(numeric_only=True))

    out_path = "ragas_eval_freeform_qa_results.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved per-example results to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())  # This ensures the event loop runs correctly