import socket, time, pickle, os, sys
from pynput import mouse
import pandas as pd

exec(open("../1_Exp_Haptic_Data/settings.txt").read())  #TODO use to run with CMD in mininet command using maketer
# db = pd.read_csv("../1_Exp_Haptic_Data/sDB.txt", sep='\t')
db = pd.read_csv("../1_Exp_Haptic_Data/Data.csv")
#exec(open("./settings.txt").read()) # Uncooment and use for directly used with xterm
# db = pd.read_csv("./sDB.txt", sep='\t')  # Uncooment and use for directly used with xterm

df =pd.DataFrame(db)
target_ip = PC_2
listen_port=kin_link_0
target_address=(target_ip,listen_port)
packet_len=packet_len
n_packets=n_packets
n_packets_expected= n_packets
send_rate_kbytes_per_s=send_rate_kbytes_per_s

def get_packet_payload(packet_n):
    send_time_seconds = time.time()
    payload = pickle.dumps((packet_n, send_time_seconds),0).decode()
    return payload

# def message_format(axis_x,axis_y,axis_z):
def message_format(axis_rssi, axis11_x, axis12_y,axis13_z,axis21_x,axis22_y,axis23_z):
    # msg = "B"  + str(i)
    msg = "B " + str(axis_rssi)
    msg = msg + " " + str(axis11_x)
    msg = msg + " " + str(axis12_y)
    msg = msg + " " + str(axis13_z)
    msg = msg + " " + str(axis21_x)
    msg = msg + " " + str(axis22_y)
    msg = msg + " " + str(axis23_z)
    # msg = "B " + str(axis_x)
    # msg = msg + " " + str(axis_y)
    # msg = msg + " " + str(axis_z)
    msg = msg + " E\n"
    return(msg)

def send_dataPackets():
    send_rate_bytes_per_s = send_rate_kbytes_per_s * 1000
    packet_rate = send_rate_bytes_per_s / packet_len
    packet_interval = 1 / packet_rate
    socket_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_out.connect(target_address)
    send_start_seconds = time.time()
    inter_packet_sleep_times_ms = []
    for packet_n in range(n_packets):
        tx_start_seconds = time.time()
        payload = get_packet_payload(packet_n)
        axis_rssi = str(df['RSSI'][packet_n])
        axis11_x = str(df['ACC_X'][packet_n])
        axis12_y = str(df['ACC_Y'][packet_n])
        axis13_z = str(df['ACC_Z'][packet_n])
        axis21_x = str(df['ACC_X'][packet_n])
        axis22_y = str(df['ACC_Y'][packet_n])
        axis23_z = str(df['ACC_Z'][packet_n])
        # axis_x = str(df['MP_x'][packet_n])
        # axis_y = str(df['MP_y'][packet_n])
        # axis_z = str(df['MP_z'][packet_n])
        n_fill_bytes = packet_len - len(payload)
        print(f"Headers:-- {len(payload)}, remaning:--{n_fill_bytes}, payload:-- {len(axis_rssi)},{len(axis11_x)}, {len(axis12_y)},{len(axis13_z)},{len(axis21_x)},{len(axis22_y)},{len(axis23_z)}")
        
        msg = message_format(axis_rssi, axis11_x, axis12_y,axis13_z,axis21_x,axis22_y,axis23_z)

        # print(f"Headers:-- {len(payload)}, remaning:--{n_fill_bytes}, payload:-- {len(axis_x)}, {len(axis_y)}, {len(axis_z)}")
        # msg = message_format(axis_x, axis_y, axis_z)

        payload = (payload + msg).encode()
        socket_out.sendall(payload)
        tx_end_seconds = time.time()
        tx_time_seconds = tx_end_seconds - tx_start_seconds
        sleep_time_seconds = packet_interval - tx_time_seconds
        inter_packet_sleep_times_ms.append("%.3f" % (sleep_time_seconds * 1000))
        if sleep_time_seconds > 0:
            time.sleep(sleep_time_seconds)
    send_end_seconds = time.time()
    print(f"sending {n_packets} packets with length {packet_len} at {target_address}")
    print("Finished sending packets!")
    total_send_duration_seconds = send_end_seconds - send_start_seconds
    n_bytes = n_packets * packet_len
    bytes_per_second = n_bytes / total_send_duration_seconds
    print("(Actually sent packets at %d kB/s)" % (round(bytes_per_second / 1e3)))
    socket_out.close()