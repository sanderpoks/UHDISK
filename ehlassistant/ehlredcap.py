# -*- coding: UTF-8 -*-
from redcap import Project, RedcapError
import logging
from typing import Optional

class APIKeyError(Exception):
    """ Tõstatub siis, kui failist ei saanud valiidset RedCap API võtit kätte. """
    pass

class RedcapConnection:
    """ See klass haldab kogu suhtlust RedCapi projektiga. """
    def __init__(self, url: str, api_key_path: str):
        self.url = url
        self.api_key = self.read_api_key(api_key_path)
        self.project = self.connect_redcap()

    def read_api_key(self, api_key_path: str):
        """ Loeb failist API key ja valideerib selle. """
        try:
            with open(api_key_path, "r") as key_file:
                api_key = key_file.read().strip()
        except IOError:
            logging.error(f"RedCapi API Key fail '{api_key_path}' puudub töökaustast. Loome uue faili.")
            raise APIKeyError

        if len(api_key) != 32:
            logging.error("API Key ei ole õige pikkusega.")
            raise APIKeyError

        return api_key

    def connect_redcap(self):
        """ Loob ühenduse RedCapi serveriga. """
        try:
            project = Project(self.url, self.api_key)
            return project
        except RedcapError:
            logging.error("Antud RedCapi API key ei võimalda andmebaasile ligipääsu.")
            raise APIKeyError

    def get_id(self, conditions: dict) -> list:
        """ Tagastab RedCapi andmebaasist kõikide tingimustele vastavate recordite redcap_id väärtused listina. """
        database_keys = list(conditions.keys())
        database_keys = database_keys.append("record_id") # Record_id väli on ka vajalik alla tõmmata, kuna seda hiljem returnime
        records = self.project.export_records(fields=database_keys) # Alguses tõmbame alla kõikide recordite meid huvitavad väljad
        results = []
        for record in records:
            is_included = True
            for key in conditions:
                if type(conditions[key]) is not list:
                    raise TypeError
                if record[key] not in conditions[key]:
                    is_included = False
            if is_included:
                results.append(record["record_id"])
        return results

    def download(self, redcap_id: int, fields: Optional[list] = None) -> dict:
        """ Laeb RedCapi serverist alla ühe uuritava infoväljad. """
        redcap_id = str(redcap_id)
        result =  self.project.export_records(records=[redcap_id,], fields=fields, export_data_access_groups=True)
        result = result[0]
        return result


    def upload(self, data: dict, redcap_id: int = None, confirm: bool = True, overwrite: bool = False):
        if redcap_id == None:
            redcap_id = data["record_id"]
        final_data = {}
        if confirm or not overwrite:
            original_data = self.download(redcap_id)
        for key in data:
            # If there already is data
            if str(original_data[key]) == str(data[key]):
                # No need to write in new data, as nothing is different
                continue
            # If there is no data to overwrite, then just write the new data in
            if original_data[key] == "":
                final_data[key] = data[key]
                continue
            if overwrite: # If overwrite is true, then just write over the original data
                final_data[key] = data[key]
                continue
            else: # If we don't want to blindly overwrite
                if confirm:
                    if self.ask_confirm(redcap_id, key, original_data[key], data[key]): # If user wants to overwrite
                        final_data[key] = data[key]
        if "record_id" not in final_data:
            final_data["record_id"] = redcap_id
        self.project.import_records([final_data])

    def ask_confirm(self, redcap_id, key, original, modified):
        print(f"RC: {redcap_id}, Key:\t {key}")
        print(f"Original:\t {original}")
        print(f"Modified:\t {modified}")
        print("Input Y/y to overwrite or N/n to not modify")
        while True:
            value = input()
            if value in ("Y", "y"):
                return True
            elif value in ("N", "n"):
                return False
            else:
                print("Please input Y/y or N/n to continue")






        


