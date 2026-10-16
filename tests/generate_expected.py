#!/usr/bin/env python3
"""
generate_expected.py: Independent Oracle for Analytical Queries Q01-Q20.
Computes reference answers purely in Python (no SQL engine) over the seed dataset,
and writes CSV files to tests/expected/Qxx.csv.
"""

import os
import csv
import re
from datetime import datetime, date

def parse_sql_inserts(filepath):
    """Parses insert tuples from 02_seed.sql into Python dictionaries."""
    data = {
        "relief_camp": [],
        "supply_item": [],
        "donor": [],
        "volunteer": [],
        "volunteer_certification": [],
        "assignment": [],
        "shelter_unit": [],
        "registered_family": [],
        "family_member": [],
        "supply_request": [],
        "request_line": [],
        "shipment": [],
        "shipment_line": [],
    }

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Character parser tracking parentheses depth and quotes
    insert_pattern = re.compile(r"INSERT INTO (\w+)\s*\((.*?)\)\s*VALUES\s*(.*?);", re.DOTALL)
    for match in insert_pattern.finditer(content):
        table = match.group(1)
        columns = [c.strip() for c in match.group(2).split(",")]
        values_block = match.group(3).strip()

        # Parse tuples respecting parentheses depth
        row_tuples = []
        depth = 0
        in_quote = False
        curr_tuple = []
        for ch in values_block:
            if ch == "'" and (len(curr_tuple) == 0 or curr_tuple[-1] != "\\"):
                in_quote = not in_quote
                if depth > 0:
                    curr_tuple.append(ch)
            elif ch == "(" and not in_quote:
                depth += 1
                if depth > 1:
                    curr_tuple.append(ch)
            elif ch == ")" and not in_quote:
                depth -= 1
                if depth == 0:
                    row_tuples.append("".join(curr_tuple).strip())
                    curr_tuple = []
                else:
                    curr_tuple.append(ch)
            elif depth > 0:
                curr_tuple.append(ch)

        for r_str in row_tuples:
            # Parse commas not inside quotes
            tokens = []
            curr = []
            in_quote = False
            for ch in r_str:
                if ch == "'":
                    in_quote = not in_quote
                    curr.append(ch)
                elif ch == "," and not in_quote:
                    tokens.append("".join(curr).strip())
                    curr = []
                else:
                    curr.append(ch)
            if curr:
                tokens.append("".join(curr).strip())

            # Convert types
            row_dict = {}
            for col, val in zip(columns, tokens):
                val_clean = val.strip()
                if val_clean.upper() == "NULL":
                    row_dict[col] = None
                elif val_clean.startswith("'") and val_clean.endswith("'"):
                    row_dict[col] = val_clean[1:-1].replace("''", "'")
                else:
                    try:
                        row_dict[col] = int(val_clean)
                    except ValueError:
                        try:
                            row_dict[col] = float(val_clean)
                        except ValueError:
                            row_dict[col] = val_clean
            data[table].append(row_dict)

    # Assign generated identity keys (1-indexed)
    for idx, r in enumerate(data["relief_camp"], 1): r["camp_id"] = idx
    for idx, r in enumerate(data["supply_item"], 1): r["item_id"] = idx
    for idx, r in enumerate(data["donor"], 1): r["donor_id"] = idx
    for idx, r in enumerate(data["volunteer"], 1): r["volunteer_id"] = idx
    for idx, r in enumerate(data["registered_family"], 1): r["family_id"] = idx
    for idx, r in enumerate(data["supply_request"], 1): r["request_id"] = idx
    for idx, r in enumerate(data["shipment"], 1): r["shipment_id"] = idx

    return data

def write_csv(filename, fieldnames, rows):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # ensure all fields are present
            clean_row = {k: ("" if r.get(k) is None else str(r[k])) for k in fieldnames}
            writer.writerow(clean_row)

