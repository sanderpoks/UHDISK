# -*- coding: UTF-8 -*-
from ehlassistant.ehlredcap import RedcapConnection
import tkinter as tk
import ehlassistant.ehlNavigeerimine as ehlNavigeerimine
import os
import sys
import logging

REDCAP_KEY_FILENAME = "./redcap_api_key"
VERSION_FILENAME = "./version"


class TkErrorCatcher:

    '''
    In some cases tkinter will only print the traceback.
    Enables the program to catch tkinter errors normally
    '''

    def __init__(self, func, subst, widget) -> None:
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit as msg:
            raise SystemExit(msg)
        except Exception as err:
            raise err


tk.CallWrapper = TkErrorCatcher


def get_version():
    try:
        with open(VERSION_FILENAME, mode="r") as file:
            version = file.read().strip()
            return version
    except IOError:
        logging.error(f"Fail {VERSION_FILENAME} ei eksisteeri.")


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

        tk.Label(text="Sisesta oma RedCap API võti:").pack(pady=10, padx=20)
        self.api_request = tk.Entry()
        self.api_request.pack()
        tk.Button(text="Salvesta võti",
                  command=lambda: self.save_api_key(self.api_request.get())
                  ).pack(pady=10)

    def save_api_key(self, api_key):
        file = open(REDCAP_KEY_FILENAME, "w")
        file.write(api_key)
        file.close()
        self.master.destroy()


class MainWindow:

    def __init__(self, master, record_manager):
        self.master = master
        self.record_manager = record_manager
        self.active_record = self.record_manager.current()

        BUTTONWIDTH = 5

        topframe = tk.Frame(master)
        botframe = tk.Frame(master)

        topframe.grid(row=0)
        botframe.grid(row=1)

        self.isikukood = tk.StringVar()
        self.hj_number = tk.StringVar()
        self.record_id = tk.StringVar()
        self.refresh_labels()

        tk.Label(topframe, textvariable=self.isikukood).pack(expand=True)
        tk.Label(topframe, textvariable=self.hj_number).pack(expand=True)
        self.record_label = tk.Label(topframe, textvariable=self.record_id)
        self.record_label.pack(expand=True)
        self.record_label.bind("<Double-Button-1>", self.edit_case)

        kiirabinupp = tk.Button(botframe, text="Kiirabi", command=lambda:ehl.navigeeri("kiirabi"), width=BUTTONWIDTH)
        paevikunupp = tk.Button(botframe, text="Päevik", command=lambda:ehl.navigeeri("paevik"), width=BUTTONWIDTH)
        triaazinupp = tk.Button(botframe, text="Triaaž", command=lambda:ehl.navigeeri("triaaz"), width=BUTTONWIDTH)
        epikriisinupp = tk.Button(botframe, text="Epikriis", command=lambda:ehl.navigeeri("Epikriis"), width=BUTTONWIDTH)

        jargminenupp = tk.Button(botframe, text="Järgmine", command = self.next, width = BUTTONWIDTH)
        eelminenupp = tk.Button(botframe, text="Eelmine", command = self.previous, width = BUTTONWIDTH)

        kiirabinupp.grid(row=0,column=0)
        paevikunupp.grid(row=0, column=1)
        triaazinupp.grid(row=0, column=2)
        epikriisinupp.grid(row=1,column=1)
        jargminenupp.grid(row=1,column=2)
        eelminenupp.grid(row=1,column=0)

        ehl.navigeeri("haiguslugu", self.active_record.isikukood, self.active_record.hj_number)


    def refresh_labels(self):
        self.isikukood.set("Isikukood: " + str(self.active_record.isikukood))
        self.hj_number.set("Haigusjuhu number: " + str(self.active_record.hj_number))
        self.record_id.set("Juhu number: " + str(self.active_record.record_id))

    def next(self):
        self.active_record = self.record_manager.next()
        self.refresh_labels()
        ehl.navigeeri("haiguslugu", self.active_record.isikukood, self.active_record.hj_number)

    def previous(self):
        self.active_record = self.record_manager.previous()
        self.refresh_labels()
        ehl.navigeeri("haiguslugu",self.active_record.isikukood, self.active_record.hj_number)

    def navigate_to(self, record_id):
        self.record_manager = RecordManager(untethered=True) # Loome uue navigeerimisindeksi, mis ei piira navigeerimist ainult meie DAGidele
        self.active_record = self.record_manager.goto_record(record_id)
        ehl.navigeeri("haiguslugu", self.active_record.isikukood, self.active_record.hj_number)
        self.refresh_labels()

    def edit_case(self, event):
        widget = event.widget
        case_entry = tk.Entry(widget)
        case_entry.place(x=0, y=0, anchor="nw", relwidth=1.0, relheight=1.0)
        case_entry.bind("<Return>", self.remove_case_entry)
        case_entry.insert(tk.END, self.active_record.record_id)
        case_entry.focus_set()

    def remove_case_entry(self, event):
        entry = event.widget
        entry_result = entry.get()
        if entry_result.isnumeric():
            entry_result = int(entry_result)
            self.navigate_to(entry_result)
        entry.destroy()


