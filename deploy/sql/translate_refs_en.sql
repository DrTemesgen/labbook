-- Translate LabBook's French demo reference data to English (labels only;
-- ids/codes/FKs untouched, so nothing breaks). Re-runnable. Other languages
-- are unaffected (this is data, not the translation packs).
SET NAMES utf8mb4;

-- ===== Roles (profile_role.pro_label) =====
UPDATE profile_role SET pro_label='Administrator'        WHERE pro_ser=1;
UPDATE profile_role SET pro_label='Biologist'            WHERE pro_ser=3;
UPDATE profile_role SET pro_label='Stock manager'        WHERE pro_ser=4;
UPDATE profile_role SET pro_label='Laboratory'           WHERE pro_ser=5;
UPDATE profile_role SET pro_label='Staff'                WHERE pro_ser=6;
UPDATE profile_role SET pro_label='Prescriber'           WHERE pro_ser=7;
UPDATE profile_role SET pro_label='Quality officer'      WHERE pro_ser=8;
UPDATE profile_role SET pro_label='Secretary'            WHERE pro_ser=9;
UPDATE profile_role SET pro_label='Senior secretary'     WHERE pro_ser=10;
UPDATE profile_role SET pro_label='Technician'           WHERE pro_ser=11;
UPDATE profile_role SET pro_label='Senior technician'    WHERE pro_ser=12;
UPDATE profile_role SET pro_label='Quality technician'   WHERE pro_ser=13;
UPDATE profile_role SET pro_label='Sample collector'     WHERE pro_ser=16;
-- (pro_ser 2 'API' and 17 'Agent' kept as-is)

-- ===== Analysis families / disciplines (sigl_dico_data) =====
UPDATE sigl_dico_data SET label='Biochemistry'                                   WHERE id_data=301;
UPDATE sigl_dico_data SET label='Blood biochemistry'                             WHERE id_data=11;
UPDATE sigl_dico_data SET label='Urine biochemistry'                             WHERE id_data=12;
UPDATE sigl_dico_data SET label='Biochemistry LDP'                               WHERE id_data=13;
UPDATE sigl_dico_data SET label='Immunology / hormonology / specific proteins'   WHERE id_data=19;
UPDATE sigl_dico_data SET label='Haematology'                                    WHERE id_data=1001;
UPDATE sigl_dico_data SET label='Haemostasis'                                    WHERE id_data=1002;
UPDATE sigl_dico_data SET label='Cytology'                                       WHERE id_data=278;
UPDATE sigl_dico_data SET label='Haematology, Immunohaematology and Haemostasis' WHERE id_data=279;
UPDATE sigl_dico_data SET label='Immunology'                                     WHERE id_data=1003;
UPDATE sigl_dico_data SET label='Immuno-Serology and Molecular Biology'          WHERE id_data=302;
UPDATE sigl_dico_data SET label='Parasitology'                                   WHERE id_data=15;
UPDATE sigl_dico_data SET label='Mycology'                                       WHERE id_data=16;
UPDATE sigl_dico_data SET label='Virology'                                       WHERE id_data=17;
UPDATE sigl_dico_data SET label='Bacteriology'                                   WHERE id_data=18;
UPDATE sigl_dico_data SET label='Pathological anatomy and cytology'              WHERE id_data=20;
UPDATE sigl_dico_data SET label='Molecular biology'                              WHERE id_data=23;
UPDATE sigl_dico_data SET label='Sanitary analyses'                              WHERE id_data=24;
UPDATE sigl_dico_data SET label='Miscellaneous'                                  WHERE id_data=25;
UPDATE sigl_dico_data SET label='Drugs and toxins'                               WHERE id_data=303;
UPDATE sigl_dico_data SET label='Spermiology'                                    WHERE id_data=304;
UPDATE sigl_dico_data SET label='Antibiotic'                                     WHERE id_data=1018;

-- ===== Sex =====
UPDATE sigl_dico_data SET label='Male'    WHERE id_data=1;
UPDATE sigl_dico_data SET label='Female'  WHERE id_data=2;
UPDATE sigl_dico_data SET label='Unknown' WHERE id_data=3;

-- ===== Billing =====
UPDATE sigl_dico_data SET label='Analysis' WHERE id_data=6;
UPDATE sigl_dico_data SET label='Sample'   WHERE id_data=7;

-- ===== Sampling status =====
UPDATE sigl_dico_data SET label='Done'    WHERE id_data=8;
UPDATE sigl_dico_data SET label='To do'   WHERE id_data=9;
UPDATE sigl_dico_data SET label='Brought' WHERE id_data=10;

