#import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import pandas as pd
import datetime
import csv
from redcap import Project, RedcapError
import platform

HIGHLIGHTS_FILE = "./highlights"


class ehlMain:
    script_load_delay=5
    page_load_delay=20
    PATH=""

    def __init__(self):
        self.pt_isikukood = ""
        self.pt_hjnumber = ""
        self.record_id = ""
        self.PATH = self.get_chromedriver_path() #"./chromedriver"
        self.driver = None
        self.kiirabikaart_tekst=""
        self.emo_andmed=""
        self.diagnoosid_tekst=""
        self.kiirabikaart_olemas=False
        self.saabus_kiirabiga=False

        self.kiirabi = [""]*23
        for i in range(1,8):
            self.kiirabi[i]="0"
        self.kiirabikaart_puudu=""

        self.kiirabi_anamnees=""
        self.emo = [""]*22
        #Muudame 0 - 6 elemendid "0"deks
        for i in range(7):
            self.emo[i]="0"
        self.emo_kaebused=""
        self.emo_triaaz_varv="6"

        self.diagnoosid = [""]*52
        for i in range(4,12):
            self.diagnoosid[i]="0"
        for i in range(15,36):
            self.diagnoosid[i] = "0"

        self.juhtiv_diagnoos = []
        self.hospitaliseerimine = []
        self.uhdisk_olemas=""

        self.elements_to_highlight = self.load_highlights()

        pt_andmed_header = ['record_id']
        kiirabi_header = ['ph', 'ph_complaints___1', 'ph_complaints___2', 'ph_complaints___3', 'ph_complaints___4',
                          'ph_complaints___5', 'ph_complaints___6', 'ph_complaints___7', 'ph_resp_qual_missing___1',
                          'ph_resp_qual', 'ph_resp_quan_missing___1', 'ph_resp_quan', 'ph_spo2_missing___1', 'ph_spo2',
                          'ph_sys_missing___1', 'ph_sys', 'ph_dia_missing___1', 'ph_dia', 'ph_hr_missing___1', 'ph_hr',
                          'ph_temp_missing___1', 'ph_temp', 'kiirabi_complete']
        emo_header = ['emo_triage', 'emo_complaints___1', 'emo_complaints___2', 'emo_complaints___3',
                      'emo_complaints___4',
                      'emo_complaints___5', 'emo_complaints___6', 'emo_complaints___7', 'emo_resp_qual_missing___1',
                      'emo_resp_qual', 'emo_resp_quan_missing___1', 'emo_resp_quan', 'emo_spo2_missing___1', 'emo_spo2',
                      'emo_sys_missing___1', 'emo_sys', 'emo_dia_missing___1', 'emo_dia', 'emo_hr_missing___1',
                      'emo_hr',
                      'emo_temp_missing___1', 'emo_temp', 'emo_complete']
        diagnoosid_header = ['earlier_diagnosis___1', 'earlier_diagnosis___2', 'earlier_diagnosis___3', 'uhdisk_exist',
                             'uhdisk_diag___1', 'uhdisk_diag___2', 'uhdisk_diag___3', 'uhdisk_diag___4',
                             'uhdisk_diag___5',
                             'uhdisk_diag___6', 'uhdisk_diag___7', 'uhdisk_diag___8', 'diag_pleural_qual',
                             'diag_pleural_quan_exist___1', 'diag_pleural_quan', 'non_uhdisk_diag___1',
                             'non_uhdisk_diag___2',
                             'non_uhdisk_diag___3', 'non_uhdisk_diag___4', 'non_uhdisk_diag___5', 'non_uhdisk_diag___6',
                             'non_uhdisk_diag___21', 'non_uhdisk_diag___7', 'non_uhdisk_diag___17',
                             'non_uhdisk_diag___8',
                             'non_uhdisk_diag___9', 'non_uhdisk_diag___10', 'non_uhdisk_diag___11',
                             'non_uhdisk_diag___12',
                             'non_uhdisk_diag___13', 'non_uhdisk_diag___14', 'non_uhdisk_diag___15',
                             'non_uhdisk_diag___16',
                             'non_uhdisk_diag___18', 'non_uhdisk_diag___19', 'non_uhdisk_diag___20',
                             'uhdisk_diag_lateral_pna',
                             'uhdisk_diag_lateral_kate', 'uhdisk_diag_lateral_eff', 'uhdisk_diag_lateral_ptx',
                             'diag_covid',
                             'diag_tamponade', 'hospitalised', 'discharge_date', 'hospitalised_duration', 'icu',
                             'icu_start',
                             'icu_end', 'icu_duration', 'hospitalised_death', 'hospitalised_secondary',
                             'diagnoosid_complete']

        self.column_names = pt_andmed_header + kiirabi_header + emo_header + diagnoosid_header + ["taustainfo_complete"]
        """
        today=datetime.date.today()
        now = datetime.datetime.now()
        current_time = now.strftime("%H%M%S")
        self.faili_nimi='[Kogutud andmed]_UH_uuring_'+str(today.year)+str(today.month)+str(today.day)+"_"+str(current_time)+'.csv'

        file=open(self.faili_nimi,"w", newline="", encoding='UTF8')
        writer = csv.writer(file)
        writer.writerow(self.column_names)
        file.close()
        """

    def get_chromedriver_path(self):
        opsys = platform.system()
        if opsys == "Linux":
            print("OS Linux")
            return "./chromedriver/chromedriver_linux"
        elif opsys == "Windows":
            print("OS Windows")
            return "./chromedriver/chromedriver_windows.exe"
        elif opsys == "Darwin":
            print("OS Mac")
            return "./chromedriver/chromedriver_mac"
        else:
            print("Operating system not supported")
        

    
    def load_highlights(self):
        highlight_list = []
        try:
            with open(HIGHLIGHTS_FILE, mode="r") as file:
                highlight_list = file.read().splitlines()
            return highlight_list
        except IOError:
            print(f"Fail {HIGHLIGHTS_FILE} ei eksisteeri.")

    def get_element(self, by, expression, name, clickable=False):
        """ See funktsioon abstrahheerib seleniumis elemendi leidmise ning võtab arvesse laadimisaega ja blokeerivaid elemente"""
        #print(f"get_element: Otsin elementi {name}")
        try:
            if clickable == False:
                element_present = EC.presence_of_element_located((by, expression))
                element = WebDriverWait(self.driver, self.page_load_delay).until(element_present)
            elif clickable == True:
                element_clickable = EC.element_to_be_clickable((by, expression))
                if element_clickable:
                    print(f"Element is clickable")
                element = WebDriverWait(self.driver, self.page_load_delay).until(element_clickable)
            return element
        except TimeoutException:
            print(f"Timeout: Elementi {name} ei jõutud ära oodata")
            raise
        #except Exception as e:
        #    print(f"Unhandled exception - {e}")

    def navigeeri(self, element):
        counter = 0
        timeout = 3
        while counter < 5:
            try:
                print(f"Funktsion NAVIGEERI parameetriga {element}")
                if element == "kiirabi":
                    self.ava_kiirabi_kaart()                    
                elif element == "paevik":
                    self.ava_paeviku_algus()
                elif element == "triaaz":
                    self.ava_emo_triaaz()
                elif element == "diagnoosid":
                    self.ava_diagnoosid()
                elif element == "digilugu_diagnoosid":
                    self.ava_diagnoosid_digilugu()
                else:
                    self.ava_menyy_alajaotis(element)
            except ElementNotInteractableException:
                print("ERROR: ElementNotInteractableException")
                sleep(timeout)
                continue
            except ElementClickInterceptedException:
                print("ERROR: ElementClickInterceptedException")
                sleep(timeout)
                continue
            else: # Erroreid ei esinenud, lõpetame navigeerimise
                return
            finally:
                counter += 1
            
                
        
    
    def ava(self):
        self.driver = webdriver.Chrome(self.PATH)
        self.driver.get("https://ehl.kliinikum.ee")

    def sulge(self):
        self.driver.quit()

    def highlight_elements(self):
        pass
