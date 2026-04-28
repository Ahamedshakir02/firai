"""
Indian Legal Corpus — Comprehensive law text for AI training.
Contains full descriptions of IPC, BNS, CrPC, BNSS, Special Acts.
This is what the AI learns from — the actual Indian law, not Gemini.

The corpus is structured as training-ready data:
each section has its full legal description, elements of offense,
punishment, and example scenarios.
"""

# ── STRUCTURE ──
# Each entry: {
#   "section": "302",
#   "act": "IPC",
#   "title": "Murder",
#   "description": "Full legal description...",
#   "elements": ["element1", "element2"],
#   "punishment": "...",
#   "cognizable": True/False,
#   "bailable": True/False,
#   "crime_type": "murder",
#   "severity": "critical",
#   "investigation_steps": ["step1", "step2"],
#   "example_scenario": "..."
# }

LEGAL_CORPUS = [
    # ════════════════════════ MURDER & HOMICIDE ════════════════════════
    {
        "section": "302", "act": "IPC",
        "title": "Punishment for Murder",
        "description": "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. Murder is defined under Section 300 as culpable homicide where the act is done with the intention of causing death, or with the intention of causing such bodily injury as the offender knows to be likely to cause death, or with the intention of causing bodily injury sufficient in the ordinary course of nature to cause death.",
        "elements": ["Intentional causing of death", "Knowledge that act is likely to cause death", "Bodily injury sufficient to cause death in ordinary course"],
        "punishment": "Death or imprisonment for life, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "murder", "severity": "critical",
        "investigation_steps": ["Secure crime scene and preserve evidence", "Record dying declaration if victim alive", "Conduct post-mortem examination", "Collect forensic evidence (blood, fingerprints, DNA)", "Record statements of eyewitnesses", "Arrest accused and record confession if any", "Prepare scene of crime mahazar", "Collect CCTV footage from vicinity"],
        "example_scenario": "A person stabs another with a knife intending to kill, resulting in death."
    },
    {
        "section": "103", "act": "BNS",
        "title": "Murder (BNS)",
        "description": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine. This section replaces IPC Section 302 under the Bharatiya Nyaya Sanhita 2023.",
        "elements": ["Intentional causing of death", "Knowledge that act likely to cause death", "Bodily injury sufficient to cause death"],
        "punishment": "Death or imprisonment for life, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "murder", "severity": "critical",
        "investigation_steps": ["Secure crime scene", "Conduct inquest and post-mortem", "Collect forensic evidence", "Record witness statements", "Arrest accused"],
        "example_scenario": "Accused attacks victim with iron rod repeatedly causing death."
    },
    {
        "section": "304", "act": "IPC",
        "title": "Culpable Homicide not amounting to Murder",
        "description": "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
        "elements": ["Causing death without premeditation", "Act done in heat of passion", "No intention to cause death but knowledge of risk"],
        "punishment": "Imprisonment for life, or up to 10 years, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "homicide", "severity": "critical",
        "investigation_steps": ["Establish circumstances of death", "Determine provocation or sudden fight", "Collect medical evidence", "Record statements"],
        "example_scenario": "During a sudden quarrel, a person pushes another who falls and hits head, causing death."
    },

    # ════════════════════════ ASSAULT & HURT ════════════════════════
    {
        "section": "323", "act": "IPC",
        "title": "Voluntarily causing hurt",
        "description": "Whoever voluntarily causes hurt shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both. Hurt means causing bodily pain, disease or infirmity to any person.",
        "elements": ["Voluntary act", "Causing bodily pain", "No dangerous weapon used"],
        "punishment": "Up to 1 year imprisonment, or fine up to Rs 1000, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "assault", "severity": "medium",
        "investigation_steps": ["Obtain medical certificate of injuries", "Record victim statement", "Identify and arrest accused", "Collect eyewitness statements"],
        "example_scenario": "During an argument, a person slaps and punches another causing minor injuries."
    },
    {
        "section": "324", "act": "IPC",
        "title": "Voluntarily causing hurt by dangerous weapons",
        "description": "Whoever voluntarily causes hurt by means of any instrument for shooting, stabbing or cutting, or any instrument which, used as a weapon of offence, is likely to cause death, or by means of fire or any heated substance, or by means of any poison or any corrosive substance, shall be punished with imprisonment for a term which may extend to three years, or with fine, or with both.",
        "elements": ["Voluntary causing of hurt", "Use of dangerous weapon or means", "Weapon likely to cause death"],
        "punishment": "Up to 3 years imprisonment, or fine, or both",
        "cognizable": True, "bailable": False,
        "crime_type": "assault", "severity": "high",
        "investigation_steps": ["Seize the weapon used", "Obtain injury report", "Photograph injuries", "Record statements of witnesses and victim"],
        "example_scenario": "Accused attacks victim with a jack lever (ജാക്കി ലിവര്‍) causing injuries."
    },
    {
        "section": "115", "act": "BNS",
        "title": "Voluntarily causing hurt (BNS)",
        "description": "Whoever voluntarily causes hurt shall be punished. Sub-section (2): If hurt is caused using dangerous weapons or means, punishment is enhanced. Replaces IPC Sections 323 and 324.",
        "elements": ["Voluntary act causing bodily pain", "Use of weapon if sub-section 2"],
        "punishment": "Up to 1 year (simple), up to 5 years with weapon",
        "cognizable": True, "bailable": True,
        "crime_type": "assault", "severity": "high",
        "investigation_steps": ["Medical examination of victim", "Seize weapon if used", "Record statements", "Arrest accused"],
        "example_scenario": "Accused beats victim with hands and threatens to kill (കൊല്ലുമെന്ന്‌ ഭീഷണിപ്പെടുത്തി)."
    },
    {
        "section": "118", "act": "BNS",
        "title": "Voluntarily causing grievous hurt (BNS)",
        "description": "Whoever voluntarily causes grievous hurt shall be punished with imprisonment up to seven years and fine. Sub-section (1) covers basic grievous hurt, sub-section (2) covers grievous hurt with dangerous weapons.",
        "elements": ["Causing grievous hurt", "Fracture, loss of limb, permanent damage", "Dangerous weapon if sub-section 2"],
        "punishment": "Up to 7 years imprisonment and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "assault", "severity": "critical",
        "investigation_steps": ["Detailed medical report with X-rays", "Document nature of injuries", "Seize weapon", "Record dying declaration if critical"],
        "example_scenario": "Accused attacks neighbour over boundary dispute causing bone fractures."
    },

    # ════════════════════════ THEFT & ROBBERY ════════════════════════
    {
        "section": "379", "act": "IPC",
        "title": "Theft",
        "description": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. Theft is defined as dishonestly taking movable property out of the possession of any person without that person's consent.",
        "elements": ["Dishonest intention", "Movable property", "Taking without consent", "Moving property out of possession"],
        "punishment": "Up to 3 years imprisonment, or fine, or both",
        "cognizable": True, "bailable": False,
        "crime_type": "theft", "severity": "medium",
        "investigation_steps": ["Record detailed list of stolen property", "Check CCTV in vicinity", "Search for stolen property at pawn shops", "Check mobile tower locations of suspects"],
        "example_scenario": "Motor cycle parked near a school was stolen by unknown persons (കള്ളന്‍മാ൪ മോശവിചാരത്തോടെ കളവ്‌ ചെയ്ത്‌)."
    },
    {
        "section": "303", "act": "BNS",
        "title": "Theft (BNS)",
        "description": "Whoever commits theft shall be punished. Sub-section (2) provides enhanced punishment for motor vehicle theft. Replaces IPC Section 379.",
        "elements": ["Dishonest intention", "Taking movable property", "Without consent"],
        "punishment": "Up to 3 years; up to 7 years for motor vehicle theft",
        "cognizable": True, "bailable": False,
        "crime_type": "theft", "severity": "medium",
        "investigation_steps": ["Register FIR with vehicle details", "Alert check posts", "Check CCTV", "Trace vehicle via GPS if available", "Check with RTO for vehicle records"],
        "example_scenario": "Motorcycle KL 60 D 5499 stolen from KSRTC bus stand parking area."
    },

    # ════════════════════════ DRUNK DRIVING ════════════════════════
    {
        "section": "185", "act": "Motor Vehicle Act",
        "title": "Driving by a drunken person or by a person under the influence of drugs",
        "description": "Whoever drives a motor vehicle while under the influence of alcohol or drugs, having blood alcohol concentration exceeding 30mg per 100ml of blood, shall be punishable. First offence: imprisonment up to 6 months and/or fine up to Rs 10,000. Second offence within 3 years: imprisonment up to 2 years and/or fine up to Rs 15,000.",
        "elements": ["Driving motor vehicle", "Under influence of alcohol/drugs", "Blood alcohol exceeding limit", "On public road"],
        "punishment": "First offence: up to 6 months and/or Rs 10,000 fine",
        "cognizable": True, "bailable": True,
        "crime_type": "drunk_driving", "severity": "high",
        "investigation_steps": ["Conduct breath analyzer test", "Record BAC reading", "Seize vehicle with seizure mahazar", "Check driving license validity", "Record witness statements of patrol party", "Preserve breath analyzer report as evidence"],
        "example_scenario": "Accused driving motorcycle at high speed on NH road, breath analyzer showed 59 mg/100ml alcohol (ആല്‍ക്കോ മീറ്ററില്‍ ഈതിച്ചതില്‍ 59 mg/100ml)."
    },
    {
        "section": "281", "act": "BNS",
        "title": "Rash driving or riding on a public way (BNS)",
        "description": "Whoever drives any vehicle, or rides, on any public way in a manner so rash or negligent as to endanger human life, or to be likely to cause hurt or injury to any other person, shall be punished with imprisonment up to six months, or with fine up to one thousand rupees, or with both.",
        "elements": ["Driving/riding on public way", "Rash or negligent manner", "Endangering human life"],
        "punishment": "Up to 6 months imprisonment, or fine, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "rash_driving", "severity": "high",
        "investigation_steps": ["Record accident spot mahazar", "Obtain accident report", "Check vehicle fitness", "Collect CCTV footage", "Medical examination for alcohol"],
        "example_scenario": "Accused driving motorcycle at excessive speed and recklessly, endangering lives (അതിവേഗതയിലും അശ്രദ്ധമായും മനുഷ്യ ജീവനു അപായം സൃഷ്ടിക്കത്തക്ക വിധത്തിലും)."
    },

    # ════════════════════════ CHEATING & FRAUD ════════════════════════
    {
        "section": "420", "act": "IPC",
        "title": "Cheating and dishonestly inducing delivery of property",
        "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment for a term which may extend to seven years, and shall also be liable to fine.",
        "elements": ["Deception", "Dishonest inducement", "Delivery of property or valuable security"],
        "punishment": "Up to 7 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "cheating", "severity": "medium",
        "investigation_steps": ["Collect documentary evidence of fraud", "Trace financial transactions", "Record victim's statement with documents", "Seize digital evidence if cyber fraud"],
        "example_scenario": "Accused promises job and collects money from multiple victims but never provides employment."
    },
    {
        "section": "318", "act": "BNS",
        "title": "Cheating (BNS)",
        "description": "Whoever cheats shall be punished. Sub-section (4) covers cheating with dishonest inducement of delivery of property, punishable up to 7 years. Replaces IPC 420.",
        "elements": ["Deception by false representation", "Dishonest inducement", "Delivery of property"],
        "punishment": "Up to 3 years (basic); up to 7 years (with property delivery)",
        "cognizable": True, "bailable": True,
        "crime_type": "cheating", "severity": "medium",
        "investigation_steps": ["Collect all communication records", "Trace bank transactions", "Identify other victims", "Seize documents and digital evidence"],
        "example_scenario": "Accused collects advance payments for goods/services and disappears."
    },

    # ════════════════════════ FORGERY ════════════════════════
    {
        "section": "465", "act": "IPC",
        "title": "Punishment for forgery",
        "description": "Whoever commits forgery shall be punished with imprisonment for a term which may extend to two years, or with fine, or with both.",
        "elements": ["Making false document", "Intent to cause damage", "Intent to defraud"],
        "punishment": "Up to 2 years imprisonment, or fine, or both",
        "cognizable": False, "bailable": True,
        "crime_type": "forgery", "severity": "medium",
        "investigation_steps": ["Seize original and forged documents", "Send for forensic handwriting analysis", "Check document trail", "Record statements"],
        "example_scenario": "Accused creates fake property documents to sell land that doesn't belong to them."
    },
    {
        "section": "468", "act": "IPC",
        "title": "Forgery for purpose of cheating",
        "description": "Whoever commits forgery, intending that the document forged shall be used for the purpose of cheating, shall be punished with imprisonment for a term which may extend to seven years, and shall also be liable to fine.",
        "elements": ["Forgery committed", "Intent to use for cheating", "Document to deceive"],
        "punishment": "Up to 7 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "forgery", "severity": "high",
        "investigation_steps": ["Forensic examination of documents", "Trace creation of forged documents", "Check notary/registration records", "Identify beneficiaries of forgery"],
        "example_scenario": "Accused forges power of attorney to sell victim's property."
    },

    # ════════════════════════ CRIMINAL INTIMIDATION ════════════════════════
    {
        "section": "506", "act": "IPC",
        "title": "Criminal Intimidation",
        "description": "Whoever commits criminal intimidation shall be punished with imprisonment for a term which may extend to two years, or with fine, or with both. If threat is to cause death or grievous hurt, or to cause destruction of property by fire, or to cause an offence punishable with death or imprisonment for life — up to seven years.",
        "elements": ["Threat to cause injury", "To person, reputation, or property", "Intent to cause alarm"],
        "punishment": "Up to 2 years (simple), up to 7 years (death threat)",
        "cognizable": False, "bailable": True,
        "crime_type": "criminal_intimidation", "severity": "high",
        "investigation_steps": ["Record exact words of threat", "Check for witnesses", "Collect call records or messages if applicable", "Assess threat credibility"],
        "example_scenario": "Accused threatens to kill victim during a dispute (കൊല്ലുമെന്ന്‌ ഭീഷണിപ്പെടുത്തി)."
    },

    # ════════════════════════ EXCISE / ABKARI ════════════════════════
    {
        "section": "15(c)", "act": "Kerala Abkari Act",
        "title": "Public intoxication / consuming liquor in public",
        "description": "Whoever is found drunk and disorderly in any public place, or consumes liquor in a public place, shall be punished under the Kerala Abkari Act. Section 15(c) specifically deals with possession or consumption of illicit liquor in public.",
        "elements": ["Public place", "Consumption or possession of liquor", "Causing nuisance or found intoxicated"],
        "punishment": "Imprisonment up to 3 years, or fine, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "excise_offense", "severity": "medium",
        "investigation_steps": ["Record location and time of offense", "Seize liquor bottles if any", "Record witness statements", "Medical examination of accused for intoxication"],
        "example_scenario": "Accused found consuming illicit liquor at roadside near a public junction."
    },

    # ════════════════════════ UNNATURAL DEATH ════════════════════════
    {
        "section": "194", "act": "BNSS",
        "title": "Inquest by Police - Unnatural Death",
        "description": "When information is received by a police officer that a person has committed suicide, or has been killed by another, or by an animal, or by machinery, or by an accident, or has died under circumstances raising a reasonable suspicion that some other person has committed an offence, the officer shall conduct an inquest. BNSS 194 replaces CrPC 174.",
        "elements": ["Death under suspicious circumstances", "Suicide", "Accidental death", "Death by animal/machinery"],
        "punishment": "N/A — procedural section for investigation",
        "cognizable": True, "bailable": None,
        "crime_type": "unnatural_death", "severity": "critical",
        "investigation_steps": ["Rush to spot and secure body", "Conduct inquest proceedings", "Send body for post-mortem", "Record statements of family members", "Check for foul play indicators", "Collect medical history"],
        "example_scenario": "Person found dead in river; elephant attack victim in forest area (ആനയുടെ ആക്രമണത്തില്‍ ആദിവാസി മരണപ്പെട്ടു)."
    },

    # ════════════════════════ SEXUAL OFFENSES ════════════════════════
    {
        "section": "354", "act": "IPC",
        "title": "Assault on woman with intent to outrage modesty",
        "description": "Whoever assaults or uses criminal force to any woman, intending to outrage or knowing it to be likely that he will thereby outrage her modesty, shall be punished with imprisonment of either description for a term which shall not be less than one year but which may extend to five years.",
        "elements": ["Assault or criminal force", "Against a woman", "Intent to outrage modesty"],
        "punishment": "1 to 5 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "sexual_offense", "severity": "high",
        "investigation_steps": ["Record victim statement in private", "Arrange female officer for recording", "Medical examination with consent", "Collect CCTV footage", "Arrest accused"],
        "example_scenario": "Accused grabs woman inappropriately in public transport."
    },

    # ════════════════════════ TRESPASS ════════════════════════
    {
        "section": "329", "act": "BNS",
        "title": "Criminal Trespass (BNS)",
        "description": "Whoever enters into or upon property in the possession of another with intent to commit an offence, or to intimidate, insult or annoy. Sub-section (3): lurking house-trespass. Sub-section (4): house-trespass with violence.",
        "elements": ["Unauthorized entry", "Property in another's possession", "Intent to commit offence or cause annoyance"],
        "punishment": "Up to 3 months (basic); up to 1 year (house-trespass)",
        "cognizable": True, "bailable": True,
        "crime_type": "trespass", "severity": "medium",
        "investigation_steps": ["Inspect property and document trespass", "Record owner's statement", "Check for property disputes", "Collect witness statements"],
        "example_scenario": "Accused enters neighbour's property during boundary dispute."
    },

    # ════════════════════════ PROPERTY DAMAGE ════════════════════════
    {
        "section": "427", "act": "IPC",
        "title": "Mischief causing damage",
        "description": "Whoever commits mischief and thereby causes loss or damage to the amount of fifty rupees or upwards, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.",
        "elements": ["Intentional destruction or damage", "To property of another", "Loss of Rs 50 or more"],
        "punishment": "Up to 2 years imprisonment, or fine, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "property_damage", "severity": "medium",
        "investigation_steps": ["Assess and document damage", "Estimate value of damaged property", "Record owner statement", "Identify accused"],
        "example_scenario": "Accused destroys food items worth Rs 28,000 at a bakery during a dispute."
    },

    # ════════════════════════ WRONGFUL RESTRAINT ════════════════════════
    {
        "section": "341", "act": "IPC",
        "title": "Wrongful Restraint",
        "description": "Whoever wrongfully restrains any person shall be punished with simple imprisonment for a term which may extend to one month, or with fine which may extend to five hundred rupees, or with both. Wrongful restraint means voluntarily obstructing a person to prevent him from proceeding in any direction.",
        "elements": ["Voluntary obstruction", "Preventing person from proceeding", "Without legal justification"],
        "punishment": "Up to 1 month imprisonment, or fine up to Rs 500, or both",
        "cognizable": False, "bailable": True,
        "crime_type": "wrongful_restraint", "severity": "low",
        "investigation_steps": ["Record statements of both parties", "Check for witnesses", "Verify if there was any provocation"],
        "example_scenario": "Accused blocks victim's path during an argument at a shop."
    },

    # ════════════════════════ PUBLIC NUISANCE ════════════════════════
    {
        "section": "294(b)", "act": "IPC",
        "title": "Obscene acts and songs in public",
        "description": "Whoever sings, recites or utters any obscene song, ballad or words, in or near any public place, shall be punished with imprisonment for a term which may extend to three months, or with fine, or with both.",
        "elements": ["Obscene words or songs", "In or near public place", "Causing annoyance"],
        "punishment": "Up to 3 months imprisonment, or fine, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "public_nuisance", "severity": "low",
        "investigation_steps": ["Record details of obscene behavior", "Collect witness statements", "Check for repeat offenses"],
        "example_scenario": "Accused uses abusive and obscene language during a dispute in public (തെറി വിളിച്ച്‌)."
    },
]


