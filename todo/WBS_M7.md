# M7 — Provider switching (optional)

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-032 | OpenAI adapter | Implement OpenAI client; share prompts; output normalization. | llm/openai.py; tests/test_openai_adapter.py | pytest -k openai_adapter | Adapter tests pass; env switch works. | backend,llm | 90 |
| T-033 | Anthropic adapter | Implement Claude client; normalize JSON; add tests. | llm/anthropic.py; tests/test_anthropic_adapter.py | pytest -k anthropic_adapter | Adapter tests pass; env switch works. | backend,llm | 90 |
| T-034 | Provider flag on reduce stage | Env flag to select provider for reduce; metrics split by provider. | pipeline/reduce_stage.py; api/config.py | make dev; run sample | A/B switch works; metrics reflect provider. | backend,llm,abtest | 60 |
