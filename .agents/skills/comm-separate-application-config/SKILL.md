---
name: comm-separate-application-config
description: Use when creating or changing application configuration, config templates, deployment settings, or Git exclusions for local configs.
---

# Separate application configuration

Inputs: configuration scope, existing loaders, ignore rules and Git state.
Preserve the project's format; example.toml/local.toml are naming examples.

1. Classify shared defaults and placeholder templates for Git; installation-specific
   settings and secrets for ignored local files. Addresses/paths are not inherently
   secrets. Keep public frontend settings separate from backend secrets.
2. Inspect existing loading/override precedence and tracked/staged paths without
   printing secrets. Create templates with placeholders; exclude exact local paths
   or bounded patterns without hiding shared configs/templates.
3. Document configuration sources, local overrides and missing-required-value errors.
   Keep backend secrets outside browser output and static-file serving roots;
   expose only explicitly selected public values. Never log secret values.
4. Check ignores with `git check-ignore -v --no-index -- path`; independently
   check tracking with `git ls-files --error-unmatch -- path`. Review staged changes
   locally without exposing secrets in reports.
5. Already tracked: .gitignore is insufficient. Obtain authority before removing
   only the named index entry while preserving its working file. Report prior
   secret exposure redacted; do not rewrite history or rotate credentials automatically.

Done: templates/shared defaults remain Git-visible; local files are ignored and
untracked; backend secrets remain private. Report paths, checks and unresolved
authorization/configuration gaps. Stop dependent changes when these are unresolved.
