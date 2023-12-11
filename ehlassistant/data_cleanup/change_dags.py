from ehlassistant.ehlredcap import RedcapConnection

def main() -> None:
    global rc
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="./redcap_api_key")
    record_list = rc.download_multiple(fields=["record_id", "taustainfo_complete"])
    dag_set = []
    for record in record_list:
        if record["redcap_data_access_group"] not in dag_set and record["redcap_data_access_group"] != "":
            dag_set.append(record["redcap_data_access_group"])
    record_dict = {}
    for i in dag_set:
        record_dict[i] = []
    for record in record_list:
        if record["taustainfo_complete"] == "0":
            record_dict[record["redcap_data_access_group"]].append(record["record_id"])
    for i in record_dict:
        print(f"{i} - {(len(record_dict[i]))}")
    
    source_dag = select_dag("Vali source DAG", dag_set)
    dest_dag = select_dag("Vali destination DAG", dag_set)
    amount = ask_amount(len(record_dict[source_dag]))
    upload_queue = []
    print(f"Kanname üle {source_dag}-ilt {dest_dag}-ile {amount} ankeeti")
    for i in range(1, amount+1):
        record_id = record_dict[source_dag].pop()
        print(f"Ülekanne {i} - {record_id}")
        return_dict = create_return_dict(record_id, dest_dag)
        upload_queue.append(return_dict)
    rc.upload_multiple(upload_queue)

def select_dag(message, dag_set):
    while True:
        print(message)
        answer = input()
        if answer in dag_set:
            return answer

def ask_amount(max):
    print(f"Mitu ankeeti üle kanda? (max {max})")
    while True:
        answer = int(input())
        if 0 < answer <= max:
            return answer

def create_return_dict(record_id, dag):
    return_dict = {}
    return_dict["record_id"] = record_id
    return_dict["redcap_data_access_group"] = dag
    return return_dict


if __name__ == "__main__":
    main()