-- ===== Title (label + short) =====
UPDATE sigl_dico_data SET label='Mr',        short_label='Mr'   WHERE id_data=260;
UPDATE sigl_dico_data SET label='Mrs',       short_label='Mrs'  WHERE id_data=261;
UPDATE sigl_dico_data SET label='Miss',      short_label='Miss' WHERE id_data=262;
UPDATE sigl_dico_data SET label='Doctor',    short_label='Dr'   WHERE id_data=263;
UPDATE sigl_dico_data SET label='Professor', short_label='Prof' WHERE id_data=264;

-- ===== Record status =====
UPDATE sigl_dico_data SET label='New'                                WHERE id_data=181;
UPDATE sigl_dico_data SET label='Administratively validated'         WHERE id_data=182;
UPDATE sigl_dico_data SET label='Intermediate (admin. validated)'    WHERE id_data=253;
UPDATE sigl_dico_data SET label='Technically validated'              WHERE id_data=254;
UPDATE sigl_dico_data SET label='Intermediate (tech. validated)'     WHERE id_data=255;
UPDATE sigl_dico_data SET label='Biologically validated'             WHERE id_data=256;

-- ===== Cancellation reason =====
UPDATE sigl_dico_data SET label='Insufficient pathological specimen'   WHERE id_data=270;
UPDATE sigl_dico_data SET label='Test removed due to previous results' WHERE id_data=271;
UPDATE sigl_dico_data SET label='Problem with pathological specimen'   WHERE id_data=272;
UPDATE sigl_dico_data SET label='Negative culture'                    WHERE id_data=273;
UPDATE sigl_dico_data SET label='Other'                               WHERE id_data=274;

-- ===== Quantity (count) =====
UPDATE sigl_dico_data SET label='None'          WHERE id_data=315;
UPDATE sigl_dico_data SET label='Rare'          WHERE id_data=316;
UPDATE sigl_dico_data SET label='A few'         WHERE id_data=317;
UPDATE sigl_dico_data SET label='Numerous'      WHERE id_data=318;
UPDATE sigl_dico_data SET label='Very numerous' WHERE id_data=319;

-- ===== Equipment status (label + short) =====
UPDATE sigl_dico_data SET label='Functional',              short_label='OK'              WHERE id_data=1768;
UPDATE sigl_dico_data SET label='Non functional',          short_label='Non funct.'      WHERE id_data=1769;
UPDATE sigl_dico_data SET label='Out of order (awaiting repair)', short_label='Out (rep.)' WHERE id_data=1770;
UPDATE sigl_dico_data SET label='Damaged',                 short_label='Damaged'         WHERE id_data=1771;
UPDATE sigl_dico_data SET label='Faulty',                  short_label='Faulty'          WHERE id_data=1772;
UPDATE sigl_dico_data SET label='Under maintenance',       short_label='Maintenance'     WHERE id_data=1773;
UPDATE sigl_dico_data SET label='Obsolete / Discarded',    short_label='Obsolete'        WHERE id_data=1774;
UPDATE sigl_dico_data SET label='In stock / Reserved',     short_label='Stock/Resv'      WHERE id_data=1775;

-- ===== Product type =====
UPDATE sigl_dico_data SET label='Consumables'      WHERE id_data=1163;
UPDATE sigl_dico_data SET label='General reagents' WHERE id_data=1164;
UPDATE sigl_dico_data SET label='Chemicals'        WHERE id_data=1165;
UPDATE sigl_dico_data SET label='Hygiene and safety' WHERE id_data=1166;
UPDATE sigl_dico_data SET label='Biochemistry'     WHERE id_data=1167;
UPDATE sigl_dico_data SET label='Haematology'      WHERE id_data=1168;
UPDATE sigl_dico_data SET label='Serology'         WHERE id_data=1169;
UPDATE sigl_dico_data SET label='Bacteriology'     WHERE id_data=1178;
UPDATE sigl_dico_data SET label='Parasitology'     WHERE id_data=1179;
UPDATE sigl_dico_data SET label='Virology'         WHERE id_data=1180;

-- ===== Product conservation =====
UPDATE sigl_dico_data SET label='Room temperature' WHERE id_data=1176;

-- ===== Control period (label + short) =====
UPDATE sigl_dico_data SET label='No',      short_label='No'      WHERE id_data=1059;
UPDATE sigl_dico_data SET label='Daily',   short_label='Daily'   WHERE id_data=1061;
UPDATE sigl_dico_data SET label='Weekly',  short_label='Weekly'  WHERE id_data=1063;
UPDATE sigl_dico_data SET label='Monthly', short_label='Monthly' WHERE id_data=1065;
UPDATE sigl_dico_data SET label='Annual',  short_label='Annual'  WHERE id_data=1067;

