# Agenda SaaS

Plataforma de agenda y reservas online para PYMEs de servicios.  
Stack: React 18 + Python/Django 5 + PostgreSQL + Celery + Redis.

---

## Requisitos previos

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- Git

---

## Setup local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/agenda-saas.git
cd agenda-saas
```

### 2. Levantar servicios (PostgreSQL + Redis)

```bash
docker compose up -d
```

### 3. Configurar el backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # edita .env con tus valores
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver      # → localhost:8000
```

### 4. Configurar el frontend (React)

```bash
cd frontend
npm install
npm run dev                     # → localhost:5173
```

### 5. Iniciar Celery (recordatorios automáticos)

```bash
cd backend
source venv/bin/activate
celery -A core worker -l info
```

---

## Estructura del proyecto

```
agenda-saas/
├── backend/
│   ├── core/                 # Configuración Django (settings, urls, wsgi)
│   ├── apps/
│   │   ├── users/            # M1: Autenticación y roles
│   │   ├── businesses/       # M2-M4: Negocio, servicios, staff
│   │   ├── appointments/     # M5-M7: Horarios, reservas, agenda
│   │   ├── notifications/    # M8: Emails y WhatsApp
│   │   └── subscriptions/    # M9-M10: Pagos y reportes
│   ├── requirements.txt
│   ├── manage.py
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/         # Llamadas a la API
│   │   └── store/            # Estado global (Zustand)
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Scripts útiles

| Comando | Descripción |
|---------|-------------|
| `docker compose up -d` | Levantar DB y Redis |
| `docker compose down` | Detener servicios |
| `python manage.py makemigrations` | Crear migraciones |
| `python manage.py migrate` | Aplicar migraciones |
| `pytest` | Correr tests |
| `npm run build` | Build de producción |

---

## Variables de entorno

Copia `backend/.env.example` a `backend/.env` y completa:

- `SECRET_KEY` — genera una con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `SENDGRID_API_KEY` — cuenta gratuita en sendgrid.com
- `STRIPE_SECRET_KEY` — usar clave de **test** durante desarrollo
- El resto de las variables están documentadas en el archivo `.env.example`

---

## Flujo de ramas

```
main        ← solo merges al final de cada sprint (código listo para producción)
develop     ← rama de integración
feature/*   ← una rama por funcionalidad (ej: feature/auth-jwt)
```

---

## Equipo

| Rol | Persona |
|-----|---------|
| Desarrollador fullstack | Juan |
