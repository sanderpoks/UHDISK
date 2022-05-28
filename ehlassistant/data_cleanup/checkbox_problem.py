# -*- coding: UTF-8 -*-
from ehlassistant.ehlredcap import RedcapConnection

def main():
    #global rc
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="edcap_api_key")
    id_list = rc.get_id({"auto_status":["3"]})
    problematic_id_list = get_problematic(rc, id_list)
    #a = get_problematic(rc, ["736"])
    print(problematic_id_list)

def get_problematic(rc: RedcapConnection, id_list: list) -> list:
    """ Downloads the records and filters out the ones that suffer from the problem """
    problematic_records = []
    records = rc.download_multiple(id_list)
    print(len(records))
    for r in records:
        if is_problematic(r):
            problem_record = r["record_id"]
#            print(f"{problem_record} is a problematic record")
            problematic_records.append(problem_record)
#        else:
#            print(f"{r['record_id']} is a good record")
    return problematic_records

def is_problematic(record:dict) -> bool:
    result = False
    upload_list = {}
    for i in (
            {"auto_ph_resp_qual_missing___1", "auto_ph_resp_qual"},
            {"auto_ph_resp_quan_missing___1", "auto_ph_resp_quan"},
            {"auto_ph_spo2_missing___1", "auto_ph_spo2"},
            {"auto_ph_sys_missing___1", "auto_ph_sys"},
            {"auto_ph_dia_missing___1", "auto_ph_dia"},
            {"auto_ph_hr_missing___1", "auto_ph_hr"},
            {"auto_ph_temp_missing___1", "auto_ph_temp"},
            {"auto_emo_triage"},
            {"auto_emo_resp_qual_missing___1", "auto_emo_resp_qual"},
            {"auto_emo_resp_quan_missing___1", "auto_emo_resp_quan"},
            {"auto_emo_spo2_missing___1", "auto_emo_spo2"},
            {"auto_emo_sys_missing___1", "auto_emo_sys"},
            {"auto_emo_dia_missing___1", "auto_emo_dia"},
            {"auto_emo_hr_missing___1", "auto_emo_hr"},
            {"auto_emo_temp_missing___1", "auto_emo_temp"},
            {"auto_earlier_diagnosis___1", "auto_earlier_diagnosis___2", "auto_earlier_diagnosis___3"},
            {"auto_hospitalised"}
            ):
        if not one_filled(record=record, group=i):
            result = True
    return result

def one_filled(record:dict, group:set):
    result = False
    for i in group:
        if record[i] not in (0, "0", ""):
            result = True
    if not result:
        print(record["record_id"])
        for i in group:
            print(f"{i} = {record[i]}")
        print("\n")
    return result




if __name__ == "__main__":
    main()
