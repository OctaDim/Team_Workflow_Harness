# Live Codex CLI invocation

Snapshot CLI version, profile, cwd, settings and plugins without secrets. Query `skills/list`. Keep configuration and installation fixed.

Run separate `codex exec --json` sessions per exact `plugin:skill` in that profile and cwd. Prompt with the name and a safe task revealing a procedure step. Omit paths and cache hints. Test listed, unlisted cached and known absent names alike. For absence use an existing basename under a missing owner if possible. Compare snapshots afterward.

Per name report version, profile, cwd, verbatim prompt, visibility, the intended owner's load event and concrete application in reply/actions. Require both. Exit 0, file presence or self-report alone cannot pass. Reject other owners and generic advice with observed reasons. Network, access or auth interruption means unverified.

Label confirmed fallback «по явному имени скилл применён через чтение из кэша». Native registration and plugin tools need independent evidence. Scope results to tested name, profile, cwd and invocation. Catalogue omission alone cannot justify requiring plugin installation.
