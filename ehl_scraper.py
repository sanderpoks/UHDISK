# -*- coding: UTF-8 -*-
from ehl_assistant import RecordManager, REDCAP_KEY_FILENAME, initiate_redcap, redcap_retrieve_remote, login_window
from redcap import Project, RedcapError
from ehlNavigeerimine import ehlMain
from time import sleep
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Iterable
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

APP_TITLE = "eHL Scraper"

class triaaz(Enum):
    PUNANE = auto()
    ORANZ = auto()
    KOLLANE = auto()
    ROHELINE = auto()
    SININE = auto()

class hingamissagedus(Enum):
    EI_HINGA = auto()
    HYPOVENTILATSIOON = auto()
    NORMOVENTILATSIOON = auto()
    HYPERVENTILATSIOON = auto()

@dataclass
class Record:
    rc_id : int
    isikukood : int = None
    hj_number : str = None

    def __post_init__(self):
        self.fill_nav_data()

    def fill_nav_data(self):
        """ Tõmbab redcapist alla uuritava isikukoodi ja HJ info ja paneb selle instantsi atribuutidesse """
        project = initiate_redcap()
        if project == None:
            print("RedCap andmebaasiga ühendumine ebaõnnestus")
            raise RedcapError
        record = redcap_retrieve_remote(project, self.rc_id)[0]
        self.isikukood = record["id_code"]
        self.hj_number = record["ref_num"]

    def __repr__(self):
        return (f"RedCap ID:\t{self.rc_id}\n"
                f"Isikukood:\t{self.isikukood}\n"
                f"Haigusjuht:\t{self.hj_number}")

@dataclass
class PhData:
    #Kiirabikaart olemas v mitte
    resp_qual : Enum = field(init=False)
    resp_quan : int = field(init=False)
    spo2 : int = field(init=False)
    sys : int = field(init=False)
    dia : int = field(init=False)
    hr : int = field(init=False)
    temp : float = field(init=False)

@dataclass
class EmoData:
    red_trauma : bool = field(init=False)
    emo_triage : Enum = field(init=False)
    emo_triage_nurse : str = field(init=False)
    emo_resp_qual : Enum = field(init=False)
    emo_resp_quan : str = field(init=False)
    emo_spo2 : int = field(init=False)
    emo_sys : int = field(init=False)
    emo_dia : int = field(init=False)
    emo_hr : int = field(init=False)
    emo_temp : float = field(init=False)

@dataclass
class PreviousDiagnosisData:
    kok_astma : bool = field(init=False)
    sydamepuudulikkus : bool = field(init=False)

@dataclass
class HospitalisationData:
    hospitalised_duration : int = field(init=False)
    icu : bool = field(init=False)
    icu_duration : int = field(init=False)
    hospitalised_death : bool = field(init=False)

@dataclass
class DiagnosisData:
    diagnosis_list: List[str] = field(init=False)

@dataclass
class UuritavData:
    ph : PhData = field(default_factory=PhData)
    emo : EmoData = field(default_factory=EmoData)
    prev_diag : PreviousDiagnosisData = field(default_factory=PreviousDiagnosisData)
    hospitalisation : HospitalisationData = field(default_factory=HospitalisationData)
    diagnosis : DiagnosisData = field(default_factory=DiagnosisData)

