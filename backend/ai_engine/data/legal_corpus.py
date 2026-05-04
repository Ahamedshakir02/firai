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

    # ════════════════════════ ATTEMPT TO MURDER ════════════════════════
    {
        "section": "307", "act": "IPC",
        "title": "Attempt to Murder",
        "description": "Whoever does any act with the intention or knowledge that if he thereby caused death he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine; and if hurt is caused to any person by such act, the offender shall be liable to imprisonment for life.",
        "elements": ["Act done with intention to cause death", "Knowledge that act could cause death", "Act falls short of causing death"],
        "punishment": "Up to 10 years imprisonment, and fine; life imprisonment if hurt is caused",
        "cognizable": True, "bailable": False,
        "crime_type": "assault", "severity": "critical",
        "investigation_steps": ["Secure crime scene and collect weapon", "Medical examination of victim with detailed injury report", "Record dying declaration if victim critical", "Collect forensic evidence (blood, fingerprints)", "Record eyewitness statements", "Arrest accused immediately", "Collect CCTV footage", "Establish motive"],
        "example_scenario": "Accused stabs victim multiple times with a knife during a dispute but victim survives after hospitalization."
    },
    {
        "section": "109", "act": "BNS",
        "title": "Attempt to Murder (BNS)",
        "description": "Whoever does any act with the intention or knowledge that if he thereby caused death he would be guilty of murder, shall be punished. Replaces IPC Section 307.",
        "elements": ["Intent to cause death", "Act done towards that end", "Death not resulting"],
        "punishment": "Up to 10 years; life imprisonment if hurt caused",
        "cognizable": True, "bailable": False,
        "crime_type": "assault", "severity": "critical",
        "investigation_steps": ["Secure scene and weapon", "Detailed medical report", "Record statements", "Forensic evidence collection", "Arrest accused"],
        "example_scenario": "Accused attacks victim with iron rod on head with intent to kill."
    },

    # ════════════════════════ KIDNAPPING ════════════════════════
    {
        "section": "363", "act": "IPC",
        "title": "Kidnapping from lawful guardianship",
        "description": "Whoever kidnaps any person from lawful guardianship shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. Kidnapping from lawful guardianship means taking or enticing any minor under 16 (male) or 18 (female) out of the keeping of the lawful guardian.",
        "elements": ["Taking or enticing a minor", "Out of keeping of lawful guardian", "Without guardian's consent"],
        "punishment": "Up to 7 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "kidnapping", "severity": "critical",
        "investigation_steps": ["Register FIR immediately", "Alert all check posts and railway stations", "Circulate photo and description of missing person", "Check CCTV at last known location", "Trace mobile phone of victim and suspect", "Coordinate with cyber cell for digital tracking", "Record detailed statement of guardian", "Check social media accounts"],
        "example_scenario": "Minor girl taken away by neighbor without parents' knowledge or consent."
    },
    {
        "section": "364", "act": "IPC",
        "title": "Kidnapping for murder or ransom",
        "description": "Whoever kidnaps or abducts any person in order that such person may be murdered or so disposed of as to be put in danger of being murdered, shall be punished with imprisonment for life or rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
        "elements": ["Kidnapping or abduction", "Intent to murder or put in danger of murder", "Or for ransom"],
        "punishment": "Life imprisonment or up to 10 years RI, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "kidnapping", "severity": "critical",
        "investigation_steps": ["Immediate FIR and alert to all units", "Set up surveillance on communication channels", "Negotiate if ransom demanded", "Coordinate with anti-kidnapping squad", "Technical surveillance of suspects", "Rescue operation planning"],
        "example_scenario": "Accused kidnaps businessman's son and demands ransom of Rs 50 lakhs."
    },

    # ════════════════════════ DOMESTIC VIOLENCE ════════════════════════
    {
        "section": "498A", "act": "IPC",
        "title": "Cruelty by husband or relatives of husband",
        "description": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine. Cruelty means willful conduct likely to drive the woman to suicide, or causing grave injury to life, limb or health, or harassment for dowry.",
        "elements": ["Accused is husband or his relative", "Victim is married woman", "Cruelty: physical or mental", "Dowry harassment or driving to suicide"],
        "punishment": "Up to 3 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "domestic_violence", "severity": "high",
        "investigation_steps": ["Record victim's statement in private with female officer", "Document injuries with photographs and medical report", "Seize dowry demand evidence (messages, letters)", "Record statements of neighbors and relatives", "Check for previous complaints", "Provide victim with protection order information", "Refer to Women's Commission if needed"],
        "example_scenario": "Husband and in-laws harass wife for additional dowry and physically assault her."
    },
    {
        "section": "85", "act": "BNS",
        "title": "Cruelty by husband or relatives (BNS)",
        "description": "Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished. Replaces IPC 498A.",
        "elements": ["Husband or relative", "Cruelty to married woman", "Dowry demand or mental/physical abuse"],
        "punishment": "Up to 3 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "domestic_violence", "severity": "high",
        "investigation_steps": ["Record victim statement with female officer", "Medical examination", "Collect evidence of dowry demand", "Provide protection order", "Arrest accused if prima facie case"],
        "example_scenario": "Wife subjected to mental and physical cruelty for not meeting dowry demands."
    },

    # ════════════════════════ CYBER CRIME ════════════════════════
    {
        "section": "66", "act": "IT Act",
        "title": "Computer related offences (Hacking)",
        "description": "If any person, dishonestly or fraudulently, does any act referred to in section 43 (unauthorized access, data theft, virus introduction, denial of service), he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.",
        "elements": ["Unauthorized access to computer system", "Dishonest or fraudulent intent", "Damage to computer/data/network"],
        "punishment": "Up to 3 years imprisonment, or fine up to Rs 5 lakh, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "cyber_crime", "severity": "medium",
        "investigation_steps": ["Preserve digital evidence immediately", "Seize devices with proper chain of custody", "Send to cyber forensics lab", "Trace IP addresses and digital footprint", "Coordinate with ISP for subscriber details", "Record technical evidence with hash values", "Check for similar complaints (pattern)"],
        "example_scenario": "Accused hacks into victim's email account and steals personal data."
    },
    {
        "section": "66C", "act": "IT Act",
        "title": "Identity theft using computer resource",
        "description": "Whoever, fraudulently or dishonestly makes use of the electronic signature, password or any other unique identification feature of any other person, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to rupees one lakh.",
        "elements": ["Fraudulent use of another's identity", "Electronic signature/password/ID", "Dishonest intent"],
        "punishment": "Up to 3 years imprisonment, and fine up to Rs 1 lakh",
        "cognizable": True, "bailable": True,
        "crime_type": "cyber_crime", "severity": "medium",
        "investigation_steps": ["Document the identity theft with screenshots", "Trace the unauthorized access logs", "Coordinate with platform/service provider", "Preserve digital evidence", "Check financial transactions if any"],
        "example_scenario": "Accused uses victim's Aadhaar and PAN details to open fake bank accounts."
    },
    {
        "section": "66D", "act": "IT Act",
        "title": "Cheating by personation using computer resource",
        "description": "Whoever, by means of any communication device or computer resource cheats by personating, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.",
        "elements": ["Cheating by impersonation", "Using communication device or computer", "Fraudulent intent"],
        "punishment": "Up to 3 years imprisonment, and fine up to Rs 1 lakh",
        "cognizable": True, "bailable": True,
        "crime_type": "cyber_crime", "severity": "medium",
        "investigation_steps": ["Collect evidence of impersonation", "Trace digital communications", "Coordinate with cyber cell", "Identify actual person behind fake accounts", "Preserve all electronic evidence"],
        "example_scenario": "Accused creates fake social media profile of victim and sends obscene messages to victim's contacts."
    },

    # ════════════════════════ DRUG OFFENSES (NDPS) ════════════════════════
    {
        "section": "20", "act": "NDPS Act",
        "title": "Punishment for contravention in relation to cannabis plant and cannabis",
        "description": "Whoever contravenes any provision of this Act relating to cannabis plant or cannabis (ganja, charas, hashish) — for small quantity: rigorous imprisonment up to 1 year, or fine up to Rs 10,000, or both; for quantity less than commercial but more than small: up to 10 years RI and fine up to Rs 1 lakh; for commercial quantity: 10-20 years RI and fine Rs 1-2 lakh.",
        "elements": ["Possession or dealing in cannabis", "Without authorization", "Quantity determines severity"],
        "punishment": "Small: up to 1 year; Medium: up to 10 years; Commercial: 10-20 years",
        "cognizable": True, "bailable": False,
        "crime_type": "drug_offense", "severity": "high",
        "investigation_steps": ["Seize substance with proper panchnama", "Weigh and photograph seized substance", "Draw samples for chemical analysis (FSL)", "Record seizure witnesses", "Arrest accused and record memorandum", "Check for supplier chain", "Send samples to forensic lab within 72 hours"],
        "example_scenario": "Accused found in possession of 500 grams of ganja during vehicle check."
    },
    {
        "section": "21", "act": "NDPS Act",
        "title": "Punishment for contravention in relation to manufactured drugs",
        "description": "Whoever contravenes any provision of this Act relating to manufactured drugs (heroin, cocaine, morphine, etc.) shall be punishable. Small quantity: up to 1 year RI or fine up to Rs 10,000 or both. Commercial quantity: 10-20 years RI and fine Rs 1-2 lakh.",
        "elements": ["Possession/sale of manufactured drugs", "Without authorization", "Type and quantity of substance"],
        "punishment": "Small: up to 1 year; Commercial: 10-20 years RI",
        "cognizable": True, "bailable": False,
        "crime_type": "drug_offense", "severity": "critical",
        "investigation_steps": ["Seize drugs with detailed panchnama", "Chemical testing of substance", "Trace supply chain and network", "Financial investigation of accused", "Coordinate with Narcotics Control Bureau", "Check international connections"],
        "example_scenario": "Accused caught selling heroin near school premises."
    },

    # ════════════════════════ DACOITY ════════════════════════
    {
        "section": "395", "act": "IPC",
        "title": "Punishment for Dacoity",
        "description": "Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. Dacoity means robbery committed by five or more persons conjointly.",
        "elements": ["Five or more persons acting together", "Commission of robbery", "Use or threat of force"],
        "punishment": "Life imprisonment or up to 10 years RI, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "dacoity", "severity": "critical",
        "investigation_steps": ["Secure crime scene", "Record victim and witness statements", "Identify all members of gang", "Check for similar dacoity patterns", "Seize weapons used", "Alert neighboring police stations", "Use technical surveillance to track gang"],
        "example_scenario": "Group of 6 armed men break into a house at night and rob gold and cash worth Rs 15 lakhs."
    },

    # ════════════════════════ EXTORTION ════════════════════════
    {
        "section": "384", "act": "IPC",
        "title": "Punishment for Extortion",
        "description": "Whoever commits extortion shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. Extortion means intentionally putting any person in fear of any injury and thereby dishonestly inducing the person to deliver property.",
        "elements": ["Putting person in fear of injury", "Dishonest inducement", "Delivery of property or valuable security"],
        "punishment": "Up to 3 years imprisonment, or fine, or both",
        "cognizable": True, "bailable": False,
        "crime_type": "extortion", "severity": "high",
        "investigation_steps": ["Record detailed victim statement", "Preserve threatening messages/calls", "Set up trap if extortion ongoing", "Trace phone numbers and accounts", "Arrest accused with evidence", "Check for other victims"],
        "example_scenario": "Accused threatens shopkeeper to pay monthly hafta or face damage to shop."
    },
    {
        "section": "308", "act": "BNS",
        "title": "Extortion (BNS)",
        "description": "Whoever commits extortion shall be punished. Replaces IPC Section 384.",
        "elements": ["Fear of injury", "Dishonest inducement", "Delivery of property"],
        "punishment": "Up to 3 years imprisonment, or fine, or both",
        "cognizable": True, "bailable": False,
        "crime_type": "extortion", "severity": "high",
        "investigation_steps": ["Record victim statement", "Preserve evidence of threats", "Technical surveillance", "Trap and arrest", "Identify accomplices"],
        "example_scenario": "Gang demands protection money from construction site workers."
    },

    # ════════════════════════ DEATH BY NEGLIGENCE ════════════════════════
    {
        "section": "304A", "act": "IPC",
        "title": "Causing death by negligence",
        "description": "Whoever causes the death of any person by doing any rash or negligent act not amounting to culpable homicide, shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.",
        "elements": ["Death of a person", "Caused by rash or negligent act", "Not amounting to culpable homicide"],
        "punishment": "Up to 2 years imprisonment, or fine, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "death_by_negligence", "severity": "critical",
        "investigation_steps": ["Secure accident scene", "Conduct inquest proceedings", "Send body for post-mortem", "Record statements of witnesses", "Prepare spot mahazar with measurements", "Check vehicle fitness and driver license", "Collect CCTV footage", "Medical examination of driver for alcohol"],
        "example_scenario": "Truck driver runs over pedestrian due to rash driving on NH road."
    },

    # ════════════════════════ ROBBERY (IPC) ════════════════════════
    {
        "section": "392", "act": "IPC",
        "title": "Punishment for Robbery",
        "description": "Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine; and if the robbery be committed on the highway between sunset and sunrise, the imprisonment may be extended to fourteen years.",
        "elements": ["Theft or extortion", "Use or threat of force", "At the time of or immediately before/after"],
        "punishment": "Up to 10 years RI and fine; up to 14 years if on highway at night",
        "cognizable": True, "bailable": False,
        "crime_type": "robbery", "severity": "high",
        "investigation_steps": ["Record victim statement immediately", "Collect description of robbers", "Check CCTV in area", "Alert patrol vehicles", "Trace stolen property", "Check with informers", "Fingerprint collection at scene"],
        "example_scenario": "Two persons snatch gold chain from woman on road by using force."
    },

    # ════════════════════════ SC/ST ATROCITY ════════════════════════
    {
        "section": "3", "act": "SC/ST (PoA) Act",
        "title": "Offences of atrocities against SC/ST",
        "description": "Whoever, not being a member of a Scheduled Caste or Scheduled Tribe, commits specified offences against members of SC/ST communities including assault, forced labor, land dispossession, sexual exploitation, false litigation, public humiliation, using casteist slurs, shall be punished with imprisonment not less than six months which may extend to five years and with fine.",
        "elements": ["Accused is non-SC/ST", "Victim is SC/ST member", "Specified offence committed", "Caste-based motivation"],
        "punishment": "6 months to 5 years imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "atrocity", "severity": "high",
        "investigation_steps": ["Register FIR under SC/ST Act mandatorily", "Investigation by DSP rank officer", "Record victim statement", "Verify caste certificates of both parties", "Collect witnesses", "No compromise or mediation permitted", "Ensure victim protection", "Provide legal aid to victim"],
        "example_scenario": "Upper caste person publicly humiliates Dalit man using casteist slurs and prevents him from accessing public water source."
    },

    # ════════════════════════ POCSO ════════════════════════
    {
        "section": "4", "act": "POCSO Act",
        "title": "Punishment for penetrative sexual assault on child",
        "description": "Whoever commits penetrative sexual assault on a child shall be punished with imprisonment of either description for a term which shall not be less than seven years but which may extend to imprisonment for life, and shall also be liable to fine. If victim is below 12 years, minimum 20 years RI extending to life imprisonment.",
        "elements": ["Penetrative sexual assault", "Victim is a child (below 18)", "Age of victim determines severity"],
        "punishment": "Minimum 7 years to life imprisonment, and fine",
        "cognizable": True, "bailable": False,
        "crime_type": "sexual_offense", "severity": "critical",
        "investigation_steps": ["Register FIR immediately — no preliminary enquiry", "Record statement by female officer in child-friendly environment", "Medical examination within 24 hours", "Do NOT subject child to repeated questioning", "Arrange for child counselor", "Statement before magistrate under BNSS 183", "Send for forensic evidence collection", "Ensure identity protection of child"],
        "example_scenario": "School teacher commits sexual assault on 10-year-old student."
    },
    {
        "section": "6", "act": "POCSO Act",
        "title": "Aggravated penetrative sexual assault on child",
        "description": "Penetrative sexual assault committed by police officer, armed forces, public servant, management of institution, or gang assault, or repeated assault, or assault causing physical/mental incapacity, or assault on child below 12 years. Minimum punishment enhanced.",
        "elements": ["Penetrative sexual assault", "Aggravating factors present", "Abuse of position of trust"],
        "punishment": "Minimum 10 years to life imprisonment, and fine (below 12: min 20 years)",
        "cognizable": True, "bailable": False,
        "crime_type": "sexual_offense", "severity": "critical",
        "investigation_steps": ["Immediate FIR and arrest", "CWC notification within 24 hours", "Medical examination with detailed documentation", "Statement before magistrate", "Special court fast-track", "Victim compensation application", "No media disclosure of identity"],
        "example_scenario": "Warden of children's home sexually assaults minor residents repeatedly."
    },

    # ════════════════════════ ROAD ACCIDENT ════════════════════════
    {
        "section": "279", "act": "IPC",
        "title": "Rash driving or riding on a public way",
        "description": "Whoever drives any vehicle, or rides, on any public way in a manner so rash or negligent as to endanger human life, or to be likely to cause hurt or injury to any other person, shall be punished with imprisonment of either description for a term which may extend to six months, or with fine which may extend to one thousand rupees, or with both.",
        "elements": ["Driving/riding on public way", "Rash or negligent manner", "Endangering human life or likely to cause injury"],
        "punishment": "Up to 6 months imprisonment, or fine up to Rs 1000, or both",
        "cognizable": True, "bailable": True,
        "crime_type": "rash_driving", "severity": "high",
        "investigation_steps": ["Prepare accident spot mahazar", "Photograph scene with measurements", "Record statements of witnesses", "Seize vehicle and documents", "Medical examination of driver", "Check vehicle fitness certificate", "Obtain accident report from motor vehicle inspector"],
        "example_scenario": "Accused drives car at excessive speed on busy road and nearly hits pedestrians."
    },

    # ════════════════════════ ARMS OFFENSE ════════════════════════
    {
        "section": "25", "act": "Arms Act",
        "title": "Punishment for certain offences — possession of illegal arms",
        "description": "Whoever acquires, has in his possession or carries any firearms or ammunition in contravention of section 3 (without license) shall be punishable with imprisonment for a term which shall not be less than one year but which may extend to three years and shall also be liable to fine.",
        "elements": ["Possession of firearm or ammunition", "Without valid license", "Contravention of Arms Act"],
        "punishment": "1 to 3 years imprisonment, and fine; up to 7 years for prohibited arms",
        "cognizable": True, "bailable": False,
        "crime_type": "arms_offense", "severity": "high",
        "investigation_steps": ["Seize weapon with detailed panchnama", "Check for arms license", "Send weapon for ballistic examination", "Record seizure witnesses", "Check weapon's history in NCRB database", "Verify source of procurement", "Check for connected cases"],
        "example_scenario": "Accused found carrying country-made pistol without license during routine vehicle check."
    },

    # ════════════════════════ MISSING PERSON ════════════════════════
    {
        "section": "174", "act": "CrPC",
        "title": "Police enquiry in case of suicide etc — Missing Person",
        "description": "When a person goes missing, the police shall register a complaint immediately. If person missing is a woman or child below 14 years, an FIR shall be registered immediately. For others, if the person is not traced within 24 hours, an FIR may be registered. Special provisions exist under BNSS 194 for unnatural death inquiry.",
        "elements": ["Person reported missing", "Complaint by family/friend", "Circumstances of disappearance"],
        "punishment": "N/A — procedural section",
        "cognizable": True, "bailable": None,
        "crime_type": "missing_person", "severity": "high",
        "investigation_steps": ["Register complaint immediately (FIR if woman/child)", "Circulate photo and description", "Check last known location and CCTV", "Trace mobile phone", "Check hospitals and mortuaries", "Inform neighboring police stations", "Publish in media if needed", "Check social media for clues"],
        "example_scenario": "Parents report 16-year-old daughter missing after she did not return from school."
    },

    # ════════════════════════ BREACH OF TRUST ════════════════════════
    {
        "section": "406", "act": "IPC",
        "title": "Criminal breach of trust",
        "description": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. Criminal breach of trust is dishonest misappropriation or conversion of property entrusted to a person.",
        "elements": ["Property entrusted to accused", "Dishonest misappropriation", "Violation of trust"],
        "punishment": "Up to 3 years imprisonment, or fine, or both",
        "cognizable": False, "bailable": True,
        "crime_type": "breach_of_trust", "severity": "medium",
        "investigation_steps": ["Collect documentary evidence of entrustment", "Trace misappropriated property/funds", "Record victim statement with documents", "Check financial records", "Verify if civil remedy already pursued"],
        "example_scenario": "Business partner misappropriates Rs 10 lakhs from joint business account for personal use."
    },
]


def _load_extracted_rules():
    import json
    import os
    
    rules_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "rules", "extracted_rules.json")
    if not os.path.exists(rules_file):
        return
        
    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Add to LEGAL_CORPUS if not already present (to preserve our curated metadata)
        existing_keys = {(s["act"].upper(), s["section"]) for s in LEGAL_CORPUS}
        
        added = 0
        for doc in data:
            act = doc["act"]
            for sec in doc["sections"]:
                key = (act.upper(), sec["section"])
                if key not in existing_keys:
                    LEGAL_CORPUS.append({
                        "section": sec["section"],
                        "act": act,
                        "title": sec["title"],
                        "description": sec["description"],
                        "elements": [],
                        "punishment": "See description",
                        "cognizable": None,
                        "bailable": None,
                        "crime_type": "other",
                        "severity": "medium",
                        "investigation_steps": []
                    })
                    added += 1
        print(f"[Legal Corpus] Loaded {added} additional sections from extracted rules.")
    except Exception as e:
        print(f"[Legal Corpus] Error loading extracted rules: {e}")

# Load the dynamic rules immediately
_load_extracted_rules()

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
