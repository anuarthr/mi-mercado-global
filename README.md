# Mi Mercado Global - API REST

API REST para una plataforma de e-commerce construida con **Django REST Framework**, **DynamoDB Local** y **Redis**. Proyecto académico para la asignatura de Bases de Datos No Relacionales.

---

## Integrantes

Anuarth Rincón
Camilo Álvarez
Danilo Díaz
Juan Narváez
Victor Jaimes

---

## Stack tecnológico

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.12 | Lenguaje base |
| Django | 5.0.4 | Framework web (sin ORM ni migraciones) |
| Django REST Framework | 3.15.1 | APIView, serializers, respuestas HTTP |
| boto3 | 1.34.84 | Cliente DynamoDB Local |
| redis | 5.0.4 | Cliente Redis (caché cache-aside) |
| gunicorn | 21.2.0 | Servidor WSGI de producción |
| drf-spectacular | 0.27.2 | Generación automática de Swagger UI |
| python-dotenv | 1.0.1 | Variables de entorno desde `.env` |
| awscli | 1.32.84 | Operaciones DynamoDB desde la terminal |
| Docker + Compose | — | Orquestación de servicios |

---

## Estructura del proyecto

```
ecommerce-project/
├── docker-compose.yml        # Orquesta DynamoDB Local, Redis y la API
├── Dockerfile                # Imagen de la API (Python 3.12-slim + gunicorn)
├── requirements.txt          # Dependencias Python
├── .env.example              # Plantilla de variables de entorno
├── .dockerignore             # Archivos excluidos del build de Docker
├── .gitignore                # Archivos excluidos de git
│
├── scripts/
│   ├── create_table.py       # Crea la tabla `mi_mercado` en DynamoDB Local
│   └── seed_data.py          # Inserta datos de prueba en la tabla
│
└── app/
    ├── manage.py             # Punto de entrada de Django CLI
    ├── config.py             # Inicializa el cliente boto3 (DynamoDB) y Redis
    │
    ├── core/
    │   ├── settings.py       # Configuración global de Django (lee desde .env)
    │   ├── urls.py           # Router principal: incluye URLs de cada módulo
    │   ├── views.py          # Endpoint /health/ (verifica DynamoDB y Redis)
    │   ├── wsgi.py           # Punto de entrada WSGI para gunicorn
    │   ├── exceptions.py     # Handler de excepciones personalizado de DRF
    │   ├── utils.py          # Constructores de claves PK/SK y generación de IDs
    │   └── cache.py          # Patrón cache-aside con Redis (get, set, invalidate)
    │
    ├── usuarios/
    │   ├── views.py          # POST /usuarios/, GET /usuarios/{id}/
    │   ├── urls.py           # Rutas del módulo usuarios
    │   ├── serializers.py    # Validación y serialización de perfiles
    │   ├── repository.py     # Operaciones DynamoDB: GetItem, PutItem (perfil)
    │   └── services.py       # Lógica de negocio: crear perfil, obtener con caché
    │
    ├── pedidos/
    │   ├── views.py          # POST /pedidos/, GET /usuarios/{id}/pedidos/, GET detalle
    │   ├── urls.py           # Rutas del módulo pedidos
    │   ├── serializers.py    # Validación y serialización de pedidos
    │   ├── repository.py     # Operaciones DynamoDB: PutItem, GetItem, Query
    │   └── services.py       # Lógica de negocio: escritura dual ORDER# + STATUS#
    │
    └── items/
        ├── views.py          # POST /pedidos/{id}/items/, GET /pedidos/{id}/items/
        ├── urls.py           # Rutas del módulo items
        ├── serializers.py    # Validación y serialización de ítems de pedido
        ├── repository.py     # Operaciones DynamoDB: PutItem, Query (ITEM#)
        └── services.py       # Lógica de negocio: agregar ítem, actualizar total
```

---

## Esquema DynamoDB — Single Table Design

Toda la información reside en una única tabla llamada `mi_mercado`. La clave primaria compuesta (`pk` + `sk`) permite modelar múltiples tipos de ítems y resolver todos los patrones de acceso sin índices secundarios.

### Tabla: `mi_mercado`

| `pk` (HASH) | `sk` (RANGE) | Atributos adicionales | Tipo de ítem |
|---|---|---|---|
| `USER#<userId>` | `PROFILE` | `nombre`, `email`, `direccion` | Perfil de usuario |
| `USER#<userId>` | `ORDER#<fecha>#<orderId>` | `estado`, `total` | Pedido |
| `USER#<userId>` | `STATUS#<estado>#<fecha>#<orderId>` | `total` | Pedido indexado por estado |
| `ORDER#<orderId>` | `ITEM#<productId>` | `nombre_producto`, `cantidad`, `precio` | Ítem de pedido |