def get_corpus():
    """Return the full legal corpus."""
    return LEGAL_CORPUS


def get_sections_by_crime(crime_type: str) -> list:
    """Get all legal sections related to a crime type."""
    return [s for s in LEGAL_CORPUS if s.get("crime_type") == crime_type]


def get_section(act: str, section: str) -> dict:
    """Look up a specific section."""
    for s in LEGAL_CORPUS:
        if s["act"].upper() in act.upper() and s["section"] == section:
            return s
    return {}


def get_investigation_steps(crime_type: str) -> list:
    """Get recommended investigation steps for a crime type."""
    sections = get_sections_by_crime(crime_type)
    steps = set()
    for s in sections:
        for step in s.get("investigation_steps", []):
            steps.add(step)
    return list(steps) if steps else [
        "Record detailed witness statements",
        "Collect physical evidence from the crime scene",
        "Verify accused identity and location",
        "Prepare scene of crime mahazar",
        "Submit charge sheet to court",
    ]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"Legal Corpus: {len(LEGAL_CORPUS)} sections loaded")
    from collections import Counter
    crimes = Counter(s["crime_type"] for s in LEGAL_CORPUS)
    print("\nCoverage by crime type:")
    for ct, count in crimes.most_common():
        print(f"  {ct}: {count} sections")
