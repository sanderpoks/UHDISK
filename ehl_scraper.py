#!/usr/bin/env python3
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
from bs4 import BeautifulSoup

APP_TITLE = "eHL Scraper"
INITIAL_VALUE = object()

class UnknownDigiluguTypeError(Exception):
    pass

class triaaz(Enum):
    PUNANE = auto()
    ORANZ = auto()
    KOLLANE = auto()
    ROHELINE = auto()
    SININE = auto()
    PUUDUB = auto()

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
    resp_qual : Enum = INITIAL_VALUE
    resp_quan : int = INITIAL_VALUE
    spo2 : int = INITIAL_VALUE
    sys : int = INITIAL_VALUE
    dia : int = INITIAL_VALUE
    hr : int = INITIAL_VALUE
    temp : float = INITIAL_VALUE

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
    red_trauma : bool = INITIAL_VALUE
    triage : Enum = INITIAL_VALUE
    triage_nurse : str = INITIAL_VALUE
    triage_subtype : str = INITIAL_VALUE
    resp_qual : Enum = INITIAL_VALUE
    resp_quan : str = INITIAL_VALUE
    spo2 : int = INITIAL_VALUE
    sys : int = INITIAL_VALUE
    dia : int = INITIAL_VALUE
    hr : int = INITIAL_VALUE
    temp : float = INITIAL_VALUE

    def __str__(self):
        return "\n".join(("### EMO ###",
        f"Punane trauma:\t{str(self.red_trauma)}",
        f"Triaaž:\t\t{str(self.triage)}",
        f"Triaažitüüp:\t{str(self.triage_subtype)}",
        f"Triaažiõde:\t{str(self.triage_nurse)}",
        f"Kval RR:\t{str(self.resp_qual)}",
        f"Kvan RR:\t{str(self.resp_quan)}",
        f"SpO2:\t\t{str(self.spo2)}",
        f"Sys BP:\t\t{str(self.sys)}",
        f"Dia BP:\t\t{str(self.dia)}",
        f"HR:\t\t{str(self.hr)}",
        f"Temp:\t\t{str(self.temp)}\n"))

@dataclass
class PreviousDiagnosisData:
    kok_astma : bool = INITIAL_VALUE
    sydamepuudulikkus : bool = INITIAL_VALUE

    def __str__(self):
        return "\n".join(("### Varasemad diagnoosid ###",
        f"KOK/Astma:\t\t{str(self.kok_astma)}",
        f"Südamepuudulikkus:\t{str(self.sydamepuudulikkus)}\n"))

@dataclass
class HospitalisationData:
    hospitalised_duration : int = INITIAL_VALUE
    icu : bool = INITIAL_VALUE
    icu_duration : int = INITIAL_VALUE
    hospitalised_death : bool =  INITIAL_VALUE

    def __str__(self):
        return "\n".join(("### Haiglaravi ###",
                f"Haiglaravi kestus:\t{str(self.hospitalised_duration)}",
                f"Intensiivravi:\t{str(self.icu)}",
                f"Intensiivravi kestus:\t{str(self.icu_duration)}",
                f"Surm haiglas:\t{str(self.hospitalised_death)}"))

