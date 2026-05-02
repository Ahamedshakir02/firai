"""
IPC ↔ BNS Cross-Mapping
========================
Maps Indian Penal Code (1860) sections to their Bharatiya Nyaya Sanhita (2023)
equivalents and vice versa. Essential for officers during the transition period.
"""

# IPC Section → BNS Section
IPC_TO_BNS = {
    # Murder & Homicide
    "299": "101", "300": "101", "302": "103", "303": "103",
    "304": "105", "304A": "106", "304B": "80", "306": "108",
    "307": "109", "308": "110",
    # Assault & Hurt
    "319": "114", "320": "114", "321": "115", "322": "115",
    "323": "115", "324": "118", "325": "117", "326": "118",
    "326A": "124", "326B": "124",
    "332": "121", "333": "121", "334": "131", "335": "131",
    # Restraint & Confinement
    "339": "126", "340": "127", "341": "126", "342": "127",
    # Force & Criminal Force
    "349": "128", "350": "129", "351": "130", "352": "131",
    "353": "132", "354": "74", "354A": "75", "354B": "76",
    "354C": "77", "354D": "78",
    # Kidnapping
    "359": "136", "360": "137", "361": "137", "362": "138",
    "363": "140", "363A": "141", "364": "140", "364A": "140",
    "365": "140", "366": "143", "366A": "144", "366B": "145",
    # Sexual Offences
    "375": "63", "376": "64", "376A": "66", "376B": "67",
    "376C": "68", "376D": "70",
    # Theft
    "378": "302", "379": "303", "380": "305", "381": "304",
    "382": "305",
    # Extortion
    "383": "306", "384": "308", "385": "307", "386": "307",
    # Robbery & Dacoity
    "390": "309", "391": "310", "392": "309", "393": "309",
    "394": "309", "395": "310", "396": "311", "397": "312",
    "398": "312", "399": "310", "400": "310", "401": "310",
    # Breach of Trust
    "403": "314", "404": "314", "405": "315", "406": "316",
    "407": "316", "408": "317", "409": "317",
    # Stolen Property
    "410": "317", "411": "317", "412": "317", "414": "317",
    # Cheating
    "415": "318", "416": "318", "417": "318", "418": "318",
    "419": "319", "420": "318(4)",
    # Property Damage
    "425": "323", "426": "323", "427": "324", "428": "325",
    "429": "325", "435": "326", "436": "326",
    # Trespass
    "441": "329", "442": "329", "447": "329", "448": "330",
    "449": "331", "450": "331", "451": "332", "452": "332",
    "453": "332", "454": "332", "455": "332", "456": "332",
    "457": "332", "458": "333",
    # Forgery
    "463": "336", "464": "336", "465": "336", "466": "337",
    "467": "338", "468": "338", "469": "339", "470": "340",
    "471": "340",
    # Criminal Intimidation
    "503": "349", "504": "352", "505": "353", "506": "351",
    "507": "351", "509": "79",
    # Domestic Violence
    "498A": "85",
    # Wrongful Restraint
    "279": "281",
    # Common Intention / Abetment
    "34": "3(5)", "107": "45", "109": "48", "120B": "61",
}

# Build reverse map: BNS → IPC
BNS_TO_IPC = {}
for ipc, bns in IPC_TO_BNS.items():
    if bns not in BNS_TO_IPC:
        BNS_TO_IPC[bns] = ipc


def get_equivalent(act: str, section: str) -> dict:
    """
    Get the equivalent section in the other code.
    IPC → BNS or BNS → IPC.

    Returns:
        {
            "source_act": "IPC", "source_section": "302",
            "equivalent_act": "BNS", "equivalent_section": "103",
            "found": True
        }
    """
    act_upper = act.upper()

    if "IPC" in act_upper or "INDIAN PENAL" in act_upper:
        equiv = IPC_TO_BNS.get(section)
        if equiv:
            return {
                "source_act": "IPC", "source_section": section,
                "equivalent_act": "BNS", "equivalent_section": equiv,
                "found": True,
            }

    elif "BNS" in act_upper or "BHARATIYA" in act_upper or "NYAYA" in act_upper:
        equiv = BNS_TO_IPC.get(section)
        if equiv:
            return {
                "source_act": "BNS", "source_section": section,
                "equivalent_act": "IPC", "equivalent_section": equiv,
                "found": True,
            }

    return {
        "source_act": act, "source_section": section,
        "equivalent_act": None, "equivalent_section": None,
        "found": False,
    }


def get_batch_equivalents(sections: list) -> list:
    """
    Get equivalents for a list of {act, section} dicts.
    Useful for mapping all sections in an FIR at once.
    """
    results = []
    for s in sections:
        act = s.get("act", "")
        for sec in s.get("sections", [s.get("section", "")]):
            results.append(get_equivalent(act, str(sec)))
    return results
