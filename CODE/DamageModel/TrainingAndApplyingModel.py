import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PolynomialFeatures



# Load data
df = pd.read_csv("CreatedData/TrainingData/ModelTrainingData.csv")

column_map = {
    "DAMAGE" : "damage",
    "STRUCTURET": "structure_type",
    "STRUCTUREC": "structure_category",
    "ROOFCONSTR": "roof_construction",
    "EAVES": "eaves",
    "VENTSCREEN": "vent_screen",
    "EXTERIORSI": "exterior_siding",
    "WINDOWPANE": "window_pane",
    "DECKPORCHO": "deckporch_ongrade",
    "DECKPORCHE": "deckporch_elevated",
    "PATIOCOVER": "patio_cover",
    "FENCEATTAC": "fence_attached_to_structure",
    "YEARBUILT": "year_built"
}

df = df.rename(columns=column_map)
# print(df.columns)
# Make the distance to fire negative if the structure is inside the fire perimeter
df.loc[df["in_perimeter"] == 1, "dist_to_fire_km"] *= -1

# Filter out inaccessible structures
df = df[df['damage'] != 'Inaccessible'].copy()

# Changing target to binary rather than multi-class 
damage_map = {
    'No Damage': 0,
    'No Damage (Synthetic)': 0,
    'Affected (1-9%)': 1,
    'Minor (10-25%)': 1,
    'Major (26-50%)': 1,
    'Destroyed (>50%)': 1
}
df['binary_damage'] = df['damage'].map(damage_map)
df = df.dropna(subset=['binary_damage'])


# Adding a few helpful features for the model
df['age'] = 2025 - df['year_built']

df['distance_category'] = 'Near'
df.loc[(df['dist_to_fire_km'] > 3) & (df['dist_to_fire_km'] < 5) &(df['in_perimeter'] == 0), 'distance_category'] = 'Medium'
df.loc[(df['dist_to_fire_km'] >= 5) & (df['in_perimeter'] == 0), 'distance_category'] = 'Far'
df['dist_to_fire_km_squared'] = df['dist_to_fire_km'] ** 2



# Features
categorical = [
    'structure_type', 'structure_category', 'roof_construction', 'eaves',
    'vent_screen', 'exterior_siding', 'window_pane', 'deckporch_ongrade',
    'deckporch_elevated', 'patio_cover', 'fence_attached_to_structure',
    'distance_category'
]
numerical = ['dist_to_fire_km', 'in_perimeter', 'age', 'dist_to_fire_km_squared']

X = df[categorical + numerical]
y = df['binary_damage']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)

num_transform = Pipeline([
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('scale', StandardScaler())
])

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
    ('num', StandardScaler(), numerical)
])

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(C = 1, max_iter=1000, class_weight='balanced'))
])

pipeline.fit(X_train, y_train)

y_proba = pipeline.predict_proba(X_test)[:, 1]  
threshold = 0.71
y_pred = (y_proba >= threshold).astype(int)

X_test_raw = X_test.copy()


test_indices = X_test_raw.index
original_test_df = df.loc[test_indices].copy()

original_test_df["predicted_probability"] = y_proba
original_test_df["predicted_damage"] = y_pred
original_test_df["actual_damage"] = y_test.values

output_columns = categorical + numerical + ["binary_damage", "predicted_probability", "predicted_damage", "actual_damage"]
final_output = original_test_df[output_columns]

# final_output.to_csv("ModelData/testingData/TestSetPredictions000.csv", index=False)

# information on model performance to evaluate model
print("\nClassification Info:\n", classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
labels = ['No Damage (0)', 'Damaged (1)']
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()


# helpful metrics to evaluate model performance
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\n Accuracy:  {acc:.4f}")
print(f" Precision: {prec:.4f}")
print(f" Recall:    {rec:.4f}")
print(f"F1 Score:  {f1:.4f}")


column_map2 = {
    "structure_": "structure_type",
    "structur_1": "structure_category",
    "roof_const": "roof_construction",
    "eaves": "eaves",
    "vent_scree": "vent_screen",
    "exterior_s": "exterior_siding",
    "window_pan": "window_pane",
    "deckporch_": "deckporch_ongrade",
    "deckporc_1": "deckporch_elevated",
    "patio_cove": "patio_cover",
    "fence_atta": "fence_attached_to_structure",
    'in_perimet': 'in_perimeter',
    'dist_to_fi': 'dist_to_fire_km',
}



risk_zones = {
    "high":   "CreatedData/ModelInputs/ModelInput_high_Risk.csv",
    "medium": "CreatedData/ModelInputs/ModelInput_medium_Risk.csv",
    "low":    "CreatedData/ModelInputs/ModelInput_low_Risk.csv",
}

for zone_name, path in risk_zones.items():
    # load zone file and make it the same as training data
    zone_df = pd.read_csv(path)
    zone_df.rename(columns=column_map2, inplace=True)
    zone_df = zone_df.drop(columns='ASSESSEDIM')
    
    zone_df.loc[zone_df["in_perimeter"] == 1, "dist_to_fire_km"] *= -1
    if 'age' not in zone_df.columns:
        zone_df['age'] = 2025 - zone_df['year_built']
        
    zone_df['distance_category'] = 'Near'
    zone_df.loc[(zone_df['dist_to_fire_km'] > 1) & (zone_df['dist_to_fire_km'] < 5) &(zone_df['in_perimeter'] == 0), 'distance_category'] = 'Medium'
    zone_df.loc[(zone_df['dist_to_fire_km'] >= 5) & (zone_df['in_perimeter'] == 0), 'distance_category'] = 'Far'

    zone_df['dist_to_fire_km_squared'] = zone_df['dist_to_fire_km'] ** 2


    # trainng data has "unknown" for missing categorical values so we have to do the same here
    zone_df[categorical] = zone_df[categorical].fillna('Unknown')
    zone_df[numerical] = zone_df[numerical].fillna(0)

    preds = pipeline.predict(zone_df)
    probs = pipeline.predict_proba(zone_df)[:, 1]

    zone_df["predicted_probability"] = probs
    zone_df["predicted_damage"] = (probs >= threshold).astype(int)

    out_path = f"CreatedData/ModelOutputs/Predicted_{zone_name}.csv"
    zone_df.to_csv(out_path, index=False)