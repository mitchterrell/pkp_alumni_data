import os
import sys
from datetime import datetime

## Global Objects
almn_dict = {}

## Util Functions
def trim_phone_number(num_str_in):
    num_str_in = num_str_in.replace(' ', '')
    num_str_in = num_str_in.replace('-', '')
    num_str_in = num_str_in.replace('(', '')
    num_str_in = num_str_in.replace(')', '')
    num_str_in = num_str_in.replace('+1', '')
    return num_str_in

def try_match(match_type, first, last, phone=''):
    local_key = ''
    if(match_type == 'name_key' or match_type == 'preferred_name_key'):
        local_key = first.lower() + '_' + last.lower()
    elif(match_type == 'name_num_key'):
        local_key = first.lower() + '_' + last.lower() + '_' + trim_phone_number(phone)
    elif(match_type == 'last_and_phone_key'):
        local_key = last.lower() + '_' + trim_phone_number(phone)
    elif(match_type == 'last_init'):
        ## Phone number is now init year
        local_key = last.lower() + '_' + phone

    match = []
    for sales_id, almn_obj in almn_dict.items():
        if(match_type == 'name_key'):
            to_check = almn_obj.name_key()
        elif(match_type == 'preferred_name_key'):
            to_check = almn_obj.preferred_name_key()
        elif(match_type == 'name_num_key'):
            to_check = almn_obj.name_num_key()
        elif(match_type == 'last_and_phone_key'):
            to_check = almn_obj.last_and_phone_key()
        elif(match_type == 'last_init'):
            to_check = almn_obj.last_init()

        if(to_check == local_key):
            match.append(almn_obj)

    return match

def check_all_match(first, last, phones, init_year, do_print=True):
        history_str = ''
        match = try_match('name_key', first, last)
        history_str += ('name_key [%d]' % len(match))

        if(len(match) == 0):
            match = try_match('preferred_name_key', first, last)
            history_str += (' | preferred_name_key [%d]' % len(match))
            if(len(match) == 0):
                for phone in phones:
                    match = try_match('last_and_phone_key', first, last, phone)
                    history_str += (' | last_and_phone_key_%d [%d]' % (phones.index(phone), len(match)))
                    if(len(match) == 1):
                        break
        elif(len(match) > 1):
            prev_match = match
            for phone in phones:
                match = try_match('name_num_key', first, last, phone)
                history_str += (' | name_num_key_%d [%d]' % (phones.index(phone), len(match)))
                if(len(match) == 1):
                    break

            if(len(match) == 0):
                for m in prev_match:
                    if(m.base_info['initiation_date'].split('/')[-1] == init_year):
                        match.append(m)

                history_str += (' | init_year [%d]' % (len(match)))


        if(len(match) == 0):
            match = try_match('last_init', first, last, phone=init_year)
            history_str += (' | last_init [%d]' % (len(match)))



        if(do_print and len(match) == 0):
            print('%s %s --> No Match' % (first, last))
            print(history_str)
        elif(do_print and len(match) > 1):
            print('%s %s --> Too many matchs [%d]' % (first, last, len(match)))
            print(history_str)


        if(len(match) == 0 or len(match) > 1):
            return None

        return match[0]

def dump_alumni_to_csv(path):
    with open(path, 'w') as to_dump:
        do_headers = True
        for key, value in almn_dict.items():
            if(do_headers):
                for h,h_val in value.base_info.items():
                    to_dump.write('%s,' % h)
                to_dump.write('\n')
                do_headers = False

            for h,h_val in value.base_info.items():
                to_dump.write('%s,' % h_val)
            to_dump.write('\n')

## Helpful tip --> Address sometimes contain newline, in excel call clean on whole file first to remove newline
#        ## Key == firtname_lastname_initYR_initMNTH_initDAY
#        init_date = datetime.strptime(dat[6], '%m/%d/%Y')
#        key = dat[0].lower() + '_' + dat[2].lower() + '_' + init_date.strftime("%Y_%m_%d")

