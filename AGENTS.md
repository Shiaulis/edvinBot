# Agent Notes

## Repo Shape

This is a small Python Discord bot. The app entrypoint is `main.py`; it defines one
`discord.py` slash command, `/raid-list`, which fetches Raid-Helper event JSON and
returns a tab-separated participant list as a `.txt` attachment.

Important files:

- `main.py` - bot logic, URL validation, Raid-Helper fetch, response formatting.
- `requirements.txt` - pinned Python dependencies.
- `railway.toml` - Railway build/start settings.
- `.env` - local secrets only; never commit it.

## Runtime

Required environment variable:

- `DISCORD_BOT_TOKEN`

Local setup:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```

The bot loads `.env` with `python-dotenv`, but Railway should provide
`DISCORD_BOT_TOKEN` through service variables.

## Change Guidelines

- Keep edits small and direct; this repo is intentionally a single-file bot.
- Preserve async `aiohttp` usage and the persistent client session on `RaidBot`.
- Be careful with Discord interaction timing: defer before network work and reply
  through `interaction.followup`.
- Treat user-provided URLs as untrusted. Keep Raid-Helper hostname validation strict
  and avoid broadening allowed domains without a clear reason.
- Do not log bot tokens, full environment dumps, or other secrets.
- Prefer adding focused pure-function tests if behavior starts growing; useful
  targets are `is_raid_helper_url`, `format_participants`, and `sanitize_filename`.

## Quick Checks

There is no committed test suite right now. At minimum, run a syntax check after
Python edits:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/edvinBot-pycache python3 -m py_compile main.py
```

The cache prefix keeps macOS Python from trying to write bytecode under
`~/Library/Caches`, which can fail in sandboxed sessions.

## Railway Deployment

This repo deploys to Railway from GitHub.

Known mapping:

- Workspace: `Telbin.dev`
- Project: `Telbin.dev Discord Bots`
- Environment: `production`
- Service: `Edvin`
- Service ID: `630f07aa-a2df-4b4a-a33d-14e0633f3d19`
- Source repo: `Shiaulis/edvinBot`
- Deploy branch: `master`

Useful commands:

```bash
railway whoami
railway project list --json
railway link --project 3e0b6f03-35b1-4737-b80f-2cef602c2a44 --environment production --service 630f07aa-a2df-4b4a-a33d-14e0633f3d19
railway status --json
railway service list --json
railway deployment list --json
```

How to verify a push deployed:

1. Run `railway status --json`.
2. Find the `production` environment and the `Edvin` service.
3. Confirm deployment metadata has `repo: Shiaulis/edvinBot` and
   `branch: master`.
4. Match `commitHash` or `commitMessage` to the pushed commit.
5. Prefer a deployment with `status: SUCCESS`, `deploymentStopped: false`, and a
   `RUNNING` instance under `instances`.
6. Check `activeDeployments`, not only `latestDeployment`; Railway can briefly
   report a stopped or in-progress latest deployment while the previous successful
   deployment is still the running one.

Railway CLI calls need network access and may require sandbox approval.
