# -*- coding: UTF-8 -*-
from redcap import Project, RedcapError
import tkinter as tk

APP_TITLE = "ehl_helper"
REDCAP_KEY_FILENAME = "redcap_api_key"


def redcap_connect():
    URL = "https://redcap.ut.ee/api/"

    try:
        fail = open(REDCAP_KEY_FILENAME, "r")
        api_key = fail.read().strip()
    except IOError:
        print(f"RedCapi API Key fail '{REDCAP_KEY_FILENAME}' puudub töökaustast. Loome uue faili.")
        return None

    if len(api_key) != 32:
        print("API Key ei ole õige pikkusega.")
        return None

    try:
        project = Project(URL, api_key)
    except RedcapError:
        print("Antud RedCapi API key ei võimalda andmebaasile ligipääsu.")
        return None

    return project

def redcap_create_api_key():
    root = tk.Tk()
    root.title(APP_TITLE)
    window = ApiRequestWindow(root)
    root.mainloop()

class ApiRequestWindow:

    def __init__(self, master):
        self.master = master
        frame = tk.Frame(master)
        frame.pack()

        tk.Label(text = "Sisesta oma RedCap API võti:").pack(pady = 10, padx = 20)
        self.api_request = tk.Entry()
        self.api_request.pack()
        tk.Button(text = "Salvesta võti",
                  command = lambda:self.save_api_key(self.api_request.get())
                  ).pack(pady = 10)

    def save_api_key(self, api_key):
        file = open(REDCAP_KEY_FILENAME, "w")
        file.write(api_key)
        file.close()
        self.master.destroy()

class MainWindow:

    def __init__(self, master):
        self.master = master
        frame = tk.Frame(master)
        frame.pack()
        
        tk.Label(text="Isikukood: " + str(uuritavad.isikukoodid[uuritavad.sisestatav_juht])).pack(expand=True)
        tk.Label(text="Haigusjuhu number: " + str(uuritavad.hj_numbrid[uuritavad.sisestatav_juht])).pack(expand=True)
        tk.Label(text="Juhu number: " + str(uuritavad.record_ids[uuritavad.sisestatav_juht])).pack(expand=True)

def main_window():
    root = tk.Tk()
    root.title(APP_TITLE)
    window = MainWindow(root)
    root.mainloop()

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

def redcap_download_list():
    uuritavad = Uuritavad()
    fields_of_interest = ["id_code", "record_id", "ref_num","taustainfo_complete",'kiirabi_complete', "emo_complete", 'diagnoosid_complete']
    subset = project.export_records(fields=fields_of_interest)
    for element in subset:
        if element["taustainfo_complete"] in ["", "0"] or element["kiirabi_complete"] in ["", "0"] or  element["emo_complete"] in ["", "0"] or element["diagnoosid_complete"] in ["", "0"]:
            uuritavad.hj_numbrid += [element["ref_num"]]
            uuritavad.isikukoodid += [element["id_code"]]
            uuritavad.record_ids += [element["record_id"]]
    return uuritavad

# Main program flow
project = redcap_connect()  # Kui API key on juba faili salvestatud ja töötab, siis seostab RedCapi projektiga.
while project is None:
    redcap_create_api_key()  # Kui aga API keyga on mingi probleem, siis laseb kasutajal selle sisestada
    project = redcap_connect()  # Ja seejärel seostab RedCapi projektiga
uuritavad = redcap_download_list()
main_window()

    