> **Fechas** en formato ISO 8601 (`YYYY-MM-DD`) para que el ordenamiento lexicográfico de la SK coincida con el cronológico.

### Patrones de acceso (AP1–AP6)

#### AP1 — Obtener perfil de usuario
```
Operación : GetItem
pk        : USER#<userId>
sk        : PROFILE
```
Recupera un único ítem. Se almacena en Redis con TTL para evitar lecturas repetidas.

---

#### AP2 — Listar todos los pedidos de un usuario
```
Operación  : Query
pk         : USER#<userId>
Condición  : sk begins_with "ORDER#"
```
Devuelve todos los pedidos del usuario ordenados cronológicamente (la fecha forma parte de la SK).

---

#### AP3 — Ver detalle de un pedido específico
```
Operación : GetItem
pk        : USER#<userId>
sk        : ORDER#<fecha>#<orderId>
```
Acceso directo a un pedido conociendo su fecha e ID exactos.

---

#### AP4 — Ver ítems de un pedido
```
Operación  : Query
pk         : ORDER#<orderId>
Condición  : sk begins_with "ITEM#"
```
Devuelve todos los productos que componen un pedido.

---

#### AP5 — Filtrar pedidos de un usuario por estado
```
Operación  : Query
pk         : USER#<userId>
Condición  : sk begins_with "STATUS#<estado>#"
```
Los ítems `STATUS#` duplican la información del pedido con el estado como prefijo de SK, habilitando este filtro sin GSI.

---

#### AP6 — Filtrar pedidos por rango de fechas
```
Operación  : Query
pk         : USER#<userId>
Condición  : sk BETWEEN "ORDER#<desde>" AND "ORDER#<hasta>"
```
Funciona porque las fechas ISO 8601 son ordenables lexicográficamente. `<desde>` y `<hasta>` son fechas en formato `YYYY-MM-DD`.

---

## Decisión de caché por patrón de acceso

**Patrón aplicado:** *cache-aside* (lazy loading) con **Redis 7** como motor.

> **Cómo funciona:**
> 1. La Lambda consulta primero Redis con la clave de la entidad.
> 2. Si HIT → responde con el valor cacheado (`X-Cache: HIT`).
> 3. Si MISS → consulta DynamoDB, guarda el resultado en Redis con TTL y responde (`X-Cache: MISS`).
> 4. Cualquier escritura sobre la entidad invalida la clave para evitar leer datos obsoletos en la siguiente lectura.

### Tabla de decisión por AP

| AP | Endpoint | Operación DynamoDB | ¿Cachea? | TTL | Clave Redis | Invalidación |
|---|---|---|---|---|---|---|
| AP1 | `GET /usuarios/{userId}` | GetItem | ✅ Sí | 300 s | `perfil:{userId}` | `POST /usuarios/` invalida la clave del mismo `userId` |
| AP2 | `GET /usuarios/{userId}/pedidos` (sin filtros) | Query | ✅ Sí | 300 s | `pedidos:{userId}` | `POST /pedidos/` invalida la clave del mismo `userId` |
| AP3 | `GET /pedidos/{pedidoId}` | GetItem | ✅ Sí | 300 s | `pedido:{pedidoId}` | No requiere — el `orderId` es nuevo en cada creación |
| AP4 | `GET /pedidos/{pedidoId}/items` | Query | ✅ Sí | 300 s | `items:{pedidoId}` | `POST /pedidos/{pedidoId}/items` invalida la clave |
| AP5 | `GET /usuarios/{userId}/pedidos?estado=` | Query | ❌ No | — | — | Filtro esporádico — consulta directa a DynamoDB |
| AP6 | `GET /usuarios/{userId}/pedidos?desde=&hasta=` | Query | ❌ No | — | — | Filtro esporádico — consulta directa a DynamoDB |

### Por qué cachear o no

- **AP1, AP3** (lecturas puntuales con `GetItem`): se cachean porque es el patrón clásico donde Redis brilla — clave estable, lectura frecuente, dato pequeño.
- **AP2, AP4** (listas asociadas a una entidad): se cachean porque "Mis Pedidos" y "ítems del pedido" se consultan repetidamente al navegar; la invalidación es simple (un solo punto de escritura por colección).
- **AP5, AP6** (consultas con filtros): **no** se cachean. Cada combinación de filtros generaría una clave distinta y una matriz de invalidación impráctica. Para los volúmenes de un curso, va directo a DynamoDB.

### TTL único de 300 s

Todas las claves usan `DEFAULT_TTL = 300` ([`lambda/shared/cache.py`](lambda/shared/cache.py)). Es un compromiso académico: lo bastante largo para que la caché tenga sentido al hacer demos, lo bastante corto para que datos huérfanos (si se nos escapara una invalidación) se auto-curen en 5 minutos.

---