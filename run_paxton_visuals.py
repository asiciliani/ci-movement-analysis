import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('outputs/user_ci_video_features.csv')

# Calculate accel and jerk on the fly since they aren't in the old CSV
dt = 1.0/30.0 # assuming 30 fps
df['torso_A_accel'] = np.gradient(df['torso_A_speed'], dt)
df['torso_A_jerk'] = np.gradient(df['torso_A_accel'], dt)

plt.style.use('dark_background')
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

low_speed_mask = (df['torso_A_speed'] < 50) & (df['torso_A_speed'] > 5)
small_dance_df = df[low_speed_mask].head(150)

if not small_dance_df.empty:
    time = small_dance_df['time_sec'] - small_dance_df['time_sec'].iloc[0]
    accel = small_dance_df['torso_A_accel']
    jerk = small_dance_df['torso_A_jerk']
    
    axes[0].plot(time, accel, color='#00FFCC', label='Micro-Aceleración')
    axes[0].plot(time, jerk/10, color='#9933FF', alpha=0.5, label='Jerk / 10')
    axes[0].set_title('"The Small Dance" (S. Paxton)\nMicro-ajustes reflejos en quietud', fontsize=12, pad=10)
    axes[0].set_xlabel('Tiempo (s)')
    axes[0].legend(loc='upper right')
    axes[0].grid(alpha=0.2)

axes[1].plot(df['pelvis_A_x'], df['pelvis_A_y'], color='#FF0044', linewidth=2, label='Pelvic Bowl (Centro de Masa)')
axes[1].plot(df['torso_A_x'], df['torso_A_y'], color='white', linewidth=0.5, alpha=0.4, label='Torso (Extremidad Superior)')
axes[1].invert_yaxis()
axes[1].set_title('"The Pelvic Bowl"\nEstabilidad del Ancla vs. Fluctuación del Torso', fontsize=12, pad=10)
axes[1].legend(loc='upper right')
axes[1].axis('equal')
axes[1].grid(alpha=0.1)

plt.tight_layout()
plt.savefig('outputs/pitch_steve_paxton.png', dpi=200, facecolor='black')
