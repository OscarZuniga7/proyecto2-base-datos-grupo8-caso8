# Caso 8 — Inicio de la aplicación Streamlit

Esta carpeta contiene únicamente los archivos nuevos o actualizados de la **primera etapa**. Para incorporarlos al repositorio existente, copiar los archivos y carpetas indicados a la raíz, **sin borrar sql/, docs/, ni SPEC.md**. El docker-compose.yml es una versión conservadora del archivo aportado: conserva `db`, `phpmyadmin` y `mysql_data`, añade `app` y un healthcheck.

1. Crear `.env` mediante `cp .env.example .env` y sustituir la contraseña de ejemplo por la clave real que usa el contenedor MySQL actual. Nunca compartir ni commitear `.env`.
2. Ejecutar `docker compose config` para validar el YAML.
3. Ejecutar `docker compose up -d --build`, sin opción `-v`.
4. `docker compose ps` y `docker compose logs --tail=100 app`.
5. En Codespaces abrir puerto 8501 desde PORTS (Open in Browser). Pulsar «Consultar datos».
6. Las cantidades esperadas tras el poblamiento de ejemplo son 240 clientes y 540 órdenes, pero deben verificarse frente a la base real.
7. Pruebas: `docker compose exec app python -m unittest discover -s tests -v`.
8. Prueba de integración: `docker compose exec -e RUN_DB_INTEGRATION=1 app python -m unittest discover -s tests -v`.
9. Validar directamente en phpMyAdmin con `SELECT COUNT(*) FROM cliente;` y `SELECT COUNT(*) FROM orden_reparacion;`.

**Nota de seguridad**: se reutiliza temporalmente `root` únicamente porque el Compose original solo suministra credenciales root. Antes de entrega real debe crearse una cuenta limitada a los permisos necesarios y cambiar `DB_USER` y `DB_PASSWORD`. No basta declarar `MYSQL_USER` en un volumen MySQL existente: ese mecanismo es solo de inicialización.
