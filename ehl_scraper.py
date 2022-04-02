# -*- coding: UTF-8 -*-



class Uuritav:

    def __init__(self, redcap_id):
        self.parameter_list = ["red_trauma", "ph", "ph_resp_qual", "ph_resp_quan", "ph_spo2", "ph_sys", "ph_dia", "ph_hr", "ph_temp",
                               "emo_triage", "emo_triage_nurse", "emo_resp_qual", "emo_resp_quan", "emo_spo2", "emo_sys", "emo_dia", "emo_hr", "emo_temp",
                               "kok_astma", "sydamepuudulikkus", "diagnoses", "hospitalised", "hospitalised_duration", "icu", "icu_duration", "hospitalised_death"]
        self.fill_nav_data(redcap_id)
        
        self.ehl_navigate(self.nav_id, self.nav_hj)
        
        self.scrape_kiirabi_kaart()
        self.scrape_triaaz()
        self.scrape_varasemad_diagnoosid()
        self.scrape_hj_diagnoosid()
        self.scrape_hospitaliseerimise_info()
        

    def set(self, parameter, value):
        if parameter in self.parameter_list:
            self.parameter = value
        else:
            raise ValueError("Parameetrit ei eksisteeri")

    def get(self, parameter):
        if parameter in self.parameter_list:
            return self.parameter
        else:
            raise ValueError("Parameetrit ei eksisteeri")

    def fill_nav_data(self, redcap_id):
        """ Tõmbab redcapist alla uuritava isikukoodi ja HJ info ja seob selle instantsiga
            self.nav_id ja self.nav_hj"""

        # SANDER
        pass

    def ehl_navigate(self, nav_id, nav_hj):
        # SANDER
        pass

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

get_redcap_id_list():
    #return ["250"]
    pass

redcap_id_list = get_redcap_id_list()
for rc_id in redcap_id_list:
    uuritav = Uuritav(rc_id)
    # Upload to redcap?
