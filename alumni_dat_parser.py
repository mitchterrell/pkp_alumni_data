import os
from datetime import datetime
import sys

class alumni_dat:

    def __init__(self):
        # HEADERS: mn_chapters_alumni_2021.csv 
        self.legal_first_name           = ''
        self.preferred_first_name       = ''
        self.legal_last_name            = ''
        self.email                      = ''
        self.chapter_initiation         = ''
        self.initiation_date            = ''
        self.primary_street             = ''
        self.primary_city               = ''
        self.primary_state              = ''
        self.primary_zip                = ''
        self.primary_country            = ''            ## Not in twin_cities_30_mi_radius_2021
        self.was_mn_alumn               = False
        
        # HEADERS: twin_cities_30_mi_radius_2021.csv 
        # all same as above but these added
        self.undergrad_status           = ''
        self.phone                      = ''
        self.chapter_graduation         = ''
        self.was_30_mil_alumn           = False
        
    def compare_against(self, other):
        label_str = ['legal_first_name', 'preferred_first_name','legal_last_name','email',
        'chapter_initiation','initiation_date','primary_street','primary_city','primary_state','primary_zip','primary_country','undergrad_status','phone','chapter_graduation']
        
        if(self.legal_first_name != other.legal_first_name):
            print('Diff [%s] self vs. other [%s] [%s]' % ('legal_first_name', self.legal_first_name, other.legal_first_name))
        if(self.preferred_first_name != other.preferred_first_name):
            print('Diff [%s] self vs. other [%s] [%s]' % ('preferred_first_name', self.preferred_first_name, other.preferred_first_name))
        if(self.legal_last_name != other.legal_last_name):
            print('Diff [%s] self vs. other [%s] [%s]' % ('legal_last_name', self.legal_last_name, other.legal_last_name))
        if(self.email != other.email):
            print('Diff [%s] self vs. other [%s] [%s]' % ('email', self.email, other.email))
        if(self.chapter_initiation != other.chapter_initiation):
            print('Diff [%s] self vs. other [%s] [%s]' % ('chapter_initiation', self.chapter_initiation, other.chapter_initiation))
        if(self.initiation_date != other.initiation_date):
            print('Diff [%s] self vs. other [%s] [%s]' % ('initiation_date', self.initiation_date, other.initiation_date))
        if(self.primary_street != other.primary_street):
            print('Diff [%s] self vs. other [%s] [%s]' % ('primary_street', self.primary_street, other.primary_street))
        if(self.primary_city != other.primary_city):
            print('Diff [%s] self vs. other [%s] [%s]' % ('primary_city', self.primary_city, other.primary_city))
        if(self.primary_state != other.primary_state):
            print('Diff [%s] self vs. other [%s] [%s]' % ('primary_state', self.primary_state, other.primary_state))
        if(self.primary_zip != other.primary_zip):
            print('Diff [%s] self vs. other [%s] [%s]' % ('primary_zip', self.primary_zip, other.primary_zip))
        if(self.primary_country != other.primary_country):
            print('Diff [%s] self vs. other [%s] [%s]' % ('primary_country', self.primary_country, other.primary_country))
        if(self.undergrad_status != other.undergrad_status):
            print('Diff [%s] self vs. other [%s] [%s]' % ('undergrad_status', self.undergrad_status, other.undergrad_status))
        if(self.phone != other.phone):
            print('Diff [%s] self vs. other [%s] [%s]' % ('phone', self.phone, other.phone))
        if(self.chapter_graduation != other.chapter_graduation):
            print('Diff [%s] self vs. other [%s] [%s]' % ('chapter_graduation', self.chapter_graduation, other.chapter_graduation))
        
almn_dict = {}

## Parse mn_chapters_alumni_2021.csv
with open(r'.\raw_inputs\mn_chapters_alumni_2021.csv', 'r') as f:
    lines = f.readlines()
    
    for i in range(1, len(lines)):
        dat = lines[i].split(',')
        
        ## Key == firtname_lastname_initYR_initMNTH_initDAY
        init_date = datetime.strptime(dat[5], '%m/%d/%Y')
        key = dat[0].lower() + '_' + dat[2].lower() + '_' + init_date.strftime("%Y_%m_%d")
        
        ## Fill object
        tmp = alumni_dat()
        tmp.legal_first_name           = dat[0]
        tmp.preferred_first_name       = dat[1]
        tmp.legal_last_name            = dat[2]
        tmp.email                      = dat[3]
        tmp.chapter_initiation         = dat[4]
        tmp.initiation_date            = dat[5]
        tmp.primary_street             = dat[6]
        tmp.primary_city               = dat[7]
        tmp.primary_state              = dat[8]
        tmp.primary_zip                = dat[9]
        tmp.primary_country            = dat[10]
        tmp.was_mn_alumn               = True
        
        if(key in almn_dict):
            print('WARNING [%s] already in dict' % key)
            #almn_dict[key].compare_against(tmp)
        else: 
            ## Save in dictionary
            almn_dict[key] = tmp
            
## Parse twin_cities_30_mi_radius_2021.csv
with open(r'.\raw_inputs\twin_cities_30_mi_radius_2021.csv', 'r') as f:
    lines = f.readlines()
    
    for i in range(1, len(lines)):
        dat = lines[i].split(',')
        
        ## Key == firtname_lastname_initYR_initMNTH_initDAY
        init_date = datetime.strptime(dat[6], '%m/%d/%Y')
        key = dat[0].lower() + '_' + dat[2].lower() + '_' + init_date.strftime("%Y_%m_%d")
            
        if(key in almn_dict):
            almn_dict[key].undergrad_status             = dat[3]
            almn_dict[key].phone                        = dat[5]
            almn_dict[key].chapter_graduation           = dat[8]
            almn_dict[key].was_30_mil_alumn             = True
        else:
            
            tmp = alumni_dat()
            tmp.legal_first_name           = dat[0]
            tmp.preferred_first_name       = dat[1]
            tmp.legal_last_name            = dat[2]
            tmp.undergrad_status           = dat[3]
            tmp.email                      = dat[4]
            tmp.phone                      = dat[5]
            tmp.initiation_date            = dat[6]
            tmp.chapter_initiation         = dat[7]
            tmp.chapter_graduation         = dat[8]
            tmp.primary_street             = dat[9]
            tmp.primary_city               = dat[10]
            tmp.primary_state              = dat[11]
            tmp.primary_zip                = dat[12]
            tmp.was_30_mil_alumn           = True
            
            almn_dict[key] = tmp
            
            
just_mn = 0
just_30 = 0
both    = 0
for key, val in almn_dict.items():
    
    if(val.was_mn_alumn and not val.was_30_mil_alumn):
        just_mn += 1
    elif(val.was_30_mil_alumn and not val.was_mn_alumn):
        just_30 += 1
        if('Minnesota' in val.chapter_initiation):
            print(key)
    else:
        both += 1
    
    
    
print('Just MN [%d] Just 30 [%d] both [%d]' % (just_mn, just_30, both))
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            