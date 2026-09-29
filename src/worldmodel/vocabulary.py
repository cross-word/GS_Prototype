"""Fixed P1 relation vocabulary; player-defined vocabulary remains world data."""

from worldkernel import ArgumentKind, RelationSchema

CONCEPT = RelationSchema("swm.Concept", (ArgumentKind.ID,))
ENTITY = RelationSchema("swm.Entity", (ArgumentKind.ID,))
LABEL = RelationSchema("swm.Label", (ArgumentKind.ID, ArgumentKind.STRING))
INSTANCE_OF = RelationSchema("swm.InstanceOf", (ArgumentKind.ID, ArgumentKind.ID))
SUBTYPE_OF = RelationSchema("swm.SubtypeOf", (ArgumentKind.ID, ArgumentKind.ID))
ATTRIBUTE_DEF = RelationSchema("swm.AttributeDef", (ArgumentKind.ID,))
ATTRIBUTE_NUMBER = RelationSchema("swm.AttributeNumber", (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.NUMBER))
ATTRIBUTE_STRING = RelationSchema("swm.AttributeString", (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.STRING))
ATTRIBUTE_BOOLEAN = RelationSchema("swm.AttributeBoolean", (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.BOOLEAN))
ATTRIBUTE_REFERENCE = RelationSchema("swm.AttributeReference", (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.ID))
RELATION_DEF = RelationSchema("swm.RelationDef", (ArgumentKind.ID,))
RELATED = RelationSchema("swm.Related", (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.ID))
