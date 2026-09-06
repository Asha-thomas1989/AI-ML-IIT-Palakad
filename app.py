from flask import Flask, request, render_template_string
from google import genai

app = Flask(__name__)

# Initialize Gemini client
client = genai.Client(api_key="YOUR_API_KEY")

# Retrieval function
def retrieve_clause(prob, tenure):
    if tenure < 3:
        return "Clause 3 — New Customer, Any Risk, Tenure < 3 months: Route to onboarding team."
    elif prob >= 0.70:
        return "Clause 1 — High Risk (probability ≥ 0.70): Offer a loyalty discount and a callback within 48 hours."
    elif prob >= 0.40:
        return "Clause 2 — Moderate Risk (0.40–0.70): Send targeted email with upgrade offer."
    else:
        return "No clause — Low risk, no action."

@app.route("/", methods=["GET", "POST"])
def advisory():
    output = ""
    if request.method == "POST":
        risk_prob = float(request.form["risk_prob"])
        tenure = int(request.form["tenure"])
        top_features = request.form["top_features"]

        # Step 2: Retrieval (fresh each time)
        clause = retrieve_clause(risk_prob, tenure)

        # Step 3: Build prompt
        system_prompt = f"""
        You are a retention advisor.
        Use only this clause: {clause}
        Explain in 3–4 sentences why the customer is at risk,
        referencing only these features: {top_features}.
        Do not mention gender, SeniorCitizen, Partner, or Dependents,
        or imply them in any way.
        """

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=system_prompt
            )
            llm_output = response.text
        except Exception as e:
            llm_output = f"Error calling Gemini: {e}"

        # Display results
        output = f"""
        <h3>Risk Tier</h3>
        Probability: {risk_prob}, Tenure: {tenure} months
        <h3>Clause</h3>
        {clause}
        <h3>LLM Advisory Explanation</h3>
        {llm_output}
        """

    return render_template_string("""
        <h2>Customer Retention Advisor</h2>
        <form method="post">
            Churn Probability (0–1): <input name="risk_prob"><br>
            Tenure (months): <input name="tenure"><br>
            Top Features (comma-separated): <input name="top_features"><br>
            <input type="submit" value="Run Advisory">
        </form>
        <hr>
        {{output|safe}}
    """, output=output)

if __name__ == "__main__":
    app.run(debug=True)
