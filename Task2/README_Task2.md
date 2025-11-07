# 🦾 Task 2 – Serial Manipulator Control
**Mechatronic Mastery – Inter-Hostel Robotics Challenge 2025**

---

## 📘 Overview
This task demonstrates **serial manipulator control** using the **UR5 robotic arm** (6 Degrees of Freedom) in **CoppeliaSim**.  
The goal is to:  
1. **Move the end-effector** to a series of given coordinates (Task 2A – Coordinate Targeting).  
2. **Trace predefined trajectories** – Circular, Square, and Sinusoidal paths (Task 2B – Path Tracing).  

The implementation combines a **Lua child script** for low-level joint actuation and a **Python Remote API client** for high-level trajectory commands.

---

## ⌛️ Demonstration



https://github.com/user-attachments/assets/ec103d0b-19f7-4eaf-98c4-782b13e8cc75



---

## ⚙️ Simulation Setup

**Platform:** CoppeliaSim Educational Edition  
**Languages:** Lua + Python (Remote API)  
**Manipulator Used:** UR5 (6 DOF serial arm)  
**Control Mode:** Inverse Kinematics (FK used for verification)

### Components
| Component | Description |
|------------|-------------|
| UR5 Base | Static mount in the manipulator arena |
| 6 Revolute Joints | `/UR5/joint` → last link joint |
| Lua Thread Script | Executes smooth joint-space motion using `sim.moveToConfig()` |
| Python Client | Sends joint angle targets and triggers different paths |
| End Effector | Virtual tool at the tip of the arm |

---

## 🧩 Control Architecture

### Lua Child Script (under UR5 arm)
- Retrieves joint handles (`joint[1..6]`).
- Converts motion limits (velocity, acceleration, jerk) to radians.
- Continuously listens for float signals `ur5_joint_target_1..6` sent by Python.
- When new targets arrive, executes smooth motion using:  
  ```lua
  sim.moveToConfig({
      joints = jointHandles,
      targetPos = targetConf,
      maxVel = maxVel,
      maxAccel = maxAccel,
      maxJerk = maxJerk
  })
  ```
- Provides realistic, dynamically smooth joint motion.

---

## 🧠 Python Remote API Script (`manual_arm_control.py`)

### Key Features
1. **Forward Kinematics**  
   - Implements the UR5 DH parameters to compute end-effector position for given joint angles.  
   - Used to verify the position of each target coordinate.  

2. **Signal Interface**
   ```python
   sim.setFloatSignal('ur5_joint_target_i', math.radians(angle))
   ```
   Sends radian angles to Lua for each joint.

3. **Two Subtasks:**

#### Task 2A – Coordinate Targeting
- Moves arm to specific joint-space configurations and prints EE position.  
- Example targets (degrees):  
  | Target | Joint Angles [deg] | EE Position (m) (approx.) |
  |---------|--------------------|----------------------------|
  | 1 | [ 0, -60, 60, 0, 90, 0 ] | [ 0.37, -0.01, 0.42 ] |
  | 2 | [ 30, -45, 70, -30, 90, 0 ] | [ 0.41, -0.03, 0.45 ] |
  | 3 | [ -30, -70, 80, 15, 90, 15 ] | [ 0.33, -0.02, 0.40 ] |

#### Task 2B – Path Tracing
The UR5 traces three paths using parametric functions:

| Path Type | Parameterization | Remarks |
|------------|------------------|----------|
| Circular | `20 cos(2πt)`, `15 sin(2πt)` modulation on joint angles | Smooth loop motion |
| Square | Piecewise corner positions → discrete segments | Sharp corners visible |
| Sinusoidal | Sine/cosine modulations on multiple joints | Continuous wave-like motion |

Each path runs for ≈ 15 seconds with 200 steps.

---

## 🧱 Arena Details
- Arena 2 (Manipulator.ttt) used.  
- Static platform with UR5 mounted on table.  
- No obstacles present.  
- All coordinates and trajectories are defined in joint space.

---

## 🎯 Achievements
✅ UR5 (6 DOF) successfully executed joint-space targets.  
✅ Smooth dynamic joint motion using `sim.moveToConfig`.  
✅ Accurate coordinate reaching verified via FK.  
✅ All three trajectories (Circular, Square, Sinusoidal) completed without collision.  

---

## 🪛 How to Run
1. Open **Arena 2 – Manipulator.ttt** in CoppeliaSim.  
2. Attach the provided Lua script to the UR5 base object.  
3. Run the Lua script once and keep simulation active.  
4. Execute `manual_arm_control.py` from terminal:  
   ```bash
   python3 manual_arm_control.py
   ```  
5. Observe end-effector motion in CoppeliaSim for both subtasks.  

---

## 📄 Notes & Assumptions
- Joint limits: ±90° clamped in Python for safety.  
- End-effector height ≥ 0.35 m to avoid table collision.  
- Time delay of 3 s between targets ensures stabilization.  
- No external libraries besides NumPy and CoppeliaSim Remote API client.  

---

## 👥 Team Info
**Team Name:** _<Your Hostel Team Name>_  
**Task:** 2 – Serial Manipulator Control  
**Members:** _<List of team members with year>_  
**Technical Secretary (PoC):** _<Name>_  

---

## 📦 Submission Contents
```
Task2/
├── Manipulator.ttt
├── manual_arm_control.py
├── ur5_lua_controller.lua
├── README.md
└── video_link.txt  (Drive link of demonstration video)
```
