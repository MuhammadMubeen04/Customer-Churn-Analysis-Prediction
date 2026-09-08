"""
Customer Churn Analysis & Prediction
------------------------------------
Part 1: Business Analytics (EDA, churn drivers)
Part 2: Machine Learning (Logistic Regression / Random Forest classification)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
CHARTS = Path(__file__).parent / "charts"
CHARTS.mkdir(exist_ok=True)
SUMMARIES = DATA / "summaries"
SUMMARIES.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (11, 6)

# ----------------------------------------------------------
# 1. LOAD DATA
# ----------------------------------------------------------
df = pd.read_csv(DATA / "customer_churn.csv")
print("=" * 60)
print("DATASET OVERVIEW")
print("=" * 60)
print(f"Shape: {df.shape}")
print(f"Churn rate: {(df['Churn']=='Yes').mean()*100:.1f}%")
print(df['Churn'].value_counts())

# ----------------------------------------------------------
# 2. OVERALL KPIs
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("OVERALL KPIs")
print("=" * 60)
print(f"Total Customers     : {len(df)}")
print(f"Churned Customers   : {(df['Churn']=='Yes').sum()}")
print(f"Churn Rate          : {(df['Churn']=='Yes').mean()*100:.2f}%")
print(f"Avg Tenure (months) : {df['Tenure'].mean():.1f}")
print(f"Avg Monthly Charges : ${df['MonthlyCharges'].mean():.2f}")
print(f"Avg Total Charges   : ${df['TotalCharges'].mean():.2f}")

# ----------------------------------------------------------
# 3. CHURN BY KEY DIMENSIONS
# ----------------------------------------------------------
def churn_rate(col):
    t = pd.crosstab(df[col], df["Churn"], normalize="index") * 100
    t["Count"] = df[col].value_counts()
    return t.round(2)

print("\nChurn by Contract:")
print(churn_rate("Contract").sort_values("Yes", ascending=False))

print("\nChurn by InternetService:")
print(churn_rate("InternetService").sort_values("Yes", ascending=False))

print("\nChurn by PaymentMethod:")
print(churn_rate("PaymentMethod").sort_values("Yes", ascending=False))

# Tenure bands
df["TenureBand"] = pd.cut(df["Tenure"], bins=[0, 6, 12, 24, 48, 100],
                          labels=["0-6m", "7-12m", "13-24m", "25-48m", "49m+"])
print("\nChurn by Tenure Band:")
print(churn_rate("TenureBand"))

# ----------------------------------------------------------
# 4. VISUALIZATIONS (Analytics)
# ----------------------------------------------------------
# 4.1 Overall Churn
fig, ax = plt.subplots()
df["Churn"].value_counts().plot.pie(autopct="%1.1f%%", colors=["#4CAF50", "#F44336"], ax=ax, startangle=90)
ax.set_ylabel("")
ax.set_title("Overall Churn Rate")
plt.tight_layout()
plt.savefig(CHARTS / "01_overall_churn.png", dpi=150)
plt.close()

# 4.2 Churn by Contract
fig, ax = plt.subplots()
sns.countplot(data=df, x="Contract", hue="Churn", ax=ax, palette={"Yes": "#F44336", "No": "#4CAF50"})
ax.set_title("Churn by Contract Type")
plt.tight_layout()
plt.savefig(CHARTS / "02_churn_by_contract.png", dpi=150)
plt.close()

# 4.3 Churn by Internet Service
fig, ax = plt.subplots()
sns.countplot(data=df, x="InternetService", hue="Churn", ax=ax, palette={"Yes": "#F44336", "No": "#4CAF50"})
ax.set_title("Churn by Internet Service")
plt.tight_layout()
plt.savefig(CHARTS / "03_churn_by_internet.png", dpi=150)
plt.close()

# 4.4 Churn by Tenure Band
fig, ax = plt.subplots()
sns.countplot(data=df, x="TenureBand", hue="Churn", ax=ax, palette={"Yes": "#F44336", "No": "#4CAF50"})
ax.set_title("Churn by Tenure Band")
plt.tight_layout()
plt.savefig(CHARTS / "04_churn_by_tenure.png", dpi=150)
plt.close()

# 4.5 Monthly Charges by Churn
fig, ax = plt.subplots()
sns.boxplot(data=df, x="Churn", y="MonthlyCharges", ax=ax, palette={"Yes": "#F44336", "No": "#4CAF50"})
ax.set_title("Monthly Charges by Churn Status")
plt.tight_layout()
plt.savefig(CHARTS / "05_charges_by_churn.png", dpi=150)
plt.close()

# 4.6 Churn by Payment Method
fig, ax = plt.subplots(figsize=(12, 5))
sns.countplot(data=df, y="PaymentMethod", hue="Churn", ax=ax, palette={"Yes": "#F44336", "No": "#4CAF50"})
ax.set_title("Churn by Payment Method")
plt.tight_layout()
plt.savefig(CHARTS / "06_churn_by_payment.png", dpi=150)
plt.close()

# 4.7 Churn by Tech Support
fig, ax = plt.subplots()
sns.countplot(data=df, x="TechSupport", hue="Churn", ax=ax, palette={"Yes": "#F44336", "No": "#4CAF50"})
ax.set_title("Churn by Tech Support")
plt.tight_layout()
plt.savefig(CHARTS / "07_churn_by_techsupport.png", dpi=150)
plt.close()

print(f"\nAnalytics charts saved to: {CHARTS}")

# ----------------------------------------------------------
# 5. MACHINE LEARNING – CHURN PREDICTION
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("MACHINE LEARNING – CHURN PREDICTION")
print("=" * 60)

try:
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score

    # Prepare features
    ml_df = df.copy()
    ml_df["ChurnFlag"] = (ml_df["Churn"] == "Yes").astype(int)

    # Encode categoricals
    cat_cols = ["Gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
                "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
                "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
                "PaperlessBilling", "PaymentMethod"]
    for col in cat_cols:
        le = LabelEncoder()
        ml_df[col] = le.fit_transform(ml_df[col].astype(str))

    features = cat_cols + ["SeniorCitizen", "Tenure", "MonthlyCharges", "TotalCharges"]
    X = ml_df[features]
    y = ml_df["ChurnFlag"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    y_prob_lr = lr.predict_proba(X_test)[:, 1]

    print("\n--- Logistic Regression ---")
    print(f"Accuracy : {accuracy_score(y_test, y_pred_lr):.3f}")
    print(f"ROC-AUC  : {roc_auc_score(y_test, y_prob_lr):.3f}")
    print(classification_report(y_test, y_pred_lr, target_names=["No Churn", "Churn"]))

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_prob_rf = rf.predict_proba(X_test)[:, 1]

    print("\n--- Random Forest ---")
    print(f"Accuracy : {accuracy_score(y_test, y_pred_rf):.3f}")
    print(f"ROC-AUC  : {roc_auc_score(y_test, y_prob_rf):.3f}")
    print(classification_report(y_test, y_pred_rf, target_names=["No Churn", "Churn"]))

    # Feature Importance
    imp = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    print("\nTop Feature Importances (Random Forest):")
    print(imp.head(10).round(3))

    # Chart: Feature Importance
    fig, ax = plt.subplots(figsize=(10, 6))
    imp.head(10).sort_values().plot(kind="barh", color="#4e79a7", ax=ax)
    ax.set_title("Top 10 Feature Importances (Random Forest)")
    plt.tight_layout()
    plt.savefig(CHARTS / "08_feature_importance.png", dpi=150)
    plt.close()

    # Chart: Confusion Matrix (RF)
    cm = confusion_matrix(y_test, y_pred_rf)
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["No Churn", "Churn"], yticklabels=["No Churn", "Churn"])
    ax.set_title("Confusion Matrix – Random Forest")
    ax.set_ylabel("Actual")
    ax.set_xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(CHARTS / "09_confusion_matrix.png", dpi=150)
    plt.close()

    # Save predictions sample
    results = X_test.copy()
    results["Actual"] = y_test.values
    results["Predicted_RF"] = y_pred_rf
    results["Churn_Probability"] = y_prob_rf.round(3)
    results.to_csv(SUMMARIES / "churn_predictions_sample.csv", index=False)

    print("\nML charts and prediction sample exported.")

except ImportError:
    print("\n[!] scikit-learn not installed. Skipping ML section.")
    print("    Run: pip install scikit-learn")
    print("    Then re-run this script to generate predictions and ML charts.")

# ----------------------------------------------------------
# 6. EXPORT SUMMARIES
# ----------------------------------------------------------
kpi = pd.DataFrame([{
    "Total_Customers": len(df),
    "Churned": (df["Churn"] == "Yes").sum(),
    "Churn_Rate_Pct": round((df["Churn"] == "Yes").mean() * 100, 2),
    "Avg_Tenure": round(df["Tenure"].mean(), 1),
    "Avg_MonthlyCharges": round(df["MonthlyCharges"].mean(), 2)
}])
kpi.to_csv(SUMMARIES / "overall_kpis.csv", index=False)

contract_sum = churn_rate("Contract")
contract_sum.to_csv(SUMMARIES / "churn_by_contract.csv")

df.to_csv(SUMMARIES / "customer_churn_enriched.csv", index=False)

print(f"\nSummaries exported to: {SUMMARIES}")
print("\n✅ Customer Churn Analysis & Prediction complete.")
print("   Next: Build Power BI dashboard using customer_churn.csv")