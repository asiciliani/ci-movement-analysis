import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = pd.read_csv('outputs/user_ci_video_features.csv')
df_clean = df.dropna(subset=['dist_pelvis', 'torso_A_speed', 'torso_B_speed', 'dir_sim_torso'])

features = df_clean[['dist_pelvis', 'dir_sim_torso', 'torso_A_speed', 'torso_B_speed']]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
df_clean['State'] = kmeans.fit_predict(X_scaled)

state_dists = df_clean.groupby('State')['dist_pelvis'].mean()
if state_dists[0] < state_dists[1]:
    flow_state = 0
    art_state = 1
else:
    flow_state = 1
    art_state = 0

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 4))

time = df_clean['time_sec']
dist = df_clean['dist_pelvis']

ax.plot(time, dist, color='gray', alpha=0.3, label='Distancia Pélvica')

flow_mask = df_clean['State'] == flow_state
art_mask = df_clean['State'] == art_state

ax.scatter(time[flow_mask], dist[flow_mask], color='#00FFCC', label='Flujo Biomecánico', s=10)
ax.scatter(time[art_mask], dist[art_mask], color='#FF0044', label='Improvisación Artística', s=10)

ax.set_title("PoC Rama 7: Clasificación No Supervisada de Estados de Danza (K-Means)", fontsize=14, pad=15)
ax.set_xlabel("Tiempo (segundos)")
ax.set_ylabel("Distancia Física (px)")
ax.legend(loc='upper right')
ax.grid(alpha=0.1)

plt.tight_layout()
plt.savefig('outputs/poc_estados_arte.png', dpi=200, facecolor='black')
