"""
Legal Knowledge Base Service
-----------------------------
Built-in IPC/BNS section reference data.
Provides section descriptions, bail status, punishment details.
"""

# Common IPC sections found in Kerala FIRs
IPC_SECTIONS = {
    "294": {"description": "Obscene acts and songs", "offense_type": "Public nuisance", "cognizable": True, "bailable": True, "punishment": "Up to 3 months imprisonment, or fine, or both"},
    "294(b)": {"description": "Sings, recites or utters any obscene song, ballad or words in or near any public place", "offense_type": "Public nuisance", "cognizable": True, "bailable": True, "punishment": "Up to 3 months imprisonment, or fine, or both"},
    "302": {"description": "Murder", "offense_type": "Murder", "cognizable": True, "bailable": False, "punishment": "Death or imprisonment for life, and fine"},
    "304": {"description": "Culpable homicide not amounting to murder", "offense_type": "Homicide", "cognizable": True, "bailable": False, "punishment": "Imprisonment for life, or up to 10 years, and fine"},
    "307": {"description": "Attempt to murder", "offense_type": "Attempt to murder", "cognizable": True, "bailable": False, "punishment": "Up to 10 years imprisonment, and fine"},
    "323": {"description": "Voluntarily causing hurt", "offense_type": "Assault", "cognizable": True, "bailable": True, "punishment": "Up to 1 year imprisonment, or fine up to Rs 1000, or both"},
    "324": {"description": "Voluntarily causing hurt by dangerous weapons or means", "offense_type": "Assault with weapon", "cognizable": True, "bailable": False, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "341": {"description": "Wrongful restraint", "offense_type": "Restraint", "cognizable": False, "bailable": True, "punishment": "Up to 1 month imprisonment, or fine up to Rs 500, or both"},
    "354": {"description": "Assault or criminal force to woman with intent to outrage her modesty", "offense_type": "Sexual offense", "cognizable": True, "bailable": False, "punishment": "1 to 5 years imprisonment, and fine"},
    "376": {"description": "Rape", "offense_type": "Sexual offense", "cognizable": True, "bailable": False, "punishment": "7 years to life imprisonment, and fine"},
    "379": {"description": "Theft", "offense_type": "Theft", "cognizable": True, "bailable": False, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "380": {"description": "Theft in dwelling house", "offense_type": "Theft", "cognizable": True, "bailable": False, "punishment": "Up to 7 years imprisonment, and fine"},
    "392": {"description": "Robbery", "offense_type": "Robbery", "cognizable": True, "bailable": False, "punishment": "Up to 10 years rigorous imprisonment, and fine"},
    "395": {"description": "Dacoity", "offense_type": "Dacoity", "cognizable": True, "bailable": False, "punishment": "Up to life imprisonment, and fine"},
    "406": {"description": "Criminal breach of trust", "offense_type": "Breach of trust", "cognizable": False, "bailable": True, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "420": {"description": "Cheating and dishonestly inducing delivery of property", "offense_type": "Cheating", "cognizable": True, "bailable": False, "punishment": "Up to 7 years imprisonment, and fine"},
    "427": {"description": "Mischief causing damage to amount of fifty rupees or upwards", "offense_type": "Property damage", "cognizable": True, "bailable": True, "punishment": "Up to 2 years imprisonment, or fine, or both"},
    "447": {"description": "Criminal trespass", "offense_type": "Trespass", "cognizable": False, "bailable": True, "punishment": "Up to 3 months imprisonment, or fine up to Rs 500, or both"},
    "448": {"description": "House-trespass", "offense_type": "Trespass", "cognizable": True, "bailable": True, "punishment": "Up to 1 year imprisonment, or fine up to Rs 1000, or both"},
    "506": {"description": "Criminal intimidation", "offense_type": "Intimidation", "cognizable": False, "bailable": True, "punishment": "Up to 2 years imprisonment, or fine, or both"},
}

# BNS (Bharatiya Nyaya Sanhita) sections - new criminal code
BNS_SECTIONS = {
    "100": {"description": "Murder", "offense_type": "Murder", "cognizable": True, "bailable": False, "punishment": "Death or imprisonment for life, and fine"},
    "103": {"description": "Murder", "offense_type": "Murder", "cognizable": True, "bailable": False, "punishment": "Death or imprisonment for life, and fine"},
    "109": {"description": "Attempt to murder", "offense_type": "Attempt to murder", "cognizable": True, "bailable": False, "punishment": "Up to 10 years imprisonment, and fine"},
    "115": {"description": "Voluntarily causing hurt", "offense_type": "Assault", "cognizable": True, "bailable": True, "punishment": "Up to 1 year imprisonment, or fine, or both"},
    "115(2)": {"description": "Voluntarily causing hurt (grave)", "offense_type": "Assault", "cognizable": True, "bailable": False, "punishment": "Up to 5 years, or fine, or both"},
    "117": {"description": "Voluntarily causing grievous hurt", "offense_type": "Grievous hurt", "cognizable": True, "bailable": False, "punishment": "Up to 7 years imprisonment, and fine"},
    "126(2)": {"description": "Wrongful restraint/confinement", "offense_type": "Restraint", "cognizable": True, "bailable": True, "punishment": "Up to 1 year imprisonment, or fine, or both"},
    "303": {"description": "Theft", "offense_type": "Theft", "cognizable": True, "bailable": False, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "308": {"description": "Extortion", "offense_type": "Extortion", "cognizable": True, "bailable": False, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "309": {"description": "Robbery", "offense_type": "Robbery", "cognizable": True, "bailable": False, "punishment": "Up to 10 years rigorous imprisonment, and fine"},
    "316": {"description": "Criminal breach of trust", "offense_type": "Breach of trust", "cognizable": False, "bailable": True, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "316(2)": {"description": "Criminal breach of trust by carrier, banker, etc.", "offense_type": "Breach of trust", "cognizable": True, "bailable": False, "punishment": "Up to 7 years imprisonment, and fine"},
    "318": {"description": "Cheating", "offense_type": "Cheating", "cognizable": True, "bailable": True, "punishment": "Up to 3 years imprisonment, or fine, or both"},
    "318(4)": {"description": "Cheating and dishonestly inducing delivery of property", "offense_type": "Cheating", "cognizable": True, "bailable": False, "punishment": "Up to 7 years imprisonment, and fine"},
    "329": {"description": "Criminal trespass and house trespass", "offense_type": "Trespass", "cognizable": True, "bailable": True, "punishment": "Up to 3 months imprisonment, or fine, or both"},
    "329(4)": {"description": "House trespass with violence", "offense_type": "Trespass", "cognizable": True, "bailable": False, "punishment": "Up to 1 year imprisonment, and fine"},
    "351": {"description": "Criminal intimidation", "offense_type": "Intimidation", "cognizable": False, "bailable": True, "punishment": "Up to 2 years imprisonment, or fine, or both"},
    "3(5)": {"description": "Common intention (joint liability)", "offense_type": "General", "cognizable": None, "bailable": None, "punishment": "As per the main offense"},
}


def lookup_section(act: str, section: str) -> dict:
    """Look up a legal section by act name and section number."""
    act_upper = act.upper()

    if "IPC" in act_upper or "INDIAN PENAL" in act_upper:
        data = IPC_SECTIONS.get(section, {})
        if data:
            return {"act": "Indian Penal Code (IPC)", "section": section, **data}

    elif "BNS" in act_upper or "BHARATIYA" in act_upper or "NYAYA" in act_upper:
        data = BNS_SECTIONS.get(section, {})
        if data:
            return {"act": "Bharatiya Nyaya Sanhita (BNS)", "section": section, **data}

    return {"act": act, "section": section, "description": "Section details not found in local KB"}


def lookup_sections_batch(acts_list: list) -> list:
    """Look up multiple sections from an acts list like [{act, sections}]."""
    results = []
    for act_entry in acts_list:
        act_name = act_entry.get("act", "")
        for section in act_entry.get("sections", []):
            info = lookup_section(act_name, section)
            results.append(info)
    return results


def get_all_sections(act_filter: str = None) -> list:
    """Get all legal sections, optionally filtered by act."""
    results = []

    if act_filter is None or "IPC" in act_filter.upper():
        for section, data in IPC_SECTIONS.items():
            results.append({"act": "Indian Penal Code (IPC)", "section": section, **data})

    if act_filter is None or "BNS" in act_filter.upper():
        for section, data in BNS_SECTIONS.items():
            results.append({"act": "Bharatiya Nyaya Sanhita (BNS)", "section": section, **data})

    return results
