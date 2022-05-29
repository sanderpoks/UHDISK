from ehlassistant.ehlredcap import RedcapConnection
from ehlassistant.ehl_scraper import Scraper, PreviousDiagnosisData, INITIAL_VALUE
from ehlassistant.ehlNavigeerimine import ehlMain
from datetime import date
from selenium.common.exceptions import TimeoutException

def main() -> None:
    global ehl
    ehl = ehlMain()
    global rc
    rc = RedcapConnection(url="https://redcap.ut.ee/api/", api_key_path="./redcap_api_key")
    id_list = rc.get_id({"auto_status": ["3","4"]})
    record_list = rc.download_multiple(redcap_id_list=id_list)
    empty_set = {"0", "", 0}
    problemrecords = [int(record["record_id"]) for record in record_list if (record["auto_earlier_diagnosis___1"] in empty_set and
        record["auto_earlier_diagnosis___2"] in empty_set and record["auto_earlier_diagnosis___3"] in empty_set)]
    scraper = Scraper(ehl)
    for record in (r for r in record_list if int(r["record_id"]) in problemrecords):
        data = PreviousDiagnosisData()
        hj_number = record["ref_num"]
        while True:
            try:
                ehl.navigeeri("haiguslugu", record["id_code"], hj_number)
                break
            except TimeoutException:
                continue
        hj_date = date(int(hj_number[:4]), int(hj_number[4:6]), int(hj_number[6:8]))
        data = scraper.scrape_varasemad_diagnoosid(data, hj_date)
        print(f"RC ID: {record['record_id']}")
        print(f"KOK/Astma: {data.kok_astma}")
        print(f"SP: {data.sydamepuudulikkus}")
        upload_queue = {}
        if data.kok_astma:
            upload_queue["auto_earlier_diagnosis___2"] = "1"
            if record["auto_status"] == "4":
                upload_queue["earlier_diagnosis___2"] = "1"
        if data.sydamepuudulikkus:
            upload_queue["auto_earlier_diagnosis___1"] = "1"
            if record["auto_status"] == "4":
                upload_queue["earlier_diagnosis___1"] = "1"
        if not data.kok_astma and not data.sydamepuudulikkus:
            upload_queue["auto_earlier_diagnosis___3"] = "1"
        rc.upload(data=upload_queue, redcap_id=record["record_id"], overwrite=True)


        
        

if __name__ == "__main__":
    main()
