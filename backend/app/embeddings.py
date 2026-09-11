"""Pluggable embedding adapters."""
import os
import hashlib
import math
from typing import List


class EmbeddingProvider:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError()


class DeterministicProvider(EmbeddingProvider):
    def __init__(self, dim: int = 32):
        self.dim = dim

    def embed(self, text: str):
        # deterministic pseudo-embedding from sha256
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        nums = [int(h[i:i+2], 16) for i in range(0, len(h), 2)]
        vec = [((n % 256) / 255.0) for n in nums]
        if len(vec) < self.dim:
            vec = (vec * ((self.dim // len(vec)) + 1))[:self.dim]
        else:
            vec = vec[:self.dim]
        return vec


class OpenAIProvider(EmbeddingProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

    def embed(self, text: str):
        # optional runtime dependency: openai
        try:
            import openai
        except Exception as e:
            raise RuntimeError('openai package not installed') from e
        if not self.api_key:
            raise RuntimeError('OPENAI_API_KEY not set')
        openai.api_key = self.api_key
        # Use text-embedding-3-small-like call if available; keep generic
        resp = openai.Embedding.create(input=text, model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small'))
        vec = resp['data'][0]['embedding']
        return vec


def get_provider(name: str | None = None) -> EmbeddingProvider:
    name = (name or os.getenv('EMBEDDING_PROVIDER', 'deterministic')).lower()
    if name == 'openai':
        return OpenAIProvider()
    return DeterministicProvider()
