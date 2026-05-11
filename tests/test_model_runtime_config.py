from src.models.runtime_config import endpoint_public_summary, resolve_model_runtime_endpoint


def test_runtime_endpoint_prefers_explicit_config_over_env(monkeypatch):
    """Adapter configs must isolate model calls from global env defaults."""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "env-key")
    monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://env.example.com")

    endpoint = resolve_model_runtime_endpoint(
        {"api_key": "config-key", "baseurl": "https://config.example.com/"},
        "DASHSCOPE",
    )

    assert endpoint.api_key == "config-key"
    assert endpoint.base_url == "https://config.example.com"
    assert endpoint.api_key_source == "api_key"
    assert endpoint.base_url_source == "baseurl"


def test_runtime_endpoint_falls_back_to_provider_env(monkeypatch):
    """Providers can be configured by {PROVIDER}_API_KEY and {PROVIDER}_BASE_URL."""
    monkeypatch.setenv("VIDU_API_KEY", "vidu-key")
    monkeypatch.setenv("VIDU_BASE_URL", "https://vidu.internal/v2")

    endpoint = resolve_model_runtime_endpoint({}, "VIDU")

    assert endpoint.api_key == "vidu-key"
    assert endpoint.base_url == "https://vidu.internal/v2"
    assert endpoint.is_configured is True


def test_runtime_endpoint_public_summary_never_exposes_secret(monkeypatch):
    """Diagnostics may expose sources and base URL, but never the key value."""
    monkeypatch.setenv("OPENAI_API_KEY", "secret-openai-key")
    endpoint = resolve_model_runtime_endpoint({}, "OPENAI")

    summary = endpoint_public_summary(endpoint)

    assert summary["api_key_configured"] is True
    assert "secret-openai-key" not in str(summary)
    assert summary["base_url"] == "https://api.openai.com/v1"
