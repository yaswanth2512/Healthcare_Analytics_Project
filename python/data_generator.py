import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta

# Create Output Directory
print("Initializing Data Generation...")
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(output_dir, exist_ok=True)

fake = Faker()
Faker.seed(42)
np.random.seed(42)

# Constants for Generation
NUM_MEMBERS = 10000
NUM_PROVIDERS = 500
NUM_PLANS = 10
NUM_CLAIMS = 30000
NUM_PHARMACY = 15000
NUM_APPOINTMENTS = 20000

print(f"Generating realistic healthcare data into: {output_dir}")

# 1. GENERATE PLANS
plan_types = ['HMO', 'PPO', 'EPO', 'POS', 'Medicare Advantage', 'Medicaid']
plans_data = []
for i in range(1, NUM_PLANS + 1):
    plans_data.append({
        'plan_id': f"PLN{i:04d}",
        'plan_name': f"{fake.company()} {random.choice(plan_types)}",
        'plan_type': random.choice(plan_types),
        'monthly_premium': round(random.uniform(200.0, 900.0), 2),
        'deductible': random.choice([500, 1000, 2500, 5000])
    })
df_plans = pd.DataFrame(plans_data)
df_plans.to_csv(f"{output_dir}/plans.csv", index=False)

# 2. GENERATE MEMBERS
members_data = []
chronic_conditions = ['None', 'Diabetes', 'Hypertension', 'Asthma', 'COPD', 'Heart Disease']
for i in range(1, NUM_MEMBERS + 1):
    members_data.append({
        'member_id': f"MEM{i:06d}",
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'dob': fake.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=90),
        'gender': random.choice(['M', 'F']),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'plan_id': random.choice(df_plans['plan_id']),
        'chronic_condition_flag': random.choice(chronic_conditions),
        'enrollment_date': fake.date_between(start_date='-5y', end_date='today')
    })
df_members = pd.DataFrame(members_data)
# Calculate age
df_members['age'] = df_members['dob'].apply(lambda x: datetime.now().year - x.year)
df_members.to_csv(f"{output_dir}/members.csv", index=False)

# 3. GENERATE PROVIDERS
providers_data = []
specialties = ['General Practice', 'Cardiology', 'Orthopedics', 'Pediatrics', 'Neurology', 'Oncology', 'Emergency']
for i in range(1, NUM_PROVIDERS + 1):
    providers_data.append({
        'provider_id': f"PRV{i:05d}",
        'provider_npi': fake.unique.random_number(digits=10, fix_len=True),
        'provider_name': f"Dr. {fake.last_name()}",
        'specialty': random.choice(specialties),
        'clinic_name': fake.company() + " Clinic",
        'city': fake.city(),
        'state': fake.state_abbr(),
        'network_status': random.choice(['In-Network', 'Out-of-Network'])
    })
df_providers = pd.DataFrame(providers_data)
df_providers.to_csv(f"{output_dir}/providers.csv", index=False)

# 4. GENERATE CLAIMS
claims_data = []
claim_statuses = ['Approved', 'Denied', 'Pending', 'In Process']
rejection_reasons = ['None', 'Missing Prior Auth', 'Duplicate Claim', 'Coding Error', 'Not Covered']
diagnosis_codes = ['E11.9', 'I10', 'J45.909', 'I25.10', 'Z00.00', 'M54.5'] # Realistic ICD-10

for i in range(1, NUM_CLAIMS + 1):
    status = random.choices(claim_statuses, weights=[70, 15, 10, 5])[0]
    reason = 'None' if status in ['Approved', 'Pending', 'In Process'] else random.choice(rejection_reasons[1:])
    
    claims_data.append({
        'claim_id': f"CLM{i:08d}",
        'member_id': random.choice(df_members['member_id']),
        'provider_id': random.choice(df_providers['provider_id']),
        'service_date': fake.date_between(start_date='-2y', end_date='today'),
        'diagnosis_code': random.choice(diagnosis_codes),
        'claim_amount': round(random.uniform(100.0, 15000.0), 2),
        'approved_amount': 0.0, # Calculated next
        'claim_status': status,
        'rejection_reason': reason,
        'submission_date': '',
        'processing_date': ''
    })

df_claims = pd.DataFrame(claims_data)
df_claims['submission_date'] = df_claims['service_date'] + pd.to_timedelta(np.random.randint(1, 10, size=len(df_claims)), unit='d')
df_claims['processing_date'] = df_claims['submission_date'] + pd.to_timedelta(np.random.randint(1, 15, size=len(df_claims)), unit='d')

# Set approved amounts based on status
df_claims.loc[df_claims['claim_status'] == 'Approved', 'approved_amount'] = df_claims['claim_amount'] * random.uniform(0.6, 1.0)
df_claims['approved_amount'] = df_claims['approved_amount'].round(2)

# Introduce some logical SLA delays for Insights
df_claims['submission_date'] = pd.to_datetime(df_claims['submission_date'])
df_claims['processing_date'] = pd.to_datetime(df_claims['processing_date'])
df_claims['sla_days'] = (df_claims['processing_date'] - df_claims['submission_date']).dt.days

df_claims.to_csv(f"{output_dir}/claims.csv", index=False)

# 5. GENERATE PHARMACY
pharmacy_data = []
medications = ['Metformin', 'Lisinopril', 'Albuterol', 'Atorvastatin', 'Amphetamine', 'Amoxicillin']
for i in range(1, NUM_PHARMACY + 1):
    pharmacy_data.append({
        'rx_id': f"RX{i:07d}",
        'member_id': random.choice(df_members['member_id']),
        'prescribing_provider_id': random.choice(df_providers['provider_id']),
        'medication_name': random.choice(medications),
        'fill_date': fake.date_between(start_date='-1y', end_date='today'),
        'cost': round(random.uniform(10.0, 1000.0), 2),
        'copay': random.choice([0, 10, 20, 50]),
        'adherence_status': random.choice(['High', 'Medium', 'Low'])
    })
df_pharmacy = pd.DataFrame(pharmacy_data)
df_pharmacy.to_csv(f"{output_dir}/pharmacy.csv", index=False)

# 6. GENERATE APPOINTMENTS & SATISFACTION SCORES
appointments_data = []
for i in range(1, NUM_APPOINTMENTS + 1):
    appointments_data.append({
        'appointment_id': f"APT{i:07d}",
        'member_id': random.choice(df_members['member_id']),
        'provider_id': random.choice(df_providers['provider_id']),
        'appointment_date': fake.date_between(start_date='-2y', end_date='today'),
        'appointment_type': random.choice(['In-Person', 'Telehealth']),
        'satisfaction_score': random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 30, 40])[0]
    })
df_appointments = pd.DataFrame(appointments_data)
df_appointments.to_csv(f"{output_dir}/appointments.csv", index=False)

print(f"Data Generation Complete. Total files 6. Total rows: >50,000")
