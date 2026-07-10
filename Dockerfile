FROM node:22-slim
WORKDIR /app
COPY package*.json ./
COPY server.js ./
COPY docs ./docs
# Cloud Run이 PORT 환경 변수를 주입하며 server.js가 이를 사용함
CMD ["node", "server.js"]
