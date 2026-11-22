import time
import json
import os
import platform
import multiprocessing
import torch

from generation.generator import Generator
from worker_func import worker_annotate
from data_loading import wikitable, open_wikitable, feverous

ROOT_DIR = os.path.join(os.path.dirname(__file__), "../")


def main():
    # Set variables directly (no argparse)
    dataset = "open_wikitq"  # Change to 'wikitq' or 'feverous' as needed
    dataset_split = "validation"  # For validation set
    dataset_sub = 128
    dataset_chunk_idx = 0
    api_keys_file = "key.txt"
    prompt_file = "templates/prompts/wikitq.txt"
    save_dir = "results/"
    debug = False
    n_processes = 2
    gold_table = False
    multi_table_count = 2
    openai_api_key = "OPENAI_API_KEY"  # Replace with your actual API key
    multi_table_type = "random"  # Options: 'bm25' or 'random'
    bm25_rerank_rows = False
    ltm = False
    ltm_select = None
    one_by_one_idx = None
    rankgpt = False
    prompt_style = "create_table_select_3_full_table"  # Modify as needed
    generate_type = "sqlite"  # Options: 'answer', 'sql', 'sqlite', 'sqlite-verifier'
    n_shots = 14
    seed = 42
    engine = "gpt-3.5-turbo"  # Options: 'gpt-3.5-turbo', 'gpt-4', etc.
    n_parallel_prompts = 1
    max_generation_tokens = 512
    max_api_total_tokens = 8001
    temperature = 0.4
    sampling_n = 1
    top_p = 1.0
    stop_tokens = '\n\n'  # Modify if needed
    verbose = False

    # Check if the dataset_split is 'validation' (as the original code expects)
    assert dataset_split == 'validation'

    # Build paths
    api_keys_file = os.path.join(ROOT_DIR, api_keys_file)
    prompt_file = os.path.join(ROOT_DIR, prompt_file)
    save_dir = os.path.join(ROOT_DIR, save_dir)
    os.makedirs(save_dir, exist_ok=True)

    start_time = time.time()

    # Print the dataset path
    dataset_path = None
    if dataset == 'open_wikitq':
        dataset_path = os.path.join(ROOT_DIR, 'data/open_wikitq')  # Adjust based on where the dataset is stored
        print(f"Dataset path: {dataset_path}")
        dataset = open_wikitable(locals())
    elif dataset == 'wikitq':
        dataset_path = os.path.join(ROOT_DIR, 'data/wikitq')  # Adjust path accordingly
        print(f"Dataset path: {dataset_path}")
        assert gold_table
        dataset = wikitable(locals())
    elif dataset == 'feverous':
        dataset_path = os.path.join(ROOT_DIR, 'data/feverous')  # Adjust path accordingly
        print(f"Dataset path: {dataset_path}")
        dataset = feverous(locals())

    # Annotate
    generator = Generator(locals(), keys=None)
    generate_eids = list(range(len(dataset)))
    generate_eids_group = [[] for _ in range(n_processes)]
    for g_eid in generate_eids:
        generate_eids_group[int(g_eid) % n_processes].append(g_eid)
    print('\n******* Annotating *******')
    g_dict = dict()
    worker_results = []

    if debug:  # Debug mode
        for pid in range(n_processes):
            worker_results.append(worker_annotate(
                pid,
                locals(),
                generator,
                generate_eids_group[pid],
                dataset
            ))
        g_dict = worker_results[0]

    else:
        pool = multiprocessing.Pool(processes=n_processes)
        for pid in range(n_processes):
            worker_results.append(pool.apply_async(worker_annotate, args=(
                pid,
                locals(),
                generator,
                generate_eids_group[pid],
                dataset
            )))
        # Merge annotation results
        for r in worker_results:
            worker_g_dict = r.get()
            g_dict.update(worker_g_dict)
        pool.close()
        pool.join()

    acc_result = torch.tensor([g_dict[k]['pred_score'] for k in g_dict.keys()]).sum().item() / len(g_dict.keys())
    print(f'EM Acc:{acc_result:.4f}')
    print(f"Elapsed time: {time.time() - start_time}")

    g_dict.update({'EM_Acc': acc_result})

    # Print out the final results
    print("\nFinal Results:")
    for key, value in g_dict.items():
        print(f"{key}: {value}")

    # Save annotation results
    save_file_name = f'program_{dataset}_{dataset_split}.json'
    with open(os.path.join(save_dir, save_file_name), 'w') as f:
        json.dump(g_dict, f, indent=4)


if __name__ == '__main__':
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')

    main()
