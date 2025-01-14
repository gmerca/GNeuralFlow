# -*- coding: utf-8 -*-
"""prescriptions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DzrnnVPyL9TW0DuaRUMgI8b-5ZSCZj6U

# MIMIC 4 data - dataset construction prescriptions

Code taken from GRU-ODE-Bayes preprocessing; simplified and adapted for MIMIC 4 1.0
"""

import pandas as pd
import torch
import os

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 300)

data_path = 'nfe/experiments/data/physionet.org/files/mimiciv/2.2'

hos = f'{data_path}/hosp'
icu_path = f'{data_path}/icu'
out_path = 'nfe/experiments/data'
proc_path = f'{out_path}/mimic4_processed'
os.makedirs(proc_path, exist_ok=True)

adm = pd.read_csv(f"{proc_path}/admissions_processed.csv")
adm.head()

# only choose previously selected admission ids
presc = pd.read_csv(f"{hos}/prescriptions.csv.gz")
adm_ids = list(adm["hadm_id"])
presc = presc.loc[presc["hadm_id"].isin(adm_ids)]

print("Number of patients remaining in the database: ")
print(presc["subject_id"].nunique())
presc.tail()

# Select entries whose drug name is in the list from the paper.
drugs_list = ["Acetaminophen", "Aspirin", "Bisacodyl", "Insulin", "Heparin", "Docusate Sodium", "D5W",
              "Humulin-R Insulin", "Potassium Chloride", "Magnesium Sulfate", "Metoprolol Tartrate",
              "Sodium Chloride 0.9%  Flush", "Pantoprazole"]
presc2 = presc.loc[presc["drug"].isin(drugs_list)]

print("Number of patients remaining in the database: ")
print(presc2["subject_id"].nunique())

print(presc2.groupby("drug")["dose_unit_rx"].value_counts())

# Units correction
presc2 = presc2.drop(presc2.loc[presc2["dose_unit_rx"].isnull()].index).copy()
presc2 = presc2.drop(presc2.loc[(presc2["drug"] == "Acetaminophen") & (presc2["dose_unit_rx"] != "mg")].index).copy()
presc2.loc[(presc2["drug"] == "D5W") & (presc2["dose_unit_rx"] == "ml"), "dose_unit_rx"] = "mL"
presc2 = presc2.drop(presc2.loc[(presc2["drug"] == "D5W") & (presc2["dose_unit_rx"] != "mL")].index).copy()
presc2 = presc2.drop(presc2.loc[(presc2["drug"] == "Heparin") & (presc2["dose_unit_rx"] != "UNIT")].index).copy()
presc2 = presc2.drop(presc2.loc[(presc2["drug"] == "Insulin") & (presc2["dose_unit_rx"] != "UNIT")].index).copy()
presc2 = presc2.drop(
    presc2.loc[(presc2["drug"] == "Magnesium Sulfate") & (presc2["dose_unit_rx"] != "gm")].index).copy()
presc2 = presc2.drop(
    presc2.loc[(presc2["drug"] == "Potassium Chloride") & (presc2["dose_unit_rx"] != "mEq")].index).copy()
presc2.loc[(presc2["drug"] == "Sodium Chloride 0.9%  Flush") & (presc2["dose_unit_rx"] == "ml"), "dose_unit_rx"] = "mL"
presc2 = presc2.drop(presc2.loc[(presc2["drug"] == "Bisacodyl") & (presc2["dose_unit_rx"] != "mg")].index).copy()
presc2 = presc2.drop(presc2.loc[(presc2["drug"] == "Pantoprazole") & (presc2["dose_unit_rx"] != "mg")].index).copy()
print(presc2.groupby("drug")["dose_unit_rx"].value_counts())

# To avoid confounding labels with labels from other tables, we add "drug" to the name
presc2['charttime'] = pd.to_datetime(presc2["starttime"], format='%Y-%m-%d %H:%M:%S')
presc2["drug"] = presc2["drug"] + " Drug"

presc2.to_csv(f"{proc_path}/prescriptions_processed.csv")
print('done')

