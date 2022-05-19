#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from ehl_assistant import RecordManager, REDCAP_KEY_FILENAME, initiate_redcap, redcap_retrieve_remote, login_window
from ehlredcap import RedcapConnection
from ehlNavigeerimine import ehlMain
from time import sleep
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Iterable, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import logging
from datetime import date

APP_TITLE = "eHL Scraper"
INITIAL_VALUE = object()

class UnknownDigiluguTypeError(Exception):
    pass

class triaaz(Enum):
    PUNANE = 1
    ORANZ = 2
    KOLLANE = 3
    ROHELINE = 4
    SININE = 5
    PUUDUB = 6

class hingamissagedus(Enum):
    EI_HINGA = 1
    HYPOVENTILATSIOON = 2
    NORMOVENTILATSIOON = 3
    HYPERVENTILATSIOON = 4

class uhdisk_diag(Enum):
    PNEUMONIA = 1
    PNEUMOTHORAX = 7
    PLEURAL_EFFUSION = 6
    PULMONARY_EDEMA = 2
    MYOCARDIAL_INFARCTION = 3
    PULMONARY_EMBOLISM = 4
    COPD_ASTHMA = 5
    PERICARDIAL_EFFUSION = 8


@dataclass
class Record:
    rc : RedcapConnection
    rc_id : int
    isikukood : int = None
    hj_number : str = None

    def __post_init__(self):
        self.fill_nav_data()

    def fill_nav_data(self):
        """ Tõmbab redcapist alla uuritava isikukoodi ja HJ info ja paneb selle instantsi atribuutidesse """
        record = self.rc.download(self.rc_id, fields = ("id_code", "ref_num"))
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
                f"Surm haiglas:\t{str(self.hospitalised_death)}\n"))

