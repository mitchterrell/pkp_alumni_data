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
                tmp_xml.set("era", era)
                if cell:
                    tmp_xml.set("cell", fix_cell(cell))
                if email:
                    tmp_xml.set("email", email.lower())
                if contact:
                    tmp_xml.set("contact", contact)


def add_penn_focs_group(assimilated):
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
                temp_xml = ET.SubElement(xml_attr, "penn_focus_group")
                temp_xml.set("era", splitter[1])
                temp_xml.set("committee", splitter[2])
                temp_xml.set("email", splitter[3].lower())
                temp_xml.set("phone", fix_cell(splitter[4]))
                temp_xml.set("confirmed", splitter[5])
                temp_xml.set("call_segment", splitter[6])
                temp_xml.set("response", splitter[7])


def add_penn_eras(assimilated):
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
                temp_xml = ET.SubElement(xml_attr, "penn_era")
                temp_xml.set("initiation", splitter[0])
                temp_xml.set("who", splitter[4])
                temp_xml.set("prospect_list", splitter[6])
                if splitter[7]:
                    temp_xml.set("comments", splitter[7])


def add_penn_contact(assimilated):
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
                temp_xml = ET.SubElement(xml_attr, "penn_contact")

                phone_labels = [
                    "preferred_phone_number",
                    "phone",
                    "home_phone",
                    "work_phone",
                ]
                numbers = []
                for pl in phone_labels:
                    numbers.append(xml_attr.get(pl))

                mobile = fix_cell(splitter[4])
                home = fix_cell(splitter[5])
                biznus = fix_cell(splitter[6])

                if mobile and mobile not in numbers:
                    temp_xml.set("mobile_phone", mobile)
                if home and home not in numbers:
                    temp_xml.set("home_phone", home)
                if biznus and biznus not in numbers:
                    temp_xml.set("biznus_phone", biznus)

                temp_xml.set("pref_year", splitter[3])

                tmp_email = splitter[7].lower()
                if tmp_email and tmp_email != temp_xml.get("email"):
                    temp_xml.set("email", tmp_email)

                tmp_address = splitter[8]
                if tmp_address and tmp_address != temp_xml.get("primary_street"):
                    temp_xml.set("primary_street", tmp_address)
                    temp_xml.set("primary_city", splitter[9])
                    temp_xml.set("primary_state_province", splitter[10])
                    temp_xml.set("primary_zip_postal_code", splitter[11])


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

    # Fix all phone numbers:
    phone_labels = ["preferred_phone_number", "phone", "home_phone", "work_phone"]
    for phone_label in phone_labels:
        for elem in foundation_xml.xpath(f"./alumni[@{phone_label}]"):
            temp_phone = fix_cell(elem.get(phone_label))
            elem.set(phone_label, temp_phone)

    # Fix all emails
    for elem in foundation_xml.xpath(f"./alumni[@email]"):
        temp_email = elem.get("email").lower()
        elem.set("email", temp_email)


def main():
    print("=== Starting PKP Alumni Data Parsing ===")

    foundation_xml = parse_foundation()
    set_dicts(foundation_xml)
    perform_corrections(foundation_xml)
    set_dicts(foundation_xml)

    add_misc_data(foundation_xml)
    add_penn_focs_group(foundation_xml)
    add_penn_eras(foundation_xml)
    add_penn_contact(foundation_xml)

    xml_to_file(
        foundation_xml, os.path.join("new_output", "assimilated_foundation.xml")
    )


if __name__ == "__main__":
    main()
