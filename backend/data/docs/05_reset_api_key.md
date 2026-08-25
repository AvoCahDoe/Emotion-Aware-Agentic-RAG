type: howto
# Reset your API key step by step

1. Open Settings → API Keys.
2. Click Revoke on the key you no longer trust — old keys stop working immediately.
3. Click Create key, copy it once, and store it in your secret manager.
4. Update your app’s NOVA_API_KEY environment variable.
5. Restart the app and call GET /health to confirm authentication works.
Never commit API keys to git.
