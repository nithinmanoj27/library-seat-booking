import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine

# Database connection settings
DB_USER = "lsatuser"
DB_PASSWORD = "password123"
DB_NAME = "library_db"
DB_HOST = "localhost"
DB_PORT = 3306

# Connect to MySQL
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# 1️⃣ Extract - fetch data from tables
def extract_data():
    users = pd.read_sql("SELECT id, erp, name, email FROM user", engine)
    seats = pd.read_sql("SELECT id, label, status FROM seat", engine)
    bookings = pd.read_sql("SELECT id, seat_id, user_id, status, start_time, end_time, expires_at FROM booking", engine)
    return users, seats, bookings

# 2️⃣ Transform - clean + join data
def transform_data(users, seats, bookings):
    # Join bookings with users & seats
    df = bookings.merge(users, left_on="user_id", right_on="id", suffixes=("_booking", "_user"), how="left")
    df = df.merge(seats, left_on="seat_id", right_on="id", suffixes=("", "_seat"), how="left")

    # Calculate booking duration
    df["duration_minutes"] = (pd.to_datetime(df["end_time"]) - pd.to_datetime(df["start_time"])).dt.total_seconds() / 60
    df["duration_minutes"] = df["duration_minutes"].fillna(0)

    # Select useful columns
    final_df = df[[
        "id_booking", "erp", "name", "email", "label", "status",
        "start_time", "end_time", "duration_minutes"
    ]].rename(columns={
        "id_booking": "booking_id",
        "label": "seat_label"
    })

    return final_df

# 3️⃣ Load - save to CSV
def load_data(final_df):
    output_dir = "etl_output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "bookings_summary.csv")
    final_df.to_csv(output_file, index=False)
    print(f"✅ ETL pipeline completed. Data saved to {output_file}")

if __name__ == "__main__":
    users, seats, bookings = extract_data()
    final_df = transform_data(users, seats, bookings)
    load_data(final_df)
