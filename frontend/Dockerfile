FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

ARG VITE_AUTH_API_URL=http://localhost:8001
ARG VITE_AI_API_URL=http://localhost:8002
ENV VITE_AUTH_API_URL=$VITE_AUTH_API_URL
ENV VITE_AI_API_URL=$VITE_AI_API_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
