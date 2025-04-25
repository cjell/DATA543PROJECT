import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PolynomialFeatures



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

# get rid of inaccessible structures
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

threshold = 0.63

# choosing degrees to test
degrees = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
train_f1_scores = []
test_f1_scores  = []

for deg in degrees:
    # dealing with numerical features
    num_pipeline = Pipeline([
        ('poly', PolynomialFeatures(degree=deg, include_bias=False)),
        ('scale', StandardScaler())
    ])

    # full preprocessor
    preprocessor = ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical),
        ('num', num_pipeline, numerical)
    ])

    # full modeling pipeline
    pipe = Pipeline([
        ('pre', preprocessor),
        ('clf', LogisticRegression(
            C=9,
            max_iter=5000,
            class_weight='balanced',
            solver='saga',
            random_state=42
        ))
    ])

    pipe.fit(X_train, y_train)

    # predict and F1 on training set
    train_probs = pipe.predict_proba(X_train)[:, 1]
    train_preds = (train_probs >= threshold).astype(int)
    train_f1 = f1_score(y_train, train_preds)
    train_f1_scores.append(train_f1)

    # predict and F1 on test set
    test_probs = pipe.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= threshold).astype(int)
    test_f1 = f1_score(y_test, test_preds)
    test_f1_scores.append(test_f1)

    print(f"Degree {deg}: Train F1 = {train_f1:.4f}, Test F1 = {test_f1:.4f}")

#plotting results
plt.figure(figsize=(8, 6))
plt.plot(degrees, train_f1_scores, marker='o', label='Train F1')
plt.plot(degrees, test_f1_scores,  marker='s', label='Test F1')
plt.xticks(degrees)
plt.xlabel("Polynomial Degree")
plt.ylabel("F1 Score (Any Damage)")
plt.title("Train vs Test F1 by Polynomial Degree")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()
