# -*- coding: UTF-8 -*-

#import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import ehlNavigeerimine
#import kiirabikaardi_analysaator
import tkinter as tk
import pandas as pd
from time import sleep
from redcap import Project, RedcapError

ehl = ehlNavigeerimine.ehlMain()


def ava_ehl():
    ehl.ava()

#Need funktsioonid töötlevad vastavad stringid läbi ja täidavad vastavad listid
def kiirabikaart_andmed():
    return

def diagnoosid_andmed():
    return

def emo_andmed():
    return

#Salvestab listides olevad andmed faili
def salvesta_haiguslugu():
    return

class Uuritavad:
    def __init__(self):
        self.hj_numbrid=[]
        self.isikukoodid=[]
        self.record_ids=[]
        self.sisestatav_juht=0
    def uus_lugu(self):
        self.sisestatav_juht+=1
    def eelmine_lugu(self):
        self.sisestatav_juht-=1

class Patsient:
    def __init__(self):
        self.hj_number=""
        self.isikukood=""
        self.kiirabikaart=""

uuritavad=Uuritavad()
patsient=Patsient()

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame=None
        self.switch_frame(StartPage)
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame=new_frame
        self._frame.pack(fill=tk.X)#paneme uue framei ekraanile

class StartPage(tk.Frame):
    def __init__(self, master):
        self.uuritavad=Uuritavad()
        tk.Frame.__init__(self, master)
        tk.Label(self,text="Sisesta oma RedCap API võti:").pack()
        self.faili_nimi = tk.Entry(self)
        self.faili_nimi.pack()
        tk.Button(
            self,
            text="Loe haigusjuhud sisse ja ava eHL",
            command=lambda:[self.ava_haiguslood(),ehl.ava(),master.switch_frame(DefaultPage)]).pack()

    #Loob ühenduse RedCapiga ja võtab minu DAGs olevad
    def ava_haiguslood(self):
        #xls = pd.read_excel(self.faili_nimi.get())
        #uuritavad.isikukoodid=xls["IK"].tolist()
        #uuritavad.hj_numbrid=xls["HJ"].tolist()

        URL = "https://redcap.ut.ee/api/"
        #Pane API siia:
        API_KEY = read_api_key()
        
        try:
            project = Project(URL, API_KEY)
        except RedcapError:
            print("Redcap error: Kontrolli et API key ei oleks vigane")
            return #See rida peaks tegelikult kogu appi kinni panema, aga ei mõelnud välja, kuidas seda teha. app.quit() ei töötanud.

        fields_of_interest = ["id_code", "record_id", "ref_num","taustainfo_complete",'kiirabi_complete', "emo_complete", 'diagnoosid_complete']
        subset = project.export_records(fields=fields_of_interest)

        for element in subset:
            if element["taustainfo_complete"] in ["", "0"] or element["kiirabi_complete"] in ["", "0"] or  element["emo_complete"] in ["", "0"] or element["diagnoosid_complete"] in ["", "0"]:
                uuritavad.hj_numbrid += [element["ref_num"]]
                uuritavad.isikukoodid += [element["id_code"]]
                uuritavad.record_ids += [element["record_id"]]

        return

def read_api_key():
    '''Laeb töökaustas olevast failist redcap_api_key RedCapiga ühendumiseks vajaliku võtme'''
    try:
        fail = open("redcap_api_key", "r")
        return fail.read().strip()
    except IOError:
        print("Programmi kasutamiseks on vajalik RedCapi API key, mis peab asuma failis redcap_api_key")

class DefaultPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Button(
            self,
            text="Ava haiguslugu",
            command=lambda: [ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),master.switch_frame(MainPage)]).pack(fill=tk.X)

        tk.Label(self, text="Isikukood: "+str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])).pack(fill=tk.X,side=tk.LEFT, expand=True)
        tk.Label(self,text="Haigusjuhu number: "+str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])).pack(fill=tk.X,side=tk.LEFT, expand=True)

def SalvestaPatsiendiAndmed():
    #Ava fail

    #Täida fail

    #Sulge fail
    return

#haiguslugude otsimise moodul
#top=tkinter.Tk()
#top.mainloop()
class MainPage(tk.Frame):
    def __init__(self, master):
        ehl.pt_isikukood=str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])
        ehl.pt_hjnumber=str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])
        ehl.record_id=str(uuritavad.record_ids[uuritavad.sisestatav_juht])

        tk.Frame.__init__(self, master)
        tk.Label(self, text="Isikukood: " + str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])).pack(fill=tk.X,expand=True)
        tk.Label(self, text="Haigusjuhu number: " + str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])).pack(fill=tk.X, expand=True)
        tk.Label(self, text="Juhu number: " + str(uuritavad.record_ids[uuritavad.sisestatav_juht])).pack(fill=tk.X,expand=True)

        tk.Button(
            self,
            text="Kiirabi",
            command=lambda: [ehl.ava_kiirabi_kaart(),master.switch_frame(Kiirabi)]).pack(fill=tk.X)
        tk.Button(
            self,
            text="Päeviku algus",
            command=lambda: [ehl.ava_paeviku_algus(),master.switch_frame(MainPage)]).pack(fill=tk.X)
        tk.Button(
            self,
            text="EMO triaaž",
            command=lambda: [ehl.ava_emo_triaaz(),master.switch_frame(EMO)]).pack(fill=tk.X)
        #Täida varasemad diagnoosid
        tk.Button(
            self,
            text="Epikriis",
            command=lambda: [ehl.ava_menyy_alajaotis("Epikriis"), master.switch_frame(MainPage)]).pack(fill=tk.X)

        tk.Button(
            self,
            text="Eelmine lugu",
            command=lambda: [uuritavad.eelmine_lugu(),ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),master.switch_frame(MainPage)]).pack(fill=tk.X,expand=True, side=tk.LEFT)


        #Salvesta kogutud andmed
        tk.Button(
            self,
            text="Salvesta & Järgmine lugu",
            command=lambda: [ehl.salvesta_lood(),uuritavad.uus_lugu(),ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),master.switch_frame(MainPage)]).pack(fill=tk.X,expand=True, side=tk.LEFT)

