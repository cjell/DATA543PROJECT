import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder

data = pd.read_csv("CreatedData/TrainingData/ModelTrainingData.csv")
print(data.columns)

# renaming important columns
column_map = {
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
    "YEARBUILT": "year_built",
    "DAMAGE": "damage",
}
data = data.rename(columns=column_map)

# making the distance to fire negative if the structure is inside the fire perimeter
data.loc[data["in_perimeter"] == 1, "dist_to_fire_km"] *= -1
data['age'] = 2025 - data['year_built']

#making the damage binary rather than multi-class
damage_map = {
    'No Damage': 'No Damage',
    'No Damage (Synthetic)': 'No Damage',
    'Affected (1-9%)': 'Damaged',
    'Minor (10-25%)': 'Damaged',
    'Major (26-50%)': 'Damaged',
    'Inaccessible': 'Damaged',
    'Destroyed (>50%)': 'Damaged'
}
data['damage'] = data['damage'].map(damage_map)
data = data.dropna(subset=['damage'])


label_map = {'No Damage': 0, 'Damaged': 1}
data['damage_encoded'] = data['damage'].map(label_map)

categorical_features = [
    'structure_type', 'structure_category', 'roof_construction', 'eaves',
    'vent_screen', 'exterior_siding', 'window_pane', 'deckporch_ongrade',
    'deckporch_elevated', 'patio_cover', 'fence_attached_to_structure'
]
numerical_features = ['dist_to_fire_km', 'in_perimeter', 'age']

# One-hot-Ecoding categorical features
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoded_cat = encoder.fit_transform(data[categorical_features])
encoded_cat_df = pd.DataFrame(encoded_cat, columns=encoder.get_feature_names_out(categorical_features))

# merging features
features_df = pd.concat([encoded_cat_df.reset_index(drop=True), data[numerical_features].reset_index(drop=True)], axis=1)
features_df['damage_encoded'] = data['damage_encoded'].reset_index(drop=True)
features_df = features_df.dropna(subset=['damage_encoded'])
features_df = features_df.drop(columns = ['dist_to_fire_km', 'in_perimeter'])


# comptuing the correlations with target
correlations = features_df.corr(numeric_only=True)['damage_encoded'].drop('damage_encoded').sort_values()
pd.set_option('display.max_rows', None)
print(correlations) 

colors = ['green' if val > 0 else 'red' for val in correlations]
plt.figure(figsize=(10, 14))
correlations.plot(kind='barh', color=colors)
plt.title("Feature Correlation with Wildfire Damage Severity")
plt.xlabel("Correlation Coefficient")
plt.grid(True)
plt.tight_layout()
plt.show()
