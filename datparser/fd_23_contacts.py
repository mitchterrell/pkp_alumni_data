from lxml import etree as ET
from datetime import datetime


def perform_query():
    print("==== Starting Alumni Parse ==== ")

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()
    almn = root.xpath(
        "./alumni[@preferred_first_name = 'Michael' and @legal_last_name = 'Ryan']"
    )

    print(len(almn))

    print(almn[0].get("salesforce_id"))


def find_pre_1960():

    names = []
    with open(
        R"raw_inputs\alumni_event_attendance\founders_day\fd_2023.csv", "r"
    ) as f:
        for line in f.readlines()[1:]:
            # print(line.split(",")[3])
            name = line.split(",")[3]
            # print(name)
            names.append(name)

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()

    last_date = datetime.strptime("01/01/1970", "%m/%d/%Y")

    names.append("Michael Ryan")
    names.append("James Frazier")
    names.append("Andrew Johnson")
    names.append("Kevin Lee")

    for name in names:
        if " " not in name:
            print(name)
            continue
        f_name = name.split(" ")[0]
        l_name = name.split(" ")[1]
        almn = root.xpath(
            f"./alumni[(@preferred_first_name = '{f_name}' or @legal_first_name = '{f_name}') and @legal_last_name = '{l_name}']"
        )

        # if len(almn) != 1:
        # print(f"ERROR: [{name}] --> {len(almn)}")
        if len(almn) == 1:
            init_date = datetime.strptime(
                almn[0].get("initiation_date"), "%m/%d/%Y"
            )
            if init_date <= last_date:
                print(
                    f"PRE 1970 --> {name:20} --> {almn[0].get('initiation_date'):10} --> {almn[0].get('chapter_of_initiation')}"
                )


def main():
    find_pre_1960()


if __name__ == "__main__":
    main()