class alumni_dat:

    def __init__(self, headers):
        # Initialize Baseline Alumni Data
        self.base_headers           = headers
        self.was_mn_base            = False
        self.was_mn_beta_almn       = False
        self.was_mn_gam_delt_almn   = False
        self.was_tc_almn            = False
        self.base_info              = { }
        for h in self.base_headers:
            self.base_info[h] = 'NA'


        ## Pennington Data [0] == headers || [1] == data
        self.penngington_feasibility_study  = []
        self.pennington_call_status         = []
        self.pennington_contact_list        = []
        self.pennington_eras                = []
        self.pennington_focus_group         = []

    def base_key(self):
        return self.base_info['salesforce_id']

    def name_key(self):
        return self.base_info['legal_first_name'].lower() + '_' + self.base_info['legal_last_name'].lower()

    def preferred_name_key(self):
        return self.base_info['preferred_first_name'].lower() + '_' + self.base_info['legal_last_name'].lower()

    def name_num_key(self):
        if(self.base_info['phone'] != ''):
            return self.base_info['legal_first_name'].lower() + '_' + self.base_info['legal_last_name'].lower() + '_' + trim_phone_number(self.base_info['phone'])
        else:
            return 'error'

    def last_and_phone_key(self):
        if(self.base_info['phone'] != ''):
            return self.base_info['legal_last_name'].lower() + '_' + trim_phone_number(self.base_info['phone'])
        else:
            return 'error'

    def last_init(self):
        if(self.base_info['initiation_date'] != ''):
            return self.base_info['legal_last_name'].lower() + '_' + self.base_info['initiation_date'].split('/')[-1]
        else:
            return 'error'

    def assimilate(self, new_one):
        for key, val in self.base_info.items():
            ## If we had an NA before and now we have value, add it
            if(val == 'NA' and new_one.base_info[key] != 'NA'):
                self.base_info[key] = new_one.base_info[key]

            ## If both were not NA and both were unequal, send error
            elif(val != 'NA' and new_one.base_info[key] != 'NA' and val != new_one.base_info[key]):
                print('ERROR: Unexpected mismatch during assimilation\n[%s] --> [%s] != [%s]' % (key, val, new_one.base_info[key]))

            self.was_mn_base        = True if(new_one.was_mn_base)      else self.was_mn_base
            self.was_mn_beta_almn   = True if(new_one.was_mn_beta_almn) else self.was_mn_beta_almn
            self.was_tc_almn        = True if(new_one.was_tc_almn)      else self.was_tc_almn


## Global Paths
# region 

## Global Foundation Data Paths
mn_beta_all_time    = r'.\raw_inputs\from_foundation\2022\mn_beta_all_time_member_list.csv'
mn_beta_alumni      = r'.\raw_inputs\from_foundation\2022\mn_beta_alumni_list.csv'
mn_gam_delt_alumni  = r'.\raw_inputs\from_foundation\2022\mn_gamma_mn_delta_2022.csv'
twin_cities_alumni  = r'.\raw_inputs\from_foundation\2022\twin_cities_alumni_list.csv'

## Global Pennington Data Paths
penn_feasability    = r'.\raw_inputs\pennington_feasibility\penngington_feasibility_study.csv'
penn_call_status    = r'.\raw_inputs\pennington_feasibility\pennington_call_status.csv'
penn_contact_list   = r'.\raw_inputs\pennington_feasibility\pennington_contact_list.csv'
penn_eras           = r'.\raw_inputs\pennington_feasibility\pennington_eras.csv'
penn_focus_group    = r'.\raw_inputs\pennington_feasibility\pennington_focus_group.csv'

## Global Alumni Event Paths
fd_base_path        = r'.\raw_inputs\alumni_event_attendance\founders_day'
fd_attendance       = { 2016: os.path.join(fd_base_path, 'fd_2016.csv'),
                        2017: os.path.join(fd_base_path, 'fd_2017.csv'),
                        2019: os.path.join(fd_base_path, 'fd_2019.csv'),
                        2020: os.path.join(fd_base_path, 'fd_2020.csv'),
                        2022: os.path.join(fd_base_path, 'fd_2022.csv')
                      }
tccup_base_path     = r'.\raw_inputs\alumni_event_attendance\tcaa_cup'
tccup_attendance    = { 2016: os.path.join(tccup_base_path, 'tcaa_2016.csv'),
                        2017: os.path.join(tccup_base_path, 'tcaa_2016.csv'),
                        2019: os.path.join(tccup_base_path, 'tcaa_2016.csv')
                      }

