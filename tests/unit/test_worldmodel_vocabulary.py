from worldkernel import ArgumentKind
from worldmodel import ATTRIBUTE_NUMBER, CONCEPT, INSTANCE_OF, LABEL, RELATED


def test_standard_world_vocabulary_has_stable_names_and_argument_kinds() -> None:
    assert CONCEPT.name == "swm.Concept"
    assert CONCEPT.argument_kinds == (ArgumentKind.ID,)
    assert LABEL.argument_kinds == (ArgumentKind.ID, ArgumentKind.STRING)
    assert INSTANCE_OF.argument_kinds == (ArgumentKind.ID, ArgumentKind.ID)
    assert ATTRIBUTE_NUMBER.argument_kinds == (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.NUMBER)
    assert RELATED.argument_kinds == (ArgumentKind.ID, ArgumentKind.ID, ArgumentKind.ID)
