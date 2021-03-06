import pickle

diagnoosikoodid = {
    "earlier_diagnosis___1" : {"I50", "I50.0", "I50.1", "I50.9", "I11.0", "I13.0", "I13.2", "I42", "I42.0", "I42.1", "I42.2", "I42.3", "I42.4", "I42.5", "I42.6", "I42.7", "I42.8", "I42.9"},
    "earlier_diagnosis___3" : set(),

    "uhdisk_diag___1" : {"J12", "J12.0", "J12.1", "J12.2", "J12.8", "J12.9", "J13", "J14", "J15", "J15.0", "J15.1", "J15.2", "J15.3", "J15.4", "J15.5",
            "J15.6", "J15.7", "J15.8", "J15.9", "J16", "J16.0", "J16.8", "J17", "J17.0", "J17.1", "J17.2", "J17.3", "J17.8", "J18", "J18.0",
            "J18.1", "J18.2", "J18.8", "J18.9", "J85.1", "J69.0", "J69.1", "J69.8"},
    "uhdisk_diag___7" : {"J93", "J93.0", "J93.1", "J93.8", "J93.9", "J94.", "S27.0", "S27.2", "J94.2", "A15.0", "A16.0", "A16.2"},
    "uhdisk_diag___6" : {"J90", "J94.0", "J91", "J94.2", "J94.8", "S27.1", "S27.2"},
    "uhdisk_diag___8" : {"I30", "I30.0", "I30.1", "I30.8", "I30.9", "I31.2", "I31.3", "I31.8", "S26.0", "I31.9", "I23.0"},
    "uhdisk_diag___3" : {"I21", "I21.0", "I21.1", "I21.2", "I21.3", "I21.4", "I21.9", "I22", "I22.0", "I22.1", "I22.8", "I22.9"},
    "uhdisk_diag___4" : {"I26", "I26.0", "I26.9"},
    "uhdisk_diag___2" : {"J81", "I50.1", "J68.1"},
    "uhdisk_diag___5" : {"J44", "J44.0", "J44.1", "J44.8", "J44.9", "J45", "J45.0", "J45.1", "J45.8", "J45.9", "J46"},

    "non_uhdisk_diag___1" : {"R10", "R10.0", "R10.1", "R10.2", "R10.3", "R10.4", "A09", "K56", "K56.0", "K56.1", "K56.2", "K56.3", "K56.4", "K56.5", "K56.6", "K56.7"},
    "non_uhdisk_diag___2" : {"M54", "M51.1", "M54.3", "M54.4", "M54.5", "M54.8", "M54.9"},
    "non_uhdisk_diag___3" : {"R07", "R07.1", "R07.2", "R07.3", "R07.4"},
    "non_uhdisk_diag___4" : {"R51", "G43", "G43.0", "G43.1", "G43.2", "G43.3", "G43.8", "G43.9", "G44", "G44.0", "G44.1", "G44.2", "G44.3", "G44.4", "G44.8", "O29.4", "O74.5", "O89.4"},
    "non_uhdisk_diag___5" : {"N39.0", "N30", "N30.0", "N30.1", "N30.2", "N30.8", "N30.9", "N10", "N11", "N11.0", "N11.1", "N11.8", "N11.9", "N12", "N20.9"},
    "non_uhdisk_diag___6" : {"K80.1", "K81", "K81.0", "K81.1", "K81.8", "K81.9", "K35", "K35.0", "K35.1", "K35.9", "K36", "K65", "K65.0", "K65.8", "K65.9", "K85", "K86.0", "K86.1"},
    "non_uhdisk_diag___7" : {"L03", "L03.0", "L03.1", "L03.2", "L03.3", "L03.8"},
    "non_uhdisk_diag___8" : set(),
    "non_uhdisk_diag___9" : {"I48"},
    "non_uhdisk_diag___10" : {"I49", "I49.8", "I49.9"},
    "non_uhdisk_diag___11" : {"I63", "I63.0", "I63.1", "I63.2", "I63.3", "I63.4", "I63.5", "I63.6", "I63.8", "I63.9", "G45", "G45.0", "G45.1", "G45.2", "G45.8", "G45.9", "I61", "I61.0", "I61.1", "I61.2", "I61.3", "I61.4", "I61.5", "I61.6", "I61.8", "I61.9"},
    "non_uhdisk_diag___12" : {"R42", "H81.1"},
    "non_uhdisk_diag___13" : {"R55", "G90.0", "T67.1"},
    "non_uhdisk_diag___14" : {"G40", "G40.0", "G40.1", "G40.2", "G40.3", "G40.4", "G40.5", "G40.6", "G40.7", "G40.8", "G40.9"},
    "non_uhdisk_diag___15" : {"R03.0"},
    "non_uhdisk_diag___16" : {"F10", "F10.0", "F10.00", "F10.01", "F10.02", "F10.03", "F10.04", "F10.05", "F10.06", "F10.07", "F10.1", "F10.2", "F10.20", "F10.21", "F10.22", "F10.23", "F10.24", "F10.25", "F10.26", "F10.3", "F10.30", "F10.31", "F10.4", "F10.40", "F10.41", "F10.5", "F10.50", "F10.51", "F10.52", "F10.53", "F10.54", "F10.55", "F10.56", "F10.6", "F10.7", "F10.70", "F10.71", "F10.72", "F10.73", "F10.74", "F10.75", "F10.8", "F10.9", "Z72.1"},
    "non_uhdisk_diag___17" : {"J00", "J01", "J01.0", "J01.1", "J01.2", "J01.3", "J01.4", "J01.8", "J01.9", "J02", "J02.0", "J02.8", "J02.9", "J03", "J03.0", "J03.8", "J03.9", "J04", "J04.0", "J04.1", "J04.2", "J05", "J05.0", "J05.1", "J06", "J06.0", "J06.8", "J06.9"},
    "non_uhdisk_diag___18" : {"D69.0", "D72.1", "H01.1", "H65.1", "H65.4", "H65.9", "J30", "J30.1", "J30.2", "J30.3", "J30.4", "J45.0", "J67.7", "J67.8", "J67.9", "L20.8", "L23", "L23.0", "L23.1", "L23.2", "L23.3", "L23.4", "L23.5", "L23.6", "L23.7", "L23.8", "L23.9", "L50.0", "L56.1", "M13.8", "M30.1", "T78.2", "T78.4", "T88.7"},
    "non_uhdisk_diag___19" : {"R11", "F50.5", "P92.0", "K91.0", "O21", "O21.0", "O21.1", "O21.2", "O21.8", "O21.9"},
    "non_uhdisk_diag___20" : set(),
    "non_uhdisk_diag___21" : {"K92.0", "K92.1", "K92.2"},
    "non_uhdisk_diag___22" : {"N20", "N20.0", "N20.1", "N20.2", "N20.9", "N21", "N21.0", "N21.1", "N21.8", "N21.9", "N22", "N22.0", "N22.8", "N23"},
    "non_uhdisk_diag___23" : {"O20", "O20.0", "O20.8", "O20.9"},
    "non_uhdisk_diag___24" : {"R33"}
}

diagnoosikoodid["earlier_diagnosis___2"] = diagnoosikoodid["uhdisk_diag___5"]
pickle.dump(diagnoosikoodid, open("diagnoses_rhk.pickle", "wb"))
