import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
from sklearn.metrics import f1_score




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

# changing target to binary rather than multi-class 
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

#Choosing regularization strength to test
C_values = np.arange(1, 101, 5)  
f1_scores = []

for C in C_values:
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(C=C, max_iter=1000, class_weight='balanced'))
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    f1_scores.append(f1_score(y_test, y_pred))

plt.figure(figsize=(8, 6))
plt.plot(C_values, f1_scores, marker='o')
plt.xlabel("C (Regularization Strength)")
plt.ylabel("F1 Score")
plt.title("F1 Score vs. Regularization Strength")
plt.grid(True)
plt.tight_layout()
plt.show()