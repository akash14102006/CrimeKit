"""
Blockchain configuration for CrimeKit.

All settings are loaded from environment variables with sensible defaults.
No PII is ever stored on-chain.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class BlockchainConfig(BaseSettings):
    """Pydantic settings for the blockchain anchoring layer."""

    model_config = {"env_prefix": "BLOCKCHAIN_", "env_file": ".env", "extra": "ignore"}

    enabled: bool = Field(default=False, alias="BLOCKCHAIN_ENABLED")
    network: str = Field(default="polygon-amoy", alias="BLOCKCHAIN_NETWORK")
    chain_id: int = Field(default=80002, alias="BLOCKCHAIN_CHAIN_ID")
    rpc_url: str = Field(default="", alias="BLOCKCHAIN_RPC_URL")
    contract_address: str | None = Field(default=None, alias="BLOCKCHAIN_CONTRACT_ADDRESS")
    private_key: str | None = Field(default=None, alias="BLOCKCHAIN_PRIVATE_KEY")
    issuer_id: str = Field(default="", alias="BLOCKCHAIN_ISSUER_ID")
    batch_size: int = Field(default=128, alias="BLOCKCHAIN_BATCH_SIZE")
    anchor_interval_seconds: int = Field(default=300, alias="BLOCKCHAIN_ANCHOR_INTERVAL_SECONDS")
    max_pending: int = Field(default=10000, alias="BLOCKCHAIN_MAX_PENDING")
    max_retries: int = Field(default=5, alias="BLOCKCHAIN_MAX_RETRIES")
    protocol_version: int = Field(default=1, alias="BLOCKCHAIN_PROTOCOL_VERSION")
    explorer_url: str | None = Field(default=None, alias="BLOCKCHAIN_EXPLORER_URL")

    @property
    def is_configured(self) -> bool:
        """Return True when the adapter has enough config to operate."""
        return bool(self.rpc_url and self.contract_address)


_settings: BlockchainConfig | None = None


def get_blockchain_config() -> BlockchainConfig:
    """Return the singleton blockchain config, creating it on first call."""
    global _settings
    if _settings is None:
        _settings = BlockchainConfig()
    return _settings
