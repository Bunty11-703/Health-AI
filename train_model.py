import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ===============================
# LOAD RAW DATA
# ===============================
df = pd.read_csv("data/dataset.csv")
df.columns = df.columns.str.strip()

# -------------------------------
# IDENTIFY SYMPTOM COLUMNS
# -------------------------------
symptom_cols = [col for col in df.columns if col.startswith("Symptom")]

# -------------------------------
# EXTRACT ALL UNIQUE SYMPTOMS
# -------------------------------
raw_values = df[symptom_cols].values.ravel()

all_symptoms = sorted(
    {s.strip().lower() for s in raw_values if isinstance(s, str)}
)

# -------------------------------
# BUILD BINARY SYMPTOM MATRIX
# -------------------------------
X = pd.DataFrame(0, index=df.index, columns=all_symptoms)

for idx, row in df[symptom_cols].iterrows():
    for symptom in row:
        if isinstance(symptom, str):
            X.at[idx, symptom.strip().lower()] = 1

# Target
y = df["Disease"]

# -------------------------------
# TRAIN MODEL
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)


model.fit(X_train, y_train)

# -------------------------------
# SAVE MODEL
# -------------------------------
pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(X.columns.tolist(), open("model/feature_names.pkl", "wb"))

print("✅ Model trained successfully")
print(f"🧠 Diseases learned: {y.nunique()}")
print(f"🧪 Symptoms used: {X.shape[1]}")
