import serial.tools.list_ports
from pymavlink import mavutil
import time
import pandas as pd

ports = serial.tools.list_ports.comports()
port_names = []

for port, desc, hwid in sorted(ports):
    print("[INFO] {}: {} [{}]".format(port, desc, hwid))
    port_names.append(port)

assert "COM9" in port_names
print("[INFO] Radio telemetry port identified!")

master = mavutil.mavlink_connection('com9', baud=57600)
master.wait_heartbeat()
print("[INFO] Connection established.")


def get_GPS():
    try:
        #gps_data = master.messages['GPS_RAW_INT']
        gps_data = master.recv_match(type='GPS_RAW_INT', blocking=True)
        timestamp = time.time_ns()
        print('[INFO] GPS data successfully retrieved')
        return gps_data, timestamp
    except:
        print('[Warning] No GPS_RAW_INT message received yet')
        return None, None

start_time = time.time()
previous_timestamp = None
gps_df = pd.DataFrame(columns=['timestamp', 'time_usec', 'fix_type', 'lat', 'lon', 'alt', 'eph', 'vel', 'cog', 'satellites_visible'])


print("[INFO] Requested the datastream.")
master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)

while time.time() < start_time+60:
    gps_data, timestamp = get_GPS()
    if gps_data is not None and timestamp != previous_timestamp:
        previous_timestamp = timestamp
        gps_df = pd.concat([gps_df, pd.DataFrame({'timestamp': [timestamp], 'time_usec': [gps_data.time_usec], 'fix_type': [gps_data.fix_type], 'lat': [gps_data.lat], 'lon': [gps_data.lon], 'alt': [gps_data.alt], 'eph': [gps_data.eph], 'vel': [gps_data.vel], 'cog': [gps_data.cog], 'satellites_visible': [gps_data.satellites_visible]})], ignore_index=True)
        print(f"[INFO] Measurement {len(gps_df)} received.")

master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 0)
print("Saving measurements")
gps_df.to_csv("GPS_measurement.csv")

