# TicketFlow

TicketFlow es una aplicación de gestión de tickets desarrollada con **FastAPI** y **SQLModel**, con foco en autorización combinada (RBAC + ABAC), una máquina de estados (FSM) para el ciclo de vida del ticket, y listados paginados con búsqueda/filtrado/ordenamiento unificados.

## Objetivo

TicketFlow permite a personas y equipos de trabajo registrar, gestionar y dar seguimiento a incidencias técnicas o solicitudes, con control de estados, roles de usuario y trazabilidad completa de cambios.

- Centraliza la gestión de incidencias o solicitudes en un solo lugar
- Elimina la pérdida de información en correos o chats
- Proporciona trazabilidad de quién hizo qué cambio y cuándo (auditoría)
- Facilita la priorización y asignación de tareas

## Stack tecnológico

- **Backend**: FastAPI
- **ORM**: SQLModel / Pydantic
- **Base de datos**: SQLite
- **Autenticación**: JWT (con blacklist de tokens para logout)
- **Documentación API**: Swagger UI (`/docs`)

## Arquitectura

El proyecto sigue un patrón por capas **Router → Service → Repository**:

```
app/
├── api/
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── usuario_router.py
│   │   ├── ticket_router.py
│   │   ├── comentario_router.py
│   │   ├── compartir_router.py
│   │   └── auditoria_router.py
│   └── dependencias.py        # Auth (JWT), RBAC (VerificarRol) y por-permiso (VerificarPermisos)
├── models/                    # Entidades SQLModel (tablas)
│   ├── usuario.py
│   ├── ticket.py
│   ├── comentario.py
│   ├── compartir_ticket.py
│   ├── auditoria.py
│   └── token_black_list.py
├── schemas/                   # Esquemas Pydantic de entrada/salida
├── services/                  # Lógica de negocio y reglas de autorización ABAC
├── repositories/              # Acceso a datos (SQLModel/SQLAlchemy)
└── core/
    ├── config.py               # Configuración (.env)
    ├── db.py                   # Conexión / sesión de BD
    ├── seguridad.py             # JWT, hashing, roles y permisos (RBAC)
    └── ticket_fsm.py            # Máquina de estados del ticket
```

### Autorización: RBAC + ABAC

- **RBAC (nivel router)**: cada endpoint sensible depende de `VerificarPermisos`, que valida contra los permisos explícitos del usuario o, en su ausencia, contra los permisos por defecto de su rol (`PERMISOS_POR_ROL`). Los roles son `user`, `admin` y `superadmin`; `admin` no tiene permisos por defecto (regla general de autorización del sistema).
- **ABAC (nivel service/repository)**: el acceso a un ticket, comentario o "compartir" específico depende de si el usuario es propietario, asignado, tiene el recurso compartido, o es `superadmin`. Esto se resuelve con el patrón `ids_permitidos`: `superadmin` recibe `None` (sin filtro) y el resto recibe la unión de sus IDs propios/asignados/compartidos (`set` union).

### FSM de tickets

Los tickets siguen el ciclo `PENDIENTE → EN_PROGRESO → FINALIZADO`, validado por `TicketFSM` (`app/core/ticket_fsm.py`), que rechaza cualquier transición fuera de ese orden.

## Instalación y ejecución

### Requisitos
- Python 3.11+
- pip

### Instalación
```bash
git clone https://github.com/DanielAlexanderDiaz/TicketFlow.git
cd TicketFlow

python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Crear un archivo `.env` en la raíz con las siguientes variables (usadas por `app/core/config.py`):
```
DATABASE_URL=sqlite:///./ticketflow.db
JWT_SECRET_KEY=tu_clave_secreta
JWT_ALGORITMO=HS256
JWT_TIEMPO_EXPIRACION=60
```

### Ejecutar la aplicación
```bash
uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

Todas las rutas están montadas bajo el prefijo `/api/v1`.

## Endpoints implementados

### Autenticación (`/api/v1/auth`)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` | Registra un usuario nuevo (rol `user` por defecto) |
| POST | `/auth/login` | Login con email/password, devuelve token JWT |
| POST | `/auth/token` | Login compatible con `OAuth2PasswordRequestForm` (usado por Swagger UI) |
| POST | `/auth/logout` | Invalida el token actual (blacklist) |

### Usuarios (`/api/v1/usuario`)
| Método | Ruta | Descripción | Requiere |
|---|---|---|---|
| PATCH | `/usuario/nombre/{id_usuario}` | Actualiza el nombre del propio usuario | Usuario autenticado |
| PATCH | `/usuario/foto/{id_usuario}` | Actualiza la foto de perfil | Usuario autenticado |
| DELETE | `/usuario/eliminar/{id_usuario}` | Elimina un usuario | `superadmin` |
| PATCH | `/usuario/rol/{id_usuario}` | Actualiza el rol de un usuario | `superadmin` |
| PATCH | `/usuario/permisos/{id_usuario}` | Actualiza permisos explícitos de un usuario | `superadmin` |
| PATCH | `/usuario/activo/{id_usuario}` | Activa/desactiva un usuario | `superadmin` |
| GET | `/usuario/usuarios` | Listado paginado con búsqueda (email, nombre), filtro (rol, activo) y ordenamiento | `superadmin` |

