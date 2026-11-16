---
name: comm-select-development-workflow
description: Use when an implementation task needs a workflow route menu or a reply to that menu needs interpretation.
---

# Confirm one workflow route

Inputs: operation, authorized scope, available skills, prior menu and user choice.
The current comm-confirm-development-workflow rule determines eligibility.
Analytics or an already unambiguous route need no new menu.

Before presenting routes read [menu](references/menu.md).
Before interpreting a reply read [choice](references/choice.md).
Show the required menu, ask for one route and wait; never choose automatically.
Apply only the confirmed route within its authorized scope.

Done: an unambiguous choice, or a precise question with dependent work stopped.
Other permissions and applicable instructions remain required.
