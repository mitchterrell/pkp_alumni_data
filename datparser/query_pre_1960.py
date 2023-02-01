from lxml import etree as ET
from datetime import datetime


def main():
    # print("==== Starting Alumni Parse ==== ")

    last_date = datetime.strptime("01/01/1970", "%m/%d/%Y")

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()
    almn = root.xpath("./alumni[emails]")

    count = 0
    for a in almn:
        init_date = datetime.strptime(a.get("initiation_date"), "%m/%d/%Y")

        if init_date < last_date:
            for email in a.findall("./emails/email"):
                eml = email.get("address")
                if "brhanson@comcast.net" not in eml:
                    print(eml)
                    # count += 1

    # print(len(almn))
    # print(count)

    # datetime.strptime(par.get("initiation_date"), "%m/%d/%Y")


if __name__ == "__main__":
    main()