class Kiirabi(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Isikukood: " + str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])).pack(fill=tk.X,expand=True)
        tk.Label(self, text="Haigusjuhu number: " + str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])).pack(fill=tk.X, expand=True)
        tk.Label(self, text="Juhu number: " + str(uuritavad.record_ids[uuritavad.sisestatav_juht])).pack(fill=tk.X, expand=True)

        frame_nupud = tk.Frame(master=self)
        frame_nupud.pack(fill=tk.BOTH, expand=True)


        #Täida kiirabi kaart ja kuva andmed ning kaebuste märkimise lahter
        tk.Button(
            frame_nupud,
            text="Kiirabi",
            command=lambda: [self.salvestaKiirabikaart()]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        tk.Button(
            frame_nupud,
            text="Päeviku algus",
            command=lambda: [self.salvestaKiirabikaart(), ehl.ava_paeviku_algus()]).pack(fill=tk.X, expand=True,
                                                                                         side=tk.LEFT)
        #Täida EMO kaart
        tk.Button(
            frame_nupud,
            text="EMO triaaž",
            command=lambda: [self.salvestaKiirabikaart(),ehl.ava_emo_triaaz(),master.switch_frame(EMO)]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        #Täida varasemad diagnoosid
        """
        tk.Button(
            frame_nupud,
            text="Varasemad diagnoosid",
            command=lambda: [self.salvestaKiirabikaart(),ehl.ava_diagnoosid(),master.switch_frame(Diagnoosid)]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        """

        tk.Button(
            frame_nupud,
            text="Epikriis",
            command=lambda: [self.salvestaKiirabikaart(), ehl.ava_menyy_alajaotis("Epikriis")]).pack(fill=tk.X,
                                                                                                     expand=True,
                                                                                                     side=tk.LEFT)
        tk.Label(self, text="Kiirabikaardi andmed:", bg="#DC143C").pack(fill=tk.X)


        #self.tulikiirabiga_kaartpuudub = tk.Checkbutton(self, text="Pt tuli siiski kiirabiga, aga kiirabikaart puudub",variable=self.dysp)
        if not ehl.kiirabikaart_olemas:
            tk.Label(self, text="[Patsiendi kiirabi kaarti ei leitud]").pack(fill=tk.X)
            #tulikiirabiga_kaartpuudub.pack(fill=tk.X)

        frame_andmed = tk.Frame(master=self)
        frame_andmed.pack(fill=tk.X)
        frame_andmed_anamnees = tk.Frame(master=frame_andmed)
        frame_andmed_anamnees.pack(fill=tk.X)
        frame_andmed_ylemine = tk.Frame(master=frame_andmed)
        frame_andmed_ylemine.pack(fill=tk.X)
        frame_andmed_alumine = tk.Frame(master=frame_andmed)
        frame_andmed_alumine.pack(fill=tk.X)


        self.dysp=tk.IntVar()
        self.rind = tk.IntVar()
        self.synk = tk.IntVar()
        self.pres = tk.IntVar()
        self.koha = tk.IntVar()
        self.norkus = tk.IntVar()
        self.pole = tk.IntVar()

        self.dysp.set(int(ehl.kiirabi[1]))
        self.rind.set(int(ehl.kiirabi[2]))
        self.synk.set(int(ehl.kiirabi[3]))
        self.pres.set(int(ehl.kiirabi[4]))
        self.koha.set(int(ehl.kiirabi[5]))
        self.norkus.set(int(ehl.kiirabi[6]))
        self.pole.set(int(ehl.kiirabi[7]))

        #tk.Label(frame_andmed_ylemine, text="[Kiirabi anamnees]", bg="yellow").pack(fill=tk.X)
        anamnees=tk.Text(frame_andmed_anamnees,height=10, width=120, bg="yellow", wrap = tk.WORD)
        scroll_bar=tk.Scrollbar(frame_andmed_anamnees)
        scroll_bar.pack(side=tk.RIGHT)
        anamnees.pack(side=tk.LEFT)
        anamnees.insert(tk.END, "[Kiirabi anamnees] " + ehl.kiirabi_anamnees)

        tk.Label(frame_andmed_ylemine, text="Millised kaebused patsiendil esinesid?").pack(fill=tk.X)
        c1=tk.Checkbutton(frame_andmed_ylemine,text="Düspnoe/hingamisraskus",variable=self.dysp)
        c2=tk.Checkbutton(frame_andmed_ylemine, text="Rindkerevalu/ebamugavus rindkeres", variable=self.rind)
        c3=tk.Checkbutton(frame_andmed_ylemine, text="Sünkoop", variable=self.synk)
        c4=tk.Checkbutton(frame_andmed_ylemine, text="Presünkoop", variable=self.pres)
        c5=tk.Checkbutton(frame_andmed_ylemine, text="Köha", variable=self.koha)
        c6=tk.Checkbutton(frame_andmed_ylemine, text="Nõrkus", variable=self.norkus)
        c7=tk.Checkbutton(frame_andmed_ylemine, text="Mitte ükski", variable=self.pole)

        c1.pack(side=tk.TOP,anchor=tk.W)
        c2.pack(side=tk.TOP,anchor=tk.W)
        c3.pack(side=tk.TOP,anchor=tk.W)
        c4.pack(side=tk.TOP,anchor=tk.W)
        c5.pack(side=tk.TOP,anchor=tk.W)
        c6.pack(side=tk.TOP,anchor=tk.W)
        c7.pack(side=tk.TOP,anchor=tk.W)

        tk.Label(frame_andmed_alumine, text="Kvalitatiivne hingamissagedus").grid(row=0, column=0, sticky="nsew")
        values = {"Ei hinga": "1",
                  "Hüpoventilatsioon": "2",
                  "Normoventilatsioon": "3",
                  "Hüperventilatsioon": "4",
                  "Puudub": "5"}
        hing_f=tk.Frame(frame_andmed_alumine)

        #Muuda see muutuja default value ära, kiirabikaardis tooduvastu
        self.hing_kvalit = tk.StringVar(self, ehl.kiirabi[9])
        if ehl.kiirabi[9]=="":
            self.hing_kvalit.set("5")

        for (text,value) in values.items():
            tk.Radiobutton(hing_f, text=text, variable=self.hing_kvalit, value=value).pack(anchor=tk.W,ipady=5)
        hing_f.grid(row=0, column=1, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Kvantitatiivne hingamissagedus").grid(row=1, column=0, sticky="nsew")
        self.hing_sag=tk.Entry(frame_andmed_alumine)
        self.hing_sag.insert(tk.END, ehl.kiirabi[11])
        self.hing_sag.grid(row=1, column=1, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="SpO2").grid(row=2, column=0, sticky="nsew")
        self.spo=tk.Entry(frame_andmed_alumine)
        self.spo.insert(tk.END, ehl.kiirabi[13])
        self.spo.grid(row=2, column=1, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Süstoolne vererõhk").grid(row=0, column=2, sticky="nsew")
        self.sys=tk.Entry(frame_andmed_alumine)
        self.sys.insert(tk.END, ehl.kiirabi[15])
        self.sys.grid(row=0, column=3, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Diastoolne vererõhk").grid(row=1, column=2, sticky="nsew")
        self.dia=tk.Entry(frame_andmed_alumine)
        self.dia.insert(tk.END, ehl.kiirabi[17])
        self.dia.grid(row=1, column=3, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Südame löögisagedus").grid(row=2, column=2, sticky="nsew")
        self.pulss=tk.Entry(frame_andmed_alumine)
        self.pulss.insert(tk.END,ehl.kiirabi[19])
        self.pulss.grid(row=2, column=3, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Kehatemperatuur").grid(row=3, column=2, sticky="nsew")
        self.temp=tk.Entry(frame_andmed_alumine)
        self.temp.insert(tk.END, ehl.kiirabi[21])
        self.temp.grid(row=3, column=3, sticky="nsew")


        tk.Button(
            self,
            text="Eelmine lugu",
            command=lambda: [self.salvestaKiirabikaart(),uuritavad.eelmine_lugu(),ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),master.switch_frame(MainPage)]).pack(fill=tk.X,expand=True, side=tk.LEFT)


        #Salvesta kogutud andmed
        tk.Button(
            self,
            text="Salvesta & Järgmine lugu",
            command=lambda: [self.salvestaKiirabikaart(),ehl.salvesta_lood(),uuritavad.uus_lugu(),ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),master.switch_frame(MainPage)]).pack(fill=tk.X,expand=True, side=tk.LEFT)

    def salvestaKiirabikaart(self):
        if not ehl.kiirabikaart_olemas:
            ehl.kiirabi[22] = "1"
            return
        ehl.kiirabi[0] = "1"
        ehl.kiirabi[1] = str(self.dysp.get())
        ehl.kiirabi[2] = str(self.rind.get())
        ehl.kiirabi[3] = str(self.synk.get())
        ehl.kiirabi[4] = str(self.pres.get())
        ehl.kiirabi[5] = str(self.koha.get())
        ehl.kiirabi[6] = str(self.norkus.get())
        ehl.kiirabi[7] = str(self.pole.get())
        ehl.kiirabi[9] = self.hing_kvalit.get()
        ehl.kiirabi[11] = self.hing_sag.get()
        ehl.kiirabi[13] = self.spo.get()
        ehl.kiirabi[15] = self.sys.get()
        ehl.kiirabi[17] = self.dia.get()
        ehl.kiirabi[19] = self.pulss.get()
        ehl.kiirabi[21] = self.temp.get()
        ehl.kiirabi[22] = "1"

        #if not ehl.kiirabikaart_olemas:
            #ehl.kiirabikaart_puudu=str(self.tulikiirabiga_kaartpuudub.get())
        print(ehl.kiirabi)
        return


class EMO(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Isikukood: " + str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])).pack(fill=tk.X,
                                                                                                        expand=True)
        tk.Label(self, text="Haigusjuhu number: " + str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])).pack(
            fill=tk.X, expand=True)
        tk.Label(self, text="Juhu number: " + str(uuritavad.record_ids[uuritavad.sisestatav_juht])).pack(fill=tk.X,
                                                                                                         expand=True)

        frame_nupud = tk.Frame(master=self)
        frame_nupud.pack(fill=tk.BOTH, expand=True)
        tk.Button(
            frame_nupud,
            text="Kiirabi",
            command=lambda: [self.salvestaEMO(), ehl.ava_kiirabi_kaart(), master.switch_frame(Kiirabi)]).pack(fill=tk.X,
                                                                                                              expand=True,
                                                                                                              side=tk.LEFT)

        tk.Button(
            frame_nupud,
            text="Päeviku algus",
            command=lambda: [self.salvestaEMO(), ehl.ava_paeviku_algus()]).pack(
            fill=tk.X,expand=True, side=tk.LEFT)

        # Täida kiirabi kaart ja kuva andmed ning kaebuste märkimise lahter

        # Täida EMO kaart
        tk.Button(
            frame_nupud,
            text="EMO triaaž",
            command=lambda: [self.salvestaEMO()]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        # Täida varasemad diagnoosid
        """
        tk.Button(
            frame_nupud,
            text="Varasemad diagnoosid",
            command=lambda: [self.salvestaEMO(), ehl.ava_diagnoosid(),master.switch_frame(Diagnoosid)]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        """
        tk.Button(
            frame_nupud,
            text="Epikriis",
            command=lambda: [self.salvestaEMO(), ehl.ava_menyy_alajaotis("Epikriis")]).pack(fill=tk.X, expand=True,
                                                                                            side=tk.LEFT)



        frame_andmed = tk.Frame(master=self)
        frame_andmed.pack(fill=tk.X)

        """
        frame_andmed_anamnees = tk.Frame(master=frame_andmed)
        frame_andmed_anamnees.pack(fill=tk.X)
        anamnees = tk.Text(frame_andmed_anamnees, height=7, bg="yellow")
        scroll_bar = tk.Scrollbar(frame_andmed_anamnees)
        scroll_bar.pack(side=tk.RIGHT)
        anamnees.pack(side=tk.LEFT,fill=tk.X)
        anamnees.insert(tk.END, "[Kaebused EMO-s] " + ehl.emo_kaebused)

        frame_andmed_ylemine = tk.Frame(master=frame_andmed)
        frame_andmed_ylemine.pack(fill=tk.X)
        frame_andmed_alumine = tk.Frame(master=frame_andmed)
        frame_andmed_alumine.pack(fill=tk.X)

        frame_andmed_ylemine_v=tk.Frame(master=frame_andmed_ylemine)
        frame_andmed_ylemine_p=tk.Frame(master=frame_andmed_ylemine)
        frame_andmed_ylemine_v.pack(side=tk.LEFT,fill=tk.BOTH)
        frame_andmed_ylemine_p.pack(side=tk.LEFT,fill=tk.BOTH)

        self.dysp = tk.IntVar()
        self.rind = tk.IntVar()
        self.synk = tk.IntVar()
        self.pres = tk.IntVar()
        self.koha = tk.IntVar()
        self.norkus = tk.IntVar()
        self.pole = tk.IntVar()

        self.dysp.set(int(ehl.emo[0]))
        self.rind.set(int(ehl.emo[1]))
        self.synk.set(int(ehl.emo[2]))
        self.pres.set(int(ehl.emo[3]))
        self.koha.set(int(ehl.emo[4]))
        self.norkus.set(int(ehl.emo[5]))
        self.pole.set(int(ehl.emo[6]))

        # tk.Label(frame_andmed_ylemine, text="[Kiirabi anamnees]", bg="yellow").pack(fill=tk.X)
        tk.Label(frame_andmed_ylemine_v, text = "Mis oli patsiendi triaažikategooria:").pack(fill=tk.X)
        values_t = {"Punane": "1",
                  "Oranž": "2",
                  "Kollane": "3",
                  "Roheline": "4",
                  "Sinine": "5",
                  "Triaaži ei teostatud": "6"}
        triaaz_f = tk.Frame(frame_andmed_ylemine_v)

        self.triaaz = tk.StringVar(self, ehl.emo_triaaz_varv)

        for (text, value) in values_t.items():
            tk.Radiobutton(triaaz_f, text=text, variable=self.triaaz, value=value).pack(anchor=tk.W)
        triaaz_f.pack(fill=tk.X)

        tk.Label(frame_andmed_ylemine_p, text="Millised kaebused patsiendil esinesid?").pack(fill=tk.X,side=tk.TOP)
        c1 = tk.Checkbutton(frame_andmed_ylemine_p, text="Düspnoe/hingamisraskus", variable=self.dysp)
        c2 = tk.Checkbutton(frame_andmed_ylemine_p, text="Rindkerevalu/ebamugavus rindkeres", variable=self.rind)
        c3 = tk.Checkbutton(frame_andmed_ylemine_p, text="Sünkoop", variable=self.synk)
        c4 = tk.Checkbutton(frame_andmed_ylemine_p, text="Presünkoop", variable=self.pres)
        c5 = tk.Checkbutton(frame_andmed_ylemine_p, text="Köha", variable=self.koha)
        c6 = tk.Checkbutton(frame_andmed_ylemine_p, text="Nõrkus", variable=self.norkus)
        c7 = tk.Checkbutton(frame_andmed_ylemine_p, text="Mitte ükski", variable=self.pole)



        c1.pack(side=tk.TOP, anchor=tk.W)
        c2.pack(side=tk.TOP, anchor=tk.W)
        c3.pack(side=tk.TOP, anchor=tk.W)
        c4.pack(side=tk.TOP, anchor=tk.W)
        c5.pack(side=tk.TOP, anchor=tk.W)
        c6.pack(side=tk.TOP, anchor=tk.W)
        c7.pack(side=tk.TOP, anchor=tk.W)

        tk.Label(frame_andmed_alumine, text="Kvalitatiivne hingamissagedus").grid(row=0, column=0, sticky="nsew")
        values = {"Ei hinga": "1",
                  "Hüpoventilatsioon": "2",
                  "Normoventilatsioon": "3",
                  "Hüperventilatsioon": "4",
                  "Puudub": "5"}
        hing_f = tk.Frame(frame_andmed_alumine)

        # Muuda see muutuja default value ära, kiirabikaardis tooduvastu
        self.hing_kvalit = tk.StringVar(self, ehl.emo[8])
        if ehl.emo[8] == "":
            self.hing_kvalit.set("5")

        for (text, value) in values.items():
            tk.Radiobutton(hing_f, text=text, variable=self.hing_kvalit, value=value).pack(anchor=tk.W)
        hing_f.grid(row=0, column=1, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Kvantitatiivne hingamissagedus").grid(row=1, column=0, sticky="nsew")
        self.hing_sag = tk.Entry(frame_andmed_alumine)
        self.hing_sag.insert(tk.END, ehl.emo[10])
        self.hing_sag.grid(row=1, column=1, sticky="nsew")

        #Jätka siit
        tk.Label(frame_andmed_alumine, text="SpO2").grid(row=2, column=0, sticky="nsew")
        self.spo = tk.Entry(frame_andmed_alumine)
        self.spo.insert(tk.END, ehl.emo[12])
        self.spo.grid(row=2, column=1, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Süstoolne vererõhk").grid(row=0, column=2, sticky="nsew")
        self.sys = tk.Entry(frame_andmed_alumine)
        self.sys.insert(tk.END, ehl.emo[14])
        self.sys.grid(row=0, column=3, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Diastoolne vererõhk").grid(row=1, column=2, sticky="nsew")
        self.dia = tk.Entry(frame_andmed_alumine)
        self.dia.insert(tk.END, ehl.emo[16])
        self.dia.grid(row=1, column=3, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Südame löögisagedus").grid(row=2, column=2, sticky="nsew")
        self.pulss = tk.Entry(frame_andmed_alumine)
        self.pulss.insert(tk.END, ehl.emo[18])
        self.pulss.grid(row=2, column=3, sticky="nsew")

        tk.Label(frame_andmed_alumine, text="Kehatemperatuur").grid(row=3, column=2, sticky="nsew")
        self.temp = tk.Entry(frame_andmed_alumine)
        self.temp.insert(tk.END, ehl.emo[20])
        self.temp.grid(row=3, column=3, sticky="nsew")
        """

        tk.Button(
            self,
            text="Eelmine lugu",
            command=lambda: [self.salvestaEMO(), uuritavad.eelmine_lugu(),
                             ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],
                                                       uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),
                             master.switch_frame(MainPage)]).pack(fill=tk.X, expand=True, side=tk.LEFT)


        # Salvesta kogutud andmed
        tk.Button(
            self,
            text="Salvesta & Järgmine lugu",
            command=lambda: [self.salvestaEMO(), ehl.salvesta_lood(), uuritavad.uus_lugu(),
                             ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],
                                                       uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),
                             master.switch_frame(MainPage)]).pack(fill=tk.X, expand=True, side=tk.LEFT)

    def salvestaEMO(self):
        """
        #Tglt peaks [0] olema triaazi värv
        ehl.emo[0] = str(self.dysp.get())
        ehl.emo[1] = str(self.rind.get())
        ehl.emo[2] = str(self.synk.get())
        ehl.emo[3] = str(self.pres.get())
        ehl.emo[4] = str(self.koha.get())
        ehl.emo[5] = str(self.norkus.get())
        ehl.emo[6] = str(self.pole.get())
        ehl.emo[8] = self.hing_kvalit.get()
        ehl.emo_triaaz_varv = self.triaaz.get()
        ehl.emo[10] = self.hing_sag.get()
        ehl.emo[12] = self.spo.get()
        ehl.emo[14] = self.sys.get()
        ehl.emo[16] = self.dia.get()
        ehl.emo[18] = self.pulss.get()
        ehl.emo[20] = self.temp.get()
        ehl.emo[21] = "1"
        print(ehl.emo)
        """
        return

