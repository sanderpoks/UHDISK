# -*- coding: UTF-8 -*-
from ehl_assistant import RecordManager, REDCAP_KEY_FILENAME, redcap_connect, redcap_retrieve_remote, login_window
from redcap import Project, RedcapError
from pyfields import field
from ehlNavigeerimine import ehlMain
from time import sleep



class Uuritav:

    def __init__(self, rc_id):
        self.parameter_list = ["red_trauma", "ph", "ph_resp_qual", "ph_resp_quan", "ph_spo2", "ph_sys", "ph_dia", "ph_hr", "ph_temp",
                               "emo_triage", "emo_triage_nurse", "emo_resp_qual", "emo_resp_quan", "emo_spo2", "emo_sys", "emo_dia", "emo_hr", "emo_temp",
                               "kok_astma", "sydamepuudulikkus", "diagnoses", "hospitalised", "hospitalised_duration", "icu", "icu_duration", "hospitalised_death"]

        # Initialize attributes
        self.rc_id = rc_id
        self.nav_id : int = field(doc="Uuritava isikukood")
        self.nav_hj : str = field(doc="Uuritava haigusjuhu number")

        self.red_trauma = None
        self.ph = None
        self.ph_resp_qual = None
        self.ph_resp_quan = None
        self.ph_spo2 = None
        self.ph_sys = None
        self.ph_dia = None
        self.ph_hr = None
        self.ph_temp = None
        self.emo_triage = None
        self.emo_triage_nurse = None
        self.emo_resp_qual = None
        self.emo_resp_quan = None
        self.emo_spo2 = None
        self.emo_sys = None
        self.emo_dia = None
        self.emo_hr = None
        self.emo_temp = None
        self.kok_astma = None
        self.sydamepuudulikkus = None
        self.diagnoses = None
        self.hospitalised = None
        self.hospitalised_duration = None
        self.icu = None
        self.icu_duration = None
        self.hospitalised_death = None
        

        # Start scraping
        self.fill_nav_data()
        self.print()
        
        self.ehl_navigate()
        
        self.scrape_kiirabi_kaart()
        self.scrape_triaaz()
        self.scrape_varasemad_diagnoosid()
        self.scrape_hj_diagnoosid()
        self.scrape_hospitaliseerimise_info()
        

    def print(self):
        print(f"RedCap ID:\t{self.rc_id}")
        print(f"Isikukood:\t{self.nav_id}")
        print(f"Haigusjuht:\t{self.nav_hj}")


    def fill_nav_data(self):
        """ Tõmbab redcapist alla uuritava isikukoodi ja HJ info ja seob selle instantsiga
            self.nav_id ja self.nav_hj"""
        project = redcap_connect()
        if project == None:
            print("RedCap andmebaasiga ühendumine ebaõnnestus")
            raise RedcapError
        record = redcap_retrieve_remote(project, self.rc_id)[0]
        self.nav_id = record["id_code"]
        self.nav_hj = record["ref_num"]

    def ehl_navigate(self):
        ehl.haiguslugude_otsimine(self.nav_id, self.nav_hj)

    def scrape_kiirabi_kaart(self):
        # M
        pass
    
    def scrape_triaaz(self):
        # M
        pass

    def scrape_varasemad_diagnoosid(self):
        # M
        pass

    def scrape_hj_diagnoosid(self):
        # SANDER
        pass

    def scrape_hospitaliseerimise_info(self):
        # M
        pass

def get_redcap_id_list():
    return [2550]
    #return range(500,510)
    #return [250,272,290]
    #pass

ehl = ehlMain()
ehl.ava()
login_window("eHL Scraper")
redcap_id_list = get_redcap_id_list()
for rc_id in redcap_id_list:
    uuritav = Uuritav(rc_id)
    # Upload to redcap?
