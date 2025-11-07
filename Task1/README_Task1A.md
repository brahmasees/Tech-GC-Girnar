# 🧭 Task 1A – Holonomic Drive Navigation
**Mechatronic Mastery – Inter-Hostel Robotics Challenge 2025**

---

## 📘 Overview
This task demonstrates **autonomous navigation** of a **holonomic mobile robot** in **CoppeliaSim**.  
The robot must traverse multiple **waypoints** while avoiding **static obstacles** using proximity sensors.  
The simulation implements a simple **path-following** and **obstacle-avoidance** algorithm written in **Lua** (embedded script).

---
## Demonstration


https://github.com/user-attachments/assets/8fd60ed2-41a5-4f37-9148-1e5b75b13509



## ⚙️ Simulation Setup

**Platform:** CoppeliaSim Educational Edition  
**Programming Language:** Lua (Child Script attached to robot base)

### Components Used
| Component | Description |
|------------|--------------|
| **Mobile Base (Start)** | The main robot body used as reference handle |
| **Left Wheels** | `rollingJoint_fl`, `rollingJoint_rl` |
| **Right Wheels** | `rollingJoint_fr`, `rollingJoint_rr` |
| **Proximity Sensors** | `sensor`, `sensor_l`, `sensor_r` |
| **Waypoints (Dummy Objects)** | `Goal`, `spot_02`, `spot_03`, `spot_04`, `spot_05` |

---

## 🧩 Control Logic

### 1️⃣ Initialization (`sysCall_init`)
- Fetches handles for robot base, wheels, proximity sensors, and waypoints.  
- Defines constants such as `maxSpeed = 5`.  
- Initializes `currentTargetIndex = 1` and `avoiding = 0`.

### 2️⃣ Actuation Loop (`sysCall_actuation`)
Executed every simulation step:
1. **Goal Computation:**  
   - Calculates vector and distance from robot to current target.  
   - On reaching within 0.3 m → switches to next target.  
2. **Obstacle Detection:**  
   - Reads three proximity sensors (front, left, right).  
   - Sets an `avoiding` flag based on which sensor detects an obstacle.  
3. **Avoidance Behavior:**  
   - If obstacle detected → rotate in place to steer clear.  
4. **Navigation Behavior:**  
   - Computes `desiredAngle` toward the target.  
   - Calculates `angleError = desired − heading`.  
   - If misalignment > 30°, robot rotates; else moves forward.  
5. **Motion Functions:**  
   - `setWheelVelocities(leftVel, rightVel)` → low-level wheel control.  
   - `run(speed)` → straight motion.  
   - `stopCar()` → halts robot.

### 3️⃣ Differential Drive (Optional Helper)
A PID-like proportional controller (`driveWithDifferential`) computes small steering corrections based on `angleError`.

---

## 🧠 Algorithm Summary
```text
While not all waypoints visited:
    if obstacle detected by left sensor:
        turn right (avoidance = 1)
    elif obstacle detected by right/front sensor:
        turn left (avoidance = -1)
    elif obstacle cleared:
        avoiding = 0
    if avoiding:
        rotate in place to bypass obstacle
    else:
        orient toward next waypoint and move forward
```

---

## 🧱 Arena Details
- Start Position (Green) → 5 Blue Waypoints.  
- Static Red Obstacles scattered across path.  
- Collisions penalized as per rules.  
- All arena objects were taken directly from the provided **Arena 1 (HolonomicDrive.ttt)** file without modification.

---

## 🎯 Achievements
✅ Autonomous navigation through all waypoints  
✅ Dynamic, continuous, physically realistic wheel motion  
✅ Collision-free path (when properly tuned)  
✅ Modular, extensible Lua script for further stages

---

## 🧰 Parameters and Tuning
| Parameter | Description | Default |
|------------|--------------|----------|
| `maxSpeed` | Maximum linear speed | 5 m/s |
| `STEP_ROT_DEG` | Rotation increment for correction | 5° approx |
| `Distance Threshold` | Distance to consider target reached | 0.3 m |

---

## 🪛 How to Run
1. Open **Arena 1 – HolonomicDrive.ttt** in CoppeliaSim.  
2. Attach the provided Lua script to the **robot base (Start)**.  
3. Ensure object names match those listed above.  
4. Click ▶ **Run Simulation**.  
5. The robot will autonomously navigate through all waypoints.

---

## 📄 Notes & Assumptions
- All obstacles are **static** (no dynamic collision handling needed).  
- The path is **hardcoded** via dummy targets to ensure reproducibility.  
- Parameters such as speed and threshold can be tuned for smoother turns.  
- No external dependencies; runs entirely inside CoppeliaSim.

---

## 👥 Team Info
**Team Name:** _<Your Hostel Team Name>_  
**Task:** 1A – Holonomic Drive Navigation  
**Members:** _<List all team members with year>_  
**Technical Secretary (PoC):** _<Name>_

---

## 📦 Submission Contents
```
Task1A/
├── Task1A_HolonomicDrive.ttt
├── task1A_navigation.lua
├── README.md
└── video_link.txt  (Drive link of demonstration video)
```
