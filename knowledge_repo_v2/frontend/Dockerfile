FROM node:19.1-alpine

LABEL description="knowledge-repo V2 frontend "


WORKDIR /app

EXPOSE 3000

COPY package.json package-lock.json ./

RUN npm install --silent

COPY . ./

CMD ["npm", "start"]