class Diagnoosid(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Isikukood: " + str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])).pack(fill=tk.X,expand=True)

        tk.Label(self, text="Haigusjuhu number: " + str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])).pack(
            fill=tk.X, expand=True)
        tk.Label(self, text="Juhu number: " + str(uuritavad.record_ids[uuritavad.sisestatav_juht])).pack(fill=tk.X,
                                                                                                         expand=True)

        frame_nupud = tk.Frame(master=self)
        frame_nupud.pack(fill=tk.BOTH,expand=True)
        tk.Button(
            frame_nupud,
            text="Epikriis",
            command=lambda: [self.salvestaDiagnoosid(), ehl.ava_menyy_alajaotis("Epikriis")]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        tk.Button(
            frame_nupud,
            text="Päeviku algus",
            command=lambda: [self.salvestaDiagnoosid(), ehl.ava_paeviku_algus()]).pack(
            fill=tk.X,expand=True, side=tk.LEFT)

        tk.Button(
            frame_nupud,
            text="Kiirabi",
            command=lambda: [self.salvestaDiagnoosid(),ehl.ava_kiirabi_kaart(),master.switch_frame(Kiirabi)]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        # Täida EMO kaart
        tk.Button(
            frame_nupud,
            text="EMO triaaž",
            command=lambda: [self.salvestaDiagnoosid(),ehl.ava_emo_triaaz(),master.switch_frame(EMO)]).pack(fill=tk.X,expand=True, side=tk.LEFT)
        # Täida varasemad diagnoosid
        tk.Button(
            frame_nupud,
            text="Varasemad diagnoosid",
            command=lambda: [self.salvestaDiagnoosid(), ehl.ava_diagnoosid()]).pack(fill=tk.X,expand=True, side=tk.LEFT)

        frame_keskmine = tk.Frame(master=self)
        frame_keskmine.pack(fill=tk.X, expand=True)
        frame_andmed = tk.Frame(master=frame_keskmine)
        frame_andmed.pack(fill=tk.BOTH,side=tk.LEFT)



        self.sydpuud = tk.IntVar(self, value=int(ehl.diagnoosid[0]))
        self.kok = tk.IntVar(self, value=int(ehl.diagnoosid[1]))
        self.puuduvad = tk.IntVar(self, value=int(ehl.diagnoosid[2]))

        frame_ylemine = tk.Frame(master=frame_andmed)
        frame_ylemine.pack(fill=tk.X)
        frame_varasemad = tk.Frame(master=frame_ylemine)
        frame_varasemad.pack(fill=tk.BOTH,side=tk.TOP)
        frame_uh= tk.Frame(master=frame_ylemine)
        frame_uh.pack(fill=tk.BOTH,side=tk.TOP)

        #Varasemad diagoonid
        tk.Label(frame_varasemad, text="Millised olid diagnoosid enne 2020-02-03?").pack(fill=tk.BOTH, side=tk.LEFT)
        c1 = tk.Checkbutton(frame_varasemad, text="Südamepuudulikkus", variable=self.sydpuud)
        c2 = tk.Checkbutton(frame_varasemad, text="KOK/astma", variable=self.kok)
        c3 = tk.Checkbutton(frame_varasemad, text="Ei kumbagi", variable=self.puuduvad)
        c1.pack(side=tk.LEFT)
        c2.pack(side=tk.LEFT)
        c3.pack(side=tk.LEFT)

        print("Diagnoosid, enne UH disk nuppe")
        print(ehl.diagnoosid)
        #UH disk JAH/EI
        tk.Label(frame_uh, text="Kas EMOs viibimise hetkel esines UHDISK diagnoos?").pack(fill=tk.BOTH,side=tk.LEFT)
        values_t = {"Jah": "1",
                    "Ei": "2"}
        jahei_f = tk.Frame(frame_uh)
        self.uhdisk_olemas = tk.StringVar(self, " ")
        if ehl.diagnoosid[3]!="":
            self.uhdisk_olemas.set(ehl.diagnoosid[3])

        for (text, value) in values_t.items():
            tk.Radiobutton(jahei_f, text=text, variable=self.uhdisk_olemas, value=value).pack(side=tk.LEFT)
        jahei_f.pack(fill=tk.BOTH,side=tk.TOP)

        tk.Label(frame_andmed, text="UHDISK diagnoos", bg="#FFB90F").pack(fill=tk.BOTH)
        #UH disk diagnoosid
        frame_uhdisk = tk.Frame(master=frame_andmed)
        frame_uhdisk.pack(fill=tk.X)

        #Pneumoonia
        frame_pneum = tk.Frame(master=frame_uhdisk)
        frame_pneum.pack(fill=tk.BOTH, side=tk.LEFT)


        #self.pneum = tk.IntVar(int(ehl.diagnoosid[4]))
        self.pneum = tk.IntVar(self,int(ehl.diagnoosid[4]))
        c4 = tk.Checkbutton(frame_pneum, text="Pneumoonia", variable=self.pneum,bg="#00FFFF")
        c4.pack(fill=tk.X)

        tk.Label(frame_pneum, text="Kummal pool pneumoonia?").pack(fill=tk.X)
        values_t = {"Vasakul": "1",
                    "Paremal": "2",
                    "Mõlemal": "3",
                    "Teadmata": "4"}
        pneupool_f = tk.Frame(frame_pneum)

        self.pneum_pool = tk.StringVar(self," ")
        if ehl.diagnoosid[36]!="":
            self.pneum_pool.set(ehl.diagnoosid[36])
        for (text, value) in values_t.items():
            tk.Radiobutton(pneupool_f, text=text, variable=self.pneum_pool, value=value).pack(anchor=tk.W)
        pneupool_f.pack(fill=tk.X)


        tk.Label(frame_pneum, text="COVID pneumoonia?").pack(fill=tk.X)
        values_t = {"Jah": "1",
                    "Ei": "2"}
        pneucov_f = tk.Frame(frame_pneum)
        self.pneum_cov = tk.StringVar(self, " ")
        if ehl.diagnoosid[40]!="":
            self.pneum_cov.set(ehl.diagnoosid[40])
        for (text, value) in values_t.items():
            tk.Radiobutton(pneucov_f, text=text, variable=self.pneum_cov, value=value).pack(anchor=tk.W, ipady=5)
        pneucov_f.pack(fill=tk.X)


        #Kopsupais/kopsuturse
        frame_pais = tk.Frame(master=frame_uhdisk)
        frame_pais.pack(fill=tk.BOTH, side=tk.LEFT)
        self.pais_turse = tk.IntVar(self,int(ehl.diagnoosid[5]))

        c5 = tk.Checkbutton(frame_pais, text="Kopsupais/turse", variable=self.pais_turse,bg="#458B74")
        c5.pack(fill=tk.X, side=tk.TOP)

        #MI
        frame_mi = tk.Frame(master=frame_uhdisk)
        frame_mi.pack(fill=tk.BOTH, side=tk.LEFT)
        self.infarkt = tk.IntVar(self,int(ehl.diagnoosid[6]))
        c6 = tk.Checkbutton(frame_mi, text="Müokardi infarkt", variable=self.infarkt, bg="#EE3B3B")
        c6.pack(fill=tk.X, side=tk.TOP)

        #KATE
        frame_kate = tk.Frame(master=frame_uhdisk)
        frame_kate.pack(fill=tk.BOTH, side=tk.LEFT)
        self.kate = tk.IntVar(self,int(ehl.diagnoosid[7]))
        c7 = tk.Checkbutton(frame_kate, text="KATE", variable=self.kate, bg="#FF6103")
        c7.pack(fill=tk.X, side=tk.TOP)

        tk.Label(frame_kate, text="Kummal pool KATE?").pack(fill=tk.X)
        values_t = {"Vasakul": "1",
                    "Paremal": "2",
                    "Mõlemal": "3",
                    "Teadmata": "4"}
        kate_f = tk.Frame(frame_kate)
        self.kate_pool = tk.StringVar(self," ")
        if ehl.diagnoosid[37]!="":
            self.kate_pool.set(ehl.diagnoosid[37])
        for (text, value) in values_t.items():
            tk.Radiobutton(kate_f, text=text, variable=self.kate_pool, value=value).pack(anchor=tk.W)
        kate_f.pack(fill=tk.X)

        #KOK/astma
        frame_kok = tk.Frame(master=frame_uhdisk)
        frame_kok.pack(fill=tk.BOTH, side=tk.LEFT)
        self.kok_astma= tk.IntVar(self,int(ehl.diagnoosid[8]))
        c8 = tk.Checkbutton(frame_kok, text="KOK/astma", variable=self.kok_astma, bg="#66CDAA")
        c8.pack(fill=tk.X, side=tk.TOP)

        #Pleuraefusioon
        frame_pleur = tk.Frame(master=frame_uhdisk)
        frame_pleur.pack(fill=tk.BOTH, side=tk.LEFT)
        self.pleur = tk.IntVar(self,int(ehl.diagnoosid[9]))
        c9 = tk.Checkbutton(frame_pleur, text="Pleuraefusioon", variable=self.pleur, bg="#76EEC6")
        c9.pack(fill=tk.X, side=tk.TOP)

        tk.Label(frame_pleur, text="Suuruse kirjeldus").pack(fill=tk.X)
        values_t = {"Väike": "1",
                    "Keskmine/mõõdukas": "2",
                    "Suur/rohke": "3",
                    "Ei ole kirjeldatud": "4"}
        efsuur_f = tk.Frame(frame_pleur)
        self.pleur_suur = tk.StringVar(self," ")
        if ehl.diagnoosid[12]!="":
            self.pleur_suur.set(ehl.diagnoosid[12])
        for (text, value) in values_t.items():
            tk.Radiobutton(efsuur_f, text=text, variable=self.pleur_suur, value=value).pack(anchor=tk.W)
        efsuur_f.pack(fill=tk.X)

        tk.Label(frame_pleur, text="Efusiooni kihipaksus:").pack(fill=tk.X)

        self.efusiooni_kihi_paksus = tk.Entry(frame_pleur)
        if ehl.diagnoosid[14] != "":
            self.efusiooni_kihi_paksus.insert(tk.END, ehl.diagnoosid[14])
        self.efusiooni_kihi_paksus.pack(fill=tk.X)

        tk.Label(frame_pleur, text="Kummal pool efusioon?").pack(fill=tk.X)
        values_t = {"Vasakul": "1",
                    "Paremal": "2",
                    "Mõlemal": "3",
                    "Teadmata": "4"}
        pleur_f = tk.Frame(frame_pleur)
        self.pleur_pool = tk.StringVar(self, " ")
        if ehl.diagnoosid[38]!="":
            self.pleur_pool.set(ehl.diagnoosid[38])
        for (text, value) in values_t.items():
            tk.Radiobutton(pleur_f, text=text, variable=self.pleur_pool, value=value).pack(anchor=tk.W)
        pleur_f.pack(fill=tk.X)

        # Pneumotooraks
        frame_toor = tk.Frame(master=frame_uhdisk)
        frame_toor.pack(fill=tk.BOTH, side=tk.LEFT)
        self.pneumotooraks = tk.IntVar(self,int(ehl.diagnoosid[10]))
        c10 = tk.Checkbutton(frame_toor, text="Pneumotooraks", variable=self.pneumotooraks, bg="#7FFFD4")
        c10.pack(fill=tk.X, side=tk.TOP)

        tk.Label(frame_toor, text="Kummal pool pneumotooraks?").pack(fill=tk.X)
        values_t = {"Vasakul": "1",
                    "Paremal": "2",
                    "Mõlemal": "3",
                    "Teadmata": "4"}
        toor_f = tk.Frame(frame_toor)
        self.pneumotooraks_pool = tk.StringVar(self," ")
        if ehl.diagnoosid[39]!="":
            self.pneumotooraks_pool.set(ehl.diagnoosid[39])
        for (text, value) in values_t.items():
            tk.Radiobutton(toor_f, text=text, variable=self.pneumotooraks_pool, value=value).pack(anchor=tk.W)
        toor_f.pack(fill=tk.X)

        #Perikardi efusioon
        frame_perikard = tk.Frame(master=frame_uhdisk)
        frame_perikard.pack(fill=tk.BOTH, side=tk.LEFT)
        self.perikard = tk.IntVar(self,int(ehl.diagnoosid[11]))
        c11 = tk.Checkbutton(frame_perikard, text="Perikardi efusioon", variable=self.perikard, bg="#FF4040")
        c11.pack(fill=tk.X, side=tk.TOP)

        tk.Label(frame_perikard, text="Tamponaadi tunnused?").pack(fill=tk.X)
        values_t = {"Jah": "1",
                    "Ei": "2"}
        tamp_f = tk.Frame(frame_perikard)
        self.tamponaad = tk.StringVar(self," ")
        if ehl.diagnoosid[41]!="":
            self.tamponaad.set(ehl.diagnoosid[41])
        for (text, value) in values_t.items():
            tk.Radiobutton(tamp_f, text=text, variable=self.tamponaad, value=value).pack(anchor=tk.W, ipady=5)
        tamp_f.pack(fill=tk.X)
        tk.Label(frame_andmed, text="Hospitaliseerimine", bg="#FFB90F").pack(fill=tk.BOTH)


        #Hospitaliseerimine
        frame_hospitaliseerimine = tk.Frame(master=frame_andmed)
        frame_hospitaliseerimine.pack(fill=tk.X)

        #Hospitaliseerimise küsimus
        frame_hosp = tk.Frame(master=frame_hospitaliseerimine)
        frame_hosp.pack(fill=tk.BOTH, side=tk.LEFT, padx=15)
        tk.Label(frame_hosp, text="EMO visiidi lõpptulemus?").pack(fill=tk.X,side=tk.TOP)
        values_t = {"Hospitaliseeriti uuringukeskuses": "1",
                    "Lubati koju": "2",
                    "Suri EMOs": "3",
                    "Suunati teise haiglasse": "4"}
        hosp_f = tk.Frame(frame_hosp)
        self.visiidi_tulemus = tk.StringVar(self," ")
        if ehl.diagnoosid[42]!="":
            self.visiidi_tulemus.set(ehl.diagnoosid[42])
        for (text, value) in values_t.items():
            tk.Radiobutton(hosp_f, text=text, variable=self.visiidi_tulemus, value=value).pack(anchor=tk.W)
        hosp_f.pack(fill=tk.X)

        #hospitaliseerimise kestvus
        frame_paevi = tk.Frame(master=frame_hospitaliseerimine)
        frame_paevi.pack(fill=tk.BOTH, side=tk.LEFT, padx=15)
        tk.Label(frame_paevi, text="Statsionaarselt ravilt lahkumise/surma kuupäev (Y-M-D):").pack(fill=tk.X, side=tk.TOP)
        self.haiglast_lahkumine=tk.Entry(frame_paevi)
        if ehl.diagnoosid[43] != "":
            self.haiglast_lahkumine.insert(tk.END, ehl.diagnoosid[43])
        self.haiglast_lahkumine.pack(fill=tk.X, side=tk.TOP)

        #diagnoosid[44] on kestvus päevades, see jääb vahele, kuna tuleb arvutada

        # Intensiivravi vajadus
        tk.Label(frame_paevi, text="Kas patsient vajas III astme intensiivravi?").pack(fill=tk.X,side=tk.TOP)
        values_t = {"Jah": "1",
                    "Ei": "2"}
        intensiiv_f = tk.Frame(frame_paevi)
        self.vajas_intensiiv= tk.StringVar(self," ")
        if ehl.diagnoosid[45] != "":
            self.vajas_intensiiv.set(ehl.diagnoosid[45])
        for (text, value) in values_t.items():
            tk.Radiobutton(intensiiv_f, text=text, variable=self.vajas_intensiiv, value=value).pack(anchor=tk.W)
        intensiiv_f.pack(fill=tk.X)

        tk.Label(frame_paevi, text="Intensiivravisse hospitaliseerimise kuupäev (Y-M-D):").pack(fill=tk.X, side=tk.TOP)
        self.intensiivravisse=tk.Entry(frame_paevi)
        if ehl.diagnoosid[46] != "":
            self.intensiivravisse.insert(tk.END, ehl.diagnoosid[46])
        self.intensiivravisse.pack(fill=tk.X, side=tk.TOP)
        tk.Label(frame_paevi, text="Intensiivravist lahkumise kuupäev (Y-M-D):").pack(fill=tk.X, side=tk.TOP)
        self.intensiivravist = tk.Entry(frame_paevi)
        if ehl.diagnoosid[47] != "":
            self.intensiivravist.insert(tk.END, ehl.diagnoosid[47])
        self.intensiivravist.pack(fill=tk.X, side=tk.TOP)

        # diagnoosid[49] on intensiivravi kestvus
        # hospitaliseerimise kestvus
        frame_lahkumine = tk.Frame(master=frame_hospitaliseerimine)
        frame_lahkumine.pack(fill=tk.BOTH, side=tk.TOP, padx=15)
        tk.Label(frame_lahkumine, text="Kas patsient suri haiglas?").pack(side=tk.TOP, anchor=tk.NW)
        values_t = {"Jah": "1",
                    "Ei": "2"}
        surm_f = tk.Frame(frame_lahkumine)
        self.suri_haiglas = tk.StringVar(self," ")
        if ehl.diagnoosid[49] != "":
            self.suri_haiglas.set(ehl.diagnoosid[49])
        for (text, value) in values_t.items():
            tk.Radiobutton(surm_f, text=text, variable=self.suri_haiglas, value=value).pack(anchor=tk.W)
        surm_f.pack(fill=tk.BOTH)

        tk.Label(frame_lahkumine, text="Kas patsient suunati aktiivraviks teise haiglasse?").pack(side=tk.TOP, anchor=tk.NW)
        values_t = {"Jah": "1",
                    "Ei": "2"}
        lahkumine_f = tk.Frame(frame_lahkumine)
        self.teine_haigla= tk.StringVar(self," ")
        if ehl.diagnoosid[50] != "":
            self.teine_haigla.set(ehl.diagnoosid[50])
        for (text, value) in values_t.items():
            tk.Radiobutton(lahkumine_f, text=text, variable=self.teine_haigla, value=value).pack(anchor=tk.W)
        lahkumine_f.pack(fill=tk.BOTH)


        frame_mitteuh = tk.Frame(master=frame_keskmine)
        frame_mitteuh.pack(fill=tk.BOTH, side=tk.LEFT)

        # Mitte UHDISK diagoonsid


        diagnooside_sildid=["Kõhuvalu","Alaseljavalu","Rindkerevalu k.a. ülaseljavalu","Peavalu","Kuseteede infektsioon","Kõhuõõne põletikuline haigus","Seedetrakti verejooks","Pehme koe infektsioon","Ülemiste hingamisteede infektsioon","Muu koldega infektsioon","Kodade virvendus või laperdus","Muud rütmihäired","Ajuinfarkt/TIA","Vertiigo","Sünkoop","Epilepsia","Kõrge vererõhk","Alkoholi kuritarvitamine","Allergilised reaktsioonid","Iiveldus/oksendamine","Muud kaebused"]
        self.mitte_uhdisk = []
        self.valikud = []
        tk.Label(frame_mitteuh, text="Mitte-UHDISK diagnoos:",bg="#FFB90F").pack(fill=tk.BOTH, side=tk.TOP)
        for i in range(len(diagnooside_sildid)):
            self.mitte_uhdisk.append(tk.IntVar(self,value=int(ehl.diagnoosid[15+i])))
            self.valikud.append(tk.Checkbutton(frame_mitteuh,text=diagnooside_sildid[i],variable=self.mitte_uhdisk[i]))
            self.valikud[i].pack(side=tk.TOP, anchor=tk.W)

        tk.Button(
            self,
            text="Eelmine lugu",
            command=lambda: [self.salvestaDiagnoosid(), uuritavad.eelmine_lugu(),
                             ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],
                                                       uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),
                             master.switch_frame(MainPage)]).pack(fill=tk.X, expand=True, side=tk.LEFT)


        # Salvesta kogutud andmed
        tk.Button(
            self,
            text="Salvesta & Järgmine lugu",
            command=lambda: [self.salvestaDiagnoosid(), ehl.salvesta_lood(), uuritavad.uus_lugu(),
                             ehl.haiguslugude_otsimine(uuritavad.isikukoodid[uuritavad.sisestatav_juht],
                                                       uuritavad.hj_numbrid[uuritavad.sisestatav_juht]),
                             master.switch_frame(MainPage)]).pack(fill=tk.X, expand=True, side=tk.LEFT)



    def salvestaDiagnoosid(self):
        print("Diagnoosid salvestaDiagnoosid alguses:")
        #Varasemad diagnoosid
        ehl.diagnoosid[0] = str(self.sydpuud.get())
        ehl.diagnoosid[1] = str(self.kok.get())
        ehl.diagnoosid[2] = str(self.puuduvad.get())
        ehl.diagnoosid[3] = self.uhdisk_olemas.get()
        ehl.diagnoosid[4] = str(self.pneum.get())
        ehl.diagnoosid[5] = str(self.pais_turse.get())
        ehl.diagnoosid[6] = str(self.infarkt.get())
        ehl.diagnoosid[7] = str(self.kate.get())
        ehl.diagnoosid[8] = str(self.kok_astma.get())
        ehl.diagnoosid[9] = str(self.pleur.get())
        ehl.diagnoosid[10] = str(self.pneumotooraks.get())
        ehl.diagnoosid[11] = str(self.perikard.get())

        for i in range(len(self.mitte_uhdisk)):
            ehl.diagnoosid[i+15]=str(self.mitte_uhdisk[i].get())

        #Pleura
        ehl.diagnoosid[12] = self.pleur_suur.get()
        ehl.diagnoosid[14] = self.efusiooni_kihi_paksus.get()
        if ehl.diagnoosid[14] != "":
            ehl.diagnoosid[13] = "1"
        else:
            ehl.diagnoosid[13] = "0"
        ehl.diagnoosid[38] = self.pleur_pool.get()

        ehl.diagnoosid[36] = self.pneum_pool.get()
        ehl.diagnoosid[37] = self.kate_pool.get()
        ehl.diagnoosid[39] = self.pneumotooraks_pool.get()
        ehl.diagnoosid[40] = self.pneum_cov.get()
        ehl.diagnoosid[41] = self.tamponaad.get()

        ehl.diagnoosid[42] = self.visiidi_tulemus.get()
        ehl.diagnoosid[43] = self.haiglast_lahkumine.get()
        #nr 44 on hospitaliseerimise kestvus
        ehl.diagnoosid[45] = self.vajas_intensiiv.get()
        ehl.diagnoosid[46] = self.intensiivravisse.get()
        ehl.diagnoosid[47] = self.intensiivravist.get()
        #nr 48 on icu kestvus
        ehl.diagnoosid[49] = self.suri_haiglas.get()
        ehl.diagnoosid[50] = self.teine_haigla.get()

        ehl.diagnoosid[51] = "1"
        print("Diagnoosid salvestaDiagnoosid lõpus:")
        print(ehl.diagnoosid)
        return

