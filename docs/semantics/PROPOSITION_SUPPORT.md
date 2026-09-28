# Proposition and Support Semantics v0

## Core model
A proposition is separate from the evidence/support for or against it.

```text
Proposition P
  ├─ positive supports
  └─ negative supports
```

## Four effective statuses
Given currently active, non-defeated supports:

| Positive | Negative | Status |
|---|---|---|
| no | no | UNKNOWN |
| yes | no | TRUE_ONLY |
| no | yes | FALSE_ONLY |
| yes | yes | CONFLICT |

`UNKNOWN` is not false.

## Open-world default
The kernel is open-world by default. Absence of positive support does not create negative support.

Closed-world behavior may later be introduced at relation/module level, but it is not the global P0 default.

## Explicit negation vs negation-as-failure
P0 supports explicit polarity:
```text
positive support for P
negative support for P
```

P0 does not treat "P is not known" as equivalent to negative support for P.

Negation-as-failure / `NOT_KNOWN` is deferred until a later milestone because it introduces non-monotonic reasoning beyond DEFAULT handling.

## Contradiction policy
CONFLICT is a valid semantic state. It does not invalidate the world and does not cause classical explosion.

Positive rules may use active positive support even when negative support also exists. Negative-premise rules may analogously use active negative support. This can propagate a contradiction, but never derive unrelated arbitrary propositions.

## Support kinds
Minimum conceptual support kinds:
- direct / asserted;
- derived;
- default-derived.

Implementation may represent these with richer origin metadata.

## Multiple justification paths
A proposition may have multiple supports of the same polarity. Removing one support path must not change effective status while another active support remains.

Example:
```text
Bird(Toto) -> Animal(Toto)
Penguin(Toto) -> Animal(Toto)
```
Removing the Bird support does not remove Animal if the Penguin derivation remains valid.

## Retraction
Retraction targets support, not abstract truth. A derived support is removed when its justification becomes invalid, while unrelated supports remain.

## Default defeat
A conflicting ordinary/direct/derived support defeats a contrary DEFAULT support for effective evaluation. The defeated default support should remain recorded for explanation.

Example:
```text
DEFAULT Bird(x) -> +CanFly(x)
DERIVE Penguin(x) -> -CanFly(x)
```
For Pingu who is both Bird and Penguin, the positive default is defeated and effective status becomes FALSE_ONLY unless another active non-default positive support exists.

If both positive and negative non-default supports exist, effective status is CONFLICT.

## Provenance requirement
Every support must record enough information to answer:
- where did it come from?
- which rule, if any, produced it?
- which supports/premises justified it?
- in which revision was it created/removed/defeated?
