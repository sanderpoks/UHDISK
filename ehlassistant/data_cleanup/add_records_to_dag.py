from ehlassistant.ehlredcap import RedcapConnection

def main() -> None:
    global rc
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="./redcap_api_key")
    record_list = rc.download_multiple(fields=["record_id", "taustainfo_complete"])
    user_id_set = []
    free_dag_list = []
    for record in record_list:
        if record["redcap_data_access_group"] == "":
            free_dag_list.append(int(record["record_id"]))
        elif record["redcap_data_access_group"] not in user_id_set:
            user_id_set.append(record["redcap_data_access_group"])
    user_counts = dict()
    for i in user_id_set:
        user_counts[i] = 0
    for record in record_list:
        if record["taustainfo_complete"] == "0" and record["redcap_data_access_group"] != "":
            user_counts[record["redcap_data_access_group"]] += 1

    free_dag_list.remove(218) #Exception
    first_open_dag = min(free_dag_list)
    print(f"First open DAG is {first_open_dag}")
    dag_name = ask_dag(user_id_set, user_counts)
    upload_queue = create_dag_allocation(first_open=first_open_dag, amount=500, dag_name=dag_name)
    input()
    #rc.upload_multiple(upload_queue)

def ask_dag(user_id_set, user_counts):
    while True:
        print("Which user to add the records to:")
        for number, name in enumerate(user_id_set):
            print(f"{number} - {name} ({user_counts[name]})")
        print(f"Insert number from 0 to {len(user_id_set)-1}")
        answer = int(input())
        if not 0 <= answer <= (len(user_id_set)-1):
            continue
        else:
            dag = user_id_set[answer]
            return dag

def create_dag_allocation(first_open: int, amount: int, dag_name: str) -> list:
    return_list = []
    for i in range(first_open, first_open + amount):
        return_dict = {}
        return_dict["record_id"] = i
        return_dict["redcap_data_access_group"] = dag_name
        return_list.append(return_dict)
    return return_list

if __name__ == "__main__":
    main()
