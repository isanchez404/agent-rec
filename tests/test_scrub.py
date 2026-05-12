from __future__ import annotations

from agent_rec.scrub import ScrubResult, scrub_text, scrub_value


def test_scrub_text_redacts_common_api_keys():
    text = "OPENAI_API_KEY=sk-abc1234567890abcdef and token ghp_abcdefghijklmnopqrstuvwxyz123456"

    result = scrub_text(text)

    assert isinstance(result, ScrubResult)
    assert "sk-abc" not in result.text
    assert "ghp_" not in result.text
    assert "[REDACTED:openai_key]" in result.text
    assert "[REDACTED:github_token]" in result.text
    assert result.redactions["openai_key"] == 1
    assert result.redactions["github_token"] == 1


def test_scrub_value_recurses_nested_structures():
    value = {
        "safe": "hello",
        "env": {"ANTHROPIC_API_KEY": "sk-ant-api03-abcdefghijklmnopqrstuvwxyz"},
        "lines": ["Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"],
    }

    result = scrub_value(value)

    assert result.value["safe"] == "hello"
    assert result.value["env"]["ANTHROPIC_API_KEY"] == "[REDACTED:secret_value]"
    assert result.value["lines"][0] == "Authorization: Bearer [REDACTED:bearer_token]"
    assert result.redactions["secret_value"] == 1
    assert result.redactions["bearer_token"] == 1
