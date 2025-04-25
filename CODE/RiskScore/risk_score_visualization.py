import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

risk_scores = gpd.read_file("CreatedData/ScoredStructures/scored_structures_normalized.shp")
risk_scores = risk_scores.to_crs(epsg=3857)  
# print(risk_scores.columns)

# This is some hardcoding to zoom in on a spot where you can ---
# --- actually see some of the scores
sampled = risk_scores.sample(n=5, random_state=42)
minx, miny, maxx, maxy = risk_scores.total_bounds
width = (maxx - minx) * 0.5
height = (maxy - miny) * 0.5
center_x = minx + (maxx - minx) * 0.75
center_y = miny + (maxy - miny) * 0.3


fig, ax = plt.subplots(figsize=(12, 10))
risk_scores.plot(
    ax=ax,
    column="final_scor",
    cmap="plasma",
    markersize=5,
    legend=True,
    legend_kwds={"label": "Normalized Risk Score", "shrink": 0.6},
    alpha=0.9,
    zorder=2
)


ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=risk_scores.crs.to_string(), alpha=0.7)
ax.set_xlim(center_x - width / 2, center_x + width / 2)
ax.set_ylim(center_y - height / 2, center_y + height / 2)
ax.set_title("Risk of Damage from Wildfire by Structure", fontsize=16)
ax.set_axis_off()
plt.tight_layout()
plt.show()

