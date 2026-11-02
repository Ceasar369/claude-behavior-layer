# Zero-turn

This local Claude Code mod formats results from hook-driven skills.
The project's Python hooks still perform the underlying actions.
When a hook completes a supported skill without a model turn,
the mod returns that completion as a normal tool result.

Install from this repository's local `layer-mods` marketplace.
From the repository root, run:

```sh
claude plugin marketplace add --scope local ./.claude/mods
claude plugin install --scope local zero-turn@layer-mods
```

The repository README explains setup and required permissions.
Restart Claude Code after installation.
This mod requires a Claude Code version supporting mods.
The release was validated with Claude Code 2.1.316.

The repository's MIT license applies.
