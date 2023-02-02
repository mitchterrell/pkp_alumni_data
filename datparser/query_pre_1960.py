from lxml import etree as ET
from datetime import datetime


def pre_70s_almn():
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


def phone_format(n):
    return format(int(n[:-1]), ",").replace(",", "-") + n[-1]


def brothers_for_andrew_johnson():
    print("Starting")

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()
    # almn = root.xpath(
    #     "./alumni[emails and @chapter_of_initiation = 'Minnesota Beta']"
    # )
    almn = root.xpath(
        "./alumni[@initiation_date and @chapter_of_initiation = 'Minnesota Beta']"
    )

    start_dat = datetime.strptime("12/31/1952", "%m/%d/%Y")
    end_dat = datetime.strptime("01/01/1955", "%m/%d/%Y")

    for a in almn:
        init_date = datetime.strptime(a.get("initiation_date"), "%m/%d/%Y")

        if init_date > start_dat and init_date < end_dat:

            print(f"{a.get('preferred_first_name')} {a.get('legal_last_name')}")
            print(f"    Initiation Date: {a.get('initiation_date')}")
            if a.find("emails") != None:
                print("    Emails:         ", end="")
                for e in a.findall("emails/email"):
                    print(f" {e.get('address')}", end=" |")
                print("")
            else:
                print("    Emails:          None")

            if a.find("phone_numbers") != None:
                print("    Phone:          ", end="")
                for e in a.findall("phone_numbers/phone"):
                    print(f" {phone_format(e.get('number'))}", end=" |")
                print("")
            else:
                print("    Phone:           None")

            # print(f"    Address?         {a.find('mailing_addresses') != None}")


def main():
    # pre_70s_almn()

    brothers_for_andrew_johnson()


if __name__ == "__main__":
    main()