## Global Misc Paths
fb_members          =  r'.\raw_inputs\misc\facebook_list_04_01_22.csv'

#endregion 

def add_to_header(header_in, file_in):
    with open(file_in, 'r') as f:
        line = f.readline()
        for h in line.split(','):
            h = h.lower().replace(' ', '_').replace('\n', '')
            if(h not in header_in):
                header_in.append(h)

def parse_base_file(file_in, header_in, true_switch=0, error_on_exist=False):
    with open(file_in, 'r') as f:
        local_headers   = { }
        for h in header_in:
            local_headers[h] = -1

        head_split = f.readline().split(',')
        for h in range(0, len(head_split)):
            local_headers[head_split[h].lower().replace(' ', '_').replace('\n', '')] = h

        lines = f.readlines()
        for l in lines:
            tmp     = alumni_dat(header_in)
            values  = l.split(',')
            for name, index in local_headers.items():
                if(index != -1):
                    tmp.base_info[name] = values[index].replace('\n', '').replace('  ', ' ')

            tmp.was_mn_base             = True if(true_switch == 0) else tmp.was_mn_base
            tmp.was_mn_beta_almn        = True if(true_switch == 1) else tmp.was_mn_beta_almn
            tmp.was_mn_gam_delt_almn    = True if(true_switch == 2) else tmp.was_mn_gam_delt_almn
            tmp.was_tc_almn             = True if(true_switch == 3) else tmp.was_tc_almn

            if(tmp.base_key() in almn_dict):
                if(error_on_exist):
                    print("ERROR: Unexpected sales force ID key repeat [%s]" % tmp.base_key())
                else:
                    almn_dict[tmp.base_key()].assimilate(tmp)
            else:
                almn_dict[tmp.base_key()] = tmp

## Parse Baseline Alumni Object
def parse_baseline():

    ## Extract unique list of headers between all three files
    #region
    headers = []
    add_to_header(headers, mn_beta_all_time)
    add_to_header(headers, mn_beta_alumni)
    add_to_header(headers, mn_gam_delt_alumni)
    add_to_header(headers, twin_cities_alumni)
    #endregion

    ## Parse the first alumni dump file
    parse_base_file(mn_beta_all_time,   headers, 0, error_on_exist=True)
    parse_base_file(mn_beta_alumni,     headers, 1, error_on_exist=False)
    parse_base_file(mn_gam_delt_alumni, headers, 2, error_on_exist=False)
    parse_base_file(twin_cities_alumni, headers, 3, error_on_exist=False)

    ## Print some final statistics
    was_mn_base_cnt         = 0
    was_mn_beta_almn_cnt    = 0
    was_tc_almn_cnt         = 0
    mn_base_not_mn_almn     = 0
    mn_almn_not_mn_base     = 0
    for key, val in almn_dict.items():
        was_mn_base_cnt         = (was_mn_base_cnt+1)       if val.was_mn_base      else was_mn_base_cnt
        was_mn_beta_almn_cnt    = (was_mn_beta_almn_cnt+1)  if val.was_mn_beta_almn else was_mn_beta_almn_cnt
        was_tc_almn_cnt         = (was_tc_almn_cnt+1)       if val.was_tc_almn      else was_tc_almn_cnt

        mn_base_not_mn_almn = (mn_base_not_mn_almn+1) if (val.was_mn_base and not val.was_mn_beta_almn) else mn_base_not_mn_almn
        mn_almn_not_mn_base = (mn_almn_not_mn_base+1) if (val.was_mn_beta_almn and not val.was_mn_base) else mn_almn_not_mn_base

    print('     TOTAL Alumni:                    [%4d]' % len(almn_dict))
    print('     MN Beta All Time Alumni Count:   [%4d]' % was_mn_base_cnt)
    print('     MN Beta Alumni Count:            [%4d]' % was_mn_beta_almn_cnt)
    print('     TC Alumni Count:                 [%4d]' % was_tc_almn_cnt)
    print('     MN Base, Not MN Alum:            [%4d]' % mn_base_not_mn_almn)
    print('     MN Alum, Not MN Base:            [%4d]' % mn_almn_not_mn_base)      
    
