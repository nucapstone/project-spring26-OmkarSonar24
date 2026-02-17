## This is to track data quality issues --
**Original Source :** /data/raw
**Cleaned files source  :** /data/processed
### Customers Data
1. 2 empty rows in excel sheet which were removed during cleaning. 

2. Duplicate CustomerID - BSB004527
![Duplicate customerID](/figs/duplicatecustomer.png)

3. Non-individual customers with gender values - 
![Gender analysis](/figs/genderdoubt.png)

### Transactions Data
1. Additional Commas in csv file under 'Merchant_Name' column. That is resolved now.

2. Missing Headers -- added

3. SQL Server Metadata - '(8234091 rows affected)' in the file which was removed.

---

*Last updated: 2026-02-02*