from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from ..utils.endpoints import PROVIDER_DEFAULTS


@dataclass(frozen=True)
class ModelRuntimeEndpoint:
    """Resolved endpoint and credential data for one model provider."""

    provider: str
    api_key: str = ""
    base_url: str = ""
    api_key_source: str = ""
    base_url_source: str = ""

    @property
    def is_configured(self) -> bool:
        """Return whether this endpoint has a usable API key."""
        return bool(self.api_key)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    """Keep resolver code defensive around optional or malformed configs."""
    return value if isinstance(value, Mapping) else {}


def _read_config_value(config: Mapping[str, Any], paths: Iterable[Tuple[str, ...]]) -> Tuple[str, str]:
    """Read the first non-empty nested config value from a set of candidate paths."""
    for path in paths:
        current: Any = config
        for part in path:
            current = _as_mapping(current).get(part)
        if current is not None and str(current).strip():
            return str(current).strip(), ".".join(path)
    return "", ""


def resolve_model_runtime_endpoint(
    config: Optional[Mapping[str, Any]],
    provider: str,
    *,
    api_key_env: Optional[str] = None,
    base_url_env: Optional[str] = None,
    default_base_url: Optional[str] = None,
    extra_api_key_paths: Iterable[Tuple[str, ...]] = (),
    extra_base_url_paths: Iterable[Tuple[str, ...]] = (),
) -> ModelRuntimeEndpoint:
    """Resolve model credentials from adapter config first, then environment.

    The resolver intentionally accepts both `base_url` and `baseurl` spellings
    because production configuration often comes from mixed vendor examples.
    """
    cfg = _as_mapping(config)
    provider_key = provider.strip().upper()
    provider_lower = provider_key.lower()
    key_env = api_key_env or f"{provider_key}_API_KEY"
    url_env = base_url_env or f"{provider_key}_BASE_URL"

    api_key_paths = (
        ("api_key",),
        ("apikey",),
        (f"{provider_lower}_api_key",),
        ("auth", "api_key"),
        ("credentials", "api_key"),
        ("params", "api_key"),
        *tuple(extra_api_key_paths),
    )
    base_url_paths = (
        ("base_url",),
        ("baseurl",),
        ("endpoint",),
        ("api_base",),
        ("api_base_url",),
        (f"{provider_lower}_base_url",),
        ("params", "base_url"),
        ("params", "baseurl"),
        *tuple(extra_base_url_paths),
    )

    api_key, api_key_source = _read_config_value(cfg, api_key_paths)
    if not api_key:
        api_key = (os.getenv(key_env) or "").strip()
        api_key_source = key_env if api_key else ""

    base_url, base_url_source = _read_config_value(cfg, base_url_paths)
    if not base_url:
        base_url = (os.getenv(url_env) or "").strip()
        base_url_source = url_env if base_url else ""

    if not base_url:
        base_url = (default_base_url or PROVIDER_DEFAULTS.get(provider_key, "")).rstrip("/")
        base_url_source = "provider_default" if base_url else ""
    else:
        base_url = base_url.rstrip("/")

    return ModelRuntimeEndpoint(
        provider=provider_key,
        api_key=api_key,
        base_url=base_url,
        api_key_source=api_key_source,
        base_url_source=base_url_source,
    )


def endpoint_public_summary(endpoint: ModelRuntimeEndpoint) -> Dict[str, Any]:
    """Return non-secret endpoint metadata for diagnostics and tests."""
    return {
        "provider": endpoint.provider,
        "base_url": endpoint.base_url,
        "api_key_configured": endpoint.is_configured,
        "api_key_source": endpoint.api_key_source,
        "base_url_source": endpoint.base_url_source,
    }
