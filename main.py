# main.py

from model import train_model, predict
from agents import diagnose, recommend

# Step 1: Train model
model = train_model()

# Step 2: Example domain input
domain = {
    "domain": "xyz.com",
    "openRate": 5,
    "bounceRate": 12,
    "complaintRate": 2
}

# Step 3: Classification
#status = predict(model, domain)
status = str(predict(model, domain))

# Step 4: Diagnosis
reasons = diagnose(domain)

# Step 5: Recommendation
actions = recommend(reasons)

# Step 6: Output
result = {
    "domain": domain["domain"],
    "status": status,
    "reasons": reasons,
    "recommendations": actions
}

print(result)