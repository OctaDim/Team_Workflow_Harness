# Storage, preparation and replacement

## Storage and identity

`rag/local_models/` is relative to the project root, never filesystem `/rag`
or `.venv`. Resolve its configured paths independently of the shell working
directory; respect existing configuration path semantics.

Git does not track empty directories. Retain the scaffold with this tracked
`rag/local_models/.gitignore`; exclude all downloaded companions, not just weights:

```gitignore
*
!.gitignore
```

Keep the tracked manifest outside that subtree, following the project's existing
configuration format. Record each role's source, immutable revision, exact files,
trusted SHA-256 values, format/quantization and compatible runtime/profile.
Include tokenizer, projector and other required companions. Keep credentials
in local configuration. A checksum calculated from an untrusted download alone
does not establish provenance. Missing inputs must be obtained, not invented.

Verify Git visibility of representative weights, JSON/tokenizers and nested files,
and visibility of the scaffold and manifest separately. Check actual tracking:
ignore rules do not remove previously indexed files. Never force-add weights.

## Preparation and startup

Prepare resources through an explicit setup/deployment command, separate from
ordinary `main`. Use pinned revisions, verified files and the existing dependency
lock and installer. Download to staging, verify the complete set before selection,
and reuse an existing set only after validating its identity. Keep model storage
independent of recreating the Python environment. Do not fetch mutable `latest`
or silently replace active files. Honor source licenses and access conditions.

Configure paths for the actual installation. Ordinary startup checks presence,
integrity and runtime compatibility; report a specific missing resource rather
than implicitly downloading it. A live process is not model/function readiness.
The production host or mounted persistent storage must provide the pinned set;
a Git checkout alone does not include weights. Network-free runtime is possible
after complete preparation.

## Replacement and evidence

Treat model changes as a coordinated release of code, manifest, profiles and tests.
Prepare the candidate alongside the current set. Update adapters, tokenizers,
prompts and projectors as needed; compare fixed representative tasks for quality,
correctness, latency and memory against explicit acceptance criteria. Check loading,
ordinary startup and affected functions on the target installation. Keep prior
artifacts, code/configuration and compatible data available for verified rollback.

For embedding changes evaluate document and query encoders, tokenizer, pooling,
normalization and vector dimension. Equal dimensions do not prove compatibility.
Recompute/reindex affected document vectors when the embedding space changes;
switch query encoder and matching index together. Obtain required data/schema
permissions before reindexing or migration. OCR/preprocessing changes may require
document reprocessing; determine this from the affected stored representations.

Record exact model identities, code version, tests and measured results, plus
pass/fail/not-run limits. Recommend promotion only for the verified scope.
Deployment, downloading, deleting old sets, transferring existing weights and
reindexing remain operations requiring their own applicable authorization.
