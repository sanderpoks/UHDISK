# -*- coding: UTF-8 -*-
from ehl_assistant import RecordManager, REDCAP_KEY_FILENAME, redcap_connect, redcap_retrieve_remote, login_window
from redcap import Project, RedcapError
from pyfields import field
from ehlNavigeerimine import ehlMain
from time import sleep

class Scraper:
    """
    Scraper koondab endas kõik funktsioonid, mis scrapevad eHList tunnuste kohta infot.
    Funktsioonid saavad scrapetud andmed otse uuritava atribuutidesse salvestada.
    """

    def scrape_kiirabi_kaart(self, uuritav):
        # Martin
        pass
    
    def scrape_triaaz(self, uuritav):
        # Martin
        pass

    def scrape_varasemad_diagnoosid(self, uuritav):
        ehl.navigeeri("digilugu_diagnoosid")

    def scrape_hj_diagnoosid(self, uuritav):
        # Martin
        pass

    def scrape_hospitaliseerimise_info(self, uuritav):
        # Martin
        pass 
    

class Uuritav:

    def __init__(self, rc_id):
        # Initialize attributes
        self.rc_id = rc_id
        self.nav_id : int = field(doc="Uuritava isikukood")
        self.nav_hj : str = field(doc="Uuritava haigusjuhu number")

        self.scraper = Scraper()

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
        self.scrape_data()
        self.print()

    def scrape_data(self):
        self.ehl_navigate()
        
        self.scraper.scrape_kiirabi_kaart(self)
        self.scraper.scrape_triaaz(self)
        self.scraper.scrape_varasemad_diagnoosid(self)
        self.scraper.scrape_hj_diagnoosid(self)
        self.scraper.scrape_hospitaliseerimise_info(self)
        

    def print(self):
        print(f"RedCap ID:\t{self.rc_id}")
        print(f"Isikukood:\t{self.nav_id}")
        print(f"Haigusjuht:\t{self.nav_hj}")


    def fill_nav_data(self):
        """ Tõmbab redcapist alla uuritava isikukoodi ja HJ info ja paneb selle instantsi atribuutidesse """
        project = redcap_connect()
        if project == None:
            print("RedCap andmebaasiga ühendumine ebaõnnestus")
            raise RedcapError
        record = redcap_retrieve_remote(project, self.rc_id)[0]
        self.nav_id = record["id_code"]
        self.nav_hj = record["ref_num"]

    def ehl_navigate(self):
        ehl.navigeeri("haiguslugu", self.nav_id, self.nav_hj)

    

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
