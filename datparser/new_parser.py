from lxml import etree as ET
import os

sfid_dict = {}
legal_name_dict = {}
pref_name_dict = {}


def name_to_xml(first, last):
    unique = f"{first.lower()}_{last.lower()}"
    if unique in legal_name_dict:
        return legal_name_dict[unique]
    elif unique in pref_name_dict:
        return pref_name_dict[unique]
    else:
        return None


def add_num_or_update_source(xml_in, cell_in, num_type, source_name):
    xml_out = xml_in.find(f"./phone_numbers/phone[@number = '{cell_in}']")
    if xml_out != None:
        cur_sorce = xml_out.get("source")
        xml_out.set("source", f"{cur_sorce};{source_name}")
    else:
        p_numbs = xml_in.find("phone_numbers")
        if p_numbs == None:
            p_numbs = ET.SubElement(xml_in, "phone_numbers")

        ET.SubElement(
            p_numbs,
            "phone",
            {"type": num_type, "number": cell_in, "source": source_name},
        )


def add_email_or_update_source(xml_in, email_in, source_name):
    xml_out = xml_in.find(f"./emails/email[@address = '{email_in}']")
    if xml_out != None:
        cur_sorce = xml_out.get("source")
        xml_out.set("source", f"{cur_sorce};{source_name}")
    else:
        p_numbs = xml_in.find("emails")
        if p_numbs == None:
            p_numbs = ET.SubElement(xml_in, "emails")

        ET.SubElement(
            p_numbs,
            "email",
            {"address": email_in, "source": source_name},
        )


def add_addr_or_update_source(
    xml_in, street_in, city_in, state_in, zip_in, source_name
):
    xml_out = xml_in.find(f"./mailing_addresses/address[@street = '{street_in}']")
    if xml_out != None:
        cur_sorce = xml_out.get("source")
        xml_out.set("source", f"{cur_sorce};{source_name}")
    else:
        p_numbs = xml_in.find("mailing_addresses")
        if p_numbs == None:
            p_numbs = ET.SubElement(xml_in, "mailing_addresses")

        ET.SubElement(
            p_numbs,
            "address",
            {
                "street": street_in,
                "city": city_in,
                "state": state_in,
                "zip": zip_in,
                "source": source_name,
            },
        )


def get_headers(xml, file_name, do_print=False):
    headers_out = [x.get("name") for x in xml.findall("./headers/head")]
    if do_print:
        print(f"Headers for [{file_name}]")
        for head in headers_out:
            print(f"    {head}")
    return headers_out


def headers_to_csv(xml_foundation, csv_out):

    origins = list(xml_foundation.keys())

    headers = []
    for file_name, xml in xml_foundation.items():
        headers.append(get_headers(xml, file_name, do_print=False))

    headers_in_all = []
    for head in headers[0]:
        in_all = True
        for header_list in headers:
            if head not in header_list:
                in_all = False

        if in_all:
            headers_in_all.append(head)

    sorted_list = []
    for head in headers:
        sorted_list.append(sorted(head))

    with open(csv_out, "w") as to_write:
        for sort in sorted_list:
            new_sort = [x for x in sort if x not in headers_in_all]
            to_write.write(origins[sorted_list.index(sort)] + ",")
            to_write.write(",".join(headers_in_all) + ",")
            to_write.write(",".join(new_sort))
            to_write.write("\n")


def csv_to_xml(csv_in):

    root = ET.Element("alumni_dat")

    with open(csv_in, "r") as csv:
        all_lines = csv.readlines()
        headers = (
            all_lines[0]
            .lower()
            .replace("\n", "")
            .replace(" ", "_")
            .replace("/", "_")
            .split(",")
        )

        headers_xml = ET.SubElement(root, "headers")
        for head in headers:
            ET.SubElement(headers_xml, "head", {"name": head})

        for line in all_lines[1:]:
            line = line.replace("\n", "")
            if line:
                temp_sub = ET.SubElement(root, "alumni")
                sub_vals = line.split(",")

                for i in range(0, len(headers)):
                    if sub_vals[i]:
                        temp_sub.set(headers[i], sub_vals[i])

    return root


