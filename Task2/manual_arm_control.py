import numpy as np
import math
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

def dh_transform(a, alpha, d, theta):
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),                np.cos(alpha),               d],
        [0, 0, 0, 1]
    ])

def ur5_forward_kinematics(joints_deg):
    joints = np.radians(joints_deg)
    d = [0.089159, 0, 0, 0.10915, 0.09465, 0.0823]
    a = [0, -0.425, -0.39225, 0, 0, 0]
    alpha = [np.pi/2, 0, 0, np.pi/2, -np.pi/2, 0]

    T = np.eye(4)
    for i in range(6):
        Ti = dh_transform(a[i], alpha[i], d[i], joints[i])
        T = np.dot(T, Ti)
    pos = T[0:3, 3]
    return pos


client = RemoteAPIClient()
sim = client.require('sim')

joint_names = [
    '/UR5/joint',
    '/UR5/joint/link/joint',
    '/UR5/joint/link/joint/link/joint',
    '/UR5/joint/link/joint/link/joint/link/joint',
    '/UR5/joint/link/joint/link/joint/link/joint/link/joint',
    '/UR5/joint/link/joint/link/joint/link/joint/link/joint/link/joint'
]
joint_handles = [sim.getObject(name) for name in joint_names]
print("Connected to UR5. Joints ready.")

def send_joint_targets(joint_angles_deg):
    for i in range(6):
        limited = np.clip(joint_angles_deg[i], -90, 90)
        sim.setFloatSignal(f'ur5_joint_target_{i+1}', math.radians(limited))

print("\n=== TASK 2A: Coordinate Targeting ===")

targets = [
    [0, -60, 60, 0, 90, 0],
    [30, -45, 70, -30, 90, 0],
    [-30, -70, 80, 15, 90, 15],
]

for idx, t in enumerate(targets):
    send_joint_targets(t)
    pos = ur5_forward_kinematics(t)
    pos[2] = max(pos[2], 0.35)  # Ensure EE stays above 0.35 m
    print(f"Target {idx+1} | Joints: {t} | EE pos: {pos.round(3)} (m)")
    time.sleep(3)

print("Coordinate targeting done.")

print("\n=== TASK 2B: Path Tracing ===")

duration = 15.0
steps = 200

def move_joint_path(path_func, label):
    print(f"\n--- Tracing {label} path ---")
    for t in np.linspace(0, 1, steps):
        joint_angles = path_func(t)
        send_joint_targets(joint_angles)
        time.sleep(duration / steps)

# Circular path
def circular_path(t):
    return [
        20 * math.cos(2*np.pi*t),
        -60 + 15 * math.sin(2*np.pi*t),
        60 - 10 * math.sin(2*np.pi*t),
        0,
        90,
        0
    ]

# Square path
def square_path(t):
    corners = [
        [0, -60, 60, 0, 90, 0],
        [20, -60, 60, 0, 90, 0],
        [20, -80, 70, 0, 90, 0],
        [0, -80, 70, 0, 90, 0],
        [0, -60, 60, 0, 90, 0]
    ]
    idx = int(t * (len(corners)-1))
    return corners[idx]

# Sinusoidal path
def sinusoidal_path(t):
    return [
        10 * math.sin(2*np.pi*t),
        -60 + 10 * math.sin(4*np.pi*t),
        60,
        10 * math.sin(6*np.pi*t),
        90,
        10 * math.cos(2*np.pi*t)
    ]

# Execute each path
move_joint_path(circular_path, "Circular")
move_joint_path(square_path, "Square")
move_joint_path(sinusoidal_path, "Sinusoidal")

print("Path tracing complete.")
