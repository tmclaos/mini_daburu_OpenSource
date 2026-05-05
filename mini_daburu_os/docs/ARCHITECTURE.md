# Mini Daburu OS Architecture

The system is intentionally small.

```text
Goal
 -> AgentOS.observe()
 -> Planner chooses a Skill
 -> Skill returns ActionRequests
 -> ToolRegistry runs tools
 -> Verifier checks reality
 -> JsonlMemory stores episode
```

## Parts

- `AgentOS`: the operating loop.
- `Planner`: chooses the most relevant skill.
- `Skill`: reusable task recipe that emits generic tool actions.
- `Tool`: one real-world ability.
- `Verifier`: decides whether the agent may say the goal is done.
- `JsonlMemory`: append-only memory.

## How To Add A Tool

1. Create a class in `agent_os/tools/`.
2. Inherit from `Tool`.
3. Implement `async run(operation, **params)`.
4. Register it in `AgentOS.__init__`.

## How To Add A Skill

1. Create a class in `agent_os/skills/`.
2. Inherit from `Skill`.
3. Implement `can_handle(goal)` and `plan(goal, observation)`.
4. Add it to `DEFAULT_SKILLS`.

Skills should use generic tools. Avoid hardcoding a full website unless the
agent has already discovered that flow and saved it as a learned recipe.

## Human Checkpoints

Use `ActionResult(requires_human=True, checkpoint="...")` when a task reaches:

- CAPTCHA
- SMS code
- payment or spending
- irreversible deployment
- credentials the vault does not have

This keeps the agent autonomous without pretending it can safely cross every
boundary alone.
