import pandas as pd
import glob
import os
import logging

# Configure basic logging for ETL simulation
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def validate_data_quality():
    csv_files = glob.glob(f"{data_dir}/*.csv")
    if not csv_files:
        logging.error("No CSV files found. Please run data_generator.py first.")
        return

    logging.info("Starting Data Validation and Quality checks...")

    for file in csv_files:
        filename = os.path.basename(file)
        logging.info(f"--- Processing {filename} ---")
        try:
            df = pd.read_csv(file)
            
            # 1. Total Rows
            logging.info(f"Total Records: {len(df)}")
            
            # 2. Check Missing Values
            missing = df.isnull().sum()
            missing_cols = missing[missing > 0]
            if not missing_cols.empty:
                logging.warning(f"Missing Values detected:\n{missing_cols}")
            else:
                logging.info("No missing values detected.")
                
            # 3. Duplicate checks
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                logging.warning(f"Found {duplicates} duplicate rows. Dropping duplicates.")
                df = df.drop_duplicates()
            else:
                logging.info("No duplicate rows found.")
                
            # 4. Specific Business Logic Validation
            if filename == 'claims.csv':
                # Validate SLA Dates (Processing shouldn't be before Service)
                invalid_dates = df[df['processing_date'] < df['service_date']]
                if not invalid_dates.empty:
                    logging.error(f"Found {len(invalid_dates)} claims with processing date before service date!")
                else:
                    logging.info("SLA date sequence validated.")
                    
            if filename == 'members.csv':
                # Validate Age boundaries
                invalid_ages = df[(df['age'] < 0) | (df['age'] > 120)]
                if not invalid_ages.empty:
                    logging.error(f"Found {len(invalid_ages)} members with invalid age!")

            logging.info(f"Validation for {filename} completed successfully.\n")

        except Exception as e:
            logging.error(f"Error processing {filename}. Exception: {str(e)}")

if __name__ == "__main__":
    validate_data_quality()