def xml_to_file(xml, file):
    tree = ET.ElementTree(xml)
    tree.write(file, pretty_print=True)


def assimilate_foundation(xml_dict):
    xml_id_dict = {}
    for name, xml in xml_dict.items():
        temp_dict = {x.get("salesforce_id"): x for x in xml.findall("alumni")}
        xml_id_dict[name] = temp_dict

    root = ET.Element("foundation_data")

    added_list = []
    for file, sfid_dict in xml_id_dict.items():
        for sfid, xml in sfid_dict.items():
            if sfid not in added_list:

                # (a) Add new element
                xml_elem = ET.SubElement(root, "alumni")
                for key, val in xml.attrib.items():
                    xml_elem.attrib[key] = val

                # (b) Add flag for what file it is in
                xml_elem.set(file, "true")

                # (b) Check asfasdf
                for file_2, sfid_dict_2 in xml_id_dict.items():
                    if file != file_2:
                        is_in_other = sfid_dict_2.get(sfid, None)
                        if is_in_other != None:
                            # (i) Check if the attribs match or add new
                            for key, val in is_in_other.attrib.items():
                                if key in xml_elem.attrib:
                                    if val != xml_elem.get(key):
                                        print(
                                            f"Mismatch: {sfid} - {key} --> [{file} - {xml_elem.get(key)}] vs [{file_2} - {val}]"
                                        )
                                else:
                                    xml_elem.set(key, val)

                            # (ii) Add the flag for in this file
                            xml_elem.set(file_2, "true")

                # (c) Add sfid to list
                added_list.append(sfid)

    return root


def fix_cell(cell_in):
    return cell_in.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")


def set_dicts(assimlated_xml):
    global sfid_dict
    global legal_name_dict
    global pref_name_dict

    sfid_dict = {x.get("salesforce_id"): x for x in assimlated_xml.findall("alumni")}
    legal_name_dict = {
        f"{x.get('legal_first_name').lower()}_{x.get('legal_last_name').lower()}": x
        for x in assimlated_xml.findall("alumni")
    }
    pref_name_dict = {
        f"{x.get('preferred_first_name').lower()}_{x.get('legal_last_name').lower()}": x
        for x in assimlated_xml.findall("alumni")
    }


def parse_foundation():
    from_foundation = {
        "mn_beta_all_time": R".\raw_inputs\from_foundation\2022\mn_beta_all_time_member_list.csv",
        "mn_beta_alumni_list": R".\raw_inputs\from_foundation\2022\mn_beta_alumni_list.csv",
        "mn_gamm_mn_delta_2022": R".\raw_inputs\from_foundation\2022\mn_gamma_mn_delta_2022.csv",
        "twin_cities_alumni_list": R".\raw_inputs\from_foundation\2022\twin_cities_alumni_list.csv",
    }

    xml_foundation_dict = {}
    for file_name, csv in from_foundation.items():
        xml_foundation_dict[file_name] = csv_to_xml(csv)

    # headers_to_csv(
    #     xml_foundation_dict, os.path.join("new_output", "sorted_headers_out.csv")
    # )

    assimilated = assimilate_foundation(xml_foundation_dict)

    return assimilated


def add_misc_data(assimilated):
    source_name = "focus_group"

    with open(
        R".\raw_inputs\pennington_feasibility\cleaned_up\misc_data.csv", "r"
    ) as misc_dat:
        for line in misc_dat.readlines()[1:]:
            line = line.replace("\n", "")
            splitter = line.split(",")
            first_name = splitter[0]
            last_name = splitter[1]
            unique = f"{first_name.lower()}_{last_name.lower()}"

            era = splitter[2]
            cell = splitter[3]
            email = splitter[4]
            contact = splitter[5]

            xml = legal_name_dict.get(unique, None)
            if xml == None:
                xml = pref_name_dict.get(unique, None)

            if xml == None:
                print(f"ERROR {unique} not in anything")
            else:
                tmp_xml = ET.SubElement(xml, "focus_group")

                # (a) Add era
                tmp_xml.set("era", era)

                # (b) Add cell if not in list or add another source
                if cell:
                    cell = fix_cell(cell)
                    add_num_or_update_source(xml, cell, "unknown", source_name)

                # (c) Add email if not in list or add another source
                if email:
                    email = email.lower()
                    add_email_or_update_source(xml, email, source_name)

                # (d) Add contact infomration if it was there
                if contact:
                    tmp_xml.set("contact", contact)


