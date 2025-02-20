from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

def custom_sort(col_name):
    """Sorts by suffix first, ensuring 'Name of the Certification' comes first within each group"""
    parts = col_name.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return (int(parts[1]), 0 if parts[0] == "Name of the Certification" else 1, parts[0])
    return (float('inf'), col_name)

def process_certification_data(df):
    """Process and pivot certification data."""
    df.columns = df.columns.str.strip()
    df['cert_count'] = df.groupby('Employee ID  & Name').cumcount() + 1
    
    required_columns = [
        'Name of the Certification', 'Certification Level', 'Select the validity expiry date', 
        'Actual date of completion', 'Certificate ID', 'Provider Name', 'PDF Reference Number', 
        'Availed Voucher', 'Voucher Provider Name', 'Voucher Reference Number', 
        'Upload certificate', 'PDF Applied (Professional Development Fund)', 
        'Certification Level Name', 'Is there a Validity period for the above certificate'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = pd.NA  
    
    df_pivot = df.pivot(index='Employee ID  & Name', columns='cert_count', values=required_columns)
    df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
    
    sorted_columns = sorted(df_pivot.columns, key=custom_sort)
    df_pivot = df_pivot[sorted_columns]
    
    df_pivot.reset_index(inplace=True)
    return df_pivot

def process_fund_data(df):
    """Process and pivot fund data."""
    df.columns = df.columns.str.strip()
    df['fund_count'] = df.groupby('Employee ID  & Name').cumcount() + 1
    
    required_columns = [
       'ZOHO_LINK_ID', 'Added Time', 'Modified Time',
       'Provider', 'Name of the Certification', 'Certification Level ',
       'Select the validity expiry date', 'Actual date of completion',
       'Certificate ID', 'Provider Name', 'PDF Reference Number',
       'Availed Voucher', 'Voucher Provider Name', 'Voucher Reference Number',
       'Upload certificate', 'PDF Applied (Professional Development  Fund)',
       'Certification Level Name',
       'Is there a Validity period for the above certificate',
       'Approval Status', 'Approver', 'Approval Time']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = pd.NA  
    
    df_pivot = df.pivot(index='Employee ID  & Name', columns='fund_count', values=required_columns)
    df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
    
    sorted_columns = sorted(df_pivot.columns, key=custom_sort)
    df_pivot = df_pivot[sorted_columns]
    
    df_pivot.reset_index(inplace=True)
    return df_pivot

@app.route("/process", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    data_type = request.form.get("dataType")

    if uploaded_file.filename.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.filename.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        return jsonify({"error": "Invalid file format"}), 400

    print(f"Received data type: {data_type}")  # Debugging
    print(f"Initial DataFrame:\n{df.head()}")  # Debugging

    if data_type == "certification":
        df_pivot = process_certification_data(df)
    elif data_type == "fund":
        df_pivot = process_fund_data(df)
    else:
        return jsonify({"error": "Invalid data type"}), 400

    if df_pivot.empty:
        return jsonify({"error": "Pivoting resulted in an empty dataset"}), 400

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_pivot.to_excel(writer, index=False, sheet_name="Pivoted Data")
    excel_buffer.seek(0)

    return send_file(
        excel_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="Processed_Data.xlsx"
    )

if __name__ == "__main__":
    app.run(debug=True)
