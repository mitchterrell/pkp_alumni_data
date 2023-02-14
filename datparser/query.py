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


def emails_for_tom():

    purchased_emails = []
    purchased_names = []

    with open(R"C:\Users\mitch\Downloads\fd_2023_sales_so_far.csv", "r") as f:

        for line in f.readlines()[1:]:
            split_vals = line.replace('"', "").split(",")

            f_name = split_vals[16].lower()
            l_name = split_vals[17].lower()
            email = split_vals[18].lower()

            purchased_emails.append(email)
            purchased_names.append(f"{f_name}_{l_name}")

    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()
    fd_contacts = root.xpath(
        "./alumni/event_attendance[@FD_2016 or @FD_2017 or @FD_2019 or @FD_2020 or @FD_2022]"
    )

    with open("C:/users/mitch/Downloads/fd_emails_for_tom.csv", "w") as f:

        header = "First Name,Last Name,Email #1,Email #2, Email #3,Email #4,FD 2016,FD 2017,FD 2019,FD 2020,FD 2022,Already Purchased\n"
        f.write(header)

        for fd in fd_contacts:
            bought_ticket = False

            par = fd.getparent()

            f_name = par.get("preferred_first_name")
            l_name = par.get("legal_last_name")

            if f"{f_name.lower()}_{l_name.lower()}" in purchased_names:
                print(f"No Use: {f_name} {l_name}")
                bought_ticket = True
                # continue

            if datetime.strptime(
                par.get("initiation_date"), "%m/%d/%Y"
            ) < datetime.strptime("01/01/1970", "%m/%d/%Y"):
                print(
                    f"WARNING: {f_name} {l_name} initiated on {par.get('initiation_date')}"
                )
                continue

            emails = [
                [x.get("address"), x.get("source")]
                for x in fd.getparent().findall("emails/email")
            ]
            emails.sort(key=lambda x: len(x[1]), reverse=True)

            FD_2016 = "FD_2016" in fd.attrib
            FD_2017 = "FD_2017" in fd.attrib
            FD_2019 = "FD_2019" in fd.attrib
            FD_2020 = "FD_2020" in fd.attrib
            FD_2022 = "FD_2022" in fd.attrib

            f.write(f"{f_name},{l_name},")
            was_email_in = False
            for i in range(0, 4):
                if i < len(emails):
                    if emails[i][0] in purchased_emails:
                        print(f"No Use {f_name} {l_name} --> {emails[i][0]}")
                        bought_ticket = True
                        # was_email_in = True
                        # break

                    f.write(f"{emails[i][0]},")
                else:
                    f.write(",")

            if was_email_in:
                continue

            f.write(
                f"{'TRUE' if FD_2016 else ''},{'TRUE' if FD_2017 else ''},{'TRUE' if FD_2019 else ''},{'TRUE' if FD_2020 else ''},{'TRUE' if FD_2022 else ''},{'YES' if bought_ticket else ''}\n"
            )

            # return


def eugene_pkp_members():
    tree = ET.parse("./new_output/assimilated_foundation.xml")
    root = tree.getroot()

    mn_gamma_members = root.xpath("./alumni[@chapter_of_initiation='Minnesota Gamma']")

    print(len(mn_gamma_members))

    min_date = datetime.now()
    max_date = datetime.min
    for member in mn_gamma_members:
        date = datetime.strptime(member.get("initiation_date"), "%m/%d/%Y")

        if date < min_date:
            min_date = date
        if date > max_date:
            max_date = date

        start = datetime.strptime("01/01/1965", "%m/%d/%Y")
        end = datetime.strptime("12/31/1969", "%m/%d/%Y")

        if date > start and date < end:
            # print(
            #     f"{member.get('preferred_first_name')} {member.get('legal_last_name')} --> {member.get('initiation_date')} --> {'Had Email' if member.find('emails') != None else ''}"
            # )
            print(
                f"{member.get('preferred_first_name')} {member.get('legal_last_name')}"
            )

    print(min_date)
    print(max_date)


def main():
    # mailchimp_23()

    # mailchimp_update()

    # emails_for_tom()

    eugene_pkp_members()


if __name__ == "__main__":
    main()
