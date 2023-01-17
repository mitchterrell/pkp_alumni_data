from lxml import etree as ET
from datetime import datetime


def old_query():

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


def mailchimp_23():
    print("=== Starting Mail Chimp 2023 ===")

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()

    # (1) Count all contacts with emails that are NOT in the mailchimp
    not_in_mc = root.xpath("./alumni[emails/email and not(mailchimp)]")
    print(len(not_in_mc))
    print(not_in_mc[1].get("salesforce_id"))

    all_mc = root.xpath("./alumni[mailchimp]")
    print(f"All MC Contacts: [{len(all_mc)}]")

    print("=== Done ===")


def mailchimp_update():
    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()

    mc_contacts = root.xpath("./alumni[mailchimp]")

    cleaner_emails = {}
    for elem in root.findall("alumni/emails/email"):
        email = elem.get("address").lower()
        if email in cleaner_emails:
            print(f"whoa error - {email}")
        cleaner_emails[email] = elem.getparent().getparent()

    print(len(cleaner_emails))

    clean_csv_path = "./mailchimp_update/members_export_56f18ab2c0/subscribed_members_export_56f18ab2c0.csv"

    # (a) Open and parse the mailchimp exported data
    og_lines = open(clean_csv_path, "r").readlines()

    with open(
        "./mailchimp_update/members_export_56f18ab2c0/output/subscribed_out.csv", "w"
    ) as f_out:
        # (a) Write the header
        f_out.write(og_lines[0])

        used_sfid = []

        # (b) Edit existing contacts
        for line in og_lines[1:]:
            split_vals = line.split(",")

            email_addr_full = split_vals[0]
            email_addr = split_vals[0].lower()
            f_name = split_vals[1]
            l_name = split_vals[2]

            if email_addr not in cleaner_emails:
                print(f"No match for {f_name} {l_name} - {email_addr}")
                f_out.write(line)
            else:

                alumn = cleaner_emails[email_addr]

                used_sfid.append(alumn.get("salesforce_id"))

                init_chapter = alumn.get("chapter_of_initiation")
                init_year = datetime.strptime(alumn.get("initiation_date"), "%m/%d/%Y")
                init_year = init_year.strftime("%m/%d/%Y")

                first_half = f"{email_addr_full},{f_name},{l_name}"
                second_half = line.split(first_half + ",,,,")[-1]

                full_line = f"{first_half},,{init_chapter},{init_year},{second_half}"
                f_out.write(full_line)

        # (c) Add new contacts
        for email, xml in cleaner_emails.items():
            if xml.get("salesforce_id") not in used_sfid:

                all_emails = xml.findall("emails/email")
                email_to_use = ""
                if len(all_emails) > 1:
                    cur_source = ""
                    for eml in all_emails:
                        if len(eml.get("source")) > len(cur_source):
                            email_to_use = eml.get("address")
                            cur_source = eml.get("source")
                else:
                    email_to_use = all_emails[0].get("address")

                f_name = xml.get("preferred_first_name")
                l_name = xml.get("legal_last_name")
                init_chapter = xml.get("chapter_of_initiation")
                init_year = datetime.strptime(xml.get("initiation_date"), "%m/%d/%Y")
                init_year = init_year.strftime("%m/%d/%Y")

                f_out.write(
                    f"{email_to_use},{f_name},{l_name},,{init_chapter},{init_year},\n"
                )


def main():
    # mailchimp_23()

    mailchimp_update()


if __name__ == "__main__":
    main()
