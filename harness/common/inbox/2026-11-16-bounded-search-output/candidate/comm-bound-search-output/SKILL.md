---
name: comm-bound-search-output
description: Use before repository file discovery, text search or reading potentially large results to bound search scope and output entering agent context.
---

# Bound search output

Inputs: question, relevant scope, required completeness, available tools.

1. Select relevant paths and filename filters before searching. Follow current
   INDEX and archive-status owners; exclude README.human.md at every depth.
   Preserve mandatory complete instruction reads through bounded chunks.
2. Choose existence, count, filenames or text according to the question. Avoid
   whole-tree listings when a scoped query suffices; narrow automatically.
3. Before returning results to context, bound combined stdout/stderr: proposed
   defaults 8192 UTF-8 bytes and 100 result records per response, including
   summary. Enforce both before tool output, including long lines/paths.
   Tool token limits are an additional backstop, not proof of completeness.
4. On overflow return scope, applied filters, limits and an explicit incomplete
   marker with a bounded sample. Report totals only when actually counted.
   Continue by narrower queries or bounded pages; never infer absence from
   omitted results. Errors remain distinguishable from no matches.

Done: sufficient evidence for the question, bounded responses, disclosed gaps.
This guidance does not technically block other tools or direct shell commands.
