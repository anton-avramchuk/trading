# Multi-stage build для Frontend

# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Копировать package files и установить зависимости
COPY package*.json ./
RUN npm ci

# Копировать исходный код и собрать
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Копировать собранное приложение
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

# Копировать nginx конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose порт
EXPOSE 80

# Запустить nginx
CMD ["nginx", "-g", "daemon off;"]
