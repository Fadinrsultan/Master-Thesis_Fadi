# utils/llm.py

import os
import time
import numpy as np
import openai

# --- LLaMA-specific env vars MUST be set before importing llama_cpp ---
os.environ["GGML_METAL_LOG_LEVEL"] = "0"   # silence Metal logs on Mac
os.environ["LLAMA_LOG_LEVEL"] = "error"    # only real errors

from llama_cpp import Llama as LlamaCpp


class ChatGPT:
    def __init__(self, model_name, key):
        self.model_name = model_name
        self.key = key

    def get_model_options(
        self,
        temperature=0,
        per_example_max_decode_steps=256,
        per_example_top_p=1,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        messages = [
            {
                "role": "system",
                "content": "I will give you some examples, you need to follow the examples and complete the text, and no other content.",
            },
            {"role": "user", "content": prompt},
        ]
        gpt_responses = None
        retry_num = 0
        retry_limit = 2
        error = None
        while gpt_responses is None:
            try:
                gpt_responses = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    stop=end_str,
                    api_key=self.key,
                    **options
                )
                error = None
            except Exception as e:
                print(str(e), flush=True)
                error = str(e)
                if "This model's maximum context length is" in str(e):
                    print(e, flush=True)
                    gpt_responses = {
                        "choices": [{"message": {"content": "PLACEHOLDER"}}]
                    }
                elif retry_num > retry_limit:
                    error = "too many retry times"
                    gpt_responses = {
                        "choices": [{"message": {"content": "PLACEHOLDER"}}]
                    }
                else:
                    time.sleep(60)
                retry_num += 1
        if error:
            raise Exception(error)
        results = []
        for i, res in enumerate(gpt_responses["choices"]):
            text = res["message"]["content"]
            fake_conf = (len(gpt_responses["choices"]) - i) / len(
                gpt_responses["choices"]
            )
            results.append((text, np.log(fake_conf)))
        #print("hi , i had been used")
        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        result = self.generate_plus_with_score(prompt, options, end_str)[0][0]
        return result


class Llama:
    """
    Local LLaMA model wrapper with the same interface as ChatGPT.
    Uses llama_cpp and a local .gguf model.
    """

    def __init__(
        self,
        model_path,
        n_ctx=2048,
        **llama_kwargs,
    ):
        """
        model_path: path to your .gguf file
        n_ctx: context window size (tokens)
        llama_kwargs: any extra kwargs to pass to llama_cpp.Llama
        """
        self.model_path = model_path
        self.n_ctx = n_ctx

        self.llm = LlamaCpp(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            verbose=False,
            **llama_kwargs,
        )

    def get_model_options(
        self,
        temperature=0.0,
        per_example_max_decode_steps=150,
        per_example_top_p=1.0,
        n_sample=1,
    ):
        """
        Same signature as ChatGPT.get_model_options so you can reuse
        the same code.
        """
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        """
        Mimic ChatGPT.generate_plus_with_score:
        returns a list of (text, log_score) tuples.
        """
        if options is None:
            options = self.get_model_options()

        temperature = options.get("temperature", 0.9)
        max_tokens = options.get("max_tokens", 300)
        top_p = options.get("top_p", 1.0)
        n_sample = options.get("n", 1)

        stop = [end_str] if end_str else None

        results = []
        for i in range(n_sample):
            resp = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                echo=False,
            )
            # llama_cpp response format: resp["choices"][0]["text"]
            text = resp["choices"][0]["text"]

            # Fake confidence, same trick as in ChatGPT wrapper
            fake_conf = (n_sample - i) / n_sample
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        """
        Simple wrapper: return only the first text, like ChatGPT.generate.
        """
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        result = self.generate_plus_with_score(prompt, options, end_str)[0][0]
        return result