-- ===== Sections (label + short) =====
UPDATE sigl_dico_data SET label='Sampling',     short_label='Sampling'     WHERE id_data=1039;
UPDATE sigl_dico_data SET label='Biochemistry', short_label='Biochemistry' WHERE id_data=1040;
UPDATE sigl_dico_data SET label='Haematology',  short_label='Haematology'  WHERE id_data=1041;
UPDATE sigl_dico_data SET label='Serology',     short_label='Serology'     WHERE id_data=1042;
UPDATE sigl_dico_data SET label='Microbiology', short_label='Microbiology' WHERE id_data=1043;

-- ===== Profile (mirrors roles) =====
UPDATE sigl_dico_data SET label='Secretary'          WHERE id_data=175;
UPDATE sigl_dico_data SET label='Senior secretary'   WHERE id_data=1160;
UPDATE sigl_dico_data SET label='Quality officer'    WHERE id_data=1161;
UPDATE sigl_dico_data SET label='Prescriber'         WHERE id_data=1162;
UPDATE sigl_dico_data SET label='Technician'         WHERE id_data=176;
UPDATE sigl_dico_data SET label='Senior technician'  WHERE id_data=1158;
UPDATE sigl_dico_data SET label='Quality technician' WHERE id_data=1159;
UPDATE sigl_dico_data SET label='Biologist'          WHERE id_data=177;
UPDATE sigl_dico_data SET label='Administrator'      WHERE id_data=266;

-- ===== Flora abundance =====
UPDATE sigl_dico_data SET label='scant'         WHERE id_data=491;
UPDATE sigl_dico_data SET label='low abundance' WHERE id_data=492;
UPDATE sigl_dico_data SET label='abundant'      WHERE id_data=493;
UPDATE sigl_dico_data SET label='very abundant' WHERE id_data=494;
UPDATE sigl_dico_data SET label='absent'        WHERE id_data=1105;

-- ===== Stool aspect =====
UPDATE sigl_dico_data SET label='Formed'          WHERE id_data=305;
UPDATE sigl_dico_data SET label='Pasty'           WHERE id_data=306;
UPDATE sigl_dico_data SET label='Hard'            WHERE id_data=307;
UPDATE sigl_dico_data SET label='Mucous'          WHERE id_data=308;
UPDATE sigl_dico_data SET label='Mucous-bloody'   WHERE id_data=309;
UPDATE sigl_dico_data SET label='Pasty bloody'    WHERE id_data=310;
UPDATE sigl_dico_data SET label='Liquid bloody'   WHERE id_data=311;
UPDATE sigl_dico_data SET label='Liquid'          WHERE id_data=312;
UPDATE sigl_dico_data SET label='Semi-liquid'     WHERE id_data=313;
UPDATE sigl_dico_data SET label='Greenish'        WHERE id_data=314;
UPDATE sigl_dico_data SET label='Soft'            WHERE id_data=1076;

-- ===== Urethral sample aspect =====
UPDATE sigl_dico_data SET label='Swab'                WHERE id_data=809;
UPDATE sigl_dico_data SET label='No discharge'        WHERE id_data=810;
UPDATE sigl_dico_data SET label='Purulent discharge'  WHERE id_data=811;
UPDATE sigl_dico_data SET label='Colourless discharge' WHERE id_data=812;
UPDATE sigl_dico_data SET label='Bloody discharge'    WHERE id_data=813;

