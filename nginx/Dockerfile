FROM nginx:alpine

# Удалить дефолтную конфигурацию
RUN rm /etc/nginx/conf.d/default.conf

# Копировать нашу конфигурацию
COPY nginx.conf /etc/nginx/conf.d/

# Создать директорию для логов
RUN mkdir -p /var/log/nginx

# Expose порт
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Запуск nginx
CMD ["nginx", "-g", "daemon off;"]
