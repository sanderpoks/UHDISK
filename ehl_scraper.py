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

    def __str__(self):
        return ("### NAV INFO ###\n"
                f"RedCap ID:\t{self.rc_id}\n"
                f"Isikukood:\t{self.isikukood}\n"
                f"Haigusjuht:\t{self.hj_number}\n")

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

    def __str__(self):
        return "\n".join(("### Kiirabikaart ###",
        f"Kval RR:\t{str(self.resp_qual)}",
        f"Kvan RR:\t{str(self.resp_quan)}",
        f"SpO2:\t\t{str(self.spo2)}",
        f"Sys BP:\t\t{str(self.sys)}",
        f"Dia BP:\t\t{str(self.dia)}",
        f"HR:\t\t{str(self.hr)}",
        f"Temp:\t\t{str(self.temp)}\n"))

@dataclass
class EmoData:
    red_trauma : bool = field(init=False)
    triage : Enum = field(init=False)
    triage_nurse : str = field(init=False)
    resp_qual : Enum = field(init=False)
    resp_quan : str = field(init=False)
    spo2 : int = field(init=False)
    sys : int = field(init=False)
    dia : int = field(init=False)
    hr : int = field(init=False)
    temp : float = field(init=False)

    def __str__(self):
        return "\n".join(("### EMO ###",
        f"Punane trauma:\t{str(self.red_trauma)}",
        f"Triaaž:\t{str(self.triage)}",
        f"Triaažiõde:\t{str(self.triage_nurseTriaaž)}",
        f"Kval RR:\t{str(self.resp_qual)}",
        f"Kvan RR:\t{str(self.resp_quan)}",
        f"SpO2:\t\t{str(self.spo2)}",
        f"Sys BP:\t\t{str(self.sys)}",
        f"Dia BP:\t\t{str(self.dia)}",
        f"HR:\t\t{str(self.hr)}",
        f"Temp:\t\t{str(self.temp)}\n"))

@dataclass
class PreviousDiagnosisData:
    kok_astma : bool = field(init=False)
    sydamepuudulikkus : bool = field(init=False)

    def __str__(self):
        return "\n".join(("### Varasemad diagnoosid ###",
        f"KOK/Astma:\t{str(self.kok_astma)}",
        f"Südamepuudulikkus:\t{str(self.sydamepuudulikkus)}"))

@dataclass
class HospitalisationData:
    hospitalised_duration : int = field(init=False)
    icu : bool = field(init=False)
    icu_duration : int = field(init=False)
    hospitalised_death : bool = field(init=False)

    def __str__(self):
        return "\n".join(("### Haiglaravi ###",
                "Haiglaravi kestus:\t{str(self.hospitalised_duration)}",
                "Intensiivravi:\t{str(self.icu)}",
                "Intensiivravi kestus:\t{str(self.icu_duration)}",
                "Surm haiglas:\t{str(self.hospitalised_death)}"))

@dataclass
class DiagnosisData:
    diagnosis_list: List[str] = field(init=False)

    def __str__(self):
        return "\n".join("### Diagnoosid ###".extend(self.diagnosis_list))

@dataclass
class UuritavData:
    ph : PhData = field(default_factory=PhData)
    emo : EmoData = field(default_factory=EmoData)
    prev_diag : PreviousDiagnosisData = field(default_factory=PreviousDiagnosisData)
    hospitalisation : HospitalisationData = field(default_factory=HospitalisationData)
    diagnosis : DiagnosisData = field(default_factory=DiagnosisData)

    def __str__(self):
        ph_str = ""
        if self.ph:
            ph_str = self.ph
        else:
            ph_str =  "Kiirabikaart puudub"
        return "\n".join((str(ph_str), str(self.emo), str(self.prev_diag), str(self.hospitalisation), str(self.diagnosis)))

class Scraper:
    """
    Scraper koondab endas kõik funktsioonid, mis scrapevad eHList tunnuste kohta infot.
    Funktsioonid saavad scrapetud andmed otse uuritava dataklassi atribuutidesse salvestada.
    """
    def __init__(self):
        self.driver = ehl.driver

    def scrape_kiirabi_kaart(self, ph_data: PhData) -> PhData:
        kiirabiAndmed = PhData()
        ehl.navigeeri("Päevik")
        element = ehl.get_element(By.XPATH, "//a[@arn-evntpar='ALL_DAYS']", "Kõik päevad")
        element.click()
        element = ehl.get_element(By.XPATH, "//a[@arn-evntid='showAll']", "Näita kõiki")
        element.click()
        #Siin võiks mingi parem lahendus olla
        sleep(1)

        # Kas kiirabi kaart on olemas
        if not self.driver.find_elements(By.XPATH, "//td[contains(text(),'Kiirabikaart nr.')]"):
            #Siin märgi, et kiirabi kaarti ei leitud ehk tagasta vastav class
            return None

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
            return None

        for i in toorandmed:
            # Kvalitatiivne hingamissagedus
            if "Hingamissageduse tase" in i and len(i.split(" ")) == 3:
                #Siin kindlasti parem viis kui järjest mingeid if-e panna.
                splitvalue = i.split(" ")[2]
                if splitvalue == "hüperventilatsioon":
                    kiirabiAndmed.resp_qual = hingamissagedus.HYPERVENTILATSIOON
                elif splitvalue == "hüpoventilatsioon":
                    kiirabiAndmed.resp_qual = hingamissagedus.HYPOVENTILATSIOON
                elif splitvalue == "normoventilatsioon":
                    kiirabiAndmed.resp_qual = hingamissagedus.NORMOVENTILATSIOON

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
        self.data.ph = self.scraper.scrape_kiirabi_kaart(self.data.ph)
        self.data.emo = self.scraper.scrape_triaaz(self.data.emo)
        self. data.prev_diag = self.scraper.scrape_varasemad_diagnoosid(self.data.prev_diag)
        self.data.diagnosis = self.scraper.scrape_hj_diagnoosid(self.data.diagnosis)
        self.data.hospitalisation = self.scraper.scrape_hospitaliseerimise_info(self.data.hospitalisation)
        

    def print(self) -> None:
        print(self.record)
        print(self.data)

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

