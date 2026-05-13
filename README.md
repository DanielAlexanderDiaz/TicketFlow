# TicketFlow

TicketFlow es una aplicación de ticket/reportes que se desarrollará con FastAPI  y SQLModel

## Objetivo

TicketFlow permite a equipos de trabajo registrar, gestionar y dar seguimiento a incidencias técnicas o solicitudes, con control de estados, roles de usuario y trazabilidad completa de cambios.

## Problema que Resuelve

- Centraliza la gestión de incidencias en un solo lugar
- Elimina la pérdida de información en correos o chats
- Proporciona trazabilidad de quién hizo qué cambio y cuándo
- Facilita la priorización y asignación de tareas

## Funcionalidades Principales

### Usuarios y Roles

- Registro y autenticación de usuarios
- Roles: `admin`, `user`, `superuser`
- Gestión de perfiles

### Tickets

- Creación de tickets con título y descripción
- Estados: `Pendiente` → `En progreso` → `Finalizado`
- Prioridades: `Baja`, `Media`, `Alta`
- Asignación a usuario creador
- **Trazabilidad**: Auditoría de cambios en campos

### Comentarios

- Comentarios en tickets para colaboración
- Relación usuario-ticket-comentario

## Stack tecnológico

- Backend: FastAPI
- ORM: SQLModel
- Bases de datos: SQLite
- Autenticación: JWT
- Documentación API: Swagger UI
