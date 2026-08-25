type: faq
# Rate limits

Free workspaces allow 100 queries per day. Pro workspaces allow 5,000 queries per day. Hitting the limit returns HTTP 429 with a retry-after header. Limits reset at 00:00 UTC. Burst traffic may temporarily throttle even under the daily cap.
