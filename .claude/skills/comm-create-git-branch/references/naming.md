# Branch naming

Format: <git-user>/<short-meaningful-name>. Use the current Git user's effective
repository email local part before @, without printing the address. Do not
substitute user.name or a hosting login. Missing/ambiguous email or invalid
derived prefix: ask for a short prefix and wait; never silently normalize it.

Choose a brief action, feature or outcome; never automatically copy a ticket
title. Common requires no Linear, ticket or ticket identifier.
Example: octadim/add-agent-use-some-tool.
Validate the literal full name with git check-ref-format --branch; do not accept
previous-checkout shorthand as the proposed literal name.
Check local and fresh intended-remote branch names. On collision warn, propose
another meaningful name and await explicit choice. Never overwrite, force-create
or invent a suffix. Recheck the chosen alternative and stop on creation races.
