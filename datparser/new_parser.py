from lxml import etree as ET
import os

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
        headers = all_lines[0].lower().replace("\n", "").replace(" ", "_").replace("/", "_").split(",")

        headers_xml = ET.SubElement(root, "headers")
        for head in headers:
            ET.SubElement(headers_xml, "head", {"name" : head})

        
        for line in all_lines[1:]:
            line = line.replace("\n", "")
            if line:
                temp_sub = ET.SubElement(root, "alumni")
                sub_vals = line.split(",")

                for i in range(0, len(headers)):
                    if(sub_vals[i]):
                        temp_sub.set(headers[i], sub_vals[i])


    return root


def main():
    print("=== Starting PKP Alumni Data Parsing ===")

    from_foundation = {
        "mn_beta_all_time" : R".\raw_inputs\from_foundation\2022\mn_beta_all_time_member_list.csv",
        "mn_beta_alumni_list" : R".\raw_inputs\from_foundation\2022\mn_beta_alumni_list.csv",
        "mn_gamm_mn_delta_2022" : R".\raw_inputs\from_foundation\2022\mn_gamma_mn_delta_2022.csv",
        "twin_cities_alumni_list" : R".\raw_inputs\from_foundation\2022\twin_cities_alumni_list.csv",
    }

    xml_foundation_dict = {}
    for file_name, csv in from_foundation.items():
        xml_foundation_dict[file_name] = csv_to_xml(csv)

    headers_to_csv(xml_foundation_dict, os.path.join("new_output", "sorted_headers_out.csv"))

    



if __name__ == "__main__":
    main()