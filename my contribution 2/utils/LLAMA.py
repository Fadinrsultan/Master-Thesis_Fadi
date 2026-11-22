# utils/llm.py
import os
import time
import json
import numpy as np
import requests
import openai

# --- LLaMA-specific env vars MUST be set before importing llama_cpp ---
os.environ["GGML_METAL_LOG_LEVEL"] = "0"   # silence Metal logs on Mac
os.environ["LLAMA_LOG_LEVEL"] = "error"    # only real errors


#from llama_cpp import Llama as LlamaCpp


class ChatGPT:
    def __init__(self, model_name, key):
        self.model_name = model_name
        self.key = key

    def get_model_options(
        self,
        temperature=0,
        per_example_max_decode_steps=150,
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

        temperature = options.get("temperature", 0.0)
        max_tokens = options.get("max_tokens", 150)
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
class LlamaAPI:
    """
    Remote LLaMA wrapper over HTTP API, compatible with your existing interface.
    Default payload matches your Colab server example: {"text": prompt}.
    """

    def __init__(
        self,
        api_url: str,
        timeout: int = 120,
        headers: dict | None = None,
        max_retries: int = 2,
        backoff_seconds: float = 2.0,
        send_options: bool = False,   # IMPORTANT: keep False unless your server supports options
        max_prompt_chars: int | None = None,  # optional safety (avoid huge prompts causing OOM)
    ):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers  # let requests set json headers automatically if None
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.send_options = send_options
        self.max_prompt_chars = max_prompt_chars

    def get_model_options(
        self,
        temperature=0.0,
        per_example_max_decode_steps=150,
        per_example_top_p=1.0,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def _build_payload(self, prompt: str, options: dict, end_str: str | None) -> dict:
        # Optional prompt length guard (crude but effective against OOM for long CoTa prompts)
        if self.max_prompt_chars is not None and len(prompt) > self.max_prompt_chars:
            prompt = prompt[-self.max_prompt_chars:]  # keep tail (often contains the actual question)

        payload = {"text": prompt}

        # Only include generation params if your server explicitly supports them
        if self.send_options:
            payload.update(
                {
                    "temperature": float(options.get("temperature", 0.0)),
                    "max_tokens": int(options.get("max_tokens", 150)),
                    "top_p": float(options.get("top_p", 1.0)),
                    "stop": end_str,
                }
            )
        return payload

    def _post_once(self, payload: dict) -> str:
        r = requests.post(
            self.api_url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )

        # If error, surface server body to help debugging
        if not r.ok:
            body_preview = r.text[:2000]  # avoid dumping huge HTML
            raise requests.HTTPError(
                f"{r.status_code} Error for {r.url}\nServer response (first 2000 chars):\n{body_preview}",
                response=r,
            )

        # Ensure JSON and expected key
        try:
            data = r.json()
        except Exception:
            raise ValueError(f"Server did not return JSON. Body:\n{r.text[:2000]}")

        if "response" not in data:
            raise ValueError(f"JSON missing 'response'. Got: {data}")

        return data["response"]

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()

        n_sample = int(options.get("n", 1))
        results = []

        for i in range(n_sample):
            payload = self._build_payload(prompt, options, end_str)

            last_err = None
            text = None
            for attempt in range(self.max_retries + 1):
                try:
                    text = self._post_once(payload)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_seconds * (attempt + 1))

            if last_err is not None:
                raise last_err

            # Client-side stop (your server may not implement it)
            if end_str and isinstance(end_str, str) and end_str in text:
                text = text.split(end_str, 1)[0]

            fake_conf = (n_sample - i) / n_sample
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        return self.generate_plus_with_score(prompt, options, end_str)[0][0]

# --- Add this near your other imports ---
from huggingface_hub import InferenceClient


class HuggingFaceLLM:
    """
    Hugging Face hosted inference wrapper (InferenceClient) compatible with your interface.
    Uses text_generation() so it works with base models that support text-generation.
    """

    def __init__(
        self,
        model_name: str,
        hf_token: str | None = None,
        provider: str = "auto",
        timeout: int = 120,
    ):
        """
        model_name: e.g. "meta-llama/Llama-3.1-8B"
        hf_token: pass explicitly or set env var HF_TOKEN
        provider: "auto" or specific provider (e.g., "hf-inference")
        """
        self.model_name = model_name
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN is missing. Set it in environment or pass hf_token=...")

        # InferenceClient supports provider routing ("auto") and token auth
        self.client = InferenceClient(
            provider=provider,
            api_key=self.hf_token,
            timeout=timeout,
        )

    def get_model_options(
        self,
        temperature=0.9,
        per_example_max_decode_steps=150,
        per_example_top_p=1.0,
        n_sample=1,
    ):
        # NOTE: HF text_generation is typically single-sample per call; we loop for n_sample.
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        """
        Returns list of (text, log_score) like your other wrappers.
        """
        if options is None:
            options = self.get_model_options()

        temperature = float(options.get("temperature", 0.0))
        max_tokens = int(options.get("max_tokens", 150))
        top_p = float(options.get("top_p", 1.0))
        n_sample = int(options.get("n", 1))

        # HF text_generation stop parameter is "stop" in some backends; InferenceClient supports stop sequences.
        # We'll also do client-side stopping for safety.
        results = []
        for i in range(n_sample):
            text = self.client.text_generation(
                model=self.model_name,
                prompt=prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=[end_str] if end_str else None,
            )

            # client-side stop fallback
            if end_str and isinstance(end_str, str) and end_str in text:
                text = text.split(end_str, 1)[0]

            fake_conf = (n_sample - i) / n_sample
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        return self.generate_plus_with_score(prompt, options, end_str)[0][0]
# --- Add this near your other imports ---
import time
import numpy as np
from google import genai


class Gemini:
    """
    Google Gemini wrapper compatible with your existing LLM interface.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3-flash-preview",
        max_retries: int = 2,
        backoff_seconds: float = 2.0,
    ):
        if not api_key:
            raise ValueError("Gemini API key must be provided")

        self.api_key = api_key
        self.model_name = model_name
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        self.client = genai.Client(api_key=self.api_key)

    def get_model_options(
        self,
        temperature=0.0,
        per_example_max_decode_steps=30000,
        per_example_top_p=1.0,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def _generate_once(self, prompt: str, options: dict, end_str: str | None):
        resp = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "temperature": float(options.get("temperature", 0.0)),
                "top_p": float(options.get("top_p", 1.0)),
                "max_output_tokens": int(options.get("max_tokens", 30000)),
            },
        )

        text = getattr(resp, "text", None)
        if text is None:
            text = str(resp)

        if end_str and end_str in text:
            text = text.split(end_str, 1)[0]

        return text

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()

        n_sample = int(options.get("n", 1))
        results = []

        for i in range(n_sample):
            last_err = None

            for attempt in range(self.max_retries + 1):
                try:
                    text = self._generate_once(prompt, options, end_str)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_seconds * (attempt + 1))

            if last_err:
                raise last_err

            fake_conf = (n_sample - i) / n_sample
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        return self.generate_plus_with_score(prompt, options, end_str)[0][0]


class Ollama:
    """
    Ollama wrapper (local or Ollama Cloud)

    - Local default base URL: http://localhost:11434 (API lives under /api)
    - Cloud base URL: https://ollama.com/api
    """

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        headers: dict | None = None,
        max_retries: int = 5,
        backoff_seconds: float = 2.0,
        system_prompt: str | None = None,
        keep_alive: str | int | None = None,  # e.g. "5m" or 0
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.system_prompt = system_prompt
        self.keep_alive = keep_alive

        # If user passes .../api already, don't double-append
        if self.base_url.endswith("/api"):
            self.chat_url = f"{self.base_url}/chat"
        else:
            self.chat_url = f"{self.base_url}/api/chat"

    def get_model_options(
        self,
        temperature=0.0,
        per_example_max_decode_steps=150,
        per_example_top_p=1.0,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def _build_payload(self, prompt: str, options: dict, end_str: str | None) -> dict:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Ollama uses runtime generation settings inside "options"
        ollama_options = {
            "temperature": float(options.get("temperature", 0.0)),
            "top_p": float(options.get("top_p", 1.0)),
            # commonly used key for max new tokens in Ollama
            "num_predict": int(options.get("max_tokens", 150)),
        }

        # Stop sequences: send + also do client-side stop as fallback
        if end_str:
            ollama_options["stop"] = [end_str]

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": ollama_options,
        }

        if self.keep_alive is not None:
            payload["keep_alive"] = self.keep_alive

        return payload

    def _post_once(self, payload: dict) -> str:
        r = requests.post(
            self.chat_url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )

        if not r.ok:
            body_preview = r.text[:2000]
            raise requests.HTTPError(
                f"{r.status_code} Error for {r.url}\nServer response (first 2000 chars):\n{body_preview}",
                response=r,
            )

        try:
            data = r.json()
        except Exception:
            raise ValueError(f"Ollama did not return JSON. Body:\n{r.text[:2000]}")

        # Expected: {"message": {"content": "..."}}
        msg = data.get("message", {})
        text = msg.get("content", None)
        if text is None:
            raise ValueError(f"Unexpected Ollama response format: {data}")

        return text

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()

        n_sample = int(options.get("n", 1))
        results = []

        for i in range(n_sample):
            payload = self._build_payload(prompt, options, end_str)

            last_err = None
            text = None
            for attempt in range(self.max_retries + 1):
                try:
                    text = self._post_once(payload)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_seconds * (attempt + 1))

            if last_err is not None:
                raise last_err

            # client-side stop fallback
            if end_str and isinstance(end_str, str) and end_str in text:
                text = text.split(end_str, 1)[0]

            fake_conf = (n_sample - i) / n_sample
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        return self.generate_plus_with_score(prompt, options, end_str)[0][0]

class OllamaAPI:
    """
    Hosted Ollama API wrapper, compatible with the same interface style
    as your other LLM classes.

    Example endpoint:
        https://ollama.com/api/chat
    """

    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str = "https://ollama.com/api",
        timeout: int = 30,#120
        headers: dict | None = None,
        max_retries: int = 2,#5
        backoff_seconds: float = 1.0,#1
        system_prompt: str | None = None,
        keep_alive: str | int | None = None,
    ):
        if not api_key:
            raise ValueError("Ollama API key must be provided")

        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.system_prompt = system_prompt
        self.keep_alive = keep_alive

        self.headers = headers or {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # If user passes .../api already, use /chat under it.
        if self.base_url.endswith("/api"):
            self.chat_url = f"{self.base_url}/chat"
        else:
            self.chat_url = f"{self.base_url}/api/chat"

    def get_model_options(
        self,
        temperature=0.0,
        per_example_max_decode_steps=100,#150
        per_example_top_p=1.0,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def _build_payload(self, prompt: str, options: dict, end_str: str | None) -> dict:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(options.get("temperature", 0.0)),
                "top_p": float(options.get("top_p", 1.0)),
                "num_predict": int(options.get("max_tokens", 150)),
            },
        }

        if end_str:
            payload["options"]["stop"] = [end_str]

        if self.keep_alive is not None:
            payload["keep_alive"] = self.keep_alive

        return payload

    def _post_once(self, payload: dict) -> str:
        response = requests.post(
            self.chat_url,
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )

        if not response.ok:
            body_preview = response.text[:2000]#2000
            raise requests.HTTPError(
                f"{response.status_code} Error for {response.url}\n"
                f"Server response (first 2000 chars):\n{body_preview}",
                response=response,
            )

        try:
            data = response.json()
        except Exception:
            raise ValueError(f"Server did not return JSON. Body:\n{response.text[:2000]}")

        message = data.get("message", {})
        text = message.get("content")
        if text is None:
            raise ValueError(f"Unexpected Ollama API response format: {data}")

        return text

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()

        n_sample = int(options.get("n", 1))
        results = []

        for i in range(n_sample):
            payload = self._build_payload(prompt, options, end_str)

            last_err = None
            text = None

            for attempt in range(self.max_retries + 1):
                try:
                    text = self._post_once(payload)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_seconds * (attempt + 1))

            if last_err is not None:
                raise last_err

            # client-side stop fallback
            if end_str and isinstance(end_str, str) and end_str in text:
                text = text.split(end_str, 1)[0]

            fake_conf = (n_sample - i) / n_sample
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        return self.generate_plus_with_score(prompt, options, end_str)[0][0]