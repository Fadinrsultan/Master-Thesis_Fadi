import pandas as pd
from utils.load_data import wrap_input_for_demo
from utils.helper import *
from utils.evaluate import *
from utils.chain import *
from operations import *
from utils.LLAMA import OllamaAPI
from utils.llm import ChatGPT


# Initialize the Ollama API client
gpt_llm = OllamaAPI(
    model_name="deepseek-v3.1:671b",
    api_key="c378cdd226bc4e4e97e7b645ddc00e88.tG-EakUly5w1hVh0f-EUKnan"
)
model_name: str = "gpt-4o-mini"
openai_api_key:str="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"
gpt_llm = ChatGPT(
    model_name=model_name,
    key=openai_api_key,
)

def process_query(statement: str, file_path: str):
    """
    Process a given statement with a machine learning model using a dataset.

    :param statement: The query or statement to be processed.
    :param file_path: Path to the dataset in JSON format.
    :return: The processed answer from the model.
    """
    # Load the dataset
    df = pd.read_json(file_path, lines=True)
    target_row = 0  # zero-based index
    row = df.iloc[target_row]
    sample_pre = row.to_dict()

    table_caption = 'nvidia facts'

    # Wrap the input for demo
    demo_sample = wrap_input_for_demo(
        statement=statement, table_caption=table_caption, table_text=sample_pre['table_text']
    )

    # Run the dynamic chain to process the sample
    proc_sample, dynamic_chain_log = dynamic_chain_exec_one_sample(
        sample=demo_sample, llm=gpt_llm, statement=statement
    )

    # Run the query against the table
    output_sample = qa_query(
        sample=proc_sample,
        table_info=get_table_info(proc_sample),
        llm=gpt_llm,
        use_demo=True,
        llm_options=gpt_llm.get_model_options(
            temperature=1, per_example_max_decode_steps=600, per_example_top_p=1.0
        ),
    )

    # Extract the result
    cotable_log = get_table_log(output_sample)
    return cotable_log[-1]['cotable_result']
x=process_query('how much was nvidia revenue in fiscal year 2017 and 2018 , i need for each year seperatly ?',"/Users/fadisultan/Desktop/FADI_SULTAN/my contribution 2/data/tabfact/execution_sample.jsonl")
print(x)