from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from app.prediction_helper import predict

app = FastAPI()

class Creditinput(BaseModel):
    age: int
    income: float
    loan_amount: float
    loan_tenure_months: int
    avg_dpd_per_delinquency: float
    delinquency_ratio: float
    credit_utilization_ratio: float
    num_open_accounts: int
    residence_type: str
    loan_purpose: str
    loan_type: str

class CreditOutput(BaseModel):
    probability: float
    credit_score: int
    rating: str
 
    
    
@app.post("/predict_credit_risk", response_model=CreditOutput)
def predict_credit_risk(input_data: Creditinput):
    # Call the predictive helper function
    probability, credit_score, rating = predict(input_data.age, input_data.income, input_data.loan_amount, input_data.loan_tenure_months,
                                                input_data.avg_dpd_per_delinquency, input_data.delinquency_ratio,
                                                input_data.credit_utilization_ratio, input_data.num_open_accounts,
                                                input_data.residence_type, input_data.loan_purpose, input_data.loan_type)

    # Return the prediction results
    return CreditOutput(
        probability=probability,
        credit_score=credit_score,
        rating=rating
    )

