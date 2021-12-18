import os
import json
from sqlite import SQLite


db_driver = SQLite.get_driver("./", "database.db")

folder = input("please enter folder name to save db data >>>")
os.makedirs(folder)

tables = ["user", "userDetails", "logs", "userAppointment", "doctorDetails",
          "specializations"]

for table in tables:
    data = db_driver.read(table, "*")
    file = os.path.join(folder, f"{table}.json")

    if data and len(data) > 0:
        with open(file, "w") as f:
            json.dump(data, f)
        print(f"[INFO] {len(data)} records saved for '{table}'")

    else:
        print(f"[INFO] no data found for '{table}'")
