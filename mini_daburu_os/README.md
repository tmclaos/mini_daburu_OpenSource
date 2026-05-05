# Mini Daburu OS

A small Agent OS inspired by DaburuChan, but intentionally minimal.

The design goal is not to hard-code every website or every thought. The goal is
to provide a clean operating loop, generic tools, memory, verification, and
skills that the agent can reuse and improve.

## Mental Model

```text
Goal
 -> Observe
 -> Plan
 -> Act with tools
 -> Verify reality
 -> Remember
 -> Continue or ask for help
```

## Body Map

- Brain: `agent_os/loop.py`, `agent_os/planner.py`
- Spinal cord: `agent_os/schemas.py`, `agent_os/tools/registry.py`
- Hands: `agent_os/tools/browser.py`, `agent_os/tools/files.py`, `agent_os/tools/shell.py`, `agent_os/tools/deploy.py`
- Voice: `agent_os/tools/email_tool.py`
- Wallet: `agent_os/tools/vault.py`
- Accountant: `agent_os/tools/monitor.py`
- Memory: `agent_os/memory/jsonl_memory.py`
- Skills: `agent_os/skills/`
- Reality check: `agent_os/verifier.py`

## Run

From this folder:

```powershell
python -m agent_os.cli run "create account on vercel.com using test@example.com"
```

Useful examples:

```powershell
python -m agent_os.cli run "deploy ./demo-app to vercel"
python -m agent_os.cli run "check uptime for https://example.com"
python -m agent_os.cli memory
python -m agent_os.cli tools
```

## Boundaries

The browser tool can navigate, click, type, and read the page when Playwright is
installed. It does not bypass CAPTCHA or anti-abuse checks. Those become human
checkpoints.

The vault is a local development vault. It avoids logging secret values, but it
is not a production-grade encrypted secret manager. Replace it with OS keychain,
1Password, Bitwarden, or cloud secret storage for real money/production work.

## Why This Is Smaller Than DaburuChan

DaburuChan mixed many research systems together. This project keeps the stable
core small and lets capability grow through tools and skills.

```text
Small stable core
 + generic tools
 + reusable skills
 + verification
 = much easier to make autonomous without making a mess
```
