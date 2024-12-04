from flask import Flask, request, render_template, redirect, url_for, session
import joblib

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# Load the saved model
model = joblib.load('model_dt.pkl')

# Preprocessing function
def preprocess_input(transaction_type, amount, old_balance_org, new_balance_orig):
    transaction_type_map = {'CASH_OUT': 1, 'PAYMENT': 2, 'CASH_IN': 3, 'TRANSFER': 4, 'DEBIT': 5}
    transaction_type = transaction_type.upper()  # Normalize input
    transaction_type_encoded = transaction_type_map.get(transaction_type, -1)
    return [transaction_type_encoded, amount, old_balance_org, new_balance_orig]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            # Retrieve form data
            transaction_type = request.form.get('transaction_type')
            amount = request.form.get('amount')
            old_balance_org = request.form.get('old_balance_org')
            new_balance_orig = request.form.get('new_balance_orig')

            # Validate inputs
            if not amount or not old_balance_org or not new_balance_orig:
                raise ValueError("All fields are required.")

            # Convert to numeric
            amount = float(amount)
            old_balance_org = float(old_balance_org)
            new_balance_orig = float(new_balance_orig)

            # Preprocess input
            input_features = [preprocess_input(transaction_type, amount, old_balance_org, new_balance_orig)]

            # Perform prediction
            prediction = model.predict(input_features)
            prediction_result = 'Fraudulent' if prediction[0] == 'Fraud' else 'Legitimate'

            # Store details in session
            session['details'] = {
                'transaction_type': transaction_type,
                'amount': amount,
                'old_balance_org': old_balance_org,
                'new_balance_orig': new_balance_orig,
                'prediction': prediction_result
            }

            return redirect(url_for('result'))
        except Exception as e:
            return render_template('index.html', error=f"Error: {str(e)}")

    return render_template('index.html')

@app.route('/result')
def result():
    details = session.get('details', {})
    return render_template('result.html', **details)

if __name__ == '__main__':
    app.run(debug=True)
