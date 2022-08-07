from ehlassistant.ehlredcap import RedcapConnection
import pickle
from ehlassistant.descriptors import descriptors
from ehlassistant.ehlreorder import order_sequence

def main() -> None:
    global rc
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="./redcap_api_key")
    records = rc.download_multiple()
    records = [record for record in records if record["taustainfo_complete"] == "0" and record["auto_status"] == "3"]
    updated_record_list = []
    for record in records:
        upload_queue = {}
        print("### ",record["record_id"], " ###")
        upload_queue = {**upload_queue, **fix_diagnoses(record)}
        for i in upload_queue:
            record[i] = upload_queue[i] #Update local copy
        upload_queue = {**upload_queue, **copy_auto(record)}
        upload_queue["auto_status"] = "4"
        upload_queue["record_id"] = record["record_id"]
        updated_record_list.append(upload_queue)
        #rc.upload(data=upload_queue, redcap_id=rc_id, overwrite=True)
        #break
    input()
    rc.upload_multiple(updated_record_list)

def fix_diagnoses(record: dict) -> None:
    if record["auto_diag"]:
        diagnosis_set = eval(record["auto_diag"])
    else:
        diagnosis_set = set()
    diagnosis_codes = pickle.load(open("ehlassistant/diagnoses_rhk.pickle", "rb"))
    upload_queue = {}
    for i in range(1,25):
        key = "non_uhdisk_diag___" + str(i)
        auto_key = "auto_non_uhdisk_diag___" + str(i)
        if record[auto_key] == "0":
            if diagnosis_set & diagnosis_codes[key]:
                upload_queue[auto_key] = "1"
                print(f"Updating - {record['record_id']} - {descriptors[key]}")
    for i in range(1,9):
        key = "uhdisk_diag___" + str(i)
        auto_key = "auto_uhdisk_diag___" + str(i)
        if record[auto_key] == "0":
            if diagnosis_set & diagnosis_codes[key]:
                upload_queue[auto_key] = "1"
                print(f"Updating - {record['record_id']} - {descriptors[key]}")
    return upload_queue

def copy_auto(record: dict) -> None:
    key_list = {"red_trauma___1", "ph", "ph_resp_qual", "ph_resp_quan", "ph_spo2", "ph_sys", "ph_dia", "ph_hr", "ph_temp", "emo_triage", "emo_resp_qual", "emo_resp_quan", "emo_spo2", "emo_sys", "emo_dia", "emo_hr", "emo_temp", "earlier_diagnosis___1", "earlier_diagnosis___2", "uhdisk_exist", "uhdisk_diag___1", "uhdisk_diag___2", "uhdisk_diag___3", "uhdisk_diag___4", "uhdisk_diag___5", "uhdisk_diag___6", "uhdisk_diag___7", "uhdisk_diag___8", "non_uhdisk_diag___1", "non_uhdisk_diag___2", "non_uhdisk_diag___3", "non_uhdisk_diag___4", "non_uhdisk_diag___5", "non_uhdisk_diag___6", "non_uhdisk_diag___7", "non_uhdisk_diag___8", "non_uhdisk_diag___9", "non_uhdisk_diag___10", "non_uhdisk_diag___11", "non_uhdisk_diag___12", "non_uhdisk_diag___13", "non_uhdisk_diag___14", "non_uhdisk_diag___15", "non_uhdisk_diag___16", "non_uhdisk_diag___17", "non_uhdisk_diag___18", "non_uhdisk_diag___19", "non_uhdisk_diag___20", "non_uhdisk_diag___21", "non_uhdisk_diag___22", "non_uhdisk_diag___23", "non_uhdisk_diag___24", "diag_covid", "hospitalised", "hospitalised_duration", "icu", "icu_duration", "hospitalised_death"}
    upload_queue = {}
    for key in key_list:
        auto_key = "auto_" + key
        if record[auto_key] in ["", "0"]:
            continue
        if record[key] in ["", "0"]:
            upload_queue[key] = record[auto_key]
        else:
            if record[key] == record[auto_key]:
                continue
            if key == "ph" or key == "hospitalised":
                continue
            print(f"Key {key} is already filled")
            input()
    return upload_queue




if __name__ == "__main__":
    main()
