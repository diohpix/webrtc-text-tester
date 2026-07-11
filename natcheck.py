#!/usr/bin/env python3
# 대칭형 NAT 판별: 같은 로컬 UDP 소켓에서 여러 STUN 서버로 binding request 를 보내
# 돌아온 공인(mapped) IP:port 를 비교한다. 목적지마다 포트가 다르면 Symmetric NAT.
import socket, struct, os, sys

MAGIC = 0x2112A442

def stun_request(sock, host, port):
    # 20바이트 헤더: type=0x0001(Binding Request), len=0, magic, 12B txid
    txid = os.urandom(12)
    msg = struct.pack('>HHI', 0x0001, 0, MAGIC) + txid
    try:
        sock.sendto(msg, (host, port))
        data, _ = sock.recvfrom(2048)
    except Exception as e:
        return None, f"error: {e}"
    if len(data) < 20:
        return None, "short response"
    mtype, mlen = struct.unpack('>HH', data[:4])
    off = 20
    end = 20 + mlen
    while off + 4 <= end:
        atype, alen = struct.unpack('>HH', data[off:off+4])
        val = data[off+4:off+4+alen]
        if atype in (0x0020, 0x0001):  # XOR-MAPPED-ADDRESS / MAPPED-ADDRESS
            fam = val[1]
            xport = struct.unpack('>H', val[2:4])[0]
            if atype == 0x0020:
                mport = xport ^ (MAGIC >> 16)
                raw = struct.unpack('>I', val[4:8])[0] ^ MAGIC
            else:
                mport = xport
                raw = struct.unpack('>I', val[4:8])[0]
            ip = socket.inet_ntoa(struct.pack('>I', raw))
            return (ip, mport), "ok"
        off += 4 + alen + ((4 - alen % 4) % 4)
    return None, "no mapped-address attr"

SERVERS = [
    ("stun.l.google.com", 19302),
    ("stun1.l.google.com", 19302),
    ("stun.cloudflare.com", 3478),
]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 0))
sock.settimeout(3)
localport = sock.getsockname()[1]
print(f"로컬 소스 포트: {localport}\n")

results = []
for host, port in SERVERS:
    mapped, status = stun_request(sock, host, port)
    if mapped:
        print(f"{host:24} → 공인 {mapped[0]}:{mapped[1]}   ({status})")
        results.append(mapped)
    else:
        print(f"{host:24} → 실패 ({status})")

print()
ports = {m[1] for m in results}
ips = {m[0] for m in results}
if len(results) < 2:
    print("판정 불가: 성공한 STUN 응답이 2개 미만")
elif len(ports) == 1:
    print(f"✅ 공인 포트 일정({ports.pop()}) → Cone NAT (endpoint-independent). STUN 만으로 P2P 가능성 높음.")
else:
    print(f"⚠️  공인 포트가 목적지마다 다름 {sorted(ports)} → ★ Symmetric NAT ★. STUN 무의미, TURN 필수.")
if len(ips) > 1:
    print(f"   (공인 IP 도 여러 개: {ips} — CGNAT 로드밸런싱 가능성)")
