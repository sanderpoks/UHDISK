# -*- coding: UTF-8 -*-
from ehlassistant.ehlredcap import RedcapConnection
from ehlassistant.ehlNavigeerimine import ehlMain
import ehlassistant.descriptors
from tabulate import tabulate
import pickle

def main():
    global diagnosis_list
    diagnosis_list = pickle.load(open("ehlassistant/diagnoses_rhk.pickle", "rb"))
    global diag_dict
    diag_dict = ehlassistant.descriptors.descriptors
#    [print(key, ":", value) for key,value in diagnosis_list.items()]
    global rc
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="redcap_api_key")
    global ehl
    ehl = ehlMain()
    ehl.ava()
    ehl.navigeeri("logi_sisse")
    id_list = rc.get_id({"auto_status":["3"], "taustainfo_complete":["1","2"], "quality___1":["0"]})
    #id_list = rc.get_id({"auto_status":["3"], "taustainfo_complete":["1","2"], "quality___1":["1"]}) # Going over already checked records
    #id_list = [286]
    for rc_id in id_list:
        print(f"\n###\t{rc_id}\t###")
        upload = solve_conflicts(rc, int(rc_id))
        if upload:
            upload["record_id"] = rc_id
            [print(key,":",value) for key,value in upload.items()]
#            raise Exception("Just stopping for a bit")
            rc.upload(upload, confirm=True, overwrite=True)

        

def solve_conflicts(rc: RedcapConnection, rc_id: int) -> dict:
    record = rc.download(rc_id)
    upload_queue = {}
    # Elulised näitajad 
    if record["ph"] == "2" and record["auto_ph"] == 2:
        keys =  {"emo_resp_qual", "emo_resp_quan", "emo_spo2", "emo_sys", "emo_dia", "emo_hr", "emo_temp"}
    else:
        keys = {"ph_resp_qual", "ph_resp_quan", "ph_spo2", "ph_sys", "ph_dia", "ph_hr", "ph_temp", "emo_resp_qual", "emo_resp_quan", "emo_spo2", "emo_sys", "emo_dia", "emo_hr", "emo_temp"}
    for vital in keys:
        result = compare_vital(record=record, key=vital)
        if result:
            upload_queue = {**upload_queue, **result}
    # Diagnoosid
    keys = {"earlier_diagnosis": 3, "uhdisk_diag": 8, "non_uhdisk_diag": 24}
    for i in keys:
        result = compare_multi(record=record, key=i, max_iter=keys[i])
        if result:
            upload_queue = {**upload_queue, **result}
    # Kõik mis järgi jääb
    keys = {"emo_triage", "uhdisk_exist", "diag_covid", "hospitalised", "hospitalised_duration", "icu", "icu_duration", "hospitalised_death"}
    for i in keys:
        result = compare_radio(record=record, key=i)
        if result:
            upload_queue = {**upload_queue, **result}
    return upload_queue

def compare_radio(record: dict, key: str) -> dict:
    key1 = key
    key2 = "auto_" + key
    if record[key1] != record[key2]:
        if record[key1] == "":
            return {key1: record[key2], "quality___1": "1"}
        print(tabulate([[key1, record[key1], record[key2]]], headers=["Key", "Original", "Modified"], numalign="center", stralign="center") + "\n")
        if ask_keep_original(record):
            return {"quality___1":"1"} # Kui jätame originaali kehtima, siis märgime quality tagi ära, et pärast uuesti sama ei küsiks
        else:
            return {key1: record[key2], "quality___1": "1", "quality_fixed___1": "1"}


def compare_multi(record: dict, key: str, max_iter: int) -> dict:
    key1 = key
    key2 = "auto_" + key
    value_list = []
    returnvalue = {}
    for i in range(1, max_iter+1):
        key_num1 = key1 + "___" + str(i)
        key_num2 = key2 + "___" + str(i)
        if record[key_num2] == "0":
            auto_diag_set = eval(record["auto_diag"])
            if "earlier_diagnosis" in key_num1:
                print(f"Skipping evaluation of {key_num1}")
            elif diagnosis_list[key_num1] & auto_diag_set:
                print(f"Key for {diag_dict[key_num1]} should be set according to diagnosis codes - {auto_diag_set}")
                record[key_num2] = "1"
                returnvalue[key_num2] = "1"
            elif record[key_num1] == "1": #Manual diagnosis is set but auto is not, chance to add RHK code to auto detection
                ask_add_diagnosis(record, key_num1)
        value_list.append([key_num1, record[key_num1], record[key_num2]])
    if is_different_multi(value_list):
        multi_tabulate_diff(value_list, key1)
        if ask_keep_original(record):
            returnvalue =  {**returnvalue, "quality___1":"1"} # Kui jätame originaali kehtima, siis märgime quality tagi ära, et pärast uuesti sama ei küsiks
        else:
            for i in value_list:
                if i[1] != i[2]:
                    if i[2] == "":
                        i[2] = "0"
                    returnvalue[i[0]] = i[2]
            returnvalue =  {**returnvalue, "quality___1": "1", "quality_fixed___1": "1"}
    return returnvalue

