# Session resources

Isolate independent contexts/profiles and conflicting ports where used; reuse
processes when isolation holds. Preserve intentional scenario state. Respect
caller settings; report conflicts, do not take another session.

Track ownership. Check live runs before restarting. Bound waits; try normal
closure, then only necessary authorized termination of proven owned processes.
No broad-name kills or foreign-profile deletion. Retain evidence; clean only
owned temporaries. Artifact creation, check outcome and process exit are distinct.