def add_penn_focus_group(assimilated):
    source_name = "penn_focus_group"
    with open(
        R".\raw_inputs\pennington_feasibility\pennington_focus_group.csv", "r"
    ) as penn_focus:
        for line in penn_focus.readlines()[1:]:
            line = line.replace("\n", "")
            splitter = line.split(",")
            xml_attr = name_to_xml(splitter[0].split(" ")[0], splitter[0].split(" ")[1])

            if xml_attr == None:
                print(f"ERROR {splitter[0]} not in alumni dat")
            else:
                temp_xml = ET.SubElement(xml_attr, source_name)
                temp_xml.set("era", splitter[1])
                temp_xml.set("committee", splitter[2])
                add_email_or_update_source(xml_attr, splitter[3].lower(), source_name)
                add_num_or_update_source(
                    xml_attr, fix_cell(splitter[4]), "unknown", source_name
                )
                temp_xml.set("confirmed", splitter[5])
                temp_xml.set("call_segment", splitter[6])
                temp_xml.set("response", splitter[7])


def add_penn_eras(assimilated):
    source_name = "penn_era"
    with open(
        R".\raw_inputs\pennington_feasibility\pennington_eras.csv", "r"
    ) as penn_eras:
        for line in penn_eras.readlines()[1:]:
            line = line.replace("\n", "")
            splitter = line.split(",")
            xml_attr = name_to_xml(splitter[1].split(" ")[0], splitter[1].split(" ")[1])

            if xml_attr == None:
                print(f"ERROR {splitter[1]} not in alumni dat")
            else:
                temp_xml = ET.SubElement(xml_attr, source_name)
                temp_xml.set("initiation", splitter[0])
                temp_xml.set("who", splitter[4])
                temp_xml.set("prospect_list", splitter[6])
                if splitter[7]:
                    temp_xml.set("comments", splitter[7])


def add_penn_contact(assimilated):
    source_name = "penn_contact"
    with open(
        R".\raw_inputs\pennington_feasibility\pennington_contact_list.csv", "r"
    ) as penn_contact:
        for line in penn_contact.readlines()[1:]:
            line = line.replace("\n", "")
            splitter = line.split(",")
            xml_attr = name_to_xml(splitter[1], splitter[2])
            if xml_attr == None:
                xml_attr = name_to_xml(
                    splitter[0].split(" ")[0], splitter[0].split(" ")[2]
                )

            if xml_attr == None:
                print(f"ERROR {splitter[0]} not in alumni dat")
            else:
                temp_xml = ET.SubElement(xml_attr, source_name)

                mobile = fix_cell(splitter[4])
                home = fix_cell(splitter[5])
                biznus = fix_cell(splitter[6])
                if mobile:
                    add_num_or_update_source(xml_attr, mobile, "mobile", source_name)
                if home:
                    add_num_or_update_source(xml_attr, home, "home", source_name)
                if biznus:
                    add_num_or_update_source(xml_attr, biznus, "buissness", source_name)

                temp_xml.set("pref_year", splitter[3])

                temp_email = splitter[7].lower()
                if temp_email:
                    add_email_or_update_source(xml_attr, temp_email, source_name)

                tmp_address = splitter[8]
                if tmp_address and tmp_address != temp_xml.get("primary_street"):
                    street = tmp_address
                    city = splitter[9]
                    state = splitter[10]
                    zip = splitter[11]
                    add_addr_or_update_source(
                        xml_attr, street, city, state, zip, source_name
                    )


