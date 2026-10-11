"""
Production Benchmark Evaluation Dataset
40 rigorously formulated operational evaluation scenarios.
"""
from typing import Dict, List, Any

BENCHMARK_TEST_CASES: List[Dict[str, Any]] = [
    {
        "id": "TC_01",
        "category": "Waiting Time",
        "query": "What are the primary factors contributing to long customer wait times during peak dinner rushes?",
        "expected_output": "Long wait times during peak dinner rushes stem from front-of-house host seating pacing bottlenecks, kitchen cook-line ticket backlogs, and delayed busser table turnaround.",
        "expected_root_causes": ['kitchen_ticket_backlog', 'host_seating_pacing', 'busser_turnaround_lapse'],
        "relevant_review_ids": ['f4Gyg3XAwjet3hhpkwiuLg', 'ifQXW99vkoubdkzigzlODw', 'U10waLMgkLQC77EfxgSEag', 'hyavHTS8U_RF341q3VOurw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_02",
        "category": "Waiting Time",
        "query": "Why are guests experiencing severe delays when ordering drinks and waiting at the bar?",
        "expected_output": "Bar delays are driven by single-bartender staffing during surge hours, glassware dishwashing bottlenecks, and service-well ticket priority conflicts.",
        "expected_root_causes": ['bartender_understaffing', 'glassware_shortage', 'service_well_backlog'],
        "relevant_review_ids": ['6WxRDF-o8pvQ9ZAQ9ro4jQ', 'frtuZrQrQiORuFYYUgqCEg', 'hyavHTS8U_RF341q3VOurw', 'c64l7NIJtm2yLKyILj7pgQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_03",
        "category": "Waiting Time",
        "query": "What is causing long lobby queues and slow table assignment on Friday evenings?",
        "expected_output": "Lobby congestion is caused by uncoordinated reservation overbooking, large party table camping, and lack of automated SMS waitlist notifications.",
        "expected_root_causes": ['reservation_overbooking', 'table_camping', 'host_coordination_deficit'],
        "relevant_review_ids": ['y941xDhv3EhupzGw7xui-A', '97bh9C48Kf4Gtq6GtcYk-A', 'dWZqVz-Z1dX2_rEhyXZzag', 'whgIyzqdDR1HQNbieW5QhQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_04",
        "category": "Waiting Time",
        "query": "Why do customers waiting for takeout and curbside pickup report 30-minute delays past the promised time?",
        "expected_output": "Takeout fulfillment delays occur when delivery tablets are unchecked, expo bagging falls behind dine-in plating, and parking space dispatch lacks tracking.",
        "expected_root_causes": ['expo_bagging_backlog', 'tablet_order_desync', 'curbside_dispatch_lag'],
        "relevant_review_ids": ['SlPD0P1ld0p-4lY4T-fz3g', '-1JTtFmo0CIqdG2dkOYKVw', 'vQWHog2wC-KfQAe4vtYGnA', 'hyavHTS8U_RF341q3VOurw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_05",
        "category": "Food Quality",
        "query": "Why are guests reporting that hot entrees and soups are arriving cold or lukewarm at tables?",
        "expected_output": "Cold entrees result from expo heat lamp holding temperature lapses, lack of dedicated food runners, and plated orders sitting on the pass.",
        "expected_root_causes": ['holding_temperature_lapse', 'food_runner_deficit', 'pass_staging_delay'],
        "relevant_review_ids": ['HW1OOzrOyyd_Dqiak7GiJQ', 'qpvF-F2NBAxD-ewR6xQDBQ', 'qqceKeIlqhuQun3Mxh_3_g', 'j4q93mTokUZnmK-X7I9Afw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_06",
        "category": "Food Quality",
        "query": "What causes complaints regarding overcooked steaks and dry, rubbery chicken entrees?",
        "expected_output": "Overcooked proteins are caused by inaccurate grill temperature calibration, unmonitored meat probe thermometer checks, and carry-over heat miscalculations.",
        "expected_root_causes": ['grill_temperature_miscalibration', 'meat_probe_omission', 'carryover_cooking_error'],
        "relevant_review_ids": ['zXAEeX2BVkt_OK2LujZT_A', 'GaFL5Snov1HRlUN0BYAFMQ', 'M0UOMsQczY-HigwaPhJgpA', 'pjUD8t2ek8glIgqwaNU8UA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_07",
        "category": "Food Quality",
        "query": "Why are customers complaining that pasta dishes taste bland and lack fresh seasoning?",
        "expected_output": "Bland pasta dishes occur due to unstandardized prep batch seasoning recipes, skipping pre-shift sauce line tastings, and rushed line prep.",
        "expected_root_causes": ['unstandardized_batch_seasoning', 'pre_shift_tasting_omission'],
        "relevant_review_ids": ['rGp5Qx1lkNXqCSbuH9wNdw', '3NfDdSZ-boDuyOFIj5d8OQ', 'XJtp0TpiXHpbTFEe_XyH8g', 'u10Dg1r61gKaJJP8rGuffg'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_08",
        "category": "Food Quality",
        "query": "What is the reason for reviews mentioning soggy fried appetizers and stale chips?",
        "expected_output": "Soggy fried items stem from fryer oil temperature drops during overloaded basket batches and holding fried goods in unvented packaging.",
        "expected_root_causes": ['fryer_oil_temp_drop', 'overloaded_fry_baskets', 'unvented_holding_steam'],
        "relevant_review_ids": ['xKUaoMHTOzfhrdVx3_oiiQ', 'jtCUPrtmwYNvx9js_0SbtA', 'yWRgGY04nr-CTGrCyMJDZA', 'oo_qhIJbwbxkaAZTDUqrzQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_09",
        "category": "Service Quality",
        "query": "What operational issues cause server inattentiveness and neglected dining sections?",
        "expected_output": "Inattentive service is triggered by assigning servers oversized 6+ table sections, absence of dedicated food runners, and inadequate floor manager zoning audits.",
        "expected_root_causes": ['oversized_table_sections', 'section_zoning_imbalance', 'floor_supervision_gap'],
        "relevant_review_ids": ['geq1SVMhPVzhD7WGz3CKkg', 'URzu89f7a4JUXgqIt_G1MQ', 'qqceKeIlqhuQun3Mxh_3_g', 'fEmS8KysqCG4dve5Pg0R6g'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_10",
        "category": "Service Quality",
        "query": "Why do guests complain that drink refills take 20 minutes and water carafes are never replenished?",
        "expected_output": "Refill delays stem from beverage station syrup backlogs, servers prioritizing check drop-offs, and lack of dedicated busser water replenishment protocols.",
        "expected_root_causes": ['busser_water_protocol_absence', 'beverage_station_backlog'],
        "relevant_review_ids": ['skXFpuUKiqi8Pn1JJeKTaw', '1sbvm_doUKF7ABuT16uqtg', 'CuK_OyoJ7b-jIC8FDwjyIQ', '8xQnGODCp2I_IghLUbLhnA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_11",
        "category": "Service Quality",
        "query": "What factors lead to disorganized service during shift transitions and server handoffs?",
        "expected_output": "Shift transition service breakdowns occur when table handoff notes are skipped between departing and incoming servers without floor manager sign-off.",
        "expected_root_causes": ['shift_handoff_communication_failure', 'manager_signoff_omission'],
        "relevant_review_ids": ['xa2kKzDqzzDnENzdZJGH7g', 'eWTWZD-QcJPuI8QD8CDtXQ', 'fEmS8KysqCG4dve5Pg0R6g', 'PeTek5GE7ajburQ0Edzjyg'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_12",
        "category": "Service Quality",
        "query": "Why are weekday lunch customers struggling to get their bill and finalize payment within 15 minutes?",
        "expected_output": "Slow payment processing during lunch is caused by POS station terminal congestion and failure to offer tableside mobile checkout options.",
        "expected_root_causes": ['pos_terminal_congestion', 'lack_of_tableside_payment'],
        "relevant_review_ids": ['b4tnn9QF8_Lzpes9uINkzA', 'ld56oZqoH-YpvvtzaHGI5g', 'CuK_OyoJ7b-jIC8FDwjyIQ', 'XatlPINVKHU_7QVbNqNuQw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_13",
        "category": "Staff Behavior",
        "query": "What operational stress factors trigger rude server interactions and dismissive attitudes toward guests?",
        "expected_output": "Rude staff interactions arise from back-to-back double shifts without meal breaks, peak shift fatigue, and lack of customer de-escalation training.",
        "expected_root_causes": ['shift_fatigue_and_burnout', 'de_escalation_training_deficit', 'understaffed_shift_stress'],
        "relevant_review_ids": ['Xz2FUhujU96J6qvkxP5ZDw', 'fdwQYTs9OqFnqn5sZVugjA', 'fEmS8KysqCG4dve5Pg0R6g', 'qqceKeIlqhuQun3Mxh_3_g'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_14",
        "category": "Staff Behavior",
        "query": "Why are guests reporting confrontational or defensive behavior from shift managers when handling complaints?",
        "expected_output": "Confrontational management behavior stems from lack of executive guest-recovery autonomy, punitive corporate food-cost policies, and absence of service recovery coaching.",
        "expected_root_causes": ['punitive_comp_policy', 'manager_service_recovery_deficit', 'defensive_leadership_culture'],
        "relevant_review_ids": ['lD8tuXOGvEaw0Yi5ELbW3w', 'xa2kKzDqzzDnENzdZJGH7g', 'umz7pC1yFTffzHkbAaamJA', 'fEmS8KysqCG4dve5Pg0R6g'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_15",
        "category": "Staff Behavior",
        "query": "What causes front-door hostess stand unwelcoming greetings and dismissive seating responses?",
        "expected_output": "Unwelcoming host greetings stem from insufficient front-of-house hospitality onboarding, lack of eye-contact standards, and phone distraction at the podium.",
        "expected_root_causes": ['host_hospitality_training_gap', 'stand_distraction', 'podium_etiquette_lapse'],
        "relevant_review_ids": ['HV5WgnGdlWCeagBeqGdHMA', 'YjCqYgUP2SeyDsdl-YeNpg', 'x9kO_NDhvTT5ss6vkfE2mQ', 'ymVZmqvwqG77sR6LgKOZdw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_16",
        "category": "Staff Behavior",
        "query": "Why do reviews mention kitchen crew shouting or using inappropriate language audible in the dining room?",
        "expected_output": "Audible kitchen disruption occurs when kitchen pass doors are propped open during ticket rushes and expo line acoustic dampening is absent.",
        "expected_root_causes": ['expo_door_propping', 'line_communication_protocol_failure', 'kitchen_noise_leakage'],
        "relevant_review_ids": ['kM4iBqcc6O7am1wSojwK_Q', 'iOyVWYSIF-UF1hlI64z9rA', '8ECIMxt-lTuAQmSRHD1zHA', 'r-dSoC1rlwBaQ_qmo2pL1Q'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_17",
        "category": "Cleanliness",
        "query": "Why are guests seated at sticky dining tables with food crumbs underneath chairs?",
        "expected_output": "Sticky tables and debris result from bussers using dirty sanitizing rag solution buckets and rushing table resets without 2-step surface cleaning.",
        "expected_root_causes": ['sanitizer_bucket_solution_exhaustion', 'single_step_wipe_rush', 'floor_sweeping_omission'],
        "relevant_review_ids": ['CiAdQSYYlhZIuyoTCxCH6g', 'I_HKK3VMkNT5OhDrROAV9w', 'TfaE8O574C6VTmBXHP4pwg', 'FD-WGwV5Ae3r391QDG0XKw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_18",
        "category": "Cleanliness",
        "query": "What causes frequent customer complaints about unsanitary restrooms, empty soap dispensers, and bad odors?",
        "expected_output": "Restroom sanitation failures occur due to skipped 30-minute maintenance log audits, unmonitored dispenser restocking, and floor drain trap drying.",
        "expected_root_causes": ['restroom_log_audit_failure', 'dispenser_restock_omission', 'floor_drain_trap_drying'],
        "relevant_review_ids": ['N780wZSyG8N0nRl818T3TA', 'pF38AJhzJ2eUAONic4MEyg', 'pml2HKaEQKcFwejlBS2WiQ', 'qWKt0SFjGcVZ2nsngt43Cw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_19",
        "category": "Cleanliness",
        "query": "Why are customers finding water spots on glassware and food residue on forks?",
        "expected_output": "Residue on tableware stems from commercial dish machine rinse temperature drops, low detergent titration levels, and lack of post-wash inspection.",
        "expected_root_causes": ['dishwasher_rinse_temp_drop', 'detergent_titration_deficit', 'post_wash_inspection_skip'],
        "relevant_review_ids": ['le9SezW7hDgAwCScfGQkMg', '-gaRXXZD5gBD66aVP6yobQ', 'Xf8TtLY0bL0ueQIYtI20pg', 'RNTxf0DyFWpuH_kOyOiDRg'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_20",
        "category": "Cleanliness",
        "query": "What triggers reports of fruit flies or pest sightings around the bar and floor drain areas?",
        "expected_output": "Fruit fly presence is caused by organic sugar sludge buildup in bar floor drains, unemptied overnight bar fruit bins, and missed enzymatic drain dosing.",
        "expected_root_causes": ['bar_drain_sludge_accumulation', 'overnight_fruit_disposal_lapse', 'enzymatic_cleaner_omission'],
        "relevant_review_ids": ['bc7BTB93QKWuhgQghlAeiA', 'MilGJaBTFhHDWtFXAlaVRw', 'XdfxNAgMLOKPF77nDC3dXw', 'br_A792md_VQbqUHGliNTQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_21",
        "category": "Pricing",
        "query": "Why do customers perceive entree portions as poor value for money compared to menu prices?",
        "expected_output": "Perceived poor value occurs when kitchen line cooks under-portion protein scoops, plate presentation lacks visual volume, and side items are skimped.",
        "expected_root_causes": ['portion_scoop_inconsistency', 'plate_presentation_volume_deficit'],
        "relevant_review_ids": ['_yne182tFt7nKkUyCP-fRg', 'AgDKpn7snaLZcqVn6PXh-g', 'Kj7HMhdzGih7D7FCL13OOw', 'FSrMuCtHqkavYT72k4PswA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_22",
        "category": "Pricing",
        "query": "What triggers disputes regarding unexpected automatic gratuity and hidden service surcharges on guest bills?",
        "expected_output": "Bill fee disputes stem from failure to disclose auto-gratuity on menus or table tents, lack of server verbal heads-up, and compounding surcharge calculations.",
        "expected_root_causes": ['unclear_surcharge_disclosure', 'auto_gratuity_verbal_notice_omission'],
        "relevant_review_ids": ['p3e-U307nTmuHULojgyurQ', '5vAjILoGoAmqVDKrWTxACA', 'pzDGJ5PqbCmhB99e3HSsSg', 'xTgIk2SPFVolShdocy8C0w'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_23",
        "category": "Pricing",
        "query": "Why are guests upset about beverage pricing discrepancies between cocktail menus and final checks?",
        "expected_output": "Beverage check discrepancies occur due to POS price desynchronization between bar and dining room databases, and unlisted premium liquor upcharges.",
        "expected_root_causes": ['pos_price_table_desync', 'unlisted_liquor_modifier_upcharges'],
        "relevant_review_ids": ['5QRxftcBQuQS5P2IxN8wfg', 'adZX3-RP5Mdc0qxOGpHPoQ', 'sGP5b2j3lVLmvtW9HFaMxw', 'FSrMuCtHqkavYT72k4PswA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_24",
        "category": "Pricing",
        "query": "What drives negative feedback about excessive charges for bread service and extra dipping sauces?",
        "expected_output": "Side charge complaints stem from servers failing to communicate sauce fees when asked, creating surprise line-item fees on guest bills.",
        "expected_root_causes": ['uncommunicated_sauce_charges', 'surprise_line_item_fees'],
        "relevant_review_ids": ['PMllK4PPptB_cMVTQTHFFA', 'N99m08tviytKpDTbXybs1w', 'FSrMuCtHqkavYT72k4PswA', 'TN5zaqzkoq7UJABsZXgrFQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_25",
        "category": "Order Accuracy",
        "query": "What operational breakdowns lead to missing entrees and forgotten side dishes in takeout bags?",
        "expected_output": "Missing takeout items occur when expo stations skip the two-step printed ticket checkoff process before stapling bags.",
        "expected_root_causes": ['ticket_staple_verification_omission', 'side_dish_station_desync'],
        "relevant_review_ids": ['jBpK9AFhE4eYEbbwFDJWTg', 'j4K0GL_7n7HQo7UPJueFiQ', 'qqceKeIlqhuQun3Mxh_3_g', 'S6DdiRG1JlhgbD7FZPrrNA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_26",
        "category": "Order Accuracy",
        "query": "Why are allergy dietary modifications (gluten-free, dairy-free) frequently ignored by the kitchen?",
        "expected_output": "Allergy modification errors happen when server special instructions are not highlighted in red on kitchen KDS screens, and expo checks are bypassed.",
        "expected_root_causes": ['kds_allergy_modifier_bypass', 'special_instruction_read_error'],
        "relevant_review_ids": ['KKXiRs0QLLtWJsnkaRhCBQ', 'nlAWdaAcwqfgpRw-jaTeSw', 'hm8YgEiwR1ehlgE6nzM_WQ', 'S6DdiRG1JlhgbD7FZPrrNA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_27",
        "category": "Order Accuracy",
        "query": "What causes tableside food runners to deliver the wrong entrees to neighboring seats or tables?",
        "expected_output": "Wrong table deliveries happen when servers enter incorrect seat pivot numbers into the POS, causing runners to auction off food.",
        "expected_root_causes": ['seat_pivot_number_error', 'food_runner_auctioning'],
        "relevant_review_ids": ['TaI36Dww2QEiQgZY4yNx9w', 'hZ-rzL45wQtRFoz7IYarYg', 'h9Ux8Voooiju5eBC62nqDA', 'UEPq8lbsLmF3DAXp5zizBw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_28",
        "category": "Order Accuracy",
        "query": "Why do customers frequently receive salads drenched in dressing when 'dressing on the side' was requested?",
        "expected_output": "Dressing on the side errors stem from pantry line cooks rushing through salad tosses without checking ticket modifier lines.",
        "expected_root_causes": ['pantry_modifier_oversight', 'ticket_read_rush'],
        "relevant_review_ids": ['4zrWXg13FYyE0AUWrIW0IA', '8ECIMxt-lTuAQmSRHD1zHA', 'grInAm8jANdKRSS1agfClg'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_29",
        "category": "Ambience",
        "query": "Why are dinner guests complaining that dining room background music is too loud for conversation?",
        "expected_output": "Excessive dining music volume results from lack of decibel limiter controls, bar staff turning up playlists during shifts, and unzoned speaker volumes.",
        "expected_root_causes": ['decibel_limiter_absence', 'unzoned_speaker_levels', 'staff_volume_tampering'],
        "relevant_review_ids": ['5QRxftcBQuQS5P2IxN8wfg', 'Oh521hZbx_AK45F3XIzMNw', '4ziEM4irfxxkgeZg8a1XzA', 'qeSxL-POvGLZD6aQ5O9kvw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_30",
        "category": "Ambience",
        "query": "What causes dining room temperature complaints regarding drafty or freezing seating areas?",
        "expected_output": "Freezing dining room temperatures are caused by HVAC damper imbalances directing AC airflow directly onto perimeter booths without seasonal calibration.",
        "expected_root_causes": ['hvac_damper_imbalance', 'unshielded_ac_airflow'],
        "relevant_review_ids": ['Joi6NuKCR70xnnftIsxsfQ', 'Mv3eIYcZmXFRNgwQtbYbcQ', '4ziEM4irfxxkgeZg8a1XzA', '8PtU0lutz85WqmKOhTY-3w'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_31",
        "category": "Ambience",
        "query": "Why do customer reviews describe the main dining room as uncomfortably dark and cramped?",
        "expected_output": "Cramped and dark dining perception results from over-dense floor table spacing below 36 inches and burned-out track lighting bulbs.",
        "expected_root_causes": ['floor_plan_overcrowding', 'lighting_fixture_maintenance_lag'],
        "relevant_review_ids": ['amJUl_664krvMM0PZQmFPw', 'OAYeAC1KBMvd7FEsQdoKdQ', '4ziEM4irfxxkgeZg8a1XzA', 'FD-WGwV5Ae3r391QDG0XKw'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_32",
        "category": "Ambience",
        "query": "What causes complaints regarding kitchen grill smoke or char odor drifting into the main dining area?",
        "expected_output": "Kitchen smoke drifting into the dining area is triggered by negative pressure differentials from exhaust hood motor belt wear and open kitchen pass baffles.",
        "expected_root_causes": ['exhaust_hood_motor_wear', 'negative_air_pressure_differential'],
        "relevant_review_ids": ['6qVrDMaYvaU5Y-5MYd7_7A', 'A2Dsugonr77OImQ9cFPPfg', 'eX2E8-IDykN1iPvMQL49wA', 'IDdXkA0YdNgmpEmCtWev1g'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_33",
        "category": "Multi-Restaurant",
        "query": "How do customer wait times and kitchen turnaround compare across our Italian dining concepts versus casual cafes?",
        "expected_output": "Italian dinner concepts show higher weekend table camping and 12-minute longer ticket latency compared to rapid lunch turnover in casual cafes.",
        "expected_root_causes": ['concept_turnover_differential', 'multi_unit_pacing_variation'],
        "relevant_review_ids": ['2kU1TxcpTXqtmpPA3VBCJw', 'rSs_oqO9ctNAPPZ9d6FclQ', 'U10waLMgkLQC77EfxgSEag', 'fEmS8KysqCG4dve5Pg0R6g'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_34",
        "category": "Multi-Restaurant",
        "query": "Which locations experience higher rates of food temperature and undercooking complaints?",
        "expected_output": "High-volume downtown locations with distant kitchen expo passes report a 14% higher rate of food temperature complaints compared to suburban open-kitchen units.",
        "expected_root_causes": ['expo_runner_distance', 'unit_layout_discrepancy'],
        "relevant_review_ids": ['ch6jJbF9PGRsBx0Ryig1dg', '9EZzyKap_mZTGzv-GcewXw', '2I9mhTz1ON1t8-JS9rnN2A', 'RNTxf0DyFWpuH_kOyOiDRg'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_35",
        "category": "Multi-Restaurant",
        "query": "Compare staff behavior ratings and service attentiveness across different regional branches.",
        "expected_output": "Branches with seasoned floor managers maintain significantly lower staff friction scores, whereas rapidly onboarded locations experience elevated server attitude complaints.",
        "expected_root_causes": ['onboarding_consistency_gap', 'store_manager_experience_variance'],
        "relevant_review_ids": ['GkBOM5osHatgPgQZrk5Qhw', 'SMHJVSvcpoynjN8Kaqpqug', 'AU2k4HWIDgseatn23DGg-A', 'PeTek5GE7ajburQ0Edzjyg'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_36",
        "category": "Ambiguous",
        "query": "Everything went wrong during our visit yesterday and it was completely terrible.",
        "expected_output": "When broad multi-aspect dissatisfaction is reported, the system triages across slow service, order errors, and manager handling to isolate primary root causes.",
        "expected_root_causes": ['compound_service_and_food_failure', 'generalized_shift_breakdown'],
        "relevant_review_ids": ['RuJiFMe2p4sBvq6nc9vRMg', 'p0hyF98o6SSbCTtTcYRXBQ', 'A_zWfscWMEtJjBQ7nD5LHQ', 'YmzrO9LJG0y80YqfJe8EOA'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_37",
        "category": "Ambiguous",
        "query": "I am deeply disappointed with the overall experience and will not be returning.",
        "expected_output": "General churn risk reviews are analyzed by extracting underlying negative sentiment keywords to pinpoint whether failure originated in kitchen timing or server interaction.",
        "expected_root_causes": ['severe_churn_risk', 'unresolved_operational_friction'],
        "relevant_review_ids": ['RrdTwYdxd-PfP_yEUKlydg', '2CFN5WF3DN6Cep6zilESfQ', 'F2W26Q14E6XkTK8b0Nsraw', '4Rwx7s4-Apd1yORzJH80AQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_38",
        "category": "Ambiguous",
        "query": "The place did not live up to expectations given its high star rating.",
        "expected_output": "Expectation gap complaints reflect discrepancies between premium pricing expectations and standard operational delivery, frequently linked to portion sizing or noisy ambience.",
        "expected_root_causes": ['value_expectation_gap', 'premium_pricing_friction'],
        "relevant_review_ids": ['nXkUfGjQ7u-dM6u3jHpJlg', '6CGPUxIIjbxFkjGv27PHsA', 'x-8GwBSYSVYZTlz6wRWd9Q', 'A_zWfscWMEtJjBQ7nD5LHQ'],
        "is_out_of_scope": False
    },
    {
        "id": "TC_39",
        "category": "Out-of-Scope",
        "query": "What is the capital of France and what are its famous monuments?",
        "expected_output": "The capital of France is Paris, famous for monuments such as the Eiffel Tower, Notre-Dame, and the Louvre. (Handled gracefully via general assistant fallback).",
        "expected_root_causes": [],
        "relevant_review_ids": [],
        "is_out_of_scope": True
    },
    {
        "id": "TC_40",
        "category": "Out-of-Scope",
        "query": "Write a Python script to calculate prime numbers using the Sieve of Eratosthenes.",
        "expected_output": "Python implementation of Sieve of Eratosthenes to compute prime numbers up to n. (Handled gracefully via general assistant fallback).",
        "expected_root_causes": [],
        "relevant_review_ids": [],
        "is_out_of_scope": True
    },
]

# Ensure backwards compatibility for consumers expecting ground_truth
for _tc in BENCHMARK_TEST_CASES:
    if "expected_output" in _tc and "ground_truth" not in _tc:
        _tc["ground_truth"] = _tc["expected_output"]
