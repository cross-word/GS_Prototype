"""P1 Standard World Model library built on the domain-neutral kernel."""

from .vocabulary import (
    ATTRIBUTE_BOOLEAN,
    ATTRIBUTE_DEF,
    ATTRIBUTE_NUMBER,
    ATTRIBUTE_REFERENCE,
    ATTRIBUTE_STRING,
    CONCEPT,
    ENTITY,
    INSTANCE_OF,
    LABEL,
    RELATED,
    RELATION_DEF,
    SUBTYPE_OF,
)
from .builders import add_boolean_attribute, add_number_attribute, add_reference_attribute, add_string_attribute, create_entity, define_attribute, define_concept
from .queries import labels_of
from .ontology import standard_ontology_rules
from .queries import boolean_attribute_values, concepts_of, instances_of, number_attribute_values, reference_attribute_values, string_attribute_values

__all__ = [
    "ATTRIBUTE_BOOLEAN", "ATTRIBUTE_DEF", "ATTRIBUTE_NUMBER",
    "ATTRIBUTE_REFERENCE", "ATTRIBUTE_STRING", "CONCEPT", "ENTITY",
    "INSTANCE_OF", "LABEL", "RELATED", "RELATION_DEF", "SUBTYPE_OF",
    "create_entity", "define_concept", "labels_of", "concepts_of", "instances_of", "standard_ontology_rules",
    "define_attribute", "add_number_attribute", "add_string_attribute", "add_boolean_attribute", "add_reference_attribute",
    "number_attribute_values", "string_attribute_values", "boolean_attribute_values", "reference_attribute_values",
]