def add_penn_call_status(assimilated):
    source_name = "penn_call_status"
    with open(
        R".\raw_inputs\pennington_feasibility\pennington_call_status.csv", "r"
    ) as penn_contact:
        for line in penn_contact.readlines()[1:]:
            line = line.replace("\n", "")
            splitter = line.split(",")
            xml_attr = name_to_xml(splitter[2], splitter[3])

            if xml_attr == None:
                print(f"ERROR {splitter[2]} {splitter[3]} not in alumni dat")
            else:
                temp_xml = ET.SubElement(xml_attr, source_name)

                temp_xml.set("status", splitter[0])

                street = splitter[4]
                city = splitter[5]
                state = splitter[6]
                zip = splitter[7]
                add_addr_or_update_source(
                    xml_attr, street, city, state, zip, source_name
                )

                home = fix_cell(splitter[8])
                cell = fix_cell(splitter[9])
                biznus = fix_cell(splitter[10])
                if home:
                    add_num_or_update_source(xml_attr, home, "home", source_name)
                if cell:
                    add_num_or_update_source(xml_attr, cell, "cell", source_name)
                if biznus:
                    add_num_or_update_source(xml_attr, biznus, "biznus", source_name)

                email = splitter[11].lower()
                if email:
                    add_email_or_update_source(xml_attr, email, source_name)

                if splitter[12]:
                    temp_xml.set("contactor", splitter[12])

                if splitter[13]:
                    temp_xml.set("comment_str", splitter[13])


def add_facebook_list(assimilated):
    fb_name_dict = {
        x.find("facebook").get("name"): x
        for x in assimilated.xpath("./alumni[./facebook]")
    }

    source_name = "facebook"
    with open(R".\raw_inputs\misc\facebook_list_04_01_22.csv", "r") as fb_list:
        for line in fb_list.readlines()[1:]:
            line = line.replace("\n", "").replace('"', "")
            splitter = line.split(",")
            xml_attr = fb_name_dict.get(splitter[0], None)

            if xml_attr == None:
                xml_attr = name_to_xml(
                    splitter[0].split(" ")[0], " ".join(splitter[0].split(" ")[1:])
                )
            if xml_attr == None and len(splitter[0].split(" ")) > 2:
                xml_attr = name_to_xml(
                    splitter[0].split(" ")[0], splitter[0].split(" ")[-1]
                )
            if xml_attr == None:
                xml_attr = name_to_xml(
                    splitter[0].split(" ")[0], splitter[0].split(" ")[1]
                )

            if xml_attr == None:
                print(f"ERROR {splitter[0]} not in alumni dat")
            else:
                do_noting = 1
                # temp_xml = ET.SubElement(xml_attr, source_name)


def add_penn_feasability(assimilated):
    source_name = "penn_feasability"
    with open(
        R".\raw_inputs\pennington_feasibility\penngington_feasibility_study.csv", "r"
    ) as penn_contact:
        for line in penn_contact.readlines()[1:]:
            line = line.replace("\n", "")

            splitter = line.split(",")
            xml_attr = name_to_xml(splitter[8], splitter[10])

            if xml_attr == None:
                print(f"ERROR {splitter[8]} {splitter[10]} not in alumni dat")
            else:
                temp_xml = ET.SubElement(xml_attr, source_name)

                if splitter[0] and splitter[0] != "-":
                    temp_xml.set("pcfs_rank", splitter[0])
                if splitter[1] and splitter[1] != "-":
                    temp_xml.set("status", splitter[1])
                if splitter[2] and splitter[2] != "-":
                    temp_xml.set("interview_date", splitter[2])
                if splitter[6] and splitter[6] != "-":
                    temp_xml.set("pcfs_low", "$" + splitter[6])
                else:
                    temp_xml.set("pcfs_low", "NA")
                if splitter[7] and splitter[7] != "-":
                    temp_xml.set("pcfs_high", "$" + splitter[7])
                else:
                    temp_xml.set("pcfs_high", "NA")

                street = splitter[11]
                city = splitter[12]
                state = splitter[13]
                zip = splitter[14]
                add_addr_or_update_source(
                    xml_attr, street, city, state, zip, source_name
                )

                home = fix_cell(splitter[15])
                if home:
                    add_num_or_update_source(xml_attr, home, "home", source_name)
                mobile = fix_cell(splitter[16])
                if mobile:
                    add_num_or_update_source(xml_attr, mobile, "mobile", source_name)

                email = splitter[17]
                if email and email != "-":
                    add_email_or_update_source(xml_attr, email, source_name)