@dataclass
class DiagnosisData:
    diagnosis_list: List[str] = INITIAL_VALUE

    def __str__(self):
        return_list = ["### Diagnoosid ###"]
        if self.diagnosis_list == INITIAL_VALUE:
            return "None"
        return_list.extend(self.diagnosis_list)
        return "\n".join(return_list)

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
        kiirabiAndmed = ph_data
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
        data = emo_data
        ehl.navigeeri("triaaz")
        # Triaažikategooria
        triaazi_varv = ehl.get_element(By.XPATH,'//*[@id="application-main-content"]/div[2]/div[2]/span[2]', "Triaažikategooria").text
        if "punane" in triaazi_varv:
            data.triage = triaaz.PUNANE
        elif "oranž" in triaazi_varv:
            data.triage = triaaz.ORANZ
        elif "kollane" in triaazi_varv:
            data.triage = triaaz.KOLLANE
        elif "roheline" in triaazi_varv:
            data.triage = triaaz.ROHELINE
        elif "sinine" in triaazi_varv:
            data.triage = triaaz.SININE
        print(f"Triaaž on {data.triage}")

        #Triaaži alatüüp
        element1 = ehl.get_element(By.XPATH, '//*[@id="fe-label-m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f1.regularTriageViewWidget.form.complaints"]', "Triaaži alatüüp")
        element2 = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[3]/div/table/tbody/tr/td/span', "Triaaži alatüüp 2")
        data.triage_subtype = element1.text + " " + element2.text
        
        #Triaažiõde
        data.triage_nurse = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td/span', "Triaažiõde").text

        # Kvalitatiivne hingamissagedus
        data.resp_qual = None #Automaatselt ei täida seda

        # Kvantitatiivne hingamissagedus
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[2]/td/span/span[2]', "Kvantitatiivne hingamissagedus"):
            data.resp_quan = None
        else:
            data.resp_quan = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[2]/td/span/span[2]', "Kvantitatiivne hingamissagedus").text
        
        # SpO2
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td/span/span[2]', "SpO2"):
            data.spo2 = None
        else:
            data.spo2 = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[3]/td/span/span[2]', "SpO2").text

        #Pulsisagedus
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[5]/td/span/span[2]', "Pulsisagedus"):
            data.hr = None
        else:
            data.hr = ehl.get_element(By.XPATH,'//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[5]/td/span/span[2]', "Hingamissagedus").text
        # Vererõhk
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td/span/span[2]', "Vererõhk"):
            data.sys = None
            data.dia = None
        else:
            bp = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td/span/span[2]', "Vererõhk").text
            sys,dia = bp.split(" / ")
            if sys:
                data.sys = sys
            else:
                data.sys = None
            if dia:
                data.dia = dia
            else:
                data.dia = None

        # Temp
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[4]/td/span/span[2]', "Temp"):
            data.temp = None
        else:
            data.temp = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[4]/td/span/span[2]', "temp").text


        return data



    def scrape_varasemad_diagnoosid(self, prev_diag_data: PreviousDiagnosisData) -> PreviousDiagnosisData:
        data = prev_diag_data
        digiloo_diag_tyybid = {
                'Ambulatoorne epikriis ' : "amb",
                'Eri-sõeluuring soolekasvaja avastamiseks ' : "soel_soole",
                'Kiirabikaart ' : "kiirabi",
                'Saatekiri ambulatoorsele vastuvõtule ' : "amb_saatekiri",
                'Saatekiri eriarsti visiidile ' : "eri_saatekiri",
                'Saatekiri uuringule ' : "uuring_saatekiri",
                'Statsionaarne epikriis ' : "stats",
                'Päevaravi epikriis ' : "paev",
                'Saatekiri haiglaravile ' : "haigla_saatekiri",
                'Eri-sõeluuring rinnanäärmekasvaja avastamiseks ' : "soel_rinna",
                'Eri-sõeluuring emakakaelakasvaja avastamiseks ' : "soel_emakakael"
                }
        kaasatud_tyybid = {"amb", "stats", "paev"}
        diagnosis_set = set()

        ehl.navigeeri("digilugu_diagnoosid")
        element = ehl.get_element(By.ID, "angularIframe", "Iframe")
        self.driver.switch_to.frame(element)
        element = ehl.get_element(By.XPATH, "/html/body/ui-view/div[2]/div[1]/div/div/form/div/div/hc-panel/div/div[2]/div/div/table/thead/tr[1]/th/a", "Kõik kirjed", clickable=True)
        element.click()
        element = ehl.get_element(By.XPATH, "/html/body/ui-view/div[2]/div[1]/div/div/form/div/div/hc-panel/div/div[2]/div/div/table/tbody", "Diagnooside tabel")
        html_text = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_text, "html.parser")
        for row in soup.findAll("tr"):
            element_list =  row.findAll("td")
            for i in element_list:
                title_text = i['data-title-text']
                if title_text == "Diagnoosi kood, nimetus":
                    rhk = i.get_text().split()[0]
                if title_text == "Pärineb dokumendist":
                    allikas = i.get_text()
            if allikas not in digiloo_diag_tyybid:
                raise UnknownDigiluguTypeError(f"Tüüpi {allikas} ei eksisteeri võimalike tüüpide nimekirjas")
            if digiloo_diag_tyybid[allikas] in kaasatud_tyybid:
                diagnosis_set.add(rhk)

        data.kok_astma = self.isDiagnosisKOKAstma(diagnosis_set)
        data.sydamepuudulikkus = self.isDiagnosisSydamepuudulikkus(diagnosis_set)
        self.driver.switch_to.default_content()
        return data

    def isDiagnosisKOKAstma(self, diagnoosid: set):
        kok_astma_set = {"J44", "J44.0", "J44.1", "J44.8", "J44.9", "J45", "J45.0", "J45.1", "J45.8", "J45.9", "J46"}
        if (diagnoosid & kok_astma_set):
            print(f"Patsiendil on KOK/astma - diagnoosid {kok_astma_set.intersection(diagnoosid)}")
            return True
        else:
            print("Patsiendil ei ole KOKi ega Astmat anamneesis")
            return False

    def isDiagnosisSydamepuudulikkus(self, diagnoosid: set):
        sydamepuudulikkus_set = {"I50", "I50.0", "I50.1", "I50.9", "I11.0", "I13.0", "I13.2", "I42", "I42.0", "I42.1", "I42.2", "I42.3", "I42.4", "I42.5", "I42.6",
                "I42.7", "I42.8", "I42.9"}
        if (diagnoosid & sydamepuudulikkus_set):
            print(f"Patsiendil on sydamepuudulikkus - diagnoosid {sydamepuudulikkus_set.intersection(diagnoosid)}")
            return True
        else:
            print("Patsiendil ei ole südamepuudulikkust anamneesis")
            return False



    def scrape_hj_diagnoosid(self, diagnoosid_data: DiagnosisData) -> DiagnosisData:
        # Martin
        pass

    def scrape_hospitaliseerimise_info(self, hosp_data: HospitalisationData) -> HospitalisationData:
        data = hosp_data
        int_osakonnad = {'KAIN - kardiointensiivravi osakond',
                "AIEI - 1. intensiivravi",
                "AITI - 2. intensiivravi",
                "AIKI - 3. intensiivravi"}
        # Lähme haigusjuhu koondandmete lehele
        element = ehl.get_element(By.XPATH, '/html/body/div[1]/form/div[2]/div[2]/div/div/div/p[2]/a[3]', "HJ koondandmed", clickable=True)
        element.click()
        hosp_paevad = {}
        tabel = ehl.get_element(By.XPATH, '//*[@id="m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f1.referrerInfoWidget.list_listUpdate"]', "HJ koondandmed").get_attribute('innerHTML')
        soup = BeautifulSoup(tabel, "html.parser")
        for row in soup.findAll("tr"):
            if len(row.get_text(strip=True)) != 0:
                element_line = row.findAll("td")
                osakond = element_line[0].get_text().strip()
                paevi = int(element_line[3].get_text().strip())
                if osakond not in hosp_paevad:
                    hosp_paevad[osakond] = paevi
                else:
                    hosp_paevad[osakond] += paevi
        data.hospitalised_duration = sum(hosp_paevad.values())
        osakonnad = hosp_paevad.keys()
        if set(osakonnad) & int_osakonnad:
            data.icu = True
            icu_days = 0
            for i in osakonnad:
                if i in int_osakonnad:
                    icu_days += hosp_paevad[i]
            data.icu_duration = icu_days
        else:
            data.icu = False
            data.icu_duration = 0
        ehl.navigeeri("Epikriis")
        element = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td', "Väljakirjutamise staatus")
        staatus = element.text
        if staatus == "Surm":
            data.hospitalised_death = True
        else:
            data.hospitalised_death = False

        return data
    
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
        self.data.prev_diag = self.scraper.scrape_varasemad_diagnoosid(self.data.prev_diag)
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