@dataclass
class DiagnosisData:
    diagnosis_list: Set[str] = INITIAL_VALUE
    uhdisk: bool = INITIAL_VALUE
    uhdisk_list : Set[Enum] = INITIAL_VALUE

    def __str__(self):
        header = "### Diagnoosid ###"
        if self.diagnosis_list == INITIAL_VALUE:
            return "None" #Mingil põhjusel pole patsiendil ühtegi diagnoosi haigusjuhus leitud
        diag_list_return = f"Diagnoosid:\t{str(self.diagnosis_list)}"
        uhdisk_return = f"UHDISK:\t{str(self.uhdisk)}"
        if self.uhdisk:
            uhdisk_list_return = f"UHDISK_diagnoosid:\t{str(self.uhdisk_list)}"
        else:
            uhdisk_list_return = "UHDISK diagnoose ei ole"
        return "\n".join([header, diag_list_return, uhdisk_return, uhdisk_list_return])

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
            sleep(3)
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
            if "Temperatuur" in i and len(i.split(" ")) == 3:
                kiirabiAndmed.temp = i.split(" ")[1]
            elif "Temperatuur" in i and len(i.split(" ")) == 4:
                kiirabiAndmed.temp = i.split(" ")[2]
        if kiirabiAndmed.resp_quan == INITIAL_VALUE:
            kiirabiAndmed.resp_quan = None
        if kiirabiAndmed.resp_qual == INITIAL_VALUE:
            kiirabiAndmed.resp_qual = None
        if kiirabiAndmed.spo2 == INITIAL_VALUE:
            kiirabiAndmed.spo2 = None
        if kiirabiAndmed.sys == INITIAL_VALUE:
            kiirabiAndmed.sys = None
        if kiirabiAndmed.dia == INITIAL_VALUE:
            kiirabiAndmed.dia = None
        if kiirabiAndmed.hr == INITIAL_VALUE:
            kiirabiAndmed.hr = None
        if kiirabiAndmed.temp == INITIAL_VALUE:
            kiirabiAndmed.temp = None
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
        logging.info(f"Triaaž on {data.triage}")

        #Triaaži alatüüp
        element1 = ehl.get_element(By.XPATH, '//*[@id="fe-label-m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f1.regularTriageViewWidget.form.complaints"]', "Triaaži alatüüp")
        element2 = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[3]/div/table/tbody/tr/td/span', "Triaaži alatüüp 2")
        data.triage_subtype = element1.text + " " + element2.text
        if data.triage_subtype == "Trauma: Trauma, mis nõuavad traumameeskonna kokkukutsumist":
            data.red_trauma = True
        else:
            data.red_trauma = False
        
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
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td/span/span[2]', "Vererõhk dex"):
            if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td/span/span[2]', "Vererõhk sin"):
                data.sys = None
                data.dia = None
            else: #Vasakul käel vererõhk
                bp = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td/span/span[2]', "Vererõhk").text
                sys,dia = bp.split(" / ")
                if sys:
                    data.sys = sys
                else:
                    data.sys = None
                if dia:
                    data.dia = dia
                else:
                    data.dia = None
        else: # Paremal käel vererõhk
            bp = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td/span/span[2]', "Vererõhk").text
            sys,dia = bp.split(" / ")
            if sys:
                data.sys = sys
                if not data.sys.isnumeric():
                    data.sys = None
            else:
                data.sys = None
            if dia:
                data.dia = dia
                if not data.dia.isnumeric():
                    data.dia = None
            else:
                data.dia = None

        # Temp
        if not ehl.element_exists(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[4]/td/span/span[2]', "Temp"):
            data.temp = None
        else:
            data.temp = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[4]/td/span/span[2]', "temp").text


        return data



    def scrape_varasemad_diagnoosid(self, prev_diag_data: PreviousDiagnosisData, index_date: date) -> PreviousDiagnosisData:
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
                'Eri-sõeluuring emakakaelakasvaja avastamiseks ' : "soel_emakakael",
                'Saatekirja vastus ' : "vastus_saatekiri",
                'Saatekiri e-konsultatsioonile ' : "e_kons_saatekiri",
                'Hambaravikaart ' : "hambaravikaart",
                'Kutse skriiningus osalemiseks ' : "skriining_kutse",
                'Saatekiri protseduurile/teenusele ' : "teenus_saatekiri",
                'Saatekiri analüüsile ' : "analyys_saatekiri",
                'Eriarstidevaheline konsultatsioon (arst-arst) ' : "erialade_vaheline_saatekiri"
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
                if title_text == "Koostamise aeg":
                    koostamise_date_str = i.get_text().split()[0]
#            if allikas not in digiloo_diag_tyybid:
#                raise UnknownDigiluguTypeError(f"Tüüpi {allikas} ei eksisteeri võimalike tüüpide nimekirjas")
            koostamise_date = date(int(koostamise_date_str[6:10]), int(koostamise_date_str[3:5]), int(koostamise_date_str[:2]))
            if allikas in digiloo_diag_tyybid:
                if digiloo_diag_tyybid[allikas] in kaasatud_tyybid and koostamise_date < index_date:
                    diagnosis_set.add(rhk)

        data.kok_astma = self.isDiagnosisKOKAstma(diagnosis_set)
        data.sydamepuudulikkus = self.isDiagnosisSydamepuudulikkus(diagnosis_set)
        self.driver.switch_to.default_content()
        return data

    def isDiagnosisKOKAstma(self, diagnoosid: set):
        kok_astma_set = {"J44", "J44.0", "J44.1", "J44.8", "J44.9", "J45", "J45.0", "J45.1", "J45.8", "J45.9", "J46"}
        if (diagnoosid & kok_astma_set):
            logging.info(f"Patsiendil on KOK/astma - diagnoosid {kok_astma_set.intersection(diagnoosid)}")
            return True
        else:
            logging.info("Patsiendil ei ole KOKi ega Astmat anamneesis")
            return False

    def isDiagnosisSydamepuudulikkus(self, diagnoosid: set):
        sydamepuudulikkus_set = {"I50", "I50.0", "I50.1", "I50.9", "I11.0", "I13.0", "I13.2", "I42", "I42.0", "I42.1", "I42.2", "I42.3", "I42.4", "I42.5", "I42.6",
                "I42.7", "I42.8", "I42.9"}
        if (diagnoosid & sydamepuudulikkus_set):
            logging.info(f"Patsiendil on sydamepuudulikkus - diagnoosid {sydamepuudulikkus_set.intersection(diagnoosid)}")
            return True
        else:
            logging.info("Patsiendil ei ole südamepuudulikkust anamneesis")
            return False



    def scrape_hj_diagnoosid(self, diagnoosid_data: DiagnosisData) -> DiagnosisData:
        data = diagnoosid_data
        pneumonia_rhk = {"J12", "J12.0", "J12.1", "J12.2", "J12.8", "J12.9", "J13", "J14", "J15", "J15.0", "J15.1", "J15.2", "J15.3", "J15.4", "J15.5",
                "J15.6", "J15.7", "J15.8", "J15.9", "J16", "J16.0", "J16.8", "J17", "J17.0", "J17.1", "J17.2", "J17.3", "J17.8", "J18", "J18.0",
                "J18.1", "J18.2", "J18.8", "J18.9", "J85.1", "J69.0", "J69.1", "J69.8"}
        pneumotooraks_rhk = {"J93", "J93.0", "J93.1", "J93.8", "J93.9", "J94.", "S27.0", "S27.2", "J94.2", "A15.0", "A16.0", "A16.2"}
        pleuraefusioon_rhk = {"J90", "J94.0", "J91", "J94.2", "J94.8", "S27.1", "S27.2"}
        perikard_rhk = {"I30", "I30.0", "I30.1", "I30.8", "I30.9", "I31.2", "I31.3", "I31.8", "S26.0", "I31.9", "I23.0"}
        mi_rhk = {"I21", "I21.0", "I21.1", "I21.2", "I21.3", "I21.4", "I21.9", "I22", "I22.0", "I22.1", "I22.8", "I22.9"}
        kate_rhk = {"I26", "I26.0", "I26.9"}
        kopsuturse_rhk = {"J81", "I50.1", "J68.1"}
        kok_astma_rhk = {"J44", "J44.0", "J44.1", "J44.8", "J44.9", "J45", "J45.0", "J45.1", "J45.8", "J45.9", "J46"}
        uhdisk_diagnoses = pneumonia_rhk.union(pneumotooraks_rhk, pleuraefusioon_rhk, perikard_rhk, mi_rhk, kate_rhk, kopsuturse_rhk, kok_astma_rhk)
        diagnoses = set()
        if not ehl.element_exists(By.XPATH, '//*[@id="m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f0.detailedEpicrisisModificationWidget._FINAL_DIAGNOSIS.list_listUpdate"]', "Diagnooside tabel"):
            ehl.navigeeri("Epikriis")
        tabel = ehl.get_element(By.XPATH, '//*[@id="m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f0.detailedEpicrisisModificationWidget._FINAL_DIAGNOSIS.list_listUpdate"]', "Diagnooside tabel").get_attribute('innerHTML')
        soup = BeautifulSoup(tabel, "html.parser")
        for row in soup.findAll("tr"):
            if len(row.get_text(strip=True)) != 0:
                element_line = row.findAll("td")
                if len(element_line) > 2:
                    diagnoses.add(element_line[2].get_text().strip())
        if diagnoses & uhdisk_diagnoses:
            data.uhdisk = True
        else:
            data.uhdisk = False
        data.diagnosis_list = diagnoses
        uhdisk_set = set()
        if diagnoses & pneumonia_rhk:
            uhdisk_set.add(uhdisk_diag.PNEUMONIA)
        if diagnoses & pneumotooraks_rhk:
            uhdisk_set.add(uhdisk_diag.PNEUMOTHORAX)
        if diagnoses & pleuraefusioon_rhk:
            uhdisk_set.add(uhdisk_diag.PLEURAL_EFFUSION)
        if diagnoses & perikard_rhk:
            uhdisk_set.add(uhdisk_diag.PERICARDIAL_EFFUSION)
        if diagnoses & mi_rhk:
            uhdisk_set.add(uhdisk_diag.MYOCARDIAL_INFARCTION)
        if diagnoses & kate_rhk:
            uhdisk_set.add(uhdisk_diag.PULMONARY_EMBOLISM)
        if diagnoses & kopsuturse_rhk:
            uhdisk_set.add(uhdisk_diag.PULMONARY_EDEMA)
        if diagnoses & kok_astma_rhk:
            uhdisk_set.add(uhdisk_diag.COPD_ASTHMA)
        data.uhdisk_list = uhdisk_set

        return data

    def scrape_hospitaliseerimise_info(self, hosp_data: HospitalisationData) -> HospitalisationData:
        data = hosp_data
        int_osakonnad = {'KAIN - kardiointensiivravi osakond',
                "AIEI - 1. intensiivravi",
                "AITI - 2. intensiivravi",
                "AIKI - 3. intensiivravi"}
        #ehl.navigeeri("Epikriis") #Eeldame, et oleme juba sel hetkel epikriisis
        element = ehl.get_element(By.XPATH, '//*[@id="application-main-content"]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td', "Väljakirjutamise staatus")
        staatus = element.text
        if staatus == "Surm":
            data.hospitalised_death = True
        else:
            data.hospitalised_death = False
        # Lähme haigusjuhu koondandmete lehele
        element = ehl.get_element(By.XPATH, '/html/body/div[1]/form/div[2]/div[2]/div/div/div/p[2]/a[3]', "HJ koondandmed", clickable=True)
        element.click()
        hosp_paevad = {}
        if not ehl.element_exists(By.XPATH, '//*[@id="m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f1.referrerInfoWidget.list_listUpdate"]', "Osakondade tabel"):
            logging.info("Patsienti ei hospitaliseeritud")
            return None #Patsient ei hospitaliseeritud
        tabel = ehl.get_element(By.XPATH, '//*[@id="m.f0.rootWidget.topC.f0.menuContainer.f1.menu.f1.referrerInfoWidget.list_listUpdate"]', "Osakondade tabel").get_attribute('innerHTML')
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

        return data
    
@dataclass
class Uuritav:
    rc : RedcapConnection
    rc_id : int
    record : Record = field(init=False)
    data : UuritavData = field(default_factory=UuritavData)
    scraper : Scraper = field(default_factory=Scraper)
    
    def __post_init__(self) -> None:
        self.record = Record(self.rc, self.rc_id)
        self.index_date = get_hj_date(self.record)

        print(self.rc_id)
        self.ehl_navigate()
        self.scrape_data()

    def scrape_data(self) -> None:
        self.data.diagnosis = self.scraper.scrape_hj_diagnoosid(self.data.diagnosis)
        self.data.hospitalisation = self.scraper.scrape_hospitaliseerimise_info(self.data.hospitalisation)
        self.data.ph = self.scraper.scrape_kiirabi_kaart(self.data.ph)
        self.data.emo = self.scraper.scrape_triaaz(self.data.emo)
        self.data.prev_diag = self.scraper.scrape_varasemad_diagnoosid(self.data.prev_diag, self.index_date)
        

    def __str__(self) -> None:
        return (str(self.record) + str(self.data))

    def ehl_navigate(self) -> None:
        ehl.navigeeri("haiguslugu", self.record.isikukood, self.record.hj_number)

    
def log_in() -> None:
    ehl.navigeeri("logi_sisse")

def setup_logger() -> None:
    logging.basicConfig(filename="ehl_log.txt", filemode='w', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    selenium_logger.disabled = True


def get_redcap_id_list(rc: RedcapConnection) -> Iterable[int]:
    result =  rc.get_id({"foreigner":["2"], "auto_status": ["", "1", "2"], "taustainfo_complete":["1"]})
    return result
    #return range(731,1001)
    #return [271]
    #return [2555]
    # return range(540,544)
    #return [250,272,290]
    #pass

def get_hj_date(record: Record) -> date:
    # Ekstaheerib haigusjuhu numbrist külastuse kuupäeva formaadis DD.MM.YYYY
    hj_number = record.hj_number
    hj_date = date(int(hj_number[:4]), int(hj_number[4:6]), int(hj_number[6:8]))
    return hj_date

def prepare_data(uuritav:Uuritav) -> dict:
    data = uuritav.data
    result = {}
    logging.info("Starting data assembly")
    # Punane trauma
    key = "auto_red_trauma___1"
    if data.emo.red_trauma:
        result[key] = "1"
    else:
        result[key] = "0"

    # Kiirabikaart
    key = "auto_ph"
    if data.ph:
        result[key] = "1"

        #Kvalitatiivne hingamissagedus
        if data.ph.resp_qual:
            key = "auto_ph_resp_qual"
            result[key] = data.ph.resp_qual.value
            key = "auto_ph_resp_qual_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_resp_qual_missing___1"
            result[key] = "1"
            key = "auto_ph_resp_qual"
            result[key] = ""

        #Kvantitatiivne hingamissagedus
        if data.ph.resp_quan:
            key = "auto_ph_resp_quan"
            result[key] = data.ph.resp_quan
            key = "auto_ph_resp_quan_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_resp_quan_missing___1"
            result[key] = "1"
            key = "auto_ph_resp_quan"
            result[key] = ""

        #SpO2
        if data.ph.spo2:
            key = "auto_ph_spo2"
            result[key] = data.ph.spo2
            key = "auto_ph_spo2_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_spo2_missing___1"
            result[key] = "1"
            key = "auto_ph_spo2"
            result[key] = ""

        # Süstoolne vererõhk
        if data.ph.sys:
            key = "auto_ph_sys"
            result[key] = data.ph.sys
            key = "auto_ph_sys_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_sys_missing___1"
            result[key] = "1"
            key = "auto_ph_sys"
            result[key] = ""

        # Diastoolne vererõhk
        if data.ph.dia:
            key = "auto_ph_dia"
            result[key] = data.ph.dia
            key = "auto_ph_dia_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_dia_missing___1"
            result[key] = "1"
            key = "auto_ph_dia"
            result[key] = ""

        # Pulsisagedus
        if data.ph.hr:
            key = "auto_ph_hr"
            result[key] = data.ph.hr
            key = "auto_ph_hr_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_hr_missing___1"
            result[key] = "1"
            key = "auto_ph_hr"
            result[key] = ""

        # Temperatuur
        if data.ph.temp:
            key = "auto_ph_temp"
            result[key] = data.ph.temp
            key = "auto_ph_temp_missing___1"
            result[key] = "0"
        else:
            key = "auto_ph_temp_missing___1"
            result[key] = "1"
            key = "auto_ph_temp"
            result[key] = ""
    else:
        result[key] = "2"

    # Triaažikategooria
    key = "auto_emo_triage"
    if data.emo.triage:
        result[key] = data.emo.triage.value
    else:
        result[key] = ""


    # Triaažitegija
    key = "auto_emo_triage_nurse"
    if data.emo.triage_nurse:
        result[key] = data.emo.triage_nurse
    else:
        result[key] = ""

    #Kvalitatiivne hingamissagedus
    if data.emo.resp_qual:
        key = "auto_emo_resp_qual"
        result[key] = data.emo.resp_qual.value
        key = "auto_emo_resp_qual_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_resp_qual_missing___1"
        result[key] = "1"
        key = "auto_emo_resp_qual"
        result[key] = ""

    #Kvantitatiivne hingamissagedus
    if data.emo.resp_quan:
        key = "auto_emo_resp_quan"
        result[key] = data.emo.resp_quan
        key = "auto_emo_resp_quan_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_resp_quan_missing___1"
        result[key] = "1"
        key = "auto_emo_resp_quan"
        result[key] = ""

    #SpO2
    if data.emo.spo2:
        key = "auto_emo_spo2"
        result[key] = data.emo.spo2
        key = "auto_emo_spo2_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_spo2_missing___1"
        result[key] = "1"
        key = "auto_emo_spo2"
        result[key] = ""

    # Süstoolne vererõhk
    if data.emo.sys:
        key = "auto_emo_sys"
        result[key] = data.emo.sys
        key = "auto_emo_sys_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_sys_missing___1"
        result[key] = "1"
        key = "auto_emo_sys"
        result[key] = ""

    # Diastoolne vererõhk
    if data.emo.dia:
        key = "auto_emo_dia"
        result[key] = data.emo.dia
        key = "auto_emo_dia_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_dia_missing___1"
        result[key] = "1"
        key = "auto_emo_dia"
        result[key] = ""

    # Pulsisagedus
    if data.emo.hr:
        key = "auto_emo_hr"
        result[key] = data.emo.hr
        key = "auto_emo_hr_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_hr_missing___1"
        result[key] = "1"
        key = "auto_emo_hr"
        result[key] = ""

    # Temperatuur
    if data.emo.temp:
        key = "auto_emo_temp"
        result[key] = data.emo.temp
        key = "auto_emo_temp_missing___1"
        result[key] = "0"
    else:
        key = "auto_emo_temp_missing___1"
        result[key] = "1"
        key = "auto_emo_temp"
        result[key] = ""

    # Anamneesis KOK ja astma
    if not data.prev_diag.kok_astma and not data.prev_diag.sydamepuudulikkus:
        key = "auto_earlier_diagnosis___3"
        result[key] = "1"

    else:
        if data.prev_diag.kok_astma:
            key = "auto_earlier_diagnosis___2"
            result[key] = "1"

        if data.prev_diag.sydamepuudulikkus:
            key = "auto_earlier_diagnosis___1"
            result[key] = "1"

    # Kõik diagnoosid
    if data.diagnosis.diagnosis_list:
        key = "auto_diag"
        result[key] = str(data.diagnosis.diagnosis_list)

    # UHDISK diagnoos
    if data.diagnosis.uhdisk:
        key = "auto_uhdisk_exist"
        result[key] = "1"
        for i in data.diagnosis.uhdisk_list:
            key = "auto_uhdisk_diag___" + str(i.value)
            result[key] = "1"
    else:
        key = "auto_uhdisk_exist"
        result[key] = "2"

    # Mitte-UHDISK diagnoos
    nud_kohuvalu = {"R10", "R10.0", "R10.1", "R10.2", "R10.3", "R10.4", "A09", "K56", "K56.0", "K56.1", "K56.2", "K56.3", "K56.4", "K56.5", "K56.6", "K56.7"}
    nud_seljavalu = {"M54", "M51.1", "M54.3", "M54.4", "M54.5", "M54.8", "M54.9"}
    nud_rindkerevalu = {"R07", "R07.1", "R07.2", "R07.3", "R07.4"}
    nud_peavalu = {"R51", "G43", "G43.0", "G43.1", "G43.2", "G43.3", "G43.8", "G43.9", "G44", "G44.0", "G44.1", "G44.2", "G44.3", "G44.4", "G44.8", "O29.4", "O74.5", "O89.4"}
    nud_uroinf = {"N39.0", "N30", "N30.0", "N30.1", "N30.2", "N30.8", "N30.9", "N10", "N11", "N11.0", "N11.1", "N11.8", "N11.9", "N12", "N20.9"}
    nud_kohuinf = {"K80.1", "K81", "K81.0", "K81.1", "K81.8", "K81.9", "K35", "K35.0", "K35.1", "K35.9", "K36", "K65", "K65.0", "K65.8", "K65.9", "K85", "K86.0", "K86.1"}
    nud_pehmeinf = {"L03", "L03.0", "L03.1", "L03.2", "L03.3", "L03.8"}
    nud_muuinf = set()
    nud_fa = {"I48"}
    nud_rytm = {"I49", "I49.8", "I49.9"}
    nud_ajuinf = {"I63", "I63.0", "I63.1", "I63.2", "I63.3", "I63.4", "I63.5", "I63.6", "I63.8", "I63.9", "G45", "G45.0", "G45.1", "G45.2", "G45.8", "G45.9", "I61", "I61.0", "I61.1", "I61.2", "I61.3", "I61.4", "I61.5", "I61.6", "I61.8", "I61.9"}
    nud_vertigo = {"R42", "H81.1"}
    nud_synkoop = {"R55", "G90.0", "T67.1"}
    nud_epilepsia = {"G40", "G40.0", "G40.1", "G40.2", "G40.3", "G40.4", "G40.5", "G40.6", "G40.7", "G40.8", "G40.9"}
    nud_bp = {"R03.0"}
    nud_alkohol = {"F10", "F10.0", "F10.00", "F10.01", "F10.02", "F10.03", "F10.04", "F10.05", "F10.06", "F10.07", "F10.1", "F10.2", "F10.20", "F10.21", "F10.22", "F10.23", "F10.24", "F10.25", "F10.26", "F10.3", "F10.30", "F10.31", "F10.4", "F10.40", "F10.41", "F10.5", "F10.50", "F10.51", "F10.52", "F10.53", "F10.54", "F10.55", "F10.56", "F10.6", "F10.7", "F10.70", "F10.71", "F10.72", "F10.73", "F10.74", "F10.75", "F10.8", "F10.9", "Z72.1"}
    nud_yhtinf = {"J00", "J01", "J01.0", "J01.1", "J01.2", "J01.3", "J01.4", "J01.8", "J01.9", "J02", "J02.0", "J02.8", "J02.9", "J03", "J03.0", "J03.8", "J03.9", "J04", "J04.0", "J04.1", "J04.2", "J05", "J05.0", "J05.1", "J06", "J06.0", "J06.8", "J06.9"}
    nud_allergia = {"D69.0", "D72.1", "H01.1", "H65.1", "H65.4", "H65.9", "J30", "J30.1", "J30.2", "J30.3", "J30.4", "J45.0", "J67.7", "J67.8", "J67.9", "L20.8", "L23", "L23.0", "L23.1", "L23.2", "L23.3", "L23.4", "L23.5", "L23.6", "L23.7", "L23.8", "L23.9", "L50.0", "L56.1", "M13.8", "M30.1", "T78.2", "T78.4", "T88.7"}
    nud_oksendamine = {"R11", "F50.5", "P92.0", "K91.0", "O21", "O21.0", "O21.1", "O21.2", "O21.8", "O21.9"}
    nud_muu = set()
    nud_giveri = {"K92.0", "K92.1", "K92.2"}
    nud_kusekivi = {"N20", "N20.0", "N20.1", "N20.2", "N20.9", "N21", "N21.0", "N21.1", "N21.8", "N21.9", "N22", "N22.0", "N22.8", "N23"}
    nud_gyn = {"O20", "O20.0", "O20.8", "O20.9"}
    nud_protseduur = {"R33"}
    nud = (nud_kohuvalu, nud_seljavalu, nud_rindkerevalu, nud_peavalu, nud_uroinf, nud_kohuinf, nud_pehmeinf, nud_muuinf, nud_fa, nud_rytm, nud_ajuinf, nud_vertigo, nud_synkoop, nud_epilepsia, nud_bp, nud_alkohol, nud_yhtinf, nud_allergia, nud_oksendamine, nud_muu, nud_giveri, nud_kusekivi, nud_gyn, nud_protseduur)
    for index, diagnosis in enumerate(nud, start=1):
        key = "auto_non_uhdisk_diag___" + str(index)
        if diagnosis & data.diagnosis.diagnosis_list:
            result[key] = "1"
        else:
            result[key] = "0"

    # Covid 19
    covid_diag = {"U07.1", "U07.2"}
    key = "auto_diag_covid"
    if covid_diag & data.diagnosis.diagnosis_list:
        result[key] = "1"
    else:
        result[key] = "2"


    # Hospitaliseerimine
    if data.hospitalisation:
        key = "auto_hospitalised"
        result[key] = "1"
        # Hospitaliseerimise kestus
        key = "auto_hospitalised_duration"
        result[key] = data.hospitalisation.hospitalised_duration

        # Intensiivravi vajadus
        if data.hospitalisation.icu:
            key = "auto_icu"
            result[key] = "1"
            key = "auto_icu_duration"
            result[key] = data.hospitalisation.icu_duration
        else:
            key = "auto_icu"
            result[key] = "2"
            key = "auto_icu_duration"
            result[key] = ""

        # Surm haiglas
        key = "auto_hospitalised_death"
        if data.hospitalisation.hospitalised_death:
            result[key] = "1"
        else:
            result[key] = "2"
    else:
        key = "auto_hospitalised"
        result[key] = "2"
        key = "auto_hospitalised_duration"
        result[key] = ""
        key = "auto_icu"
        result[key] = "2"
        key = "auto_icu_duration"
        result[key] = ""


    key = "automaatkontroll_complete"
    result[key] = "1"
    return result




def upload_data(rc: RedcapConnection, uuritav: Uuritav) -> None:
    rc_id = uuritav.rc_id
    logging.info("Preparing data")
    result = prepare_data(uuritav)
    result["record_id"] = rc_id
    logging.info("Starting upload")
    rc.upload({"record_id" : rc_id, "auto_status" : 2}, overwrite=True)
    rc.upload(result, confirm=False)
    rc.upload({"record_id" : rc_id, "auto_status" : 3, "automaatkontroll_complete" : "1"}, overwrite=True)
    logging.info("Upload complete")
    



def main():
    try:
        setup_logger()
        global ehl
        ehl = ehlMain()
        ehl.ava()
        #login_window("eHL Scraper")
        rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="../redcap_api_key")
        log_in()
        while True:
            try:
                redcap_id_list = get_redcap_id_list(rc)
                for rc_id in redcap_id_list:
                    uuritav = Uuritav(rc, rc_id)
                    upload_data(rc, uuritav)
            except TimeoutException:
                continue
    except Exception as e:
        logging.exception(e)
        raise


if __name__ == "__main__":
    main()