-- ===== Sample type =====
UPDATE sigl_dico_data SET label='Waste water'             WHERE id_data=1015;
UPDATE sigl_dico_data SET label='Surface water'           WHERE id_data=1016;
UPDATE sigl_dico_data SET label='Joint puncture fluid'    WHERE id_data=34;
UPDATE sigl_dico_data SET label='Ascites puncture fluid'  WHERE id_data=35;
UPDATE sigl_dico_data SET label='Biopsy'                  WHERE id_data=38;
UPDATE sigl_dico_data SET label='Drinking water'          WHERE id_data=1014;
UPDATE sigl_dico_data SET label='Sputum'                  WHERE id_data=50;
UPDATE sigl_dico_data SET label='Bronchoalveolar lavage'  WHERE id_data=56;
UPDATE sigl_dico_data SET label='Throat sample'           WHERE id_data=75;
UPDATE sigl_dico_data SET label='Cerebrospinal fluid'     WHERE id_data=99;
UPDATE sigl_dico_data SET label='Bronchial puncture fluid' WHERE id_data=100;
UPDATE sigl_dico_data SET label='Alveolar puncture fluid' WHERE id_data=102;
UPDATE sigl_dico_data SET label='Pleural puncture fluid'  WHERE id_data=104;
UPDATE sigl_dico_data SET label='Blood'                   WHERE id_data=138;
UPDATE sigl_dico_data SET label='Stool'                   WHERE id_data=141;
UPDATE sigl_dico_data SET label='Pus sample'              WHERE id_data=1189;
UPDATE sigl_dico_data SET label='Urethral sample'         WHERE id_data=152;
UPDATE sigl_dico_data SET label='Urine'                   WHERE id_data=153;
UPDATE sigl_dico_data SET label='Vaginal sample'          WHERE id_data=162;
UPDATE sigl_dico_data SET label='Genital sample'          WHERE id_data=1000;
UPDATE sigl_dico_data SET label='Nasopharyngeal swab'     WHERE id_data=1776;
UPDATE sigl_dico_data SET label='Oropharyngeal swab'      WHERE id_data=1777;
UPDATE sigl_dico_data SET label='Nasal swab'              WHERE id_data=1778;
UPDATE sigl_dico_data SET label='Other'                   WHERE id_data=163;

-- ===== Result type (config labels) =====
UPDATE sigl_dico_data SET label='Label'                          WHERE id_data=265;
UPDATE sigl_dico_data SET label='Character string'               WHERE id_data=226;
UPDATE sigl_dico_data SET label='Integer'                        WHERE id_data=227;
UPDATE sigl_dico_data SET label='Malaria species'                WHERE id_data=617;
UPDATE sigl_dico_data SET label='Real (number)'                  WHERE id_data=228;
UPDATE sigl_dico_data SET label='Calculated'                     WHERE id_data=229;
UPDATE sigl_dico_data SET label='Positive / negative'            WHERE id_data=230;
UPDATE sigl_dico_data SET label='Positive/Negative/Indeterminate' WHERE id_data=635;
UPDATE sigl_dico_data SET label='Yes / No'                       WHERE id_data=231;
UPDATE sigl_dico_data SET label='Absent / Present'               WHERE id_data=246;
UPDATE sigl_dico_data SET label='Abundance'                      WHERE id_data=583;
UPDATE sigl_dico_data SET label='Stool aspect'                   WHERE id_data=584;
UPDATE sigl_dico_data SET label='Genital sample aspect'          WHERE id_data=585;
UPDATE sigl_dico_data SET label='AFB'                            WHERE id_data=614;
UPDATE sigl_dico_data SET label='Urethral sample aspect'         WHERE id_data=808;
UPDATE sigl_dico_data SET label='Bacteria'                       WHERE id_data=586;
UPDATE sigl_dico_data SET label='Broth'                          WHERE id_data=587;
UPDATE sigl_dico_data SET label='Crystals'                       WHERE id_data=588;
UPDATE sigl_dico_data SET label='Cast'                           WHERE id_data=589;
UPDATE sigl_dico_data SET label='Flora'                          WHERE id_data=590;
UPDATE sigl_dico_data SET label='Yeast form'                     WHERE id_data=591;
UPDATE sigl_dico_data SET label='Balanced/unbalanced'            WHERE id_data=1142;
UPDATE sigl_dico_data SET label='Germ'                           WHERE id_data=592;

