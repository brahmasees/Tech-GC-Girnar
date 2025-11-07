# 🤖 Task 3 – Integrated Mobile Manipulation
**Mechatronic Mastery – Inter-Hostel Robotics Challenge 2025**

---

## 📘 Overview
This task integrates **mobile base navigation** and **manipulator control** into one coordinated system using the **KUKA youBot** platform.  
The system is designed to:
1. Move the mobile base (teleoperated) to specific colored cuboid locations.  
2. Detect and pick up cuboids using the manipulator (Inverse Kinematics used everywhere for the arm).  
3. Place them in their respective drop zones.

Manual teleoperation through the **keyboard** (Python Remote API) is used to position the mobile base, while the **manipulator operates autonomously via IK** for precise pickup and placement.

---

## ⚙️ Simulation Setup

**Platform:** CoppeliaSim Educational Edition  
**Languages:** Python (Remote API) + Lua (Manipulator Control)  
**Robot Used:** KUKA youBot (unified system = **8 DOF total**)  
- **Arm:** 5 DOF (manipulator)  
- **Base:** 3 DOF (omnidirectional platform)  

**Control Modes:**  
- Mobile Base – Keyboard Teleoperation (Python)  
- Manipulator – **Inverse Kinematics (IK)** (Lua, auto triggered via string signals)

---

### Components
| Component | Description |
|------------|-------------|
| **Mobile Base** | Omnidirectional youBot platform (3 DOF: planar x, y, yaw) |
| **Mounted Manipulator** | youBot manipulator (5 DOF) controlled through IK group |
| **Vehicle Target / Reference** | `/youBot_vehicleTargetPosition`, `/youBot_vehicleReference` used by tele-op |
| **Pickup/Drop Signals** | `pickup_now`, `pickup_done`, `drop_now`, `drop_done` for arm-base coordination |
| **Sensors** | Virtual color detection and proximity sensors for cuboid identification |
| **Drop Zones** | Zone_A (Red), Zone_B (Blue), Zone_C (Green) |

---

## 🧩 Control Architecture

### Mobile Base — Teleoperation (Python)
- `task3_motion_control.py` connects to CoppeliaSim via the ZMQ remote API.
- Keyboard controls:
  - `W/S` — forward/back
  - `A/D` — left/right strafing
  - `Q/E` — rotate left/right
  - `P` — initiate pickup (prompts object name)
  - `O` — initiate drop (prompts zone name)
- The script modifies the vehicle **target** relative to a **reference** object:
  - `move_target(dx, dy, dyaw_deg)` translates/rotates `/youBot_vehicleTargetPosition`.
- Pickup and drop actions are coordinated by sending string signals; the Python tele-op waits for a corresponding `<action>_done` signal.

### Manipulator — Inverse Kinematics (IK)
- **IK is used everywhere for manipulator motions** (explicit requirement).
- The manipulator script (Lua) listens for `pickup_now` / `drop_now` string signals from the tele-op client.
- On receiving a pickup request:
  1. The arm computes an IK solution for the target pose (above the cuboid).
  2. Executes a smooth IK-based trajectory to approach, close gripper (friction-based grasp), and lift.
  3. Sends `pickup_done` when complete.
- On receiving a drop request:
  1. The arm computes IK for the drop zone pose.
  2. Places the object upright and releases using friction contact, then sends `drop_done`.

**Note:** Using IK ensures Cartesian-space accuracy for end-effector positioning and orientation — required for reliable pick-and-place.

---

## 🧠 Coordination & Safety
- The tele-op only moves the mobile base; manipulator tasks are executed autonomously to avoid unsafe concurrent motions.
- The tele-op waits for `*_done` signals to ensure the manipulator has finished before allowing the next pickup/drop command.
- End-effector approach heights and gripper forces are tuned to minimize cuboid falls (falling objects incur penalties per the rules).

---

## 🎯 Achievements
✅ Integrated tele-op for omnidirectional mobile navigation.  
✅ Reliable IK-based manipulator pickup and placement.  
✅ Signal-based synchronization between base and arm to ensure safe sequencing.  
✅ Friction-based gripping (no artificial joints) for realistic grasping.

---

## 🪛 How to Run
1. Open **Arena 3 – MobileManipulator.ttt** in CoppeliaSim.  
2. Ensure the Lua manipulator controller is attached and an IK group is configured for the arm.  
3. Start the CoppeliaSim simulation.  
4. Run the tele-op controller:
   ```bash
   python3 task3_motion_control.py
   ```
5. Use the keyboard controls to position the base, press `P` to pick (enter object name), and `O` to drop (enter zone).  
6. The Python script will wait for the manipulator to finish each action before resuming.

---

## 📄 Notes & Assumptions
- **DOF Clarification:** The KUKA youBot unified system is treated as **8 DOF** (5 DOF arm + 3 DOF base). This README reflects that corrected definition.
- All manipulator motions are performed via **IK** for accuracy and compliance with the task requirement.
- Pickup uses friction-based grasping (no fixed joints) to comply with rules.
- Tele-op networked via ZMQ Remote API on `localhost:23000` (default configuration in `task3_motion_control.py`).