def main():
    seed_sql = os.path.join(os.path.dirname(__file__), "..", "db", "02_seed.sql")
    out_dir = os.path.join(os.path.dirname(__file__), "expected")
    data = parse_sql_inserts(seed_sql)

    # Q01: camps where registered members exceed 90% of capacity
    # camp_id, camp_name, capacity, registered_members, occupancy_pct
    camp_lookup = {c["camp_id"]: c for c in data["relief_camp"]}
    family_camp = {f["family_id"]: f["camp_id"] for f in data["registered_family"]}
    camp_member_counts = {c["camp_id"]: 0 for c in data["relief_camp"]}
    for m in data["family_member"]:
        c_id = family_camp[m["family_id"]]
        camp_member_counts[c_id] += 1
    
    q01_rows = []
    for c_id, count in sorted(camp_member_counts.items()):
        c = camp_lookup[c_id]
        pct = round((count / c["capacity"]) * 100.0, 1)
        if count > 0.90 * c["capacity"]:
            q01_rows.append({
                "camp_id": c_id,
                "camp_name": c["camp_name"],
                "capacity": c["capacity"],
                "registered_members": count,
                "occupancy_pct": pct
            })
    write_csv(os.path.join(out_dir, "Q01.csv"), ["camp_id", "camp_name", "capacity", "registered_members", "occupancy_pct"], q01_rows)

    # Q02: total quantity of each item sent to each camp
    # camp_id, camp_name, item_id, item_name, total_quantity_sent
    item_lookup = {i["item_id"]: i for i in data["supply_item"]}
    shipment_camp = {s["shipment_id"]: s["camp_id"] for s in data["shipment"]}
    camp_item_sent = {}
    for sl in data["shipment_line"]:
        c_id = shipment_camp[sl["shipment_id"]]
        key = (c_id, sl["item_id"])
        camp_item_sent[key] = camp_item_sent.get(key, 0) + sl["quantity_sent"]
    
    q02_rows = []
    for (c_id, i_id), total in sorted(camp_item_sent.items()):
        q02_rows.append({
            "camp_id": c_id,
            "camp_name": camp_lookup[c_id]["camp_name"],
            "item_id": i_id,
            "item_name": item_lookup[i_id]["item_name"],
            "total_quantity_sent": total
        })
    write_csv(os.path.join(out_dir, "Q02.csv"), ["camp_id", "camp_name", "item_id", "item_name", "total_quantity_sent"], q02_rows)

    # Q03: pending critical requests with no later shipment of the same item to that camp
    # request_id, request_date, camp_id, camp_name, item_id, item_name, urgency
    delivered_or_sent_shipments = []
    for sl in data["shipment_line"]:
        s = [x for x in data["shipment"] if x["shipment_id"] == sl["shipment_id"]][0]
        delivered_or_sent_shipments.append((s["camp_id"], sl["item_id"], s["shipment_date"]))
    
    q03_rows = []
    for req in data["supply_request"]:
        if req["urgency"] == "critical":
            r_lines = [rl for rl in data["request_line"] if rl["request_id"] == req["request_id"]]
            for rl in r_lines:
                # check if shipment exists with same camp and item on or after request_date
                has_shipment = any(
                    c_id == req["camp_id"] and i_id == rl["item_id"] and s_date >= req["request_date"]
                    for (c_id, i_id, s_date) in delivered_or_sent_shipments
                )
                if not has_shipment:
                    q03_rows.append({
                        "request_id": req["request_id"],
                        "request_date": req["request_date"],
                        "camp_id": req["camp_id"],
                        "camp_name": camp_lookup[req["camp_id"]]["camp_name"],
                        "item_id": rl["item_id"],
                        "item_name": item_lookup[rl["item_id"]]["item_name"],
                        "urgency": req["urgency"]
                    })
    q03_rows.sort(key=lambda x: (x["request_id"], x["item_id"]))
    write_csv(os.path.join(out_dir, "Q03.csv"), ["request_id", "request_date", "camp_id", "camp_name", "item_id", "item_name", "urgency"], q03_rows)

    # Q04: donors who have shipped to every camp
    # donor_id, donor_name
    donor_lookup = {d["donor_id"]: d for d in data["donor"]}
    total_camps = len(data["relief_camp"])
    donor_camps = {}
    for s in data["shipment"]:
        donor_camps.setdefault(s["donor_id"], set()).add(s["camp_id"])
    q04_rows = []
    for d_id, c_set in sorted(donor_camps.items()):
        if len(c_set) == total_camps:
            q04_rows.append({
                "donor_id": d_id,
                "donor_name": donor_lookup[d_id]["donor_name"]
            })
    write_csv(os.path.join(out_dir, "Q04.csv"), ["donor_id", "donor_name"], q04_rows)

    # Q05: top 3 donors per item category by total quantity delivered
    # category, donor_id, donor_name, total_quantity, category_rank
    cat_donor_qty = {}
    shipment_lookup = {s["shipment_id"]: s for s in data["shipment"]}
    for sl in data["shipment_line"]:
        sh = shipment_lookup[sl["shipment_id"]]
        if sh["status"] == "delivered":
            cat = item_lookup[sl["item_id"]]["category"]
            key = (cat, sh["donor_id"])
            cat_donor_qty[key] = cat_donor_qty.get(key, 0) + sl["quantity_sent"]
    
    # rank per category
    cats = sorted(set(k[0] for k in cat_donor_qty.keys()))
    q05_rows = []
    for c in cats:
        donor_list = [(k[1], qty) for k, qty in cat_donor_qty.items() if k[0] == c]
        donor_list.sort(key=lambda x: (-x[1], x[0]))
        # dense rank
        curr_rank = 0
        last_qty = None
        for d_id, qty in donor_list:
            if qty != last_qty:
                curr_rank += 1
                last_qty = qty
            if curr_rank <= 3:
                q05_rows.append({
                    "category": c,
                    "donor_id": d_id,
                    "donor_name": donor_lookup[d_id]["donor_name"],
                    "total_quantity": qty,
                    "category_rank": curr_rank
                })
    write_csv(os.path.join(out_dir, "Q05.csv"), ["category", "donor_id", "donor_name", "total_quantity", "category_rank"], q05_rows)

    # Q06: unmet demand per camp and item: requested minus delivered, only positive
    # camp_id, camp_name, item_id, item_name, qty_requested, qty_delivered, unmet_quantity
    camp_item_req = {}
    for rl in data["request_line"]:
        req = [r for r in data["supply_request"] if r["request_id"] == rl["request_id"]][0]
        key = (req["camp_id"], rl["item_id"])
        camp_item_req[key] = camp_item_req.get(key, 0) + rl["qty_requested"]

    camp_item_del = {}
    for sl in data["shipment_line"]:
        sh = shipment_lookup[sl["shipment_id"]]
        if sh["status"] == "delivered":
            key = (sh["camp_id"], sl["item_id"])
            camp_item_del[key] = camp_item_del.get(key, 0) + sl["quantity_sent"]

    all_keys = sorted(set(list(camp_item_req.keys()) + list(camp_item_del.keys())))
    q06_rows = []
    for key in all_keys:
        c_id, i_id = key
        r_qty = camp_item_req.get(key, 0)
        d_qty = camp_item_del.get(key, 0)
        unmet = r_qty - d_qty
        if unmet > 0:
            q06_rows.append({
                "camp_id": c_id,
                "camp_name": camp_lookup[c_id]["camp_name"],
                "item_id": i_id,
                "item_name": item_lookup[i_id]["item_name"],
                "qty_requested": r_qty,
                "qty_delivered": d_qty,
                "unmet_quantity": unmet
            })
    write_csv(os.path.join(out_dir, "Q06.csv"), ["camp_id", "camp_name", "item_id", "item_name", "qty_requested", "qty_delivered", "unmet_quantity"], q06_rows)

    # Q07: volunteers with expired certifications currently assigned to a camp
    # volunteer_id, volunteer_name, cert_name, expiry_date, camp_id, camp_name
    vol_lookup = {v["volunteer_id"]: v for v in data["volunteer"]}
    q07_rows = []
    for a in data["assignment"]:
        v_certs = [vc for vc in data["volunteer_certification"] if vc["volunteer_id"] == a["volunteer_id"]]
        for vc in v_certs:
            if vc["expiry_date"] and vc["expiry_date"] < "2026-09-30":
                q07_rows.append({
                    "volunteer_id": a["volunteer_id"],
                    "volunteer_name": vol_lookup[a["volunteer_id"]]["volunteer_name"],
                    "cert_name": vc["cert_name"],
                    "expiry_date": vc["expiry_date"],
                    "camp_id": a["camp_id"],
                    "camp_name": camp_lookup[a["camp_id"]]["camp_name"]
                })
    q07_rows.sort(key=lambda x: (x["volunteer_id"], x["cert_name"]))
    write_csv(os.path.join(out_dir, "Q07.csv"), ["volunteer_id", "volunteer_name", "cert_name", "expiry_date", "camp_id", "camp_name"], q07_rows)

    # Q08: camps with no medical-skilled volunteer
    # camp_id, camp_name, district
    camps_with_med = set()
    for a in data["assignment"]:
        if vol_lookup[a["volunteer_id"]]["skill"] == "medical":
            camps_with_med.add(a["camp_id"])
    q08_rows = []
    for c in data["relief_camp"]:
        if c["camp_id"] not in camps_with_med:
            q08_rows.append({
                "camp_id": c["camp_id"],
                "camp_name": c["camp_name"],
                "district": c["district"]
            })
    q08_rows.sort(key=lambda x: x["camp_id"])
    write_csv(os.path.join(out_dir, "Q08.csv"), ["camp_id", "camp_name", "district"], q08_rows)

    # Q09: running total of delivered quantity per camp over time
    # camp_id, camp_name, shipment_id, shipment_date, quantity_sent, running_total_quantity
    delivered_ships = [s for s in data["shipment"] if s["status"] == "delivered"]
    ship_lines_qty = {}
    for sl in data["shipment_line"]:
        ship_lines_qty[sl["shipment_id"]] = ship_lines_qty.get(sl["shipment_id"], 0) + sl["quantity_sent"]
    
    # Sort by camp_id, shipment_date, shipment_id
    delivered_ships.sort(key=lambda s: (s["camp_id"], s["shipment_date"], s["shipment_id"]))
    q09_rows = []
    curr_camp = None
    running_tot = 0
    for s in delivered_ships:
        if s["camp_id"] != curr_camp:
            curr_camp = s["camp_id"]
            running_tot = 0
        q_sent = ship_lines_qty.get(s["shipment_id"], 0)
        running_tot += q_sent
        q09_rows.append({
            "camp_id": s["camp_id"],
            "camp_name": camp_lookup[s["camp_id"]]["camp_name"],
            "shipment_id": s["shipment_id"],
            "shipment_date": s["shipment_date"],
            "quantity_sent": q_sent,
            "running_total_quantity": running_tot
        })
    write_csv(os.path.join(out_dir, "Q09.csv"), ["camp_id", "camp_name", "shipment_id", "shipment_date", "quantity_sent", "running_total_quantity"], q09_rows)

    # Q10: average days from request to first fulfilling shipment
    # avg_days_to_fulfillment
    fulfillment_days = []
    for rl in data["request_line"]:
        req = [r for r in data["supply_request"] if r["request_id"] == rl["request_id"]][0]
        matching_dates = []
        for sl in data["shipment_line"]:
            if sl["item_id"] == rl["item_id"]:
                sh = shipment_lookup[sl["shipment_id"]]
                if sh["camp_id"] == req["camp_id"] and sh["shipment_date"] >= req["request_date"]:
                    matching_dates.append(datetime.strptime(sh["shipment_date"], "%Y-%m-%d").date())
        if matching_dates:
            min_ship_date = min(matching_dates)
            req_d = datetime.strptime(req["request_date"], "%Y-%m-%d").date()
            diff = (min_ship_date - req_d).days
            fulfillment_days.append(diff)
    
    avg_days = round(sum(fulfillment_days) / len(fulfillment_days), 2) if fulfillment_days else 0.0
    write_csv(os.path.join(out_dir, "Q10.csv"), ["avg_days_to_fulfillment"], [{"avg_days_to_fulfillment": avg_days}])

    # Q11: per camp: count of children under 5 and elders over 60
    # camp_id, camp_name, children_under_5, elders_over_60
    c_children = {c["camp_id"]: 0 for c in data["relief_camp"]}
    c_elders = {c["camp_id"]: 0 for c in data["relief_camp"]}
    for m in data["family_member"]:
        c_id = family_camp[m["family_id"]]
        if m["age"] < 5:
            c_children[c_id] += 1
        elif m["age"] > 60:
            c_elders[c_id] += 1
    q11_rows = []
    for c in data["relief_camp"]:
        q11_rows.append({
            "camp_id": c["camp_id"],
            "camp_name": c["camp_name"],
            "children_under_5": c_children[c["camp_id"]],
            "elders_over_60": c_elders[c["camp_id"]]
        })
    q11_rows.sort(key=lambda x: x["camp_id"])
    write_csv(os.path.join(out_dir, "Q11.csv"), ["camp_id", "camp_name", "children_under_5", "elders_over_60"], q11_rows)

    # Q12: month-over-month change in shipment volume
    # shipment_month, monthly_shipments, previous_month_shipments, mom_change
    month_counts = {}
    for s in data["shipment"]:
        m_str = s["shipment_date"][:7] # YYYY-MM
        month_counts[m_str] = month_counts.get(m_str, 0) + 1
    q12_rows = []
    prev_cnt = None
    for m_str in sorted(month_counts.keys()):
        cnt = month_counts[m_str]
        change = (cnt - prev_cnt) if prev_cnt is not None else None
        q12_rows.append({
            "shipment_month": m_str + "-01",
            "monthly_shipments": cnt,
            "previous_month_shipments": prev_cnt if prev_cnt is not None else "",
            "mom_change": change if change is not None else ""
        })
        prev_cnt = cnt
    write_csv(os.path.join(out_dir, "Q12.csv"), ["shipment_month", "monthly_shipments", "previous_month_shipments", "mom_change"], q12_rows)

    # Q13: items requested but never shipped
    # item_id, item_name, category
    shipped_items = set(sl["item_id"] for sl in data["shipment_line"])
    requested_items = set(rl["item_id"] for rl in data["request_line"])
    req_never_shipped = requested_items - shipped_items
    q13_rows = []
    for i_id in sorted(req_never_shipped):
        it = item_lookup[i_id]
        q13_rows.append({
            "item_id": i_id,
            "item_name": it["item_name"],
            "category": it["category"]
        })
    write_csv(os.path.join(out_dir, "Q13.csv"), ["item_id", "item_name", "category"], q13_rows)

    # Q14: total shelter capacity vs registered members per camp
    # camp_id, camp_name, total_shelter_capacity, total_registered_members, capacity_difference
    camp_shelter_cap = {c["camp_id"]: 0 for c in data["relief_camp"]}
    for su in data["shelter_unit"]:
        camp_shelter_cap[su["camp_id"]] += su["unit_capacity"]
    q14_rows = []
    for c in data["relief_camp"]:
        c_id = c["camp_id"]
        scap = camp_shelter_cap[c_id]
        mems = camp_member_counts[c_id]
        q14_rows.append({
            "camp_id": c_id,
            "camp_name": c["camp_name"],
            "total_shelter_capacity": scap,
            "total_registered_members": mems,
            "capacity_difference": scap - mems
        })
    q14_rows.sort(key=lambda x: x["camp_id"])
    write_csv(os.path.join(out_dir, "Q14.csv"), ["camp_id", "camp_name", "total_shelter_capacity", "total_registered_members", "capacity_difference"], q14_rows)

    # Q15: pairs of volunteers with the same skill at the same camp
    # camp_id, camp_name, skill, volunteer_1_id, volunteer_1_name, volunteer_2_id, volunteer_2_name
    q15_rows = []
    assignments = data["assignment"]
    for i in range(len(assignments)):
        for j in range(i + 1, len(assignments)):
            a1, a2 = assignments[i], assignments[j]
            if a1["camp_id"] == a2["camp_id"]:
                v1 = vol_lookup[a1["volunteer_id"]]
                v2 = vol_lookup[a2["volunteer_id"]]
                if v1["skill"] == v2["skill"]:
                    # order by id
                    v_first, v_sec = (v1, v2) if v1["volunteer_id"] < v2["volunteer_id"] else (v2, v1)
                    q15_rows.append({
                        "camp_id": a1["camp_id"],
                        "camp_name": camp_lookup[a1["camp_id"]]["camp_name"],
                        "skill": v1["skill"],
                        "volunteer_1_id": v_first["volunteer_id"],
                        "volunteer_1_name": v_first["volunteer_name"],
                        "volunteer_2_id": v_sec["volunteer_id"],
                        "volunteer_2_name": v_sec["volunteer_name"]
                    })
    q15_rows.sort(key=lambda x: (x["camp_id"], x["skill"], x["volunteer_1_id"]))
    write_csv(os.path.join(out_dir, "Q15.csv"), ["camp_id", "camp_name", "skill", "volunteer_1_id", "volunteer_1_name", "volunteer_2_id", "volunteer_2_name"], q15_rows)

    # Q16: camps whose total received quantity is above the average across camps
    # camp_id, camp_name, total_received_quantity
    camp_rec_qty = {c["camp_id"]: 0 for c in data["relief_camp"]}
    for sl in data["shipment_line"]:
        sh = shipment_lookup[sl["shipment_id"]]
        if sh["status"] == "delivered":
            camp_rec_qty[sh["camp_id"]] += sl["quantity_sent"]
    avg_camp_qty = sum(camp_rec_qty.values()) / len(camp_rec_qty)
    q16_rows = []
    for c_id, tot in sorted(camp_rec_qty.items()):
        if tot > avg_camp_qty:
            q16_rows.append({
                "camp_id": c_id,
                "camp_name": camp_lookup[c_id]["camp_name"],
                "total_received_quantity": tot
            })
    write_csv(os.path.join(out_dir, "Q16.csv"), ["camp_id", "camp_name", "total_received_quantity"], q16_rows)

    # Q17: items that were requested or shipped but not both
    # item_id, item_name, activity_type
    only_req = requested_items - shipped_items
    only_ship = shipped_items - requested_items
    q17_rows = []
    for i_id in sorted(only_req):
        q17_rows.append({
            "item_id": i_id,
            "item_name": item_lookup[i_id]["item_name"],
            "activity_type": "requested_only"
        })
    for i_id in sorted(only_ship):
        q17_rows.append({
            "item_id": i_id,
            "item_name": item_lookup[i_id]["item_name"],
            "activity_type": "shipped_only"
        })
    q17_rows.sort(key=lambda x: x["item_id"])
    write_csv(os.path.join(out_dir, "Q17.csv"), ["item_id", "item_name", "activity_type"], q17_rows)

    # Q18: donors with shipments in every month of the seed period
    # donor_id, donor_name, distinct_months_count
    donor_months = {}
    for s in data["shipment"]:
        donor_months.setdefault(s["donor_id"], set()).add(s["shipment_date"][:7])
    q18_rows = []
    for d_id, m_set in sorted(donor_months.items()):
        if len(m_set) == 9:
            q18_rows.append({
                "donor_id": d_id,
                "donor_name": donor_lookup[d_id]["donor_name"],
                "distinct_months_count": len(m_set)
            })
    write_csv(os.path.join(out_dir, "Q18.csv"), ["donor_id", "donor_name", "distinct_months_count"], q18_rows)

    # Q19: view camp_status_dashboard
    # camp_id, camp_name, capacity, registered_members, open_requests, assigned_volunteers
    camp_req_cnt = {c["camp_id"]: 0 for c in data["relief_camp"]}
    for r in data["supply_request"]:
        camp_req_cnt[r["camp_id"]] += 1
    camp_vol_cnt = {c["camp_id"]: 0 for c in data["relief_camp"]}
    for a in data["assignment"]:
        camp_vol_cnt[a["camp_id"]] += 1
    q19_rows = []
    for c in data["relief_camp"]:
        c_id = c["camp_id"]
        q19_rows.append({
            "camp_id": c_id,
            "camp_name": c["camp_name"],
            "capacity": c["capacity"],
            "registered_members": camp_member_counts[c_id],
            "open_requests": camp_req_cnt[c_id],
            "assigned_volunteers": camp_vol_cnt[c_id]
        })
    q19_rows.sort(key=lambda x: x["camp_id"])
    write_csv(os.path.join(out_dir, "Q19.csv"), ["camp_id", "camp_name", "capacity", "registered_members", "open_requests", "assigned_volunteers"], q19_rows)

    # Q20: materialized view stock by category per district
    # district, category, total_quantity_on_hand
    dist_cat_stock = {}
    for (c_id, i_id), qty in camp_item_del.items():
        dist = camp_lookup[c_id]["district"]
        cat = item_lookup[i_id]["category"]
        key = (dist, cat)
        dist_cat_stock[key] = dist_cat_stock.get(key, 0) + qty
    q20_rows = []
    for (d, cat), qty in sorted(dist_cat_stock.items()):
        q20_rows.append({
            "district": d,
            "category": cat,
            "total_quantity_on_hand": qty
        })
    write_csv(os.path.join(out_dir, "Q20.csv"), ["district", "category", "total_quantity_on_hand"], q20_rows)

    print(f"Generated 20 expected reference CSVs in {out_dir}")

if __name__ == "__main__":
    main()
