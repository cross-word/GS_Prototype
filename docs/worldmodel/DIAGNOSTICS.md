# Diagnostics

Diagnostics are non-authoritative observations over evaluated snapshots. P1
emits a deterministic `subtype_cycle` warning for cyclic subtype structures;
it does not reject otherwise well-formed world patches or change truth status.
