# Emotion-aware strategy comparison

Same factual intents asked with different emotional framing. Strategy labels come from the agent decision layer (`concise` / `scaffolded` / `standard`). Answer notes below are representative of expected behavior; re-run `python -m eval.run_comparison` against a live API to refresh verbatim outputs.

| Base intent | Framing | Expected emotion signal | Strategy | Answer character |
|---|---|---|---|---|
| Upload docs | Frustrated | anger / high arousal | concise | Short, reassuring; points to Upload -> Indexed |
| Upload docs | Confused | sadness / low confidence | scaffolded | Numbered steps 1–5 with jargon clarified |
| Upload docs | Curious | joy / surprise / neutral | standard | Balanced how-to overview |
| Reset API key | Frustrated | anger | concise | Direct revoke → create → restart |
| Reset API key | Confused | sadness | scaffolded | Safety-first walkthrough |
| Reset API key | Neutral | neutral | standard | Clear FAQ-style answer |
| Login help | Frustrated | anger | concise | Forgot password / SSO one-liner path |
| Login help | Confused | sadness | scaffolded | Password vs SSO decision tree |
| Billing → Pro | Frustrated | anger | concise | Settings → Billing → Upgrade |
| Billing → Pro | Confused | sadness | scaffolded | Upgrade, cancel, invoice explained |
| Wrong answers | Frustrated | anger / disgust | concise | Check Indexed + rephrase |
| Wrong answers | Confused | sadness | scaffolded | Causes listed as steps |
| Slack connect | Confused | sadness | scaffolded | OAuth steps expanded |
| Slack connect | Neutral | neutral | standard | Compact integration steps |
| Privacy | Curious | joy / surprise | standard | Retention windows + deletion |

## Why this matters

A static RAG pipeline would retrieve and phrase similarly for all rows. The agentic layer changes **retrieval top-k / doc-type preference** and **generation prompts** from the affective signal, and surfaces a one-line rationale for each choice (Explainable AI).

## Reproduce

```bash
# with backend running and DEEPSEEK_API_KEY set
cd backend
python -m eval.run_comparison --api http://localhost:8000
```