### Tickets (`/api/v1/ticket`)
| Método | Ruta | Descripción | Permiso |
|---|---|---|---|
| POST | `/ticket/crear` | Crea un ticket | `puede_crear_ticket` |
| PATCH | `/ticket/actualizar/{id_ticket}` | Actualiza título/descripción/prioridad (ABAC: propietario, asignado, compartido o superadmin) | `puede_actualizar_ticket` |
| DELETE | `/ticket/eliminar/{id_ticket}` | Elimina el ticket junto a sus comentarios y "compartir" asociados | `puede_eliminar_ticket` |
| PATCH | `/ticket/estado/{id_ticket}` | Cambia el estado siguiendo la FSM (`pendiente → en_progreso → finalizado`) | `puede_cambiar_estado_ticket` |
| PATCH | `/ticket/asignar/{id_ticket}` | Asigna el ticket a un usuario | `puede_asignar_ticket` |
| PATCH | `/ticket/quitar_asignar/{id_ticket}` | Quita la asignación del ticket | `puede_desasignar_ticket` |
| GET | `/ticket/tickets` | Listado paginado unificado: búsqueda (título, descripción), filtros (N° ticket, prioridad, estado, asignado, rango de fechas) y ordenamiento. ABAC vía `ids_permitidos` | Usuario autenticado |

> **Nota**: la subida de imagen de ticket (`app/utils/uploads_file.py`) y la vigencia (activo/inactivo) del ticket están soportadas a nivel de modelo pero aún no tienen ruta expuesta en `ticket_router.py`.

### Comentarios (`/api/v1/comentario`)
| Método | Ruta | Descripción | Permiso |
|---|---|---|---|
| POST | `/comentario/?id_ticket={id}` | Crea un comentario (ABAC: propietario, asignado, compartido o superadmin del ticket) | `puede_crear_comentario` |
| PATCH | `/comentario/{id_comentario}?id_ticket={id}` | Actualiza un comentario, solo si es el último del ticket y es propio | `puede_actualizar_comentario` |
| DELETE | `/comentario/{id_comentario}?id_ticket={id}` | Elimina un comentario, solo si es el último del ticket y es propio | `puede_eliminar_comentario` |
| GET | `/comentario/comentarios` | Listado paginado con filtros (ticket, usuario, comentario, fechas) y ordenamiento, con ABAC | Usuario autenticado |

> **Problema conocido**: `ComentarioRepositorio.ultimo_comentario()` usa `.one()`, lo que lanza una excepción no controlada cuando el ticket todavía no tiene comentarios (por ejemplo, al intentar actualizar/eliminar sobre un ticket sin comentarios). Está pendiente manejarlo explícitamente (ver sección "Próximos pasos").

### Compartir (`/api/v1/compartir`)
| Método | Ruta | Descripción | Permiso |
|---|---|---|---|
| POST | `/compartir/compartir/{id_ticket}` | Comparte un ticket con otro usuario (ABAC: propietario, asignado o superadmin) | `puede_compartir_ticket` |
| DELETE | `/compartir/quitar_compartir/{id_ticket}` | Quita el ticket compartido a un usuario destino | `puede_descompartir_ticket` |
| GET | `/compartir/compartidos` | Listado paginado con filtros (ticket, usuario origen/destino, fecha) y ordenamiento, con ABAC | Usuario autenticado |

### Auditoría (`/api/v1/auditoria`)
| Método | Ruta | Descripción | Requiere |
|---|---|---|---|
| GET | `/auditoria/auditoria` | Listado paginado de eventos de auditoría (usuario, ticket, comentario, compartir), con búsqueda, filtros y ordenamiento | `superadmin` |

## Modelo de datos (resumen)

- **Usuario**: id, nombre_usuario, email, password (hash), rol, fecha_creacion, activo, imagen_url, permiso (lista de permisos explícitos, opcional)
- **Ticket**: id, titulo, descripcion, fecha_creacion, fecha_actualizacion, estado, prioridad, id_usuario_creador, asignado, activo, imagen_url
- **TicketCompartir**: id, id_ticket, id_usuario_origen, id_usuario_destino, fecha_creacion
- **Comentario**: id, id_ticket, id_usuario, comentario, fecha_creacion, fecha_actualizacion
- **Auditoria**: id, entidad, id_entidad, id_usuario, campo_cambiado, fecha_cambio, valor_anterior, valor_nuevo, accion
- **TokenBlackList**: id, jti, expira_en, creado_en (para invalidar tokens en logout)

## Patrón de listados (búsqueda + filtro + orden + paginación)

Todos los listados (`/usuario/usuarios`, `/ticket/tickets`, `/comentario/comentarios`, `/compartir/compartidos`, `/auditoria/auditoria`) siguen el mismo patrón en el repositorio:

1. Búsqueda por coincidencia parcial (`ilike`) sobre campos de texto
2. Filtrado por coincidencia exacta (`==`) sobre campos categóricos/IDs/fechas
3. Ordenamiento dinámico según un mapa de columnas permitidas
4. Paginación con `limit`/`offset`, calculando `total` y `total_paginas`

Estas cuatro operaciones se ejecutan en una sola consulta, evitando separarlas en llamadas independientes.

## Próximos pasos

- Corregir el `ultimo_comentario()` de `ComentarioRepositorio` para que no lance excepción cuando el ticket no tiene comentarios
- Exponer rutas pendientes: visualización de un ticket individual (RF-17, distinta del listado paginado), subida de imagen y cambio de vigencia (activo/inactivo) del ticket
- Adoptar disciplina **API-First**: escribir los contratos OpenAPI (YAML) en una carpeta `openapi/` antes de implementar nuevos endpoints
- Exportar el `/openapi.json` actual como línea base y versionarlo en el repositorio
- Validar los contratos con `schemathesis`

## Licencia

Proyecto educativo, desarrollado como ejercicio de aprendizaje de backend con FastAPI y SQLModel.