# COST & CACHING POLICY

## Token budgets
- Map: max_tokens=700, temperature=0.2
- Reduce: max_tokens=1200, temperature=0.2

## Modeling
- Map: fast tier; Reduce: HQ tier only
- Provider: default Azure OpenAI; switchable via env

## Cache
- Key: `videoId|lang|modelTier|promptVer|chunking`
- TTL: 14 days
- Bypass cache when prompt/model version changes

## Alerts
- Log warn if estimated cost/run exceeds target
