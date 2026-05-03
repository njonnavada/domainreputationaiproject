import streamlit as st
from model import train_model, predict
from agents import diagnose, recommend

# Train model once
model = train_model()

st.title("📧 Domain AI Analyzer")

# Input fields
domain_name = st.text_input("Domain Name")
open_rate = st.number_input("Open Rate")
bounce_rate = st.number_input("Bounce Rate")
complaint_rate = st.number_input("Complaint Rate")

if st.button("Analyze"):

    domain = {
        "domain": domain_name,
        "openRate": open_rate,
        "bounceRate": bounce_rate,
        "complaintRate": complaint_rate
    }

    status = str(predict(model, domain))
    reasons = diagnose(domain)
    actions = recommend(reasons)

    st.subheader("Result")

    st.write("Status:", status)

    st.write("Reasons:")
    for r in reasons:
        st.write("-", r)

    st.write("Recommendations:")
    for a in actions:
        st.write("-", a)