-- ===== Specialties =====
UPDATE sigl_dico_data SET label='Allergist'                  WHERE id_data=186;
UPDATE sigl_dico_data SET label='Andrologist'                WHERE id_data=187;
UPDATE sigl_dico_data SET label='Pathologist'                WHERE id_data=189;
UPDATE sigl_dico_data SET label='Anaesthetist'               WHERE id_data=190;
UPDATE sigl_dico_data SET label='Oncologist'                 WHERE id_data=192;
UPDATE sigl_dico_data SET label='Cardiologist'               WHERE id_data=193;
UPDATE sigl_dico_data SET label='Surgeon'                    WHERE id_data=194;
UPDATE sigl_dico_data SET label='Dermatologist'              WHERE id_data=195;
UPDATE sigl_dico_data SET label='Endocrinologist'            WHERE id_data=196;
UPDATE sigl_dico_data SET label='Gastroenterologist'         WHERE id_data=197;
UPDATE sigl_dico_data SET label='Geneticist'                 WHERE id_data=198;
UPDATE sigl_dico_data SET label='Geriatrician'               WHERE id_data=199;
UPDATE sigl_dico_data SET label='Gynaecologist'              WHERE id_data=200;
UPDATE sigl_dico_data SET label='Haematologist'              WHERE id_data=201;
UPDATE sigl_dico_data SET label='Infectious disease specialist' WHERE id_data=202;
UPDATE sigl_dico_data SET label='General practitioner'       WHERE id_data=204;
UPDATE sigl_dico_data SET label='Emergency physician'        WHERE id_data=205;
UPDATE sigl_dico_data SET label='Occupational medicine'      WHERE id_data=206;
UPDATE sigl_dico_data SET label='Nutritionist - dietician'   WHERE id_data=207;
UPDATE sigl_dico_data SET label='Nephrologist'               WHERE id_data=208;
UPDATE sigl_dico_data SET label='Neurosurgeon'               WHERE id_data=209;
UPDATE sigl_dico_data SET label='Neurologist'                WHERE id_data=210;
UPDATE sigl_dico_data SET label='Oncologist'                 WHERE id_data=211;
UPDATE sigl_dico_data SET label='Ophthalmologist'            WHERE id_data=212;
UPDATE sigl_dico_data SET label='ENT specialist'             WHERE id_data=213;
UPDATE sigl_dico_data SET label='Paediatrician'              WHERE id_data=215;
UPDATE sigl_dico_data SET label='Child psychiatrist'         WHERE id_data=216;
UPDATE sigl_dico_data SET label='Psychiatrist'               WHERE id_data=217;
UPDATE sigl_dico_data SET label='Radiologist'                WHERE id_data=219;
UPDATE sigl_dico_data SET label='Rheumatologist'             WHERE id_data=220;
UPDATE sigl_dico_data SET label='Stomatologist'              WHERE id_data=221;
UPDATE sigl_dico_data SET label='Urologist'                  WHERE id_data=222;
UPDATE sigl_dico_data SET label='Dentist'                    WHERE id_data=225;
UPDATE sigl_dico_data SET label='Orthopaedic surgeon'        WHERE id_data=1006;
UPDATE sigl_dico_data SET label='Nurse'                      WHERE id_data=1007;
UPDATE sigl_dico_data SET label='Midwife'                    WHERE id_data=1008;
UPDATE sigl_dico_data SET label='Pulmonologist'              WHERE id_data=1009;
UPDATE sigl_dico_data SET label='Internal medicine'          WHERE id_data=1010;

-- ===== Specialty short labels (the displayed abbreviations) =====
UPDATE sigl_dico_data SET short_label='Anaesth.'     WHERE id_data=190;
UPDATE sigl_dico_data SET short_label='Oncol.'       WHERE id_data=192;
UPDATE sigl_dico_data SET short_label='Genet.'       WHERE id_data=198;
UPDATE sigl_dico_data SET short_label='Geriatr.'     WHERE id_data=199;
UPDATE sigl_dico_data SET short_label='Gynae.'       WHERE id_data=200;
UPDATE sigl_dico_data SET short_label='Haemat.'      WHERE id_data=201;
UPDATE sigl_dico_data SET short_label='ID spec.'     WHERE id_data=202;
UPDATE sigl_dico_data SET short_label='GP'           WHERE id_data=204;
UPDATE sigl_dico_data SET short_label='Occ. med.'    WHERE id_data=206;
UPDATE sigl_dico_data SET short_label='Nephro.'      WHERE id_data=208;
UPDATE sigl_dico_data SET short_label='Paediatr.'    WHERE id_data=215;
UPDATE sigl_dico_data SET short_label='Child psych.' WHERE id_data=216;
UPDATE sigl_dico_data SET short_label='Nurse'        WHERE id_data=1007;
UPDATE sigl_dico_data SET short_label='Int. med.'    WHERE id_data=1010;

-- ===== Result type (remaining displayed labels; short_label is a dico_ code, left intact) =====
UPDATE sigl_dico_data SET label='None to very numerous'               WHERE id_data=599;
UPDATE sigl_dico_data SET label='Resistant / Sensitive'              WHERE id_data=600;
UPDATE sigl_dico_data SET label='Culture result'                    WHERE id_data=603;
UPDATE sigl_dico_data SET label='Yeast (presence)'                  WHERE id_data=609;
UPDATE sigl_dico_data SET label='Resistant/Sensitive/Not applicable' WHERE id_data=1012;
UPDATE sigl_dico_data SET label='Phenotypes'                        WHERE id_data=1188;

-- ===== Sample type short labels =====
UPDATE sigl_dico_data SET short_label='Nasophar.' WHERE id_data=1776;
UPDATE sigl_dico_data SET short_label='Orophar.'  WHERE id_data=1777;
