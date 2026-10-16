#!/usr/bin/env python3
"""
generate_seed.py: Deterministic Seed Data Generator for Disaster Relief Logistics DB.
Creates /db/02_seed.sql meeting all exact schema constraints and engineered edge cases.
"""

import sys
import os
from datetime import date, timedelta

def main():
    out_path = os.path.join(os.path.dirname(__file__), "..", "db", "02_seed.sql")
    out_path = os.path.abspath(out_path)

    sql_lines = []
    def emit(line=""):
        sql_lines.append(line)

    def q(s):
        if s is None:
            return "NULL"
        return "'" + str(s).replace("'", "''") + "'"

    emit("-- ============================================================================")
    emit("-- 02_seed.sql: Deterministic Seed Data (Indian Disaster Relief Context)")
    emit("-- Temporal Scope: 2026-01-01 to 2026-09-30")
    emit("-- ============================================================================")
    emit()
    emit("BEGIN;")
    emit()

    # 1. relief_camp (12 camps)
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 1. RELIEF CAMPS (12 Camps across disaster-prone Indian districts)")
    emit("-- ----------------------------------------------------------------------------")
    camps = [
        ("Meppadi High School Relief Camp", "Wayanad", 100, "active"),          # Camp 1 (Target: >90% capacity)
        ("Kalpetta Community Shelter", "Wayanad", 120, "active"),              # Camp 2
        ("Silchar Central Flood Shelter", "Cachar", 150, "active"),            # Camp 3 (Target: NO medical volunteers)
        ("Hailakandi Town Hall Camp", "Hailakandi", 80, "active"),             # Camp 4
        ("Joshimath Sector A Transit Camp", "Chamoli", 90, "active"),          # Camp 5
        ("Karnaprayag Relief Center", "Chamoli", 110, "active"),               # Camp 6
        ("Kendrapara Cyclone Shelter No. 1", "Kendrapara", 140, "active"),     # Camp 7
        ("Paradip Coastal Care Camp", "Jagatsinghpur", 130, "active"),         # Camp 8
        ("Mandi Valley Emergency Camp", "Mandi", 95, "active"),                # Camp 9
        ("Kullu Relief Hub", "Kullu", 100, "active"),                          # Camp 10
        ("Uttarkashi Base Camp", "Uttarkashi", 85, "active"),                  # Camp 11
        ("Rudraprayag Youth Shelter", "Rudraprayag", 110, "active"),           # Camp 12
    ]
    emit("INSERT INTO relief_camp (camp_name, district, capacity, status) VALUES")
    camp_vals = [f"  ({q(c[0])}, {q(c[1])}, {c[2]}, {q(c[3])})" for c in camps]
    emit(",\n".join(camp_vals) + ";")
    emit()

    # 2. supply_item (40 items across 6 categories)
    # Edge case 5: Item 39 is requested but NEVER shipped.
    #              Item 40 is shipped but NEVER requested.
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 2. SUPPLY ITEMS (40 items across 6 categories)")
    emit("-- Edge Case: Item 39 requested but never shipped; Item 40 shipped but never requested")
    emit("-- ----------------------------------------------------------------------------")
    items = [
        # food (8)
        ("Rice (25kg bag)", "food", "bag"),
        ("Wheat Flour (10kg bag)", "food", "bag"),
        ("Toor Dal (5kg packet)", "food", "packet"),
        ("Mustard Oil (1L pouch)", "food", "pouch"),
        ("Baby Food Cereal (500g tin)", "food", "tin"),
        ("Biscuits (Carton of 50)", "food", "carton"),
        ("Iodized Salt (1kg packet)", "food", "packet"),
        ("Ready-to-Eat Khichdi Meals", "food", "packet"),
        # water (6)
        ("Packaged Drinking Water (20L Jar)", "water", "jar"),
        ("Mineral Water Bottles (1L Carton)", "water", "carton"),
        ("Water Purification Tablets (100 tab box)", "water", "box"),
        ("Chlorine Drops (100ml bottle)", "water", "bottle"),
        ("Mobile Water Filter Unit", "water", "unit"),
        ("Jerry Can 10L", "water", "can"),
        # medical (8)
        ("First Aid Kit (Comprehensive)", "medical", "kit"),
        ("Paracetamol 500mg (Strips of 10)", "medical", "strip"),
        ("Oral Rehydration Salts (ORS 50 pkts)", "medical", "box"),
        ("Bandage Rolls (Pack of 12)", "medical", "pack"),
        ("Antiseptic Liquid (500ml)", "medical", "bottle"),
        ("Ciprofloxacin 500mg", "medical", "strip"),
        ("Disposable Syringes (Pack of 50)", "medical", "box"),
        ("Emergency Trauma Dressing", "medical", "piece"),
        # shelter (6)
        ("Family Tarpaulin 15x12 ft", "shelter", "piece"),
        ("Waterproof Groundsheet 12x10 ft", "shelter", "piece"),
        ("Nylon Rope (30m bundle)", "shelter", "bundle"),
        ("Foldable Steel Cot", "shelter", "cot"),
        ("Bamboo Poles (Bundle of 5)", "shelter", "bundle"),
        ("Solar Lantern (Emergency)", "shelter", "unit"),
        # clothing (6)
        ("Woolen Blanket (Heavy)", "clothing", "piece"),
        ("Cotton Bedsheets (Double)", "clothing", "piece"),
        ("Men's Dhoti & Kurta Set", "clothing", "set"),
        ("Women's Saree & Blouse Set", "clothing", "set"),
        ("Children's Thermal Wear Set", "clothing", "set"),
        ("Rain Ponchos (Pack of 5)", "clothing", "pack"),
        # hygiene (6)
        ("Sanitary Napkins (Pack of 20)", "hygiene", "pack"),
        ("Bathing Soap (Pack of 4)", "hygiene", "pack"),
        ("Detergent Powder (1kg pack)", "hygiene", "pack"),
        ("Toothpaste & Brush Family Kit", "hygiene", "kit"),
        ("Antiseptic Hand Wash (250ml)", "hygiene", "bottle"),   # Item 39: REQUESTED ONLY, NEVER SHIPPED
        ("Mosquito Repellent Ointment", "hygiene", "tube"),     # Item 40: SHIPPED ONLY, NEVER REQUESTED
    ]
    emit("INSERT INTO supply_item (item_name, category, unit) VALUES")
    item_vals = [f"  ({q(it[0])}, {q(it[1])}, {q(it[2])})" for it in items]
    emit(",\n".join(item_vals) + ";")
    emit()

    # 3. donor (25 donors)
    # Edge case 1 & 2: Donor 1 (PM National Relief Fund) ships to ALL 12 camps and across ALL 9 months
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 3. DONORS (25 Donors across 4 donor types)")
    emit("-- Edge Case: Donor 1 ships to all 12 camps and in all 9 months (Jan-Sep 2026)")
    emit("-- ----------------------------------------------------------------------------")
    donors = [
        ("PM National Relief Fund", "government", "011-23012312"),                 # Donor 1 (All camps, all 9 months)
        ("Tata Community Initiatives Trust", "corporate", "022-66658282"),        # Donor 2
        ("Goonj Disaster Relief NGO", "ngo", "011-26972351"),                       # Donor 3
        ("Red Cross Society of India", "ngo", "011-23716441"),                     # Donor 4
        ("Reliance Foundation Relief Team", "corporate", "022-44770000"),          # Donor 5
        ("Infosys Disaster Care Cell", "corporate", "080-28520261"),               # Donor 6
        ("Dr. Anandita Sen", "individual", "9830112345"),                          # Donor 7
        ("Col. Rajeshwar Chauhan (Retd)", "individual", "9811223344"),             # Donor 8
        ("Oxfam India Response", "ngo", "011-46538000"),                           # Donor 9
        ("SEEDS India Relief Division", "ngo", "011-26174208"),                     # Donor 10
        ("Adani Foundation", "corporate", "079-26565555"),                         # Donor 11
        ("Wipro Cares Foundation", "corporate", "080-28440011"),                   # Donor 12
        ("HelpAge India", "ngo", "011-41688955"),                                  # Donor 13
        ("State Disaster Mitigation Authority", "government", "0471-2331639"),     # Donor 14
        ("Smt. Sunita Deshmukh", "individual", "9820334455"),                      # Donor 15
        ("Shri Vikramaditya Singhania", "individual", "9810445566"),              # Donor 16
        ("Bharat Petroleum CSR Relief", "corporate", "022-22713000"),              # Donor 17
        ("Habitat for Humanity India", "ngo", "022-67846868"),                     # Donor 18
        ("Ramakrishna Mission Seva Pratishthan", "ngo", "033-24753636"),           # Donor 19
        ("ActionAid Association India", "ngo", "011-40640500"),                    # Donor 20
        ("Mahindra Foundation", "corporate", "022-24901441"),                      # Donor 21
        ("Prof. K. R. Nambiar", "individual", "9447112233"),                       # Donor 22
        ("Larsen & Toubro Public Charitable Trust", "corporate", "022-67525656"),  # Donor 23
        ("CARE India Solutions", "ngo", "011-49241111"),                           # Donor 24
        ("District Magistrate Relief Fund", "government", "0135-2622340"),         # Donor 25
    ]
    emit("INSERT INTO donor (donor_name, donor_type, phone) VALUES")
    donor_vals = [f"  ({q(d[0])}, {q(d[1])}, {q(d[2])})" for d in donors]
    emit(",\n".join(donor_vals) + ";")
    emit()

    # 4. volunteer (60 volunteers)
    # Edge case 6: Camp 3 has NO medical-skilled volunteers.
    # Edge case 9: Two volunteers with the same skill at Camp 1 (e.g. Volunteer 3 and 4: nursing).
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 4. VOLUNTEERS (60 volunteers across diverse emergency relief skills)")
    emit("-- ----------------------------------------------------------------------------")
    vols = [
        ("Dr. Arvind Sharma", "9811122301", "medical"),              # 1
        ("Dr. Priya Namboodiri", "9811122302", "medical"),          # 2
        ("Sister Mary Joseph", "9811122303", "nursing"),            # 3 (Nursing at Camp 1)
        ("Sister Latha Kurien", "9811122304", "nursing"),           # 4 (Nursing at Camp 1 -> Edge Case 9)
        ("Rohan Deshmukh", "9811122305", "logistics"),              # 5 (Assigned Camp 3)
        ("Amitabh Sen", "9811122306", "search_and_rescue"),         # 6 (Assigned Camp 3)
        ("Gurpreet Singh", "9811122307", "cooking"),                # 7 (Assigned Camp 3)
        ("Manish Tiwari", "9811122308", "driving"),                 # 8 (Assigned Camp 3)
        ("Dr. Kavita Nair", "9811122309", "medical"),               # 9
        ("Farhan Akhtar", "9811122310", "logistics"),               # 10 (Expired cert, currently assigned -> Edge Case 4)
        ("Deepak Joshi", "9811122311", "search_and_rescue"),        # 11
        ("Pooja Hegde", "9811122312", "counselling"),               # 12
        ("Suresh Prabhu", "9811122313", "driving"),                 # 13
        ("Ananya Roy", "9811122314", "logistics"),                  # 14
        ("Karan Verma", "9811122315", "search_and_rescue"),         # 15
        ("Dr. Bikas Das", "9811122316", "medical"),                 # 16
        ("Meenakshi Sundaram", "9811122317", "cooking"),            # 17
        ("Vikram Rathore", "9811122318", "logistics"),              # 18
        ("Harish Rawat", "9811122319", "driving"),                  # 19
        ("Dr. Sneha Patil", "9811122320", "medical"),               # 20
        ("Rakesh Pandey", "9811122321", "search_and_rescue"),       # 21
        ("Fatima Begum", "9811122322", "cooking"),                 # 22
        ("Nitin Gadkari", "9811122323", "logistics"),               # 23
        ("Sunil Chhetri", "9811122324", "driving"),                 # 24
        ("Dr. Tarun Gogoi", "9811122325", "medical"),               # 25
        ("Archana Puran", "9811122326", "counselling"),             # 26
        ("Devendra Jhajharia", "9811122327", "logistics"),          # 27
        ("Sanjay Manjrekar", "9811122328", "driving"),              # 28
        ("Gauri Shinde", "9811122329", "cooking"),                  # 29
        ("Dr. Alok Nath", "9811122330", "medical"),                 # 30
    ]
    # Volunteers 31 to 60
    other_skills = ["logistics", "cooking", "driving", "search_and_rescue", "counselling", "nursing", "medical"]
    fnames = ["Arun", "Bhavna", "Chirag", "Divya", "Eshwar", "Geeta", "Hemant", "Indira", "Jitendra", "Kiran",
              "Laxman", "Manoj", "Neelam", "Omkar", "Pratibha", "Qasim", "Radha", "Satish", "Tanvi", "Umesh",
              "Varun", "Wahida", "Xavier", "Yogesh", "Zoya", "Ashok", "Bindu", "Chetan", "Damodar", "Ekta"]
    lnames = ["Bose", "Chatterjee", "Dutta", "Goswami", "Iyengar", "Jha", "Kulkarni", "Lodhi", "Mishra", "Naik",
              "Oza", "Patnaik", "Qureshi", "Reddy", "Srinivasan", "Tripathi", "Upadhyay", "Venkatesh", "Wani", "Yadav"]
    for i in range(30):
        vols.append((f"{fnames[i]} {lnames[i % len(lnames)]}", f"98223344{i:02d}", other_skills[i % len(other_skills)]))

    emit("INSERT INTO volunteer (volunteer_name, phone, skill) VALUES")
    vol_vals = [f"  ({q(v[0])}, {q(v[1])}, {q(v[2])})" for v in vols]
    emit(",\n".join(vol_vals) + ";")
    emit()


    # 5. volunteer_certification (~90 certifications)
    # Edge case 4: Volunteer 10 (Farhan Akhtar) has expired certification (e.g. expired 2026-03-01) and is assigned to Camp 1!
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 5. VOLUNTEER CERTIFICATIONS (Weak Entity: PK (volunteer_id, cert_no))")
    emit("-- Edge Case: Volunteer 10 has an expired certification and is currently assigned")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO volunteer_certification (volunteer_id, cert_no, cert_name, issued_by, expiry_date) VALUES")
    cert_vals = []
    # Volunteer 10 (Farhan Akhtar) expired cert
    cert_vals.append("  (10, 1, 'Hazardous Material Handling', 'National Disaster Management Authority', '2026-03-01')")
    # Medical doctors with valid certs
    med_certs = [
        (1, 1, "Advanced Trauma Life Support", "All India Institute of Medical Sciences", "2027-12-31"),
        (1, 2, "Disaster Triage Specialist", "Indian Red Cross", "2028-06-30"),
        (2, 1, "Emergency Pediatric Care", "Indian Academy of Pediatrics", "2027-05-15"),
        (9, 1, "Public Health in Emergencies", "World Health Organization", "2027-11-20"),
        (16, 1, "Field Surgery Protocols", "Armed Forces Medical College", "2028-01-10"),
        (20, 1, "Infectious Disease Control", "National Centre for Disease Control", "2027-09-05"),
        (25, 1, "Mass Casualty Management", "Disaster Management Cell", "2027-04-12"),
        (30, 1, "Advanced Cardiac Life Support", "American Heart Association India", "2027-08-18"),
        (3, 1, "Critical Care Nursing", "Trained Nurses Association of India", "2027-10-15"),
        (4, 1, "Emergency Triage Nursing", "Kerala Nursing Council", "2027-07-25"),
    ]
    for c in med_certs:
        cert_vals.append(f"  ({c[0]}, {c[1]}, '{c[2]}', '{c[3]}', '{c[4]}')")

    # Track next cert_no per volunteer
    cert_counts = {}
    for c in cert_vals:
        # extract v_id from "  (v_id, ..."
        vid = int(c.strip()[1:].split(",")[0].strip())
        cert_counts[vid] = cert_counts.get(vid, 0) + 1

    cert_pool = [
        "First Aid & CPR", "Disaster Search & Rescue", "Heavy Vehicle Emergency Driving",
        "Community Water Sanitation", "Psychological First Aid", "Incident Command System 100",
        "Shelter Management Fundamentals", "Emergency Radio Communications"
    ]
    issuers = ["Indian Red Cross Society", "NDRF Training Academy", "St. John Ambulance", "Civil Defence Corps", "State Disaster Authority"]
    c_count = len(cert_vals)
    for v_id in range(1, 61):
        if c_count >= 90:
            break
        curr_cnt = cert_counts.get(v_id, 0)
        if curr_cnt >= 2:
            continue
        to_add = 1 if curr_cnt == 1 else 2
        for _ in range(to_add):
            curr_cnt += 1
            cert_counts[v_id] = curr_cnt
            c_name = cert_pool[(v_id + curr_cnt) % len(cert_pool)]
            issuer = issuers[(v_id * curr_cnt) % len(issuers)]
            exp_year = 2027 + (curr_cnt % 2)
            exp_month = ((v_id * 2 + curr_cnt) % 12) + 1
            exp_d = f"{exp_year}-{exp_month:02d}-15"
            cert_vals.append(f"  ({v_id}, {curr_cnt}, {q(c_name)}, {q(issuer)}, '{exp_d}')")
            c_count += 1
            if c_count >= 90:
                break

    emit(",\n".join(cert_vals) + ";")
    emit()

    # 6. assignment (M:N Associative table: PK (volunteer_id, camp_id))
    # Edge case 6: Camp 3 has NO medical-skilled volunteers. (Volunteers 5, 6, 7, 8 are logistics, search, cooking, driving)
    # Edge case 9: Two volunteers with the same skill at Camp 1 (Volunteers 3 and 4, nursing)
    # Edge case 4: Volunteer 10 (expired cert) assigned to Camp 1
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 6. ASSIGNMENTS (M:N Associative Entity: PK (volunteer_id, camp_id))")
    emit("-- Edge Case: Camp 3 has no medical volunteers. Camp 1 has two nursing volunteers.")
    emit("-- Edge Case: Volunteer 10 (expired cert) is assigned to Camp 1.")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO assignment (volunteer_id, camp_id, role, shift) VALUES")
    assign_vals = []
    # Camp 1: Mary Joseph (3), Latha Kurien (4), Farhan Akhtar (10), Arvind Sharma (1)
    assign_vals.append("  (1, 1, 'Chief Medical Officer', 'morning')")
    assign_vals.append("  (3, 1, 'Triage Nurse', 'morning')")
    assign_vals.append("  (4, 1, 'Night Triage Nurse', 'night')")
    assign_vals.append("  (10, 1, 'Warehouse Coordinator', 'evening')")

    # Camp 3: ONLY logistics, search_and_rescue, cooking, driving (NO medical!)
    assign_vals.append("  (5, 3, 'Inventory Supervisor', 'morning')")
    assign_vals.append("  (6, 3, 'Rescue Team Lead', 'morning')")
    assign_vals.append("  (7, 3, 'Community Kitchen Chef', 'evening')")
    assign_vals.append("  (8, 3, 'Ambulance & Logistics Driver', 'night')")
    assign_vals.append("  (11, 3, 'Search Patrol', 'night')")
    assign_vals.append("  (13, 3, 'Supply Truck Driver', 'morning')")

    # Assign remaining volunteers across camps 2, 4-12
    assigned_vols = {1, 3, 4, 10, 5, 6, 7, 8, 11, 13}
    shifts = ['morning', 'evening', 'night']
    roles = ['Camp Volunteer', 'Supply Handler', 'Food Distribution', 'Security & Shelter Care', 'Registration Desk']
    for v_id in range(1, 61):
        if v_id in assigned_vols:
            continue
        # Ensure we don't assign medical volunteers to Camp 3
        v_skill = vols[v_id - 1][2]
        target_camp = (v_id % 12) + 1
        if target_camp == 3 and v_skill in ['medical', 'nursing']:
            target_camp = 2
        shift = shifts[v_id % len(shifts)]
        role = f"{v_skill.replace('_', ' ').title()} Support"
        assign_vals.append(f"  ({v_id}, {target_camp}, '{role}', '{shift}')")
    emit(",\n".join(assign_vals) + ";")
    emit()

    # 7. shelter_unit (~60 units across 12 camps)
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 7. SHELTER UNITS (Weak Entity: PK (camp_id, unit_no))")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO shelter_unit (camp_id, unit_no, unit_type, unit_capacity) VALUES")
    shelter_vals = []
    unit_types = ["tent", "hall", "prefab"]
    for c_id in range(1, 13):
        # 5 units per camp = 60 units total
        for u_no in range(1, 6):
            u_type = unit_types[(c_id + u_no) % len(unit_types)]
            cap = 20 if u_type == "hall" else (6 if u_type == "tent" else 12)
            shelter_vals.append(f"  ({c_id}, {u_no}, '{u_type}', {cap})")
    emit(",\n".join(shelter_vals) + ";")
    emit()

    # 8. registered_family (150 families)
    # Edge case 3: Camp 1 registered members exceed 90% of capacity (Capacity = 100, we put 92 members!)
    # Edge case 8: Families with members aged under 5 AND over 60
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 8. REGISTERED FAMILIES (150 families)")
    emit("-- ----------------------------------------------------------------------------")
    heads = [
        "Rameshwar Prasad", "Sita Devi", "Kishore Kumar", "Fatima Bi", "Devendra Yadav",
        "Sunita Bai", "Gopalakrishnan Nair", "Anand Rao", "Laxmi Soren", "Mohammad Rafiq",
        "Bhagwan Das", "Manju Warrier", "Subhash Chandra", "Kalyani Amma", "Harishankar Tiwari"
    ]
    villages = [
        "Vellarmala", "Chooralmala", "Munderi", "Attamala", "Dholidhar", "Raini",
        "Kandi", "Batabari", "Sunabeda", "Astaranga", "Pandoh", "Aut", "Bhatwari", "Joshimath Gaon"
    ]
    emit("INSERT INTO registered_family (head_name, origin_village, registered_on, camp_id) VALUES")
    fam_vals = []
    # Families 1 to 20 assigned to Camp 1 to achieve >90 members
    # Families 21 to 150 distributed across camps 2 to 12
    for f_id in range(1, 151):
        c_id = 1 if f_id <= 20 else ((f_id % 11) + 2)
        h_name = f"{heads[(f_id - 1) % len(heads)]} ({f_id})"
        v_name = villages[(f_id * 3) % len(villages)]
        day = ((f_id * 7) % 200) + 1
        reg_date = date(2026, 1, 1) + timedelta(days=day)
        fam_vals.append(f"  ({q(h_name)}, {q(v_name)}, '{reg_date}', {c_id})")
    emit(",\n".join(fam_vals) + ";")
    emit()

    # 9. family_member (~600 members)
    # Edge case 3: Camp 1 families (1-20) total EXACTLY 92 members (>90% of capacity 100).
    # Edge case 8: Families with children < 5 and elders > 60 (Families 1, 5, 10, 25, 40).
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 9. FAMILY MEMBERS (Weak Entity: PK (family_id, member_no))")
    emit("-- Edge Case: Camp 1 registered members = 92 (exceeds 90% of capacity 100).")
    emit("-- Edge Case: Families with both children under 5 and elders over 60.")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO family_member (family_id, member_no, member_name, age, special_need) VALUES")
    mem_vals = []
    # Camp 1: 20 families. To get 92 members: 12 families of 5 (60) + 8 families of 4 (32) = 92 members.
    c1_members = 0
    for f_id in range(1, 21):
        num_m = 5 if f_id <= 12 else 4
        c1_members += num_m
        for m_no in range(1, num_m + 1):
            if f_id == 1 and m_no == 1:
                # Elder over 60
                mem_vals.append(f"  ({f_id}, {m_no}, 'Grandfather Shivaram', 72, 'Arthritis - Mobility Support')")
            elif f_id == 1 and m_no == 2:
                # Child under 5
                mem_vals.append(f"  ({f_id}, {m_no}, 'Toddler Aarav', 3, 'Requires Infant Formula')")
            elif f_id == 5 and m_no == 1:
                mem_vals.append(f"  ({f_id}, {m_no}, 'Dadi Kamla', 68, 'Hypertension')")
            elif f_id == 5 and m_no == 2:
                mem_vals.append(f"  ({f_id}, {m_no}, 'Baby Ananya', 2, NULL)")
            else:
                age = 15 + ((f_id * 3 + m_no * 7) % 40)
                sp = "NULL" if (m_no != 3 or f_id % 4 != 0) else "'Asthma Inhaler Needed'"
                mem_vals.append(f"  ({f_id}, {m_no}, 'Member {f_id}-{m_no}', {age}, {sp})")

    # Families 21 to 150: average ~4 members per family = ~520 members + 92 = ~612 members total.
    for f_id in range(21, 151):
        num_m = 4 if f_id % 3 != 0 else 3
        for m_no in range(1, num_m + 1):
            if f_id == 25 and m_no == 1:
                mem_vals.append(f"  ({f_id}, {m_no}, 'Elderly Narayan', 75, 'Wheelchair Required')")
            elif f_id == 25 and m_no == 2:
                mem_vals.append(f"  ({f_id}, {m_no}, 'Baby Vihaan', 1, NULL)")
            elif f_id == 40 and m_no == 1:
                mem_vals.append(f"  ({f_id}, {m_no}, 'Ba Rukmini', 81, 'Hearing Impairment')")
            elif f_id == 40 and m_no == 2:
                mem_vals.append(f"  ({f_id}, {m_no}, 'Child Diya', 4, NULL)")
            else:
                age = ((f_id * 7 + m_no * 11) % 65) + 5
                sp = "NULL" if (f_id % 10 != 0 or m_no != 1) else "'Diabetic Care'"
                mem_vals.append(f"  ({f_id}, {m_no}, 'Family Person {f_id}-{m_no}', {age}, {sp})")

    emit(",\n".join(mem_vals) + ";")
    emit()

    # 10. supply_request (120 requests)
    # Edge case 7: Pending critical request older than 14 days with no matching shipment after request date.
    # Request 1: Camp 2, item 20 (Ciprofloxacin), date 2026-02-10, urgency 'critical'. No shipment of item 20 to Camp 2 after this!
    # Edge case 5: Item 39 (Antiseptic Hand Wash) is requested here, but will NEVER appear in any shipment_line.
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 10. SUPPLY REQUESTS (120 requests)")
    emit("-- Edge Case: Request 1 is critical, stale (>14 days), unfulfilled.")
    emit("-- Edge Case: Item 39 is requested across multiple requests, but never shipped.")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO supply_request (request_date, urgency, camp_id) VALUES")
    req_vals = []
    # Request 1: Critical unfulfilled request
    req_vals.append("  ('2026-02-10', 'critical', 2)")
    # Generate requests 2 to 120 across camps and dates
    urgencies = ['low', 'medium', 'high', 'critical']
    start_d = date(2026, 1, 5)
    for r_id in range(2, 121):
        c_id = ((r_id * 3) % 12) + 1
        u_idx = (r_id % 4)
        urg = urgencies[u_idx]
        r_date = start_d + timedelta(days=((r_id * 2) % 250))
        req_vals.append(f"  ('{r_date}', '{urg}', {c_id})")
    emit(",\n".join(req_vals) + ";")
    emit()

    # 11. request_line (~350 lines across 120 requests)
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 11. REQUEST LINES (Weak Entity: PK (request_id, line_no))")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO request_line (request_id, line_no, item_id, qty_requested) VALUES")
    req_l_vals = []
    # Request 1 line: Item 20 (Ciprofloxacin), qty 50
    req_l_vals.append("  (1, 1, 20, 50)")

    # Request 2 and 3 include Item 39 (Antiseptic Hand Wash, requested but NEVER shipped)
    req_l_vals.append("  (2, 1, 39, 100)")
    req_l_vals.append("  (3, 1, 39, 150)")

    # Note: Item 40 (Mosquito Repellent Ointment) is NEVER requested!
    total_rl = 3
    for r_id in range(2, 121):
        num_lines = 3 if (r_id % 2 == 0) else 2
        for l_no in range(1, num_lines + 1):
            if r_id in [2, 3] and l_no == 1:
                continue # already added item 39
            # Items 1 to 38 (never item 40!)
            item_choice = ((r_id * 5 + l_no * 7) % 38) + 1
            qty = 20 + ((r_id + l_no * 15) % 180)
            req_l_vals.append(f"  ({r_id}, {l_no}, {item_choice}, {qty})")
            total_rl += 1
    emit(",\n".join(req_l_vals) + ";")
    emit()

    # 12. shipment (200 shipments)
    # Edge case 1: Donor 1 (PM Relief Fund) ships to ALL 12 camps.
    # Edge case 2: Donor 1 has shipments in ALL 9 months (Jan through Sep 2026).
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 12. SHIPMENTS (200 shipments)")
    emit("-- Edge Case: Donor 1 ships to all 12 camps and in all 9 months.")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO shipment (shipment_date, vehicle_no, status, donor_id, camp_id) VALUES")
    ship_vals = []
    veh_prefixes = ["KL-11-BH", "AS-11-CA", "UK-07-TR", "OD-05-CX", "HP-33-DL", "DL-01-GA"]

    # First 12 shipments: Donor 1 shipping to each of the 12 camps across all 9 months
    # Months 1 to 9 distributed over 12 camps:
    d1_schedule = [
        (1, date(2026, 1, 15)),
        (2, date(2026, 2, 12)),
        (3, date(2026, 3, 10)),
        (4, date(2026, 4, 8)),
        (5, date(2026, 5, 14)),
        (6, date(2026, 6, 20)),
        (7, date(2026, 7, 18)),
        (8, date(2026, 8, 22)),
        (9, date(2026, 9, 25)),
        (10, date(2026, 3, 28)),
        (11, date(2026, 5, 29)),
        (12, date(2026, 7, 30)),
    ]
    for s_id, (target_c, s_date) in enumerate(d1_schedule, start=1):
        v_num = f"{veh_prefixes[s_id % len(veh_prefixes)]}-{1000 + s_id}"
        ship_vals.append(f"  ('{s_date}', '{v_num}', 'delivered', 1, {target_c})")

    # Generate remaining 188 shipments (total 200)
    # Ensure status is mostly 'delivered' so camp_stock is populated, with some 'dispatched', 'in_transit', 'cancelled'
    statuses = ['delivered', 'delivered', 'delivered', 'in_transit', 'dispatched', 'cancelled']
    for s_id in range(13, 201):
        d_id = ((s_id * 3) % 24) + 2 # Donors 2 to 25
        c_id = ((s_id * 7) % 12) + 1
        stat = statuses[s_id % len(statuses)]
        s_date = date(2026, 1, 5) + timedelta(days=((s_id * 3) % 260))
        v_num = f"{veh_prefixes[s_id % len(veh_prefixes)]}-{1000 + s_id}"
        ship_vals.append(f"  ('{s_date}', '{v_num}', '{stat}', {d_id}, {c_id})")

    emit(",\n".join(ship_vals) + ";")
    emit()

    # 13. shipment_line (~700 lines)
    # Edge case 5: Item 40 (Mosquito Repellent Ointment) is shipped, but was never requested!
    # Ensure Item 39 is NEVER shipped.
    # Ensure Item 20 (Ciprofloxacin) is NEVER shipped to Camp 2 on or after 2026-02-10 (protecting Edge Case 7).
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 13. SHIPMENT LINES (Weak Entity: PK (shipment_id, line_no))")
    emit("-- Edge Case: Item 40 shipped in Shipment 1; Item 39 never shipped anywhere.")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO shipment_line (shipment_id, line_no, item_id, quantity_sent) VALUES")
    sline_vals = []
    # Shipment 1: includes Item 40 (shipped but never requested)
    sline_vals.append("  (1, 1, 40, 200)")
    sline_vals.append("  (1, 2, 1, 150)")
    sline_vals.append("  (1, 3, 9, 100)")

    # Generate lines for shipments 2 to 200 (~3-4 lines per shipment)
    total_sl = 3
    for s_id in range(2, 201):
        num_lines = 4 if (s_id % 3 == 0) else 3
        # Target camp for this shipment
        target_camp = d1_schedule[s_id - 1][0] if s_id <= 12 else (((s_id * 7) % 12) + 1)
        used_items = set()
        for l_no in range(1, num_lines + 1):
            # Select items from 1 to 38, or 40. NEVER item 39!
            candidate_item = ((s_id * 7 + l_no * 11) % 38) + 1
            if candidate_item == 20 and target_camp == 2:
                # Avoid shipping item 20 to camp 2 to preserve unfulfilled edge case 7
                candidate_item = 21
            if candidate_item in used_items:
                candidate_item = ((candidate_item + 3) % 38) + 1
            used_items.add(candidate_item)
            qty = 30 + ((s_id * 4 + l_no * 15) % 350)
            sline_vals.append(f"  ({s_id}, {l_no}, {candidate_item}, {qty})")
            total_sl += 1

    emit(",\n".join(sline_vals) + ";")
    emit()

    # 14. camp_stock (populated consistently with delivered shipments)
    emit("-- ----------------------------------------------------------------------------")
    emit("-- 14. CAMP STOCK (Populated consistently from delivered shipments)")
    emit("-- ----------------------------------------------------------------------------")
    emit("INSERT INTO camp_stock (camp_id, item_id, quantity_on_hand)")
    emit("SELECT ")
    emit("  s.camp_id,")
    emit("  sl.item_id,")
    emit("  SUM(sl.quantity_sent) AS quantity_on_hand")
    emit("FROM shipment s")
    emit("JOIN shipment_line sl ON s.shipment_id = sl.shipment_id")
    emit("WHERE s.status = 'delivered'")
    emit("GROUP BY s.camp_id, sl.item_id;")
    emit()

    emit("COMMIT;")
    emit()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))

    print(f"Generated {out_path} successfully ({len(sql_lines)} lines).")

if __name__ == "__main__":
    main()
