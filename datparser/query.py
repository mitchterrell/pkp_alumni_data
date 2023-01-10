from lxml import etree as ET
from datetime import datetime


def main():

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()

    # val = root.xpath(
    #     "./alumni[@legal_first_name = 'William' and @legal_last_name = 'Johnson']"
    # )
    # print(val[0].get("salesforce_id"))
    # return

    almn = root.xpath(
        "./alumni[@chapter_of_initiation = 'Minnesota Beta' and @chapter_of_initiation_roll_number < 941 and @chapter_of_initiation_roll_number > 902]"
    )

    alive_pre_yearbook = root.xpath(
        # "./alumni[@chapter_of_initiation = 'Minnesota Beta' and @chapter_of_initiation_roll_number < 941 and not(@deceased)]"
        "./alumni[@chapter_of_initiation = 'Minnesota Beta' and @chapter_of_initiation_roll_number < 993 and not(@deceased)]"
    )

    print(len(alive_pre_yearbook))
    alive_pre_yearbook.sort(
        key=lambda x: datetime.strptime(x.get("initiation_date"), "%m/%d/%Y")
    )

    e = ET.Element("alumni_pre_1970")
    e.extend(alive_pre_yearbook)
    print("Got here")
    # print(r.tostring(pretty_print=True))
    with open(R"C:\Users\mitch\downloads\alumni_out.xml", "w") as f:
        f.write(ET.tostring(e).decode("utf-8"))
    print("Done")
    return

    for a in alive_pre_yearbook:
        print(
            f"[{a.get('initiation_date')}] [{a.get('salesforce_id')}] --> [{'good' if a.find('event_attendance') != None else ''}]"
        )

    return

    #

    # print(datetime.strptime(almn[0].get("initiation_date"), "%m/%d/%Y"))

    almn.sort(key=lambda x: datetime.strptime(x.get("initiation_date"), "%m/%d/%Y"))

    for a in almn:
        print(
            f"[{a.get('initiation_date')}] [{a.get('legal_first_name')},{a.get('legal_last_name')}] --> [{a.get('salesforce_id')}] --> [{a.get('deceased', default='')}] --> [{'good' if a.find('event_attendance') != None else ''}] "
        )

    print(len(almn))


if __name__ == "__main__":
    main()