def main_window(record_manager):
    root = tk.Tk()
    root.title(APP_TITLE)
    window = MainWindow(root, record_manager)
    root.mainloop()

def login_window(APP_TITLE):
    root = tk.Tk()
    root.title(APP_TITLE)
    window = LoginWindow(root)
    root.mainloop()

class LoginWindow:

    def __init__(self, master):
        self.master = master

        tk.Button(text="Olen eHLi sisse loginud", command = self.quit).pack(padx = 20, pady = 20)

    def quit(self):
        self.master.destroy()

class Record:
    def __init__(self, record_id):
        self.record_id = record_id
        record = redcap_retrieve_remote(record_id)
        logging.info(record)
        self.isikukood = record["id_code"]
        self.hj_number = record["ref_num"]

    def print(self):
        print(f"Record ID:\t{self.record_id}\nIsikukood:\t{self.isikukood}\nHJ number:\t{self.hj_number}\n")


def redcap_retrieve_remote(record_id):
    fields_of_interest = ["id_code", "ref_num"]
    record = rc.download(redcap_id=record_id,fields=fields_of_interest)
    return record  # Tagastab dictionary

def redcap_download_available():
    ''' See funktsioon tõmbab alla ainult anonümiseeritud andmed'''
    fields_of_interest = ["record_id", "taustainfo_complete",'kiirabi_complete', "emo_complete", 'diagnoosid_complete']
    records = rc.download_multiple(fields=fields_of_interest)
    results = []
    for element in records:
        if element["taustainfo_complete"] in ["", "0"] or element["kiirabi_complete"] in ["", "0"] or  element["emo_complete"] in ["", "0"] or element["diagnoosid_complete"] in ["", "0"]:
            if element["redcap_data_access_group"] == "poks":
                results.append(element["record_id"])
    return results

class RecordManager():
    ''' Haldab info järjepidevat allalaadimist RedCapist"'''
    def __init__(self, untethered=False):
        if untethered: # Kui navigeerime kõiki Redcapi uuritavaid sõltumata staatusest ja DAGist
            self.record_id_list = range(1,21299) #Kokku 21299 uuritavat
        else:   # Kui navigeerime ainult meie DAGi uurimata uuritavaid
            self.record_id_list = redcap_download_available()
        self.records = []
        self.index = 0

    def current(self):
        current_record_id = self.record_id_list[self.index]
        logging.info(f"Current record ID is {current_record_id}")
        return self.retrieve_record(current_record_id)

    def next(self):
        self.index += 1
        logging.info(f"Index is {self.index}")
        if self.index > len(self.record_id_list):
            self.index -= 1
        return self.current()

    def previous(self):
        self.index -= 1
        if self.index < 0:
            self.index = 0
        return self.current()

    def goto_record(self, record_id):
        self.current_record_id = record_id
        self.index = record_id - 1
        return self.current()


    def retrieve_record(self, current_record_id):
        try:
            record = self.records[self.index]
            logging.info("Record found locally")
            return record
        except IndexError:
            logging.info("Record not found locally, retrieveing")
            record = Record(current_record_id)
            self.records.append(record)
            return(record)


def setup_logger() -> None:
    logging.basicConfig(filename="ehl_log.txt", filemode='w', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    selenium_logger.disabled = True

if __name__ == "__main__":
    # Viime aktiivse töökausta faili asukohta, et lisafailid oleks leitavad
    os.chdir(os.path.join(os.path.dirname(sys.argv[0]), ".."))


    # Main program flow
    VERSION = get_version()
    APP_TITLE = f"ehl_helper - {VERSION}"

    setup_logger()


    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path=REDCAP_KEY_FILENAME)

    record_manager = RecordManager()
    ehl = ehlNavigeerimine.ehlMain()
    #login_window(APP_TITLE) # Loob akna, mille kaudu märku anda, kui eHLi on sisse logitud.
    main_window(record_manager) # Avab navigeerimispaneeli
