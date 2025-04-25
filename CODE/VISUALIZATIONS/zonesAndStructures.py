# This shows the risk zones and all structures in butte county
# There is probably a better way to do this but I was lazy so I just took ---
#  --- the code from making the risk zones and added the structures to it

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import box
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

gdb_path = 'DATA/fire23_1.gdb'
fires = gpd.read_file(gdb_path, layer='firep23_1')
counties = gpd.read_file('DATA/COUNTYBOUNDS/CA_Counties.shp')

fires = fires.to_crs("EPSG:3310")
counties = counties.to_crs("EPSG:3310")
butte = counties[counties['NAME'] == 'Butte']

fires_butte = gpd.clip(fires, butte)

# This create 1 km x 1 km grid over Butte so we can count the number of fires in each cell --- 
# --- And use that to assign risk levels based on location
cell_size = 1000
minx, miny, maxx, maxy = butte.total_bounds
grid_cells = [
    box(x, y, x + cell_size, y + cell_size)
    for x in np.arange(minx, maxx, cell_size)
    for y in np.arange(miny, maxy, cell_size)
]
grid = gpd.GeoDataFrame(geometry=grid_cells, crs="EPSG:3310")
grid = gpd.clip(grid, butte).reset_index(drop=True)
grid["cell_id"] = grid.index

# Counting the number of fires in each grid cell
joined = gpd.sjoin(grid, fires_butte, how="left", predicate="intersects")
fire_counts = joined.groupby("cell_id")["index_right"].count()
grid["fire_count"] = grid["cell_id"].map(fire_counts).fillna(0).astype(int)

# Assign riks levels based on the number of fires in each cell
grid["risk_level"] = "None"
grid.loc[grid["fire_count"].between(1, 2), "risk_level"] = "Low"
grid.loc[grid["fire_count"].between(3, 4), "risk_level"] = "Medium"
grid.loc[grid["fire_count"] >= 5,        "risk_level"] = "High"

# Merge contiguous cells by risk level so we can treat them as a single polygon 
dissolved_polygons = grid.dissolve(by="risk_level", as_index=False)
clusters = dissolved_polygons.explode(ignore_index=True)

# mapping risk to color
colors = {
    "None":   "#E0E0E0",  
    "Low":    "#4CAF50",  
    "Medium": "#FFB74D",  
    "High":   "#E53935",  
}

fig, ax = plt.subplots(figsize=(10, 10))
butte.boundary.plot(ax=ax, color="black", linewidth=2)

for level, color in colors.items():
    subset = clusters[clusters["risk_level"] == level]
    subset.plot(
        ax=ax,
        facecolor=color,
        edgecolor="grey",
        linewidth=0.5,
        label=level
    )

addresses = gpd.read_file("DATA/addresses/shape.shp")
addresses = addresses.to_crs("EPSG:3310")

ax.set_title("Wildfire Risk Zones and Structures")
addresses.plot(
    ax=ax,
    markersize=2,
    color="black",
    alpha=0.5,
    label="Structures"
)
legend_elements = [
    Patch(facecolor=colors["High"], edgecolor="grey", label="High Risk"),
    Patch(facecolor=colors["Medium"], edgecolor="grey", label="Medium Risk"),
    Patch(facecolor=colors["Low"], edgecolor="grey", label="Low Risk"),
    Patch(facecolor=colors["None"], edgecolor="grey", label="No Risk"),
    Line2D([0], [0], marker='o', color='w', label='Structures',
           markerfacecolor='black', markersize=5, alpha=0.5)
]

ax.legend(handles=legend_elements, loc="upper right", frameon=True)
ax.set_axis_off()
plt.tight_layout()
plt.show()

