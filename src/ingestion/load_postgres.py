import os

import pandas as pd
import psycopg
from  psycopg import sql

from config.settings import PROCESSED_DATA_DIR



COLUMN_MAPPING = {
    "Period": "period",
    "Org Code": "org_code",
    "Parent Org": "parent_org",
    "Org name": "org_name",
    "A&E attendances Type 1": "ae_attendances_type_1",
    "A&E attendances Type 2": "ae_attendances_type_2",
    "A&E attendances Other A&E Department": "ae_attendances_other_department",
    "A&E attendances Booked Appointments Type 1": "ae_booked_appointments_type_1",
    "A&E attendances Booked Appointments Type 2": "ae_booked_appointments_type_2",
    "A&E attendances Booked Appointments Other Department": "ae_booked_appointments_other_department",
    "Attendances over 4hrs Type 1": "attendances_over_4hrs_type_1",
    "Attendances over 4hrs Type 2": "attendances_over_4hrs_type_2",
    "Attendances over 4hrs Other Department": "attendances_over_4hrs_other_department",
    "Attendances over 4hrs Booked Appointments Type 1": "over_4hrs_booked_type_1",
    "Attendances over 4hrs Booked Appointments Type 2": "over_4hrs_booked_type_2",
    "Attendances over 4hrs Booked Appointments Other Department": "over_4hrs_booked_other_department",
    "Patients who have waited 4-12 hs from DTA to admission": "dta_wait_4_to_12hrs",
    "Patients who have waited 12+ hrs from DTA to admission": "dta_wait_12plus_hrs",
    "Emergency admissions via A&E - Type 1": "emergency_admissions_type_1",
    "Emergency admissions via A&E - Type 2": "emergency_admissions_type_2",
    "Emergency admissions via A&E - Other A&E department": "emergency_admissions_other_department",
    "Other emergency admissions": "other_emergency_admissions",
}

def prepare_data() -> pd.DataFrame:
    """Read and Validate all cleaned Nhs A&E csv files"""

    files=sorted(PROCESSED_DATA_DIR.glob("ae_*_clean.csv"))

    if not files:
        raise FileNotFoundError("no cleaned nhs files found")


    frames=[]


    for file in files:
        df=pd.read_csv(file)



        missing=set(COLUMN_MAPPING)-set(df.columns)

        if missing:
             raise ValueError(
              f"{file.name} is missing columns:{sorted(missing)}"
            )

        frames.append(df[list(COLUMN_MAPPING)])
    combined=pd.concat(frames,ignore_index=True)

    if combined.isna().any().any():
        raise ValueError("missing values found in nhs data")
    if combined.duplicated(subset=["Period","Org Code"]).any():
        raise ValueError("Duplicate period and organisation code found")
    combined=combined.rename(columns=COLUMN_MAPPING)

    return combined


def load_to_postgres(df:pd.DataFrame)->int:
    """"Insert NHS recordes into PostgreSql without duplicating keys"""

    columns=list(COLUMN_MAPPING.values())

    insert_query=sql.SQL("""
        INSERT INTO staging.ae_attendances({columns})
        VALUES ({placeholders})
        ON CONFLICT(period,org_code) DO NOTHING


""").format(
    columns=sql.SQL(",").join(
          sql.Identifier(column) for column in columns


    ),
    placeholders=sql.SQL(",").join(
        sql.Placeholder() for _ in columns
    ),


)


    rows = [
        tuple(
            str(value) if index < 4 else int(value)
            for index, value in enumerate(row)
        )
        for row in df[columns].itertuples(index=False, name=None)
    ]

    with psycopg.connect(
        dbname=os.getenv("PGDATABASE", "nhs_ae"),
        host=os.getenv("PGHOST", "localhost"),
    ) as conn:
        with conn.cursor() as cursor:
            cursor.executemany(insert_query, rows)
            inserted = cursor.rowcount

    return inserted

def main() -> None:
    df = prepare_data()

    print(f"Prepared {len(df)} NHS records")

    inserted = load_to_postgres(df)

    print(f"Inserted {inserted} new records into PostgreSQL")


if __name__ == "__main__":
    main()