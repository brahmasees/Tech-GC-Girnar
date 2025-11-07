#!/usr/bin/env python3
import time, math, sys, termios, tty, select, json, csv, os
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


STEP_TRANSLATION = 0.05
STEP_ROT_DEG = 5
LOOP_DT = 0.05
STATE_FILE = 'youbot_states.json'
HARD_FILE = 'youbot_states_hardcode.json'
PATH_CSV = 'youbot_path.csv'


client = RemoteAPIClient('localhost', 23000)
sim = client.require('sim')
print("Connected to CoppeliaSim youBot tele-op system.")

vehicleTarget = sim.getObject('/youBot_vehicleTargetPosition')
vehicleReference = sim.getObject('/youBot_vehicleReference')
gripper = sim.getObject('/youBot_gripper')

saved_states = {}
recorded_path = []

def get_key(timeout=0.05):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        rlist, _, _ = select.select([fd], [], [], timeout)
        return sys.stdin.read(1) if rlist else None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def get_pose():
    p = sim.getObjectPosition(vehicleReference, -1)
    o = sim.getObjectOrientation(vehicleReference, -1)
    yaw_deg = math.degrees(o[2])
    return (p[0], p[1], yaw_deg)

def move_target(dx=0.0, dy=0.0, dyaw_deg=0.0):
    pos = sim.getObjectPosition(vehicleTarget, vehicleReference)
    pos[0] += dx
    pos[1] += dy
    sim.setObjectPosition(vehicleTarget, vehicleReference, pos)
    if abs(dyaw_deg) > 1e-6:
        ori = sim.getObjectOrientation(vehicleTarget, vehicleReference)
        ori[2] += math.radians(dyaw_deg)
        sim.setObjectOrientation(vehicleTarget, vehicleReference, ori)

def goto_pose(x, y, yaw_deg):
    sim.setObjectParent(vehicleTarget, -1, True)
    sim.setObjectPosition(vehicleTarget, -1, [x, y, 0])
    sim.setObjectOrientation(vehicleTarget, -1, [0, 0, math.radians(yaw_deg)])
    sim.setObjectParent(vehicleTarget, vehicleReference, True)
    time.sleep(0.1)
    sim.setObjectParent(vehicleTarget, -1, True)
    print(f"Target set to world pose: x={x:.2f}, y={y:.2f}, yaw={yaw_deg:.1f}°")

def wait_until_reached(tol=0.02, yaw_tol=2.0):
    while True:
        rel = sim.getObjectPosition(vehicleTarget, vehicleReference)
        rel_o = sim.getObjectOrientation(vehicleTarget, vehicleReference)
        if abs(rel[0]) < tol and abs(rel[1]) < tol and abs(math.degrees(rel_o[2])) < yaw_tol:
            break
        time.sleep(0.05)

def goto_state(name):
    if name not in saved_states:
        print(f"No saved state '{name}' found.")
        return
    s = saved_states[name]
    print(f"Moving to '{name}' (x={s['x']:.2f}, y={s['y']:.2f}, yaw={s['yaw']:.1f}°)")
    goto_pose(s['x'], s['y'], s['yaw'])
    wait_until_reached()

def gripper_action(action):
    sim.setStringProperty(gripper, 'customData.activity', action)
    print(f"Gripper -> {action.upper()}")

def send_signal_and_wait(sig_name, payload, done_sig, timeout=20):
    sim.setStringSignal(sig_name, payload)
    print(f"Sent: {sig_name}='{payload}'")
    t0 = time.time()
    while time.time() - t0 < timeout:
        val = sim.getStringSignal(done_sig)
        if val == "":
            sim.clearStringSignal(done_sig)
            print(f"{done_sig} confirmed.")
            return True
        time.sleep(0.05)
    print("Timeout waiting for done signal.")
    return False

def pickup_object(obj_name):
    print(f"Starting pickup: {obj_name}")
    gripper_action('open')
    time.sleep(0.5)
    send_signal_and_wait('pickup_now', obj_name, 'pickup_done')
    gripper_action('close')
    time.sleep(0.5)
    print(f"Pickup complete: {obj_name}")

def drop_object(zone_name):
    send_signal_and_wait('drop_now', zone_name, 'drop_done')
    gripper_action('open')
    time.sleep(0.5)
    print(f"Drop complete: {zone_name}")

def save_state(name):
    x, y, yaw = get_pose()
    saved_states[name] = {'x': x, 'y': y, 'yaw': yaw}
    print(f"Saved state '{name}': ({x:.3f}, {y:.3f}, {yaw:.1f}°)")

def save_states_to_disk():
    with open(STATE_FILE, 'w') as f:
        json.dump(saved_states, f, indent=2)
    print(f"Saved {len(saved_states)} states to {os.path.abspath(STATE_FILE)}")

def save_hardcoded_for_lua():
    lua_ready = [{'name': k, 'x': v['x'], 'y': v['y'], 'yaw': v['yaw']} for k, v in saved_states.items()]
    with open(HARD_FILE, 'w') as f:
        json.dump(lua_ready, f, indent=2)
    print(f"Exported hardcoded Lua JSON to {os.path.abspath(HARD_FILE)}")

def load_states_from_disk():
    global saved_states
    try:
        with open(STATE_FILE) as f:
            saved_states = json.load(f)
        print(f"Loaded {len(saved_states)} saved states.")
    except FileNotFoundError:
        saved_states = {}


def main():
    load_states_from_disk()
    print("\nTele-Op Controls:")
    print("  W/S : forward/backward")
    print("  A/D : left/right")
    print("  Q/E : rotate left/right")
    print("  P   : pickup cube (auto-grip)")
    print("  O   : drop cube (auto-grip)")
    print("  T   : save current state")
    print("  G   : go to saved state")
    print("  H   : export hardcoded JSON (for Lua)")
    print("  L   : list saved states")
    print("  ESC : exit\n")

    while True:
        key = get_key(timeout=LOOP_DT)
        if not key:
            continue

        if key == '\x1b': 
            break
        elif key.lower() == 'w': move_target(0, STEP_TRANSLATION)
        elif key.lower() == 's': move_target(0, -STEP_TRANSLATION)
        elif key.lower() == 'a': move_target(-STEP_TRANSLATION, 0)
        elif key.lower() == 'd': move_target(STEP_TRANSLATION, 0)
        elif key.lower() == 'q': move_target(0, 0, STEP_ROT_DEG)
        elif key.lower() == 'e': move_target(0, 0, -STEP_ROT_DEG)
        elif key.lower() == 'p':
            obj = input("Pickup object (e.g. Red_1): ").strip()
            if obj:
                pickup_object(obj)
        elif key.lower() == 'o':
            zone = input("Drop zone (e.g. Zone_A): ").strip()
            if zone:
                drop_object(zone)
        elif key.lower() == 't':
            name = input("Enter state name: ").strip()
            if name: save_state(name)
        elif key.lower() == 'g':
            name = input("Go to state: ").strip()
            if name: goto_state(name)
        elif key.lower() == 'h':
            save_hardcoded_for_lua()
        elif key.lower() == 'l':
            print("📍 Saved States:")
            for k, v in saved_states.items():
                print(f"   {k}: {v}")

    save_states_to_disk()
    print("Exiting tele-op.")

if __name__ == "__main__":
    try:
        sim.startSimulation()
        time.sleep(0.5)
        main()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            save_states_to_disk()
            sim.stopSimulation()
        except:
            pass
