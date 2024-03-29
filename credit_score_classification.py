# -*- coding: utf-8 -*-
"""Credit Score Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ldv-XMZ5TeE-u0PJxA_ftxOzFI0cMylK
"""

import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('/content/drive/MyDrive/Credit Score classification/train.csv')

df.head(10)

df.info()

"""

1.   Age:
Correct the age values by using the mode after doing a regex cleanup for non numeric values.
2.   Annual Income:
Use mode after regex cleanup values.
3.   


"""

df['Age'] = df.Age.apply(lambda a: re.findall(r'\d+',a)[0])
df['Age'] = df.groupby('Customer_ID')['Age'].transform(lambda x: x.mode()[0]).astype('int')

df['Annual_Income'] = df['Annual_Income'].apply(lambda a: re.findall(r'\d+.\d+', a)[0]).astype('float')

df['Monthly_Inhand_Salary'] = df.groupby('Customer_ID')['Monthly_Inhand_Salary'].transform(lambda x: x.mode()[0])

df['Num_of_Loan'] = df.Num_of_Loan.apply(lambda a: re.findall(r'\d+',a)[0])
df['Num_of_Loan'] = df.groupby('Customer_ID')['Num_of_Loan'].transform(lambda x: x.mode()[0]).astype('int')

df['loan_type_count'] = df['Type_of_Loan'].apply(lambda x: 0 if pd.isna(x) else len(x.split(', ')))

pattern_1 = r'(\w+)_spent'
a = df['Payment_Behaviour'].apply(lambda x: re.findall(pattern_1, x))
df['pb_spent'] = a.apply(lambda x: x[0] if len(x) > 0 else np.nan).astype('str')

pattern_2 = r'_spent_(\w+)_value_payments'
a = df['Payment_Behaviour'].apply(lambda x: re.findall(pattern_2, x))
df['pb_value_pmnts'] = a.apply(lambda x: x[0] if len(x) > 0 else np.nan).astype('str')

dummies = pd.get_dummies(df['pb_spent'], prefix = 'pb_spent')[['pb_spent_High', 'pb_spent_nan']]
df = pd.concat([df,dummies], axis=1)

dummies = pd.get_dummies(df['pb_value_pmnts'], prefix = 'pb_value_pmnts')
df = pd.concat([df,dummies], axis=1)

df.head()

# Checking if there is any parity in Occupation-wise credit score performance
a = df.groupby('Occupation')['Credit_Score'].value_counts()*100/df.groupby('Occupation')['Credit_Score'].count()
catplot = sns.catplot(data=a,x='Occupation',hue='Credit_Score')
catplot.set_xticklabels(rotation=90)
plt.show()

"""No identifiable difference between occupation and credit score. Shall drop the column for simplicity sake."""

dummies = pd.get_dummies(df['Payment_of_Min_Amount'], prefix = 'p_min_amt')
df = pd.concat([df,dummies], axis=1)

month_to_int = {
    'january': 1,
    'february': 2,
    'march': 3,
    'april': 4,
    'may': 5,
    'june': 6,
    'july': 7,
    'august': 8,
    'september':9,
    'october':10,
    'november':11,
    'december':12
}
df['Month'] = df['Month'].str.lower().map(month_to_int)

a = df['Changed_Credit_Limit'].apply(lambda x: re.findall(r'\d+.\d+', x))
df['Changed_Credit_Limit'] = a.apply(lambda x: float(x[0]) if len(x) > 0 else 0)

df['Credit_Mix'] = df['Credit_Mix'].replace({'_':'Unknown'})
dummies = pd.get_dummies(df['Credit_Mix'], prefix = 'Credit_Mix')
df = pd.concat([df,dummies], axis=1)

df['Outstanding_Debt'] = df['Outstanding_Debt'].apply(lambda x: float(re.findall(r'\d+.\d+', x)[0]))

def ch_age(row):
  ch_age_pattern = r'(\d+) Years and (\d+) Months'
  if pd.isna(row):
    return np.nan
  tup = re.findall(ch_age_pattern, row)[0]
  age = 12*int(tup[0])+int(tup[1])
  return age

df['Credit_History_Age'] = df['Credit_History_Age'].apply(lambda row: ch_age(row)).fillna(method='ffill')

# Handling odd value
df['inv_unknown'] = (df['Amount_invested_monthly'] == '__10000__').astype(int)

# For other float values
a = df['Amount_invested_monthly'].apply(lambda x: re.findall(r'\d+.\d+', str(x)))
df['Amount_invested_monthly'] = a.apply(lambda x: float(x[0]) if len(x) > 0 else 0)

# Converting Balance to float
a = df['Monthly_Balance'].apply(lambda x: re.findall(r'\d+.\d+', str(x)))
df['Monthly_Balance'] = a.apply(lambda x: float(x[0]) if len(x) > 0 else np.nan)

# Marking Unknown balance
df['Monthly_Bal_Unknown'] = pd.isna(df['Monthly_Balance']).astype(int)

# Filling 0 for unknown values
df['Monthly_Balance'] = df['Monthly_Balance'].fillna(0)

a = df['Num_of_Delayed_Payment'].fillna(method = 'ffill').apply(lambda x: re.findall(r'\d+', str(x)))
b = a.apply(lambda x: int(x[0]) if len(x) > 0 else 0)

# Cutting off Max number of dalyed payments at 36
df['Num_of_Delayed_Payment'] = b.apply(lambda x: x if x <= 36 else 36)

# Marking off Higher freq delayed payments separately
df['High_freq_delayed_pymnt'] = (b > 36).astype(int)

df['Num_Credit_Inquiries'] = df['Num_Credit_Inquiries'].fillna(0)

drop = ['ID','Customer_ID','Name', 'SSN', 'Occupation','Type_of_Loan','pb_spent','pb_value_pmnts', 'Payment_of_Min_Amount','Credit_Mix', 'Payment_Behaviour','Num_of_Delayed_Payment']

"""**Training Model**"""

X = df.drop(columns=drop)
y = X.pop('Credit_Score')

X.info()

