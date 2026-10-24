# Model Pricing Table

Official token pricing table for estimating API usage costs within the Ghost Audit LLM subsystem.

| Provider | Model | Input Price ($ / 1M tokens) | Output Price ($ / 1M tokens) | Input Price / Token | Output Price / Token |
|---|---|---|---|---|---|
| google | gemini-2.5-flash | $0.075 | $0.300 | $0.000000075 | $0.000000300 |
| google | gemini-2.0-flash | $0.100 | $0.400 | $0.000000100 | $0.000000400 |
| google | gemini-1.5-flash | $0.075 | $0.300 | $0.000000075 | $0.000000300 |
| google | gemini-1.5-pro | $1.250 | $5.000 | $0.000001250 | $0.000005000 |
| mock | mock-model | $0.000 | $0.000 | $0.000000000 | $0.000000000 |
| fallback | deterministic | $0.000 | $0.000 | $0.000000000 | $0.000000000 |

## Cost Calculation Rules
1. `Cost = (input_tokens * input_rate) + (output_tokens * output_rate)`.
2. Cache hits incur 0 external API cost.
3. Fallback / deterministic executions incur 0 external API cost.
4. Total costs are reconciled per-case and globally in the usage ledger.
