# Agent Notes

## Railway Deployment Checks

This repo deploys to Railway from GitHub.

Known Railway mapping:

- Project: `Telbin.dev Discord Bots`
- Environment: `production`
- Service: `Edvin`
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
2. In the `Edvin` service, check `latestDeployment.status` is `SUCCESS`.
3. Confirm `latestDeployment.meta.repo` is `Shiaulis/edvinBot`.
4. Confirm `latestDeployment.meta.branch` is `master`.
5. Confirm `latestDeployment.meta.commitHash` or `commitMessage` matches the pushed commit.
6. Confirm there is one running replica under `instances` or `replicas`.

If the folder is not linked, run the `railway link ...` command above before checking status. Railway CLI network calls may require approval in sandboxed Codex sessions.