##        for word_to_highlight in self.elements_to_highlight:
##            #Siin peame otsima nii suure kui väikese tähega => tuleb muuta universaalseks => selleks kasutan translate() funktsiooni
##            elements = self.driver.find_elements(By.XPATH, "//td[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'" + word_to_highlight + "')]")
##
##            for i in range(len(elements)):
##                element_inner=elements[i].get_attribute("innerHTML")
##                element_inner=element_inner.lower()
##                #print(element_inner)
##                asendatavad_symbolid = ["'", ":", ";", "=", "\n"]
##                for symbol in asendatavad_symbolid:
##                    element_inner = element_inner.replace(symbol, "")
##                new_text=element_inner.replace(word_to_highlight,"<span style=\"background-color: #FFFF00\">"+word_to_highlight+"</span>")
##                #new_text="EMO triaazis-> RR: 156/74mmHg, fr: 72x', SpO2: 97%, T:36,6C"
##                #print(new_text)
##                #new_text="AAA"
##                #print("arguments[0].innerText = "+new_text)
##                self.driver.execute_script("arguments[0].innerHTML = \'"+new_text+"\'", elements[i])

    #mitte registrid
    def haiguslugude_otsimine_EMO_konto(self, hj_number):

        #Kui eelmine haiguslugu lahti, siis sulge
        if self.driver.find_elements(By.ID,"patientBarExitLink"):
            self.driver.find_element(By.ID,"patientBarExitLink").click()

        #Muudame arvelduse menüü nähtavaks
        self.driver.find_element(By.ID, "nav02").find_element(By.LINK_TEXT, "Arveldus").click()
        try:
            element_present = EC.presence_of_element_located((By.LINK_TEXT, "Haiguslugude otsimine"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            #Script ei laadinud piisavalt kiirelt, funktsioon lõpetab
            return 0

        #Valime menüüst "haiguslugude otsimine"
        self.driver.find_element(By.ID, "submenu02").find_element(By.CLASS_NAME, "submenu").find_element(By.CLASS_NAME,"aranea-link-button").click()

        #Sisestame haigusjuhu numbri, mida soovime otsida
        self.driver.find_element(By.ID,"m.f0.rootWidget.topC.f0.menuContainer.f0.menu.f0.form.searchForm.sicknessCaseNumber").send_keys(hj_number)

        # Vajutame otsi nuppu
        self.driver.find_element(By.XPATH, "//input[@value='Otsi']").click()

        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'" + hj_number + "')]"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            #Ei leidnud soovitud HJ, funktsioon tagastab 0
            return 0

        #Haigusjuht on nüüd olemas, avame selle
        self.driver.find_element(By.XPATH, "//a[@arn-evntid='openTreatmentService']").click()
        self.andmete_vaatamise_pohjendus()
        #Funktsioon avas edukalt HJ
        return 1

    #registritest:
    def haiguslugude_otsimine(self, isikukood, hj_number):
        # Nulli kõik väärtused:
        self.kiirabikaart_tekst = ""
        self.emo_andmed = ""
        self.diagnoosid_tekst = ""
        self.kiirabikaart_olemas = False
        self.saabus_kiirabiga = False
        self.kiirabi = [""] * 23
        for i in range(1, 8):
            self.kiirabi[i] = "0"
        self.kiirabi_anamnees = ""
        self.emo = [""] * 22
        # Muudame 0 - 6 elemendid "0"deks
        for i in range(7):
            self.emo[i] = "0"
        self.emo_kaebused = ""
        self.emo_triaaz_varv = "6"
        self.diagnoosid = [""] * 52
        for i in range(4, 12):
            self.diagnoosid[i] = "0"
        for i in range(15, 36):
            self.diagnoosid[i] = "0"
        self.juhtiv_diagnoos = []
        self.hospitaliseerimine = []
        self.uhdisk_olemas = ""

        #Kui eelmine haiguslugu lahti, siis sulge
        if self.driver.find_elements(By.ID,"patientBarExitLink"):
            #Ava registrid:
            self.driver.find_element(By.XPATH,"//a[@title='Konto valik']").click()
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Registrid')]"))
                WebDriverWait(self.driver, self.script_load_delay).until(element_present)
            except TimeoutException:
                return
            sleep(1)
            self.driver.find_element(By.XPATH, "//a[contains(text(),'Registrid')]").click()
            #Oota, kuni laeb ära:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//div[@id='nav']"))
                WebDriverWait(self.driver, self.page_load_delay).until(element_present)
            except TimeoutException:
                return

        #Muudame arvelduse menüü nähtavaks
        self.driver.find_element(By.XPATH, "//div[@id='nav']").find_element(By.ID, "nav01").find_element(By.TAG_NAME,"a").click()
        try:
            element_present = EC.presence_of_element_located((By.LINK_TEXT, "Patsiendid"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            #Script ei laadinud piisavalt kiirelt, funktsioon lõpetab
            return

        #Valime menüüst "haiguslugude otsimine"
        self.driver.find_element(By.LINK_TEXT, "Patsiendid").click()

        #Ootame kuni laeb ja sisestame haigusjuhu numbri, mida soovime otsida
        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//input[@value='Otsi']"))
            WebDriverWait(self.driver, self.page_load_delay).until(element_present)
        except TimeoutException:
            return
        self.driver.find_element(By.ID,"m.f0.rootWidget.topC.f0.menuContainer.f0.menu.f0.f0.filterWidget.form.legalCode").send_keys(isikukood)

        # Vajutame otsi nuppu
        self.driver.find_element(By.XPATH, "//input[@value='Otsi']").click()
        sleep(0.5)

        #Laeme ära ja vaatame, kas pt on juba andmebaasis
        #if not self.driver.find_elements(By.XPATH, "//*[contains(text(),'Otsinguparameetritele vastavat kirjet ei leitud!')]")


        #Ootame kuni laeb ja kontrollime, kas pt on registris:
        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//input[@value='Lisa isikuid valimisse']"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            #Ei leidnud soovitud HJ, funktsioon tagastab 0
            return

        if not self.driver.find_elements(By.XPATH, "//a[@arn-evntid='showTreatmentHistory']"):
            #Lisame patsiendi registrisse
            self.lisa_isik_registrisse()

        self.driver.find_element(By.XPATH,"//a[@arn-evntid='showTreatmentHistory']").click()


        #Ootame kuni laeb ja siis avame kõik haigusjuhud:
        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//a[@arn-evntid='showAll']"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            return
        self.driver.find_element(By.XPATH, "//a[@arn-evntid='showAll']").click()
        sleep(1)

        #Kui lugu olemas, siis scrolli ja ava see
        if not self.driver.find_elements(By.LINK_TEXT, str(hj_number)):
            return

        #lugu = self.driver.find_element(By.XPATH, "//a[contains(text(),'"+str(hj_number)+"')]")
        lugu = self.driver.find_element(By.LINK_TEXT, str(hj_number))
        actions = ActionChains(self.driver)
        # Scrollime lehel otsitava elemendini
        actions.move_to_element(lugu).click().perform()
        self.andmete_vaatamise_pohjendus()

        return

    def lisa_isik_registrisse(self):
        self.driver.find_element(By.XPATH, "//input[@value='Lisa isikuid valimisse']").click()
        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//button[@arn-evntid='complete']"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            return
        self.driver.find_element(By.XPATH, "//button[@arn-evntid='complete']").click()
        return

    def andmete_vaatamise_pohjendus(self):
        try:  # ootame kuni javascript menüü ilmub nähtavale
            element_present = EC.presence_of_element_located((By.ID, "o.f0.form.accessReason-SCIENTIFIC_RESEARCH"))
            WebDriverWait(self.driver, self.script_load_delay).until(element_present)
        except TimeoutException:
            return 0 #Põhjust ei olnud vaja sisestada

        if self.driver.find_elements(By.ID, "o.f0.form.accessReason-SCIENTIFIC_RESEARCH"):
            self.driver.find_element(By.ID, "o.f0.form.accessReason-SCIENTIFIC_RESEARCH").click()
            self.driver.find_element(By.XPATH, "//input[@value='Jätka']").click()

        #Andmete vaatamise põhjendus oli vajalik funktsioon tagastab 1
        return 1

    def ava_menyy_alajaotis(self, valik):
        #try:  # ootame kuni javascript menüü ilmub nähtavale
        #    element_present = EC.presence_of_element_located((By.CLASS_NAME, "arrow"))
        #    WebDriverWait(self.driver, self.page_load_delay).until(element_present)
        #except TimeoutException:
        #    return 0 #Põhjust ei olnud vaja sisestada
        #menu = self.driver.find_element(By.CLASS_NAME,"arrow")
        menu = self.get_element(By.CLASS_NAME, "arrow", "Rippmenüü nool")


        #hidden = self.driver.find_element(By.XPATH,"//a[contains(text(),'"+valik+"')]")
        hidden = self.get_element(By.XPATH, "//a[contains(text(),'"+valik+"')]", "Menüülement " + valik)

        actions = ActionChains(self.driver)
        actions.move_to_element(menu)
        actions.pause(1)
        actions.click(hidden)
        actions.perform()
        return 1
            
        #except Exception as e:
        #    print(f"Rippmenüü navigeerimisel tekkis probleem: {e}")

    def ava_kiirabi_kaart(self):
        self.ava_menyy_alajaotis("Päevik")
        self.driver.find_element(By.XPATH, "//a[@arn-evntpar='ALL_DAYS']").click()
        self.driver.find_element(By.XPATH, "//a[@arn-evntid='showAll']").click()
        sleep(1)

        #Kas kiirabi kaart on olemas
        if not self.driver.find_elements(By.XPATH, "//td[contains(text(),'Kiirabikaart nr.')]"):
            self.kiirabikaart_tekst=""
            self.tootle_kiirabikaart()
            return

        kiirabikaart = self.driver.find_element(By.XPATH, "//td[contains(text(),'Kiirabikaart nr.')]").find_element(By.TAG_NAME, "a")
        actions = ActionChains(self.driver)
        #Scrollime lehel otsitava elemendini
        actions.move_to_element(kiirabikaart).click().perform()
        sleep(2.5)
        #self.driver.find_element(By.XPATH, "//a[@arn-evntpar='journalEntryDate']").click()
        #actions.move_to_element(self.driver.find_element(By.XPATH, "//td[contains(text(),'Teostatud protseduurid')]")).perform()

        #Kõik avatud aknad:
        handles = self.driver.window_handles
        size = len(handles)

        #Salvestan põhiakna
        parent_handle = self.driver.current_window_handle
        self.kiirabikaart_tekst = ""
        for i in range(size):
            if handles[i] != parent_handle:
                self.driver.switch_to.window(handles[i])
                self.kiirabikaart_tekst = self.driver.find_element(By.ID,"mainTable").text
                #Sulgen kõrval akna
                # self.driver.close()  # Ei sulge esialgu kiirabikaardi akent, et uurijad saaksid manuaalselt tutvuda
                break
        #Taastan algse akna
        self.driver.switch_to.window(parent_handle)  # Ei vaheta fookust ka esialgu, kuni manuaalse täitmisega piirdume
        self.tootle_kiirabikaart()
        self.kiirabikaart_olemas=True
        self.saabus_kiirabiga=True
        return

    def tootle_kiirabikaart(self):
        toorandmed=self.kiirabikaart_tekst.splitlines()
        if not toorandmed:
            self.kiirabi[0]="2"
            #Väljasta andmed
            #Välju programmist
            return
        #print(toorandmed)
        for i in toorandmed:
            #Kvalitatiivne hingamissagedus
            if "Hingamissageduse tase" in i and self.kiirabi[9]=="" and len(i.split(" ")) == 3:
                self.kiirabi[9]=i.split(" ")[2]
                if self.kiirabi[9] == "hüperventilatsioon":
                    self.kiirabi[9]="4"
                if self.kiirabi[9] == "hüpoventilatsioon":
                    self.kiirabi[9]="2"
                if self.kiirabi[9] == "normoventilatsioon":
                    self.kiirabi[9]="3"
                self.kiirabi[8] = "0"
            elif self.kiirabi[8] == "":
                self.kiirabi[8]="1"

            #Kvantitatiivne hingamissagedus
            if "Hingamissagedus" in i and "korda/min" in i and self.kiirabi[11]=="" and len(i.split(" ")) == 3:
                self.kiirabi[11]=i.split(" ")[1]
                self.kiirabi[10] = "0"
            elif self.kiirabi[10] == "":
                self.kiirabi[10]="1"

            #SpO2
            if "SpO2" in i and self.kiirabi[13]=="" and len(i.split(" ")) == 3:
                self.kiirabi[13]=i.split(" ")[1]
                self.kiirabi[12] = "0"
            elif self.kiirabi[12] == "":
                self.kiirabi[12]="1"

            #Süstoolne vererõhk
            if "süstoolne" in i and self.kiirabi[15]=="" and len(i.split(" ")) == 4:
                self.kiirabi[15]=i.split(" ")[2]
                self.kiirabi[14] = "0"
            elif self.kiirabi[14] == "":
                self.kiirabi[14]="1"

            #Diastoolne vererõhk
            if "diastoolne" in i and self.kiirabi[17]=="" and len(i.split(" ")) == 4:
                self.kiirabi[17]=i.split(" ")[2]
                self.kiirabi[16] = "0"
            elif self.kiirabi[16] == "":
                self.kiirabi[16]="1"

            #Südame löögisagedus
            if "Pulsisagedus" in i and self.kiirabi[19]=="" and len(i.split(" ")) == 3:
                self.kiirabi[19]=i.split(" ")[1]
                self.kiirabi[18] = "0"
            elif self.kiirabi[18] == "":
                self.kiirabi[18]="1"

            #Temperatuur
            if "Temperatuur" in i and self.kiirabi[21]=="" and len(i.split(" ")) == 4:
                self.kiirabi[21]=i.split(" ")[2]
                self.kiirabi[20] = "0"
            elif self.kiirabi[20] == "":
                self.kiirabi[20]="1"

        anamneesi_algus=0
        #Lisame ka anamneesi (ÄRA SEDA REDCAPi SAADA)
        for i in range(len(toorandmed)):
            if toorandmed[i].find("Anamnees")!=-1:
                anamneesi_algus=i
                break
        #Ei toimi, mingid tühikud rikuvad ära
        #anamneesi_algus = toorandmed.index("Anamnees")
        anamneesi_lopp = toorandmed.index("Patsiendi objektiivne staatus")
        self.kiirabi_anamnees = " ".join(toorandmed[anamneesi_algus:anamneesi_lopp])

        return

    def ava_emo_triaaz(self):
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, "arrow"))
            WebDriverWait(self.driver, self.page_load_delay).until(element_present)
        except TimeoutException:
            return #Põhjust ei olnud vaja sisestada

        #muuda kõik markide kohta
        if self.driver.find_elements(By.XPATH, "//a[@class='ico-tip mark one']"):
            self.emo_triaaz_varv = "1"
            self.driver.find_element(By.XPATH, "//a[@class='ico-tip mark one']").click()
        elif self.driver.find_elements(By.XPATH, "//a[@class='ico-tip mark two']"):
            self.emo_triaaz_varv = "2"
            self.driver.find_element(By.XPATH, "//a[@class='ico-tip mark two']").click()
        elif self.driver.find_elements(By.XPATH, "//a[@class='ico-tip mark three']"):
            self.emo_triaaz_varv = "3"
            self.driver.find_element(By.XPATH, "//a[@class='ico-tip mark three']").click()
        elif self.driver.find_elements(By.XPATH, "//a[@class='ico-tip mark four']"):
            self.emo_triaaz_varv = "4"
            self.driver.find_element(By.XPATH, "//a[@class='ico-tip mark four']").click()
        elif self.driver.find_elements(By.XPATH, "//a[@class='ico-tip mark five']"):
            self.emo_triaaz_varv = "5"
            self.driver.find_element(By.XPATH, "//a[@class='ico-tip mark five']").click()
        else:
            return
        #self.driver.find_element(By.XPATH, "//a[@class='ico-tip mark three']").click()
        self.emo_andmed=""

        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//div[@id='main']"))
            WebDriverWait(self.driver, self.page_load_delay).until(element_present)
        except TimeoutException:
            return 0

        self.emo_andmed=self.driver.find_elements(By.XPATH, "//table[@class='form']")[2].text
        self.emo_andmed+="\n"+self.driver.find_elements(By.XPATH, "//table[@class='form']")[3].text
        self.emo_kaebused=self.driver.find_elements(By.XPATH,"//div[@class='form-cols clear']")[2].text

        """
        triaazi_varv=self.driver.find_element(By.XPATH,"//span[@class='status adjustable status-warning']").text

        if "punane" in triaazi_varv:
            self.emo_triaaz_varv="1"
        if "oranž" in triaazi_varv:
            self.emo_triaaz_varv="2"
        if "kollane" in triaazi_varv:
            self.emo_triaaz_varv="3"
        if "roheline" in triaazi_varv:
            self.emo_triaaz_varv="4"
        if "sinine" in triaazi_varv:
            self.emo_triaaz_varv="5"
        """
        #print("Emo triaazi värv ja kaebused:")
        #print(self.emo_triaaz_varv)
        #print(self.emo_kaebused)

        self.tootle_emo()

    def tootle_emo(self):
        toorandmed=self.emo_andmed.splitlines()
        if not toorandmed:
            return
        for i in toorandmed:
            # Kvalitatiivne hingamissagedus (kui näed triaaži kaardil, siis täida ära)
            """
            if "" in i and self.emo[8] == "" and len(i.split(" ")) == 3:
                self.emo[8] = i.split(" ")[2]
                self.emo[7] = "0"
            else:
                self.emo[7] = "1"
            """
            i = " ".join(i.split())
            # Hingamissagedus
            if "Hingamissagedus" in i and self.emo[10] == "" and len(i.split(" ")) == 3:
                self.emo[10] = i.split(" ")[1]
                self.emo[9] = "0"
            elif self.emo[9] == "":
                self.emo[9] = "1"

            # SpO2
            if "SpO2" in i and self.emo[12] == "" and len(i.split(" ")) == 3:
                self.emo[12] = i.split(" ")[1]
                self.emo[11] = "0"
            elif self.emo[11] == "":
                self.emo[11] = "1"

            # Vererõhk:
            if (("Parem käsi" in i and "- / -" not in i) or ("Vasak käsi" in i and "- / -" not in i)) and \
                            self.emo[14] == "" and self.emo[16] == "" and len(i.split(" ")) == 6:
                # Süstoolne:
                self.emo[14] = i.split(" ")[2]
                # Diastoolne
                self.emo[16] = i.split(" ")[4]

                self.emo[13] = "0"
                self.emo[15] = "0"
            elif self.emo[15] == "":
                self.emo[13] = "1"
                self.emo[15] = "1"

            # Pulss:
            if "Pulss" in i and self.emo[18] == "" and len(i.split(" ")) == 3:
                self.emo[18] = i.split(" ")[1]
                self.emo[17] = "0"
            elif self.emo[17] == "":
                self.emo[17] = "1"

            # Kehatemperatuur:
            if "Kehatemperatuur" in i and self.emo[20] == "" and len(i.split(" ")) == 3:
                self.emo[20] = i.split(" ")[1]
                self.emo[19] = "0"
            elif self.emo[19]=="":
                self.emo[19] = "1"

        #Kui tahame, et indeksid tabeliga kattuks, tuleks ühe võrra vasakule liigutada

        return

    def ava_diagnoosid(self):
        try:  # ootame kuni javascript menüü ilmub nähtavale
            element_present = EC.presence_of_element_located((By.CLASS_NAME, "arrow"))
            WebDriverWait(self.driver, self.page_load_delay).until(element_present)
        except TimeoutException:
            return 0 #Põhjust ei olnud vaja sisestada
        self.ava_menyy_alajaotis("Meditsiinilised andmed")
        element=self.driver.find_element(By.XPATH, "//div[@class='inside']").find_element(By.XPATH, "//div[@class='head clear expander_head']")
        element.find_element(By.TAG_NAME, "a").click()
        sleep(1)
        self.diagnoosid_tekst=self.driver.find_element(By.CLASS_NAME,"inside").find_element(By.CLASS_NAME,"data").text
        self.tootle_diagnoosid()
        return

    def ava_diagnoosid_digilugu(self):
        startdate = "01.01.1990"
        self.ava_menyy_alajaotis("Digiloo päringud")
        try:
            # Esmalt avame õige iframe'i
            element = WebDriverWait(self.driver, self.page_load_delay).until(EC.presence_of_element_located((By.ID, "angularIframe")))
            self.driver.switch_to.frame(element)
            # Siis otsime diagnooside radio inputi
            element = WebDriverWait(self.driver, self.page_load_delay).until(EC.presence_of_element_located((By.NAME, "51")))
            element.click()
            # Suus valime filtri alguskuupäeva inputi ja täidame selle
            element = self.driver.find_element(By.XPATH, "/html/body/ui-view/div[2]/div[2]/hc-navbar-filter/div/div/div[3]/div/span/form/div[1]/div[4]/div/hc-date-picker[1]/div/input")
            element.clear()
            element.send_keys(Keys.HOME)
            element.send_keys(startdate)
            element.send_keys(Keys.ENTER)
            # Ja lõpuks vajutame otsimisnuppu
            element = self.driver.find_element(By.XPATH, "/html/body/ui-view/div[2]/div[2]/hc-navbar-filter/div/div/div[3]/div/span/form/div[2]/div/button")
            element.click()
        except TimeoutException:
            return 0
        finally:
            self.driver.switch_to.default_content()

    def tootle_diagnoosid(self):
        toorandmed = self.diagnoosid_tekst.lower()
        #print(toorandmed)
        sydamepuudulikkus = ["südamepuudulikkus", "i50"]
        kok_astma = ["krooniline obstruktiivne kopsuhaigus", "astma", "j45", "j44"]

        #lisa kuupäeva kontroll (peab vist ride realt läbi analüüsima)
        if any(i in toorandmed for i in sydamepuudulikkus):
            self.diagnoosid[0] = "1"

        if any(i in toorandmed for i in kok_astma):
            self.diagnoosid[1] = "1"

        if all(i == "" for i in self.diagnoosid[0:3]):
            self.diagnoosid[2] = "1"

        for i in range(3):
            if self.diagnoosid[i]=="":
                self.diagnoosid[i]="0"

        #print("Töötle diagnoosid:")
        #print(self.diagnoosid)
        return

    def ava_paeviku_algus(self):
        self.ava_menyy_alajaotis("Päevik")
        self.get_element(By.XPATH, "//a[@arn-evntpar='ALL_DAYS']", "Kõikide päevade sissekanded").click()
        self.get_element(By.XPATH, "//a[@arn-evntid='showAll']", "Näita kõiki").click()
        sleep(1)
        element = self.get_element(By.XPATH, "//a[@arn-evntid='order']", "Reasta kronoloogiliselt", clickable=True)
        element.click()
        sleep(1)
        self.highlight_elements()

    def lugu_ei_sobi(self):
        self.kiirabikaart_tekst = ""
        self.emo_andmed = ""
        self.diagnoosid_tekst = ""
        self.kiirabikaart_olemas = False
        self.saabus_kiirabiga = False
        self.kiirabi = [""] * 23
        for i in range(1, 8):
            self.kiirabi[i] = "0"

        self.kiirabi_anamnees = ""
        self.emo = [""] * 23
        # Muudame 0 - 6 elemendid "0"deks
        for i in range(7):
            self.emo[i] = "0"
        self.emo_kaebused = ""
        self.emo_triaaz_varv = "6"

        self.diagnoosid = [""] * 54
        for i in range(4, 12):
            self.diagnoosid[i] = "0"
        for i in range(15, 36):
            self.diagnoosid[i] = "0"

        self.diagnoosid[51]="0"
        self.kiirabi[22]="0"
        self.emo[21]="0"

        return

    def salvesta_lood(self):

        """
        pt_andmed_kogutud = [self.record_id]
        emo_kogutud = [self.emo_triaaz_varv] + self.emo
        sisu = pt_andmed_kogutud + self.kiirabi + emo_kogutud + self.diagnoosid + ["1"]

        for i in range(len(sisu)):
            if sisu[i]==" ":
                sisu[i]=""
        lae_yles=dict(zip(self.column_names, sisu))
        #Asenda siin sõnastikus space => "" (kuskil millegi pärast lisab andmestiku space sümboli)
        if lae_yles["emo_resp_qual"]=="5":
            lae_yles["emo_resp_qual"]=""
            lae_yles["emo_resp_qual_missing___1"]="1"
        if lae_yles["ph_resp_qual"]=="5":
            lae_yles["ph_resp_qual"]=""
            lae_yles["ph_resp_qual_missing___1"] = "1"

        print(lae_yles)
       """

        return
