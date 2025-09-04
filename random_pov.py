import random
import json

lyric_data = {
    "lyric_pov_types": [
        {
            "pov": "First-Person",
            "pronouns": ["I", "Me", "My", "We", "Us", "Our"],
            "sub_types": [
                "Confessional/Autobiographical",
                "Declarative/Statement of Intent",
                "Reflective/Introspective",
                "Narrative (First-Person Storyteller)",
                "Addressing a second person"
            ]
        },
        {
            "pov": "Second-Person",
            "pronouns": ["You", "Your"],
            "sub_types": [
                "Instructional/Advice",
                "Accusatory/Confrontational",
                "Conversational/Direct Address",
                "Narrative about another person"
            ]
        },
        {
            "pov": "Third-Person",
            "pronouns": ["He", "She", "It", "They", "Him", "Her", "Them"],
            "sub_types": [
                "Narrative/Storytelling",
                "Observational/Descriptive",
                "Social Commentary"
            ]
        },
        {
            "pov": "Impersonal",  # Changed from "Impersonal/No Clear POV"
            "pronouns": [],
            "sub_types": [
                "Abstract",  # Separate subtypes
                "Universal"
            ]
        }
    ]
}


def generate_random_pov():
    """Generates a random POV and sub-type from the lyric data."""

    pov_type = random.choice(lyric_data["lyric_pov_types"])
    pov = pov_type["pov"]

    if "sub_types" in pov_type and pov_type["sub_types"]:
        sub_type = random.choice(pov_type["sub_types"])
        return f"{pov} {sub_type}"
    else:
        return pov  # this should not happen now, Impersonal have subtypes


def generate_random_pov_separate():
    """Generates a random POV and sub-type separately."""
    pov_type = random.choice(lyric_data["lyric_pov_types"])
    pov = pov_type["pov"]
    sub_type = random.choice(pov_type["sub_types"]) if "sub_types" in pov_type and pov_type["sub_types"] else None
    return pov, sub_type