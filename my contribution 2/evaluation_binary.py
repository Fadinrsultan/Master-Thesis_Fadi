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

# ----------------------------------------------------
# 1. Load JSONL
# ----------------------------------------------------
file_path = "/Users/fadisultan/PycharmProjects/my contribution 2/data/tabfact/846_all_binary_corrected.jsonl"

df = pd.read_json(file_path, lines=True)

# how many to evaluate
n_eval = min(1, len(df))

#print(f"Evaluating on first {n_eval} examples...")
print(f"Evaluating on  {(n_eval)} examples...")

# ----------------------------------------------------
# 2. Helper: map CoTable log to 0/1 label
# ----------------------------------------------------
import re

def recall(cotable_log):
    """
    Return 1 if the last Chain-of-Table result contains the word 'yes'
    (case-insensitive), else 0.
    If log is empty or malformed, return 0.
    """

    if not cotable_log or not isinstance(cotable_log, list):
        return 0

    last = cotable_log[-1]
    if not isinstance(last, dict):
        return 0

    result = last.get("cotable_result", "")
    if not isinstance(result, str):
        return 0

    return 1 if re.search(r"\bYES\b", result, re.IGNORECASE) else 0




# ----------------------------------------------------
# 3. Evaluation loop
# ----------------------------------------------------
gold_labels = []
pred_labels = []

for idx in range(n_eval):
    row = df.iloc[idx]
    sample_pre = row.to_dict()

    statement = sample_pre["statement"]
    table_caption = sample_pre["table_caption"]
    table_text = sample_pre["table_text"]
    gold_label = int(sample_pre["label"])

    try:
        # --- Wrap input for Chain-of-Table ---
        demo_sample = wrap_input_for_demo(
            statement=statement,
            table_caption=table_caption,
            table_text=table_text,
        )

        # --- Run dynamic chain ---
        proc_sample, dynamic_chain_log = dynamic_chain_exec_one_sample(statement,
            sample=demo_sample,
            llm=gpt_llm,
        )
        #print(proc_sample)
        # --- Query final answer ---
        output_sample = simple_query(
            sample=proc_sample,
            table_info=get_table_info(proc_sample),
            llm=gpt_llm,
            use_demo=True,
            llm_options=gpt_llm.get_model_options(
                temperature=0.0,
                per_example_max_decode_steps=500,
                per_example_top_p=1.0,
            ),
        )

        # --- Extract chain-of-table result & map to 0/1 ---
        cotable_log = get_table_log(output_sample)
        #print("co:",cotable_log[-1])
        #print("cotable_log_result:",cotable_log[-1]['cotable_result'])
        pred_label = recall(cotable_log)

    except Exception as e:
        print(f"[ERROR] index {idx}: {e}")
        # you can choose to skip or treat as wrong; here we skip
        continue

    gold_labels.append(gold_label)
    pred_labels.append(pred_label)
    #print("gold_label:",gold_label)
    #print("pred_label:",pred_label)

    if (idx + 1) % 10 == 0:
        print(f"Processed {(idx)+ 1}/{(n_eval)} examples...")


# ----------------------------------------------------
# 4. Compute metrics
# ----------------------------------------------------
def safe_div(a, b):
    return a / b if b != 0 else 0.0

total = len(gold_labels)
correct = sum(int(g == p) for g, p in zip(gold_labels, pred_labels))
accuracy = safe_div(correct, total)

print("\n========== EVALUATION RESULTS ==========")
print(f"Evaluated examples: {(total)}")
print(f"Accuracy: {accuracy:.4f}")

# Confusion matrix
counts = Counter(zip(gold_labels, pred_labels))
tn = counts[(0, 0)]
fp = counts[(0, 1)]
fn = counts[(1, 0)]
tp = counts[(1, 1)]

print("\nConfusion matrix (gold × predicted):")
print(f"  TN (0→0): {tn}")
print(f"  FP (0→1): {fp}")
print(f"  FN (1→0): {fn}")
print(f"  TP (1→1): {tp}")

# Metrics for class 1 (TRUE)
precision = safe_div(tp, tp + fp)
recall_metric = safe_div(tp, tp + fn)
f1 = safe_div(2 * precision * recall_metric, precision + recall_metric) if (precision + recall_metric) > 0 else 0.0

print("\nMetrics for label=1 (TRUE):")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall_metric:.4f}")
print(f"  F1-score:  {f1:.4f}")
print("========================================")