#ava haiguslugude fail:

app = App()
app.mainloop()
"""
#Avame akna
window=tk.Tk()
window.title("Ultraheli EMOs")

#Loome nupu
button = tk.Button(
    master=window,
    text="Ava eHL",
    command=ava_ehl
)

button.pack()

#Käivitame rakenduse
window.mainloop()
"""

"""
while input("Vajuta [y] kui soovid jätkata:")=="y":
    HJ_number="20201006-334262"
    #ehl.haiguslugude_otsimine(HJ_number)
    #kiirabikaart=ehl.ava_kiirabi_kaart().splitlines()
    kiirabikaart=["Digiloo haigusjuhtum nr 2010060179", "Kiirabikaart nr 90007141MUSTVEE91320201006063235 versioon 1", "Tervishoiuasutus SA Tartu Kiirabi", "Registreerimiskood 90007141", "Aadress Riia 18, 51010, Eesti", "Telefon", "7408800", "E-post", "kiirabi@kiirabi.ee", "Faks", "7408800", "Koostaja", "Nimi DENISS ŠRAMOV Kood N09892", "Eriala N120 Erakorralise meditsiini õendus", "Patsient", "Isikukood 36810192770", "Eesnimi ANDRES", "Perekonnanimi PIIRI", "Sünniaeg 19.10.1968", "Sugu mees", "Elukoht , Eesti, Jõgeva maakond, Jõgeva vald, Kõnnu küla, Metsapiiri", "Perearst TATJANA ŠTŠASLIVAJA; D01901", "Perearsti kontaktid", "tel:772 6677", "Täiendavad patsiendi andmed", "Identifitseeritud identifitseeritud suuliselt", "Vanus (täpne) 51 aastat", "Brigaad", "Tüüp õebrigaad", "Kutsung MUSTVEE 913", "Liikmed", "Tüüp Nimi THT Kood tase", "juhtiv liige Deniss Šramov N09892 õde", "teine liige Vadim Verhovski N13978 õde", "kolmas liige IVAR VINKMANN kiirabitehnik", "Häirekeskuse juhtumi andmed", "Häirekeskuse juhtumi number 2010060179", "Hädaabiteate vastuvõtmise aeg 06.10.2020 06:29:06", "Prioriteet C", "Tüüpjuhtum rütmihäired; M 52 õhupuudus, covid 19 kokkupuude ja kaebused puuduvad, valu all pool", "Oletatav abivajajate arv 1", "Abivajaja ANDRE PIIRI; mees; 52 aastat", "Häirekeskusesse teataja andre piiri; 058370300", "Sündmuskoht , Metsapiiri, Kõnnu küla, Jõgeva vald, Jõgeva mk. Alastvere teeotsas metsa 2km, 3- 4. maja , GPS koordinaadid: 6523699.73,662856.98", "Hädaabikutse ja väljasõidukorralduse ning kutse täitmise andmed", "Hädaabikutse ja väljasõidukorralduse ning kutse täitmise andmed", "Väljasõidukorralduse edastamine, aeg 06.10.2020 06:29:06", "Väljasõit, aeg 06.10.2020 06:31:35", "Sündmuskohale jõudmine, aeg 06.10.2020 06:46:36", "Lahkumine sündmuskohalt haiglasse, aeg 06.10.2020 07:29:26", "Sisestatud hädaabikutse ja väljasõidukorralduse ning kutse täitmise andmed", "Hädaabikutse ja väljasõidukorralduse ning kutse täitmise andmed", "Lahkumine sündmuskohalt haiglasse, aeg 06.10.2020 07:29:26", "Patsiendi üleandmine haiglale", "Anamnees", "Kaebused", "Ülakõhuvalu 12 tundi. Ise võtnud t Diklofenaki. Hetkel 24 tundi ei ole alkohooli tarbinud.", "Haiguse kulg", "Hüpervenrileerib, kahvatu. Viimati söönud 24 tundi tagasi. Valu ülakõhus, rohkem vasakul.", " Jalad turses. 02 foonil hüperventileerib vähem, üritab O2 maski eest ara võtta. Autos", " kaebab iiveldust. Ütleb, et igalt poolt valutab. Kroonilist kopsuhaigust eitab. Haiglas", " polevat enda sõnul olnud.", "Patsiendi igapäevaselt tarvitatavad ravimid", "Nebivelol, allopurinol, jentadueto,codalnessa, plaquenil,xarelto, torasemid.", "Patsiendi objektiivne staatus", "Neuroloogiline leid 06.10.2020 07:19", "Teadvus selge", "Glasgow kooma skaala (GKS) 15", "Silmade avamine spontaanne (4p)", "Sõnaline kontakt orienteeritud / lalin, vadin (5p)", "Motoorne vastus täidab käsklusi / liigutab spontaanselt (6p)", "Pupillid", "Pupillide suurus normaalne", "Pupillidiferents võrdsed", "Valgusreaktsioon (parem pupill) reageerib", "Valgusreaktsioon (vasak pupill) reageerib", "Hingamine 06.10.2020 07:46", "Hingamissageduse tase hüperventilatsioon", "Hoiab hingamisteid lahti jah", "Oksügenisatsioon", "SpO2 97 %", "Hingamine 06.10.2020 07:20", "Hingamissageduse tase hüperventilatsioon", "Hingamissagedus 24 korda/min", "Hoiab hingamisteid lahti jah", "Oksügenisatsioon", "SpO2 92 %", "Hingamine 06.10.2020 07:06", "Hingamissageduse tase hüperventilatsioon", "Hingamissagedus 28 korda/min", "Hoiab hingamisteid lahti jah", "Oksügenisatsioon", "SpO2 78 %", "Kopsu kuulatusleid (parem kops) vesikulaarne hingamiskahin", "Kopsu kuulatusleid (parem kops) räginad", "Kopsu kuulatusleid (vasak kops) vesikulaarne hingamiskahin", "Kopsu kuulatusleid (vasak kops) räginad", "Hemodünaamika 06.10.2020 07:56", "Vererõhk", "Vererõhk süstoolne 110 mmHg", "Vererõhk diastoolne 72 mmHg", "Vererõhk keskmine arteriaalne (arvutuslik) 85 mmHg", "Pulss", "Pulsisagedus 90 korda/min", "Pulsi regulaarsus ebaregulaarne", "Hemodünaamika 06.10.2020 07:44", "Vererõhk", "Vererõhk süstoolne 126 mmHg", "Vererõhk diastoolne 55 mmHg", "Vererõhk keskmine arteriaalne (arvutuslik) 79 mmHg", "Pulss", "Pulsisagedus 78 korda/min", "Hemodünaamika 06.10.2020 07:28", "Vererõhk", "Vererõhk süstoolne 110 mmHg", "Pulss", "Pulsisagedus 83 korda/min", "Pulsi regulaarsus regulaarne", "EKG leid SR 97/ min", "Hemodünaamika 06.10.2020 07:24", "Vererõhk", "Vererõhk süstoolne 70 mmHg", "Vererõhk diastoolne 30 mmHg", "Vererõhk keskmine arteriaalne (arvutuslik) 43 mmHg", "Pulss", "Pulsisagedus 80 korda/min", "Pulsi regulaarsus regulaarne", "EKG leid Kodade virvendus arütmia I, II, aVF, V3-V6 ST depressioonid.", "Teised elutähtsad näitajad 06.10.2020 07:48", "Veresuhkur 5.7 mmol/l", "Teised elutähtsad näitajad 06.10.2020 07:32", "Veresuhkur 5.3 mmol/l", "Teised elutähtsad näitajad 06.10.2020 07:05", "Veresuhkur Mõõtmatu madal", "Temperatuur (kõrvast) 36.0 Cel", "Teostatud protseduurid", "Veeni kanüleerimine (perifeerne veen)", "Kanüüli suurus G18", "Katsete arv 1", "Veeni kanüleerimine", "Veeni kanüleerimine (perifeerne veen)", "Kanüüli suurus G20", "Katsete arv 1", "Protseduuri õnnestumine jah", "Infusioon", "Pulssoksümeetria 06.10.2020 07:08", "EKG tegemine 06.10.2020 07:29", "Kordade arv 2", "Veresuhkru määramine", "Kordade arv 3", "Temperatuuri mõõtmine", "Kordade arv 1", "Hapnikravi (reservuaarmaskiga) 06.10.2020 07:46", "Hapniku manustamise kogus 8 l/min", "Hapnikravi (maskiga) 06.10.2020 07:19", "Hapniku manustamise kogus 10 l/min", "Manustatud ravimid", "Manustamise aeg Manustamine Annus Ravimivorm Ravim (ATC) Lisainfo", "06.10.2020 07:55 perifeersesse veeni - infusioonina 1000 mg infusioonilahus N02BE01 - N02BE01 paratsetamool (paratsetamool)", "  06.10.2020 07:46 perifeersesse veeni - süstena 50 mg süstelahus C03CA01 - C03CA01 furosemiid (furosemiid)", "  06.10.2020 07:30 perifeersesse veeni - süstena 10 mg süstelahus A03FA01 - A03FA01 metoklopramiid (metoklopramiid)", "  06.10.2020 07:23 perifeersesse veeni - infusioonina 250 ml infusioonilahus B05BA03 - B05BA03 süsivesikud (Glükoos 5% 250ml)", "  06.10.2020 07:05 perifeersesse veeni - süstena 24 mg süstelahus B05BA03 - B05BA03 süsivesikud (Glükoos 40% 10ml)", "  Lõplik kliiniline diagnoos", "Liik Diagnoos Sõnaline diagnoos Statistiline liik", "Põhihaigus K85 - K85 Äge pankreatiit e kõhunäärmepõletik", "Kaasuv haigus I50.9 - I50 Südamepuudulikkus - I50.9 Täpsustamata südamepuudulikkus", "Visiidi tulemus", "Visiidi tulemus hospitaliseeriti", "Patsiendi üleandmine haiglale", "; TARTU ÜLIKOOLI KLIINIKUM SA; 90001478; EMO", "Dokument koostatud 06.10.2020 08:09:22", "Dokumendi keel EST", "Konfidentsiaalsus:", "Patsiendile/Eestkostjale avatud", "Lapsevanemale/Usaldusisikule avatud", "Vastutaja", "Asutuse/isiku nimi SA Tartu Kiirabi", "Kood 90007141"]
    #analyys_kiirabi=kiirabikaardi_analysaator.kiirabikaart(kiirabikaart)
    #analyys_kiirabi.UH_uuringu_andmed()
"""
