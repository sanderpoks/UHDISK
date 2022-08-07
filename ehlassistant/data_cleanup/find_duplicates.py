from ehlassistant.ehlredcap import RedcapConnection
import copy

def main() -> None:
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="./redcap_api_key")
    print("Download 1")
    records = rc.download_multiple()
    r = records[0]
    keys = r.keys()
    auto_list = [x for x in keys if "auto_" in x]
    auto_list.append("record_id")
    exceptions = ("record_id", "redcap_data_access_group")
    print("Download 2")
    records = rc.download_multiple(fields=auto_list)
    print("Downloads complete")
    records_dupl = []
    records_uniq = []
    records_copy = copy.deepcopy(records)
    for record in records_copy:
        rc_id = record["record_id"]
        record.pop("record_id")
        record.pop("redcap_data_access_group")
        if record not in records_uniq:
            records_uniq.append(record)
            print(f"N {rc_id}")
        else:
            records_dupl.append(record)
            print(f"D {rc_id}")
    print(f"Duplicates: {len(records_dupl)}")
    result = set()
    for i in records_dupl:
        current_result = []
        for record in records:
            if i.items() <= record.items():
                current_result.append(int(record["record_id"]))
                print(f"Dupe append - {record['record_id']}")
        result.add(str(current_result))
    print(result)
    f = open("duplicates.txt", "w")
    f.write(result)
    f.close()


if __name__ == "__main__":
    main()
