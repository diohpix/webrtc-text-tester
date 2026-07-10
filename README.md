# WebRTC DataChannel 텍스트 송수신 테스터

브라우저에서 WebRTC DataChannel로 텍스트를 주고받는 정적 페이지.
시그널링은 HTTP long-poll 릴레이 서버(signalsvc)를 사용하며, 화면에서 원하는
시그널 서버 주소를 직접 입력해 테스트할 수 있다.

## 사용법

1. 페이지를 열고 시그널 서버 주소와 방 이름을 입력해 입장
2. 같은 방에 다른 피어(브라우저 또는 edge)가 있으면 자동으로 P2P 연결
3. 연결 후 텍스트 송수신 — 시그널 서버는 연결 수립까지만 관여

쿼리 파라미터 `?signal=<base-url>` 로도 시그널 서버를 지정할 수 있다.

## 시그널링 프로토콜

```
POST /rooms/{room}/join   {peer_id?}                → {peer_id, token, peers}
POST /rooms/{room}/send   {from, token, to?, kind, payload}
GET  /rooms/{room}/poll   ?peer_id=&token=&wait=25  → {messages}   (long-poll)
POST /rooms/{room}/leave  {peer_id, token}
```

kind: `offer` / `answer` / `ice` + 서버 발행 `peer-joined` / `peer-left`.
payload는 브라우저 `RTCPeerConnection` JSON과 호환. 나중에 입장한 쪽이
기존 피어들에게 offer를 보낸다 (edge는 answerer 전용).

## 로컬 실행

```
npm start   # http://localhost:3000 (docs/ 디렉토리 서빙)
```