def perform_corrections(foundation_xml):
    sfid_dict["0036A00000YeHoyQAF"].set("preferred_first_name", "Andy")
    sfid_dict["0036A00000YeHydQAF"].set("preferred_first_name", "Randy")
    sfid_dict["0036A00000YeWcqQAF"].set("preferred_first_name", "Rob")
    sfid_dict["0036A00000YeZb8QAF"].set("preferred_first_name", "Joey")
    sfid_dict["0036A00000YedljQAB"].set("preferred_first_name", "Matt")
    sfid_dict["0036A00000YeIidQAF"].set("preferred_first_name", "Dave")
    sfid_dict["0036A00000YebkQQAR"].set("preferred_first_name", "Pete")
    sfid_dict["0036A00000YeY31QAF"].set("preferred_first_name", "Josh")
    sfid_dict["0036A00000YeXbmQAF"].set("preferred_first_name", "Andy")
    sfid_dict["0036A00000YeIi9QAF"].set("preferred_first_name", "Mike")
    sfid_dict["0036A00000YeIiDQAV"].set("preferred_first_name", "Mike")
    sfid_dict["0036A00000YeVweQAF"].set("preferred_first_name", "Ro")
    sfid_dict["0036A00000YeIRvQAN"].set("preferred_first_name", "Bob")
    sfid_dict["0036A00000YeHwTQAV"].set("preferred_first_name", "Ted")
    sfid_dict["0036A00000YeY6HQAV"].set("preferred_first_name", "Tim")
    sfid_dict["0036A00000YeY2yQAF"].set("preferred_first_name", "Steve")
    sfid_dict["0036A00000YeIigQAF"].set("preferred_first_name", "Bill")
    sfid_dict["0036A00000YeZWEQA3"].set("preferred_first_name", "Ben")
    sfid_dict["0036A00000dzULNQA2"].set("preferred_first_name", "Max")
    sfid_dict["0033u00001QkIAMAA3"].set("legal_first_name", "Finnegan")
    sfid_dict["0033u00001OEaHdAAL"].set("legal_first_name", "Thomas")
    sfid_dict["0036A00000dzUM6QAM"].set("preferred_first_name", "Zach")
    sfid_dict["0036A00000dzULhQAM"].set("preferred_first_name", "Ben")
    sfid_dict["0033u00001aTKM7AAO"].set("preferred_first_name", "Benny")
    sfid_dict["0033u000012E33UAAS"].set("preferred_first_name", "Luke")
    sfid_dict["0033u000012E348AAC"].set("preferred_first_name", "Max")
    sfid_dict["0033u000012E33PAAS"].set("preferred_first_name", "Will")
    sfid_dict["0036A00000dzUMBQA2"].set("preferred_first_name", "Harry")
    sfid_dict["0036A00000YeSFCQA3"].set("preferred_first_name", "Shane")
    sfid_dict["0036A00000Yeg9eQAB"].set("preferred_first_name", "Bob")
    sfid_dict["0036A00000Yehl9QAB"].set("preferred_first_name", "Phil")
    sfid_dict["0036A00000YeTf5QAF"].set("preferred_first_name", "Chris")
    sfid_dict["0036A00000dzUKjQAM"].set("preferred_first_name", "Luke")
    sfid_dict["0036A00000Yeg9UQAR"].set("preferred_first_name", "Mark")
    sfid_dict["0036A00000YeaoWQAR"].set("preferred_first_name", "Pete")
    sfid_dict["0036A00000YeXbpQAF"].set("preferred_first_name", "Paul")
    sfid_dict["0036A00000YeSb9QAF"].set("preferred_first_name", "Pat")
    sfid_dict["0036A00000YeVleQAF"].set("preferred_first_name", "Geoff")
    sfid_dict["0036A00000YeHxtQAF"].set("preferred_first_name", "Chuck")
    sfid_dict["0036A00000YeaoZQAR"].set("preferred_first_name", "Jamie")
    sfid_dict["0036A00000YebkEQAR"].set("preferred_first_name", "Danny")
    sfid_dict["0036A00000Yeca2QAB"].set("preferred_first_name", "Ben")
    sfid_dict["0036A00000YeTBOQA3"].set("preferred_first_name", "Mick")
    sfid_dict["0036A00000YedloQAB"].set("preferred_first_name", "AJ")
    sfid_dict["0036A00000YeHySQAV"].set("preferred_first_name", "Jeff")
    sfid_dict["0036A00000YeWIUQA3"].set("preferred_first_name", "Chriss")
    sfid_dict["0036A00000YeWcsQAF"].set("preferred_first_name", "Chucho")
    sfid_dict["0036A00000YebkVQAR"].set("preferred_first_name", "Chris")
    sfid_dict["0036A00000YebkFQAR"].set("preferred_first_name", "Alex")
    sfid_dict["0036A00000YebkOQAR"].set("preferred_first_name", "Zack")
    sfid_dict["0036A00000YeSb8QAF"].set("preferred_first_name", "Dan")
    sfid_dict["0036A00000YeVlbQAF"].set("preferred_first_name", "Dave")
    sfid_dict["0036A00000YebkMQAR"].set("preferred_first_name", "Nick")
    sfid_dict["0036A00000YebkUQAR"].set("preferred_first_name", "Sam")
    sfid_dict["0036A00000YeZGtQAN"].set("preferred_first_name", "TJ")
    sfid_dict["0036A00000YeaLgQAJ"].set("preferred_first_name", "Tom")
    sfid_dict["0036A00000YeaoYQAR"].set("preferred_first_name", "Luke")
    sfid_dict["0036A00000YeXC8QAN"].set("preferred_first_name", "Matt")
    sfid_dict["0036A00000YeaLfQAJ"].set("preferred_first_name", "Chad")
    sfid_dict["0036A00000YeZWDQA3"].set("preferred_first_name", "Dave")
    sfid_dict["0036A00000YealZQAR"].set("preferred_first_name", "TJ")
    sfid_dict["0036A00000YeaLbQAJ"].set("preferred_first_name", "Alex")
    sfid_dict["0036A00000YeZwTQAV"].set("preferred_first_name", "Matt")
    sfid_dict["0036A00000YeYr9QAF"].set("preferred_first_name", "Ben")
    sfid_dict["0036A00000YealVQAR"].set("preferred_first_name", "Josh")
    sfid_dict["0036A00000YeX3iQAF"].set("preferred_first_name", "Jon")
    sfid_dict["0036A00000YeYmNQAV"].set("preferred_first_name", "Mike")
    sfid_dict["0036A00000YeaLYQAZ"].set("preferred_first_name", "Chris")
    sfid_dict["0036A00000YeYrAQAV"].set("preferred_first_name", "Nick")

    ## Add facebook names manually for some that are tricky
    id_fb_name = {
        "0033u00001QkIAHAA3": "Aaron Latterell",
        "0033u000012E34XAAS": "Dylan Tripp Surprise",
        "0036A00000YeePNQAZ": "Mimmy Turphy",
        "0036A00000Yeez0QAB": "Joey Griffiths",
        "0036A00000YeiDTQAZ": "David William Walker",
        "0036A00000Yeez1QAB": "Andrew Hancock Turner",
        "0036A00000YecZyQAJ": "Aaron Jay-Donald Cotton",
        "0036A00000YeePSQAZ": "David Brink Watts",
        "0036A00000YefKpQAJ": "Justin Nathan",
        "0036A00000YegXwQAJ": "Luke Ashley",
        "0036A00000YedgjQAB": "Andrew Dobin",
        "0036A00000YegZ1QAJ": "Meir Avila",
        "0036A00000YebkJQAR": "Ravi Kiran",
        "0036A00000YeVljQAF": "Rick Licki",
        "0036A00000YeYGuQAN": "Levon Esay",
        "0036A00000YeYGsQAN": "Christian Wallace",
        "0036A00000YegZDQAZ": "Ian Ni-kaza",
    }
    for id, fb_name in id_fb_name.items():
        ET.SubElement(sfid_dict[id], "facebook", {"name": fb_name})

    # Fix all phone numbers and add as a child element:
    phone_labels = ["preferred_phone_number", "phone", "home_phone", "work_phone"]
    for phone_label in phone_labels:
        for elem in foundation_xml.xpath(f"./alumni[@{phone_label}]"):
            # (a) Extract the number
            temp_phone = fix_cell(elem.get(phone_label))

            # (b) Find or create the phone_numbers child element
            phone_xml = elem.find("phone_numbers")
            if phone_xml == None:
                phone_xml = ET.SubElement(elem, "phone_numbers")

            # (c) Add the number to the phone_numbers child element
            ET.SubElement(
                phone_xml,
                "phone",
                {"type": phone_label, "number": temp_phone, "source": "foundation"},
            )

            # (d) Delete the number as an attribute
            del elem.attrib[phone_label]

    # Fix all emails
    for elem in foundation_xml.xpath(f"./alumni[@email]"):
        # (a) Extract the email and force it to lower case
        temp_email = elem.get("email").lower()

        # (b) Find or create the emails child element
        email_xml = elem.find("emails")
        if email_xml == None:
            email_xml = ET.SubElement(elem, "emails")

        # (c) Add the email to the emails child element
        ET.SubElement(
            email_xml,
            "email",
            {"address": temp_email, "source": "foundation"},
        )

        # (d) Delete the number as an attribute
        del elem.attrib["email"]

    # Fix addresses
    for elem in foundation_xml.xpath(f"./alumni[@primary_street]"):
        # (a) Extract the address
        street = elem.get("primary_street", "Unkown")
        city = elem.get("primary_city", "Unkown")
        state = elem.get("primary_state_province", "Unkown")
        zip = elem.get("primary_zip_postal_code", "Unkown")

        # (b) Find or create the addresses child element
        mail_xml = elem.find("mailing_addresses")
        if mail_xml == None:
            mail_xml = ET.SubElement(elem, "mailing_addresses")

        # (c) Add the mailling address
        ET.SubElement(
            mail_xml,
            "address",
            {
                "street": street,
                "city": city,
                "state": state,
                "zip": zip,
                "source": "foundation",
            },
        )

        # (d) Delete the mailing information attributes
        if street != "Unkown":
            del elem.attrib["primary_street"]
        if city != "Unkown":
            del elem.attrib["primary_city"]
        if state != "Unkown":
            del elem.attrib["primary_state_province"]
        if zip != "Unkown":
            del elem.attrib["primary_zip_postal_code"]


def main():
    print("=== Starting PKP Alumni Data Parsing ===")

    foundation_xml = parse_foundation()
    set_dicts(foundation_xml)
    perform_corrections(foundation_xml)
    set_dicts(foundation_xml)

    add_misc_data(foundation_xml)
    add_penn_focus_group(foundation_xml)
    add_penn_eras(foundation_xml)
    add_penn_contact(foundation_xml)
    add_penn_call_status(foundation_xml)
    add_penn_feasability(foundation_xml)
    add_facebook_list(foundation_xml)

    xml_to_file(
        foundation_xml, os.path.join("new_output", "assimilated_foundation.xml")
    )


if __name__ == "__main__":
    main()