class Scraper:
    """
    Scraper koondab endas kõik funktsioonid, mis scrapevad eHList tunnuste kohta infot.
    Funktsioonid saavad scrapetud andmed otse uuritava dataklassi atribuutidesse salvestada.
    """
    def __init__(self):
        self.driver = ehl.driver

    def scrape_kiirabi_kaart(self, ph_data: PhData) -> PhData:
        kiirabiAndmed = PhData()
        ehl.ava_menyy_alajaotis("Päevik")
        self.driver.find_element(By.XPATH, "//a[@arn-evntpar='ALL_DAYS']").click()
        self.driver.find_element(By.XPATH, "//a[@arn-evntid='showAll']").click()
        #Siin võiks mingi parem lahendus olla
        sleep(1)

        # Kas kiirabi kaart on olemas
        if not self.driver.find_elements(By.XPATH, "//td[contains(text(),'Kiirabikaart nr.')]"):
            #Siin märgi, et kiirabi kaarti ei leitud ehk tagasta vastav class
            return

        kiirabikaart = self.driver.find_element(By.XPATH, "//td[contains(text(),'Kiirabikaart nr.')]").find_element(By.TAG_NAME, "a")
        actions = ActionChains(self.driver)
        # Scrollime lehel otsitava elemendini
        actions.move_to_element(kiirabikaart).click().perform()
        sleep(2.5)

        # Kõik avatud aknad:
        handles = self.driver.window_handles

        # Salvestan põhiakna
        parent_handle = self.driver.current_window_handle
        kiirabikaart_tekst = ""
        for i in range(len(handles)):
            if handles[i] != parent_handle:
                self.driver.switch_to.window(handles[i])
                kiirabikaart_tekst = self.driver.find_element(By.ID, "mainTable").text
                # Sulgen kõrval akna
                self.driver.close()
                break
        # Taastan algse akna
        self.driver.switch_to.window(parent_handle)

        #Scrapime kiirabi kaardi
        toorandmed = kiirabikaart_tekst.splitlines()
        if not toorandmed:
            #Tagastan tühja klassi, None tagastada ei lase - pean seda veel uurima.
            return kiirabiAndmed()

        for i in toorandmed:
            # Kvalitatiivne hingamissagedus
            if "Hingamissageduse tase" in i and len(i.split(" ")) == 3:
                #Siin kindlasti parem viis kui järjest mingeid if-e panna.
                splitvalue = i.split(" ")[2]
                if splitvalue == "hüperventilatsioon":
                    kiirabiAndmed.resp_qual = "4" #Siin pean kõik järjest classi muutujatega asendama.
                if splitvalue == "hüpoventilatsioon":
                    kiirabiAndmed.resp_qual = "2"
                if splitvalue == "normoventilatsioon":
                    kiirabiAndmed.resp_qual = "3"

            # Kvantitatiivne hingamissagedus
            if "Hingamissagedus" in i and "korda/min" in i  and len(i.split(" ")) == 3:
                kiirabiAndmed.resp_quan = i.split(" ")[1]
            #elif self.kiirabi[10] == "":
            #    self.kiirabi[10] = "1"

            # SpO2
            if "SpO2" in i and len(i.split(" ")) == 3:
                kiirabiAndmed.spo2 = i.split(" ")[1]

            # Süstoolne vererõhk
            if "süstoolne" in i and len(i.split(" ")) == 4:
                kiirabiAndmed.sys = i.split(" ")[2]

            # Diastoolne vererõhk
            if "diastoolne" in i and len(i.split(" ")) == 4:
                kiirabiAndmed.dia = i.split(" ")[2]

            # Südame löögisagedus
            if "Pulsisagedus" in i and len(i.split(" ")) == 3:
                kiirabiAndmed.hr = i.split(" ")[1]

            # Temperatuur
            if "Temperatuur" in i and len(i.split(" ")) == 4:
                kiirabiAndmed.temp = i.split(" ")[2]

        print(kiirabiAndmed)
        return kiirabiAndmed
    
    def scrape_triaaz(self, emo_data: EmoData) -> EmoData:
        # Martin
        pass

    def scrape_varasemad_diagnoosid(self, prev_diag_data: PreviousDiagnosisData) -> PreviousDiagnosisData:
        ehl.navigeeri("digilugu_diagnoosid")
        element = ehl.get_element(By.ID, "angularIframe", "Iframe")
        self.driver.switch_to.frame(element)
#        element = ehl.get_element(By.XPATH, "/html/body/ui-view/div[2]/div[1]/div/div/form/div/div/hc-panel/div/div[2]/div/div/table/thead/tr[1]/th/a", "Kõik kirjed", clickable=True)
#        element.click
        # See veel ei tööta, jätkan järgmine kord siit

    def scrape_hj_diagnoosid(self, diagnoosid_data: DiagnosisData) -> DiagnosisData:
        # Martin
        pass

    def scrape_hospitaliseerimise_info(self, hosp_data: HospitalisationData) -> HospitalisationData:
        # Martin
        pass 
    
@dataclass
class Uuritav:
    rc_id : int
    record : Record = field(init=False)
    data : UuritavData = field(default_factory=UuritavData)
    scraper : Scraper = field(default_factory=Scraper)
    
    def __post_init__(self) -> None:
        self.record = Record(self.rc_id)

        self.log_in()
        self.ehl_navigate()
        self.scrape_data()
        self.print()

    def scrape_data(self) -> None:
        self.scraper.scrape_kiirabi_kaart(self.data.ph)
        self.scraper.scrape_triaaz(self.data.emo)
        self.scraper.scrape_varasemad_diagnoosid(self.data.prev_diag)
        self.scraper.scrape_hj_diagnoosid(self.data.diagnosis)
        self.scraper.scrape_hospitaliseerimise_info(self.data.hospitalisation)
        

    def print(self) -> None:
        print(self.record)

    def log_in(self):
        ehl.navigeeri("logi_sisse")

    def ehl_navigate(self) -> None:
        ehl.navigeeri("haiguslugu", self.record.isikukood, self.record.hj_number)

    

def get_redcap_id_list() -> Iterable[int]:
    return [2555]
    #return range(500,510)
    #return [250,272,290]
    #pass

def main():
    global ehl
    ehl = ehlMain()
    ehl.ava()
    #login_window("eHL Scraper")
    redcap_id_list = get_redcap_id_list()
    for rc_id in redcap_id_list:
        uuritav = Uuritav(rc_id)
        # Upload to redcap?

if __name__ == "__main__":
    main()

