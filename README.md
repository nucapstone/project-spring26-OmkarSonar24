## Project Title 
FinSights

## Project Name 
Customer – Transactions Activity & Spending Patterns

## Contributors 
Omkar Sonar

## Project Description 
### Stakeholder 
Sean Reardon <br>
Data & Analytics Manager <br>
Bangor Savings Bank
 
### Story 
Bank transactions record the rhythm of daily life and though masked and concise, they reveal a customer's habits, routines and financial behavior. Analyzing these patterns allows a bank to understand who their customers truly are, not just demographically, but behaviorally.
The initial goal of this project was fraud detection and anomaly analysis. However, early exploration revealed that making supervised fraud detection is not feasible. This led to a pivot toward customer segmentation and spending pattern prediction, a direction that provides measurable outcomes and concrete business value.
The project now aims to build a **customer intelligence system** that segments Bangor Savings Bank customers by their
transaction behavior and predicts spending pattern changes. This enables the bank **to identify customers who may be struggling financially** before their situation worsens, determine which customers are **good candidates for the bank's rewards program (Buoy Local)**, deliver **personalized cashback incentives** aligned with actual spending habits, and **promote local businesses** to relevant customer segments. This system can complement the bank's existing
recommendation engine with data-driven behavioral insights.
 
### Data 
#### Customer Demographics: 
276,838 records containing customer profiles including relationship tenure, various product types in use, active status.
![Customer data](/figs/customers_dt.png)

#### Customer Transactions: 
Around 8 million (8,234,091) debit card transaction records including merchant name and category, ATM address and location, transaction amount, date/time
Both datasets contain a customerID (masked) which serves as a linking identifier.
![Transactions data](/figs/transactions_dt.png)