def ask_add_diagnosis(record: dict, key: str) -> None:
    redcap_diagnosis_set = eval(record["auto_diag"])
    redcap_diagnosis_list = list(redcap_diagnosis_set)
    print(f"Diagnosis {diag_dict[key]} is set. Diagnosis codes are {redcap_diagnosis_set}.\nWould you like to associate one of the codes with {diag_dict[key]}?")
    while True:
        result = input()
        if result in ["Y", "y"]:
            if len(redcap_diagnosis_list) == 1:
                add_diagnosis_code(key=key, code=redcap_diagnosis_list[0])
                return
            print(f"Select, which code do you want to associate with {diag_dict[key]}")
            for index, code in enumerate(redcap_diagnosis_list, start=0):
                print(index, " - ", code)
            while True:
                result = input()
                if 0 <= int(result) < len(redcap_diagnosis_list):
                    add_diagnosis_code(key=key, code=redcap_diagnosis_list[int(result)])
                    return
                else:
                    print(f"Enter number between 0 and {len(redcap_diagnosis_list)-1}")
                    continue
        elif result in ["N", "n"]:
            return None
        elif result in ["E", "e"]:
            ehl.navigeeri("haiguslugu", record["id_code"], record["ref_num"])
        else:
            print("Enter Y/y or N/n or e/E for navigation")
            continue

def add_diagnosis_code(key: str, code: str) -> None:
    current_set = diagnosis_list[key]
    print(f"Old set: {current_set}")
    current_set.add(code)
    print(f"New set: {current_set}")
    diagnosis_list[key] = current_set
    pickle.dump(diagnosis_list,open("ehlassistant/diagnoses_rhk.pickle", "wb"))


def multi_tabulate_diff(value_list: list, key: str) -> None:
    table_list = []
    for i in value_list:
        if i[1] != i[2]:
            table_list.append([diag_dict[i[0]], i[1], i[2]])
    print(tabulate(table_list, headers=["Diag", "Original", "Modified"], numalign="center", stralign="center") + "\n")

def is_different_multi(value_list: list) -> bool:
    result = False
    for i in value_list:
        if i[1] != i[2]:
            result = True
    return result

def compare_vital(record: dict, key: str) -> dict:
    vital1 = key
    vital2 = "auto_" + key
    vital1_missing = key + "_missing___1"
    vital2_missing = "auto_" + key + "_missing___1"
    if record[vital1] != record[vital2] or record[vital1_missing] != record[vital2_missing]: # Kui manuaal ja auto ei matchi
        if vital1 in ["ph_temp", "emo_temp"]: # temperatuuri korral loeme võrdseks sõltumata kas komakoht on, nt 36.0 = 36
            if record[vital1] != "" and record[vital2] != "":
                if float(record[vital1]) == float(record[vital2]):
                    return
        if record[vital1] == "" and record[vital2] == "" and record[vital1_missing] == "0" and record[vital2_missing] == "1": # Missing on märkimata
            return {vital1: record[vital2], vital1_missing: record[vital2_missing], "quality___1":"1"}
        table = [[vital1, record[vital1], record[vital2]], [vital1_missing, record[vital1_missing], record[vital2_missing]]]
        print(tabulate(table, headers=["Key", "Original", "Auto"], numalign="center", stralign="center") + "\n")
        if ask_keep_original(record):
            return {"quality___1":"1"} # Kui jätame originaali kehtima, siis märgime quality tagi ära, et pärast uuesti sama ei küsiks
        else:
            return {vital1: record[vital2], vital1_missing: record[vital2_missing], "quality___1" : "1", "quality_fixed___1" : "1"} # Kui parandame, siis märgime lisaks qualitile ka quality_fixed

def ask_keep_original(record: dict) -> bool:
    while True:
        print("y/Y to keep original, n/N to overwrite original with auto version, e/E to navigate to record, u/U - user, i/I - ID, d/D - diag")
        answer = input()
        if answer in ["y", "Y"]:
            return True
        if answer in ["n", "N"]:
            return False
        if answer in ["e", "E"]:
           print(f"Navigating to {record['record_id']}...") 
           ehl.navigeeri("haiguslugu", record["id_code"], record["ref_num"])
           ehl.navigeeri("paevik")
        if answer in ["u", "U"]:
            print(record["entry_username"])
        if answer in ["i", "I"]:
            print(record["id_code"])
        if answer in ["d", "D"]:
            print(record["auto_diag"])
        else:
            print("Please answer y/Y or n/N")
            continue
    


    


if __name__ == "__main__":
    main()