def parse_pennington_data():

    '''
    penngington_feasibility_study.csv:
        PCFS Rank
        Status
        Contact: PCFS Interview Date
        Contact: Preferred Year
        Campaign Member View: Last Activity Date
        Contact: Constituent Solicitor
        Contact: PCFS Estimate (Low)
        Contact: PCFS Estimate (High)
        Contact: First Name
        Contact: Maiden Name
        Contact: Last Name
        Contact: Mailing Address Line 1
        Contact: Mailing City
        Contact: Mailing State/Province
        Contact: Mailing Zip/Postal Code
        Contact: Home Phone
        Contact: Mobile
        Contact: Email
    '''

    pennington_dict = { }

    ## Assimliate <first_name>_<last_name> with Baseline list, print any matches
    lines = []
    with open(penn_feasability, 'r') as penn:
        lines = penn.readlines()

    headers = lines[0]

    for i in range(1, len(lines)):
        first       = lines[i].split(',')[8].lower()
        last        = lines[i].split(',')[10].lower()
        phones      = [lines[i].split(',')[15], lines[i].split(',')[16]]
        init_year   = lines[i].split(',')[3]

        match       = check_all_match(first, last, phones, init_year)

        if(match != None):
            match.penngington_feasibility_study.append(headers)
            match.penngington_feasibility_study.append(lines[i])
    
    ## Penn Call Status
    lines = []
    with open(penn_call_status, 'r') as penn:
        lines = penn.readlines()

    headers = lines[0]

    for i in range(1, len(lines)):
        first       = lines[i].split(',')[2].lower()
        last        = lines[i].split(',')[3].lower()
        phones      = [lines[i].split(',')[8], lines[i].split(',')[9], lines[i].split(',')[10]]
        init_year   = lines[i].split(',')[1]

        match       = check_all_match(first, last, phones, init_year)

        if(match != None):
            match.pennington_call_status.append(headers)
            match.pennington_call_status.append(lines[i])

    ## Penn Contact List
    lines = []
    with open(penn_contact_list, 'r') as penn:
        lines = penn.readlines()

    headers = lines[0]

    for i in range(1, len(lines)):
        first       = lines[i].split(',')[1].lower()
        last        = lines[i].split(',')[2].lower()
        phones      = [lines[i].split(',')[4], lines[i].split(',')[5]]
        init_year   = lines[i].split(',')[3]

        match       = check_all_match(first, last, phones, init_year)

        if(match != None):
            match.pennington_contact_list.append(headers)
            match.pennington_contact_list.append(lines[i])

    ## Penn Eras
    lines = []
    with open(penn_eras, 'r') as penn:
        lines = penn.readlines()

    headers = lines[0]

    for i in range(1, len(lines)):
        first       = lines[i].split(',')[1].lower().split(' ')[0]
        last        = lines[i].split(',')[1].lower().split(' ')[1]
        phones      = ['1234']
        init_year   = lines[i].split(',')[0]

        match       = check_all_match(first, last, phones, init_year)

        if(match != None):
            match.pennington_eras.append(headers)
            match.pennington_eras.append(lines[i])


    ## Penn Focus Group
    lines = []
    with open(penn_focus_group, 'r') as penn:
        lines = penn.readlines()

    headers = lines[0]

    for i in range(1, len(lines)):
        first       = lines[i].split(',')[0].lower().split(' ')[0]
        last        = lines[i].split(',')[0].lower().split(' ')[1]
        phones      = ['1234']
        init_year   = lines[i].split(',')[1]

        match       = check_all_match(first, last, phones, init_year)

        if(match != None):
            match.pennington_focus_group.append(headers)
            match.pennington_focus_group.append(lines[i])

def main():
    print("==== Starting Alumni Parse ==== ")

    print('\n = Parsing Baseline =')
    parse_baseline()

    # dump_alumni_to_csv(r'C:\Users\mitch\OneDrive\Documents\Masters\Misc\phi_kappa_psi\HC\new_property\misc\alumni_data\datparser\new_dumper.csv')

    print('\n = Parsing Pennington Data =')
    parse_pennington_data()

if __name__ == "__main__":
    main()
     