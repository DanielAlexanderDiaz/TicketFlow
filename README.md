# TicketFlow

TicketFlow es una aplicación de gestión de tickets desarrollada con FastAPI y SQLModel

## Objetivo

TicketFlow permite a equipos de trabajo registrar, gestionar y dar seguimiento a incidencias técnicas o solicitudes, con control de estados, roles de usuario y trazabilidad completa de cambios.

## Problema que Resuelve

- Centraliza la gestión de incidencias en un solo lugar
- Elimina la pérdida de información en correos o chats
- Proporciona trazabilidad de quién hizo qué cambio y cuándo
- Facilita la priorización y asignación de tareas

## Funcionalidades Principales (Implementadas)

### Usuarios y Roles

- ✅ Registro y autenticación de usuarios
- ✅ Roles: `admin`, `user`, `superuser`
- ✅ Gestión de perfiles
- ✅ Carga de imagen de perfil

### Tickets

- ✅ Creación de tickets con título y descripción
- ✅ Estados: `Pendiente` → `En progreso` → `Finalizado`
  - Validación de transiciones permitidas
  - Cambio de estado con endpoint dedicado
- ✅ Prioridades: `Baja`, `Media`, `Alta`
- ✅ Asignación a usuario creador
- ✅ Listado de tickets (usuarios ven sus tickets, admins ven todos)
- ✅ Listado paginado con filtros por estado, prioridad, vigencia, título
- ✅ Actualización de tickets
- ✅ Control de vigencia (activo/inactivo)
- ✅ Carga de imagen en tickets
- ✅ **Trazabilidad**: Auditoría completa de cambios en campos
- ✅ Historial de cambios por ticket

### Comentarios

- ✅ Comentarios en tickets para colaboración
- ✅ Relación usuario-ticket-comentario

### Compartir Tickets

- ✅ Funcionalidad para compartir tickets entre usuarios

## Stack tecnológico

- Backend: FastAPI
- ORM: SQLModel
- Bases de datos: SQLite
- Autenticación: JWT
- Documentación API: Swagger UI

## Estructura del Proyecto

```
app/
├── api/
│   ├── routers/           # Endpoints de la API
│   │   ├── auth_router.py
│   │   ├── usuario_router.py
│   │   ├── ticket_router.py
│   │   ├── comentario_router.py
│   │   ├── compartir_router.py
│   └── dependencias.py    # Dependencias comunes (auth, db, etc.)
├── models/                # Modelos de base de datos
│   ├── usuario.py
│   ├── ticket.py
│   ├── comentario.py
│   ├── compartir_ticket.py
│   └── auditoria.py
├── schemas/               # Esquemas de validación Pydantic
├── services/              # Lógica de negocio
│   ├── ticket_estado_services.py
│   ├── ticket_services.py
│   └── otros...
├── repositories/          # Acceso a datos
└── core/
    ├── config.py         # Configuración
    ├── db.py            # Conexión a BD
    └── seguridad.py     # Funciones de seguridad
```

## Estado Actual del Proyecto

- **Funcionalidades Core**: Implementadas ✅
  - Gestión completa de usuarios y autenticación
  - CRUD de tickets con validación de estados
  - Sistema de auditoría
  - Comentarios y compartir tickets

- **En Desarrollo**: 
  - Mejora de la funcionalidad de cambio de estado (ver commit: "se agrega funcionalidad de cambiar estado del ticket pero falta mejorar")

## Instalación y Ejecución

### Requisitos
- Python 3.9+
- pip

### Instalación
```bash
# Clonar repositorio
git clone <repo-url>
cd TicketFlow

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`
La documentación Swagger en `http://localhost:8000/docs`

## Endpoints Principales

### Autenticación
- `POST /auth/login` - Obtener token JWT
- `POST /auth/register` - Registrar nuevo usuario

### Tickets
- `GET /ticket/listar` - Listar tickets del usuario actual
- `GET /ticket/listar_todos` - Listar todos los tickets (admin)
- `GET /ticket/listar_paginado` - Listado paginado con filtros
- `POST /ticket/` - Crear nuevo ticket
- `GET /ticket/` - Obtener información de un ticket
- `PATCH /ticket/{id_ticket}` - Actualizar ticket
- `PATCH /ticket/{id_ticket}/estado` - Cambiar estado del ticket
- `PATCH /ticket/{id_ticket}/imagen` - Subir imagen al ticket
- `PATCH /ticket/{id_ticket}/vigencia` - Marcar ticket como activo/inactivo
- `GET /ticket/{id_ticket}/historial` - Ver historial de cambios

### Usuarios
- `GET /usuario/` - Información del usuario actual
- `PATCH /usuario/` - Actualizar perfil
- `PATCH /usuario/imagen` - Cambiar foto de perfil

### Comentarios
- `POST /comentario/` - Crear comentario en ticket
- `GET /comentario/` - Obtener comentarios de un ticket

### Compartir
- `POST /compartir/` - Compartir ticket con otro usuario