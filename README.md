# Proyecto Backend Roles - Django REST Framework

Este proyecto fue desarrollado con **Django** y **Django REST Framework** como parte del **Módulo 04: Pruebas de Software y Calidad** del Instituto **IDAT**.

El sistema permite gestionar **usuarios, roles y planos** mediante una **API REST**, integrando funcionalidades CRUD (Crear, Leer, Actualizar, Eliminar).

---


## 👨‍🏫 Docente responsable

- **Ing. Marco Manrique**

---


## 👥 Integrantes del equipo

- **Kadú Desposorio**
- **Nataly Salcedo**
- **Nayeli De La Cruz**

---

## ⚙️ Instalación y configuración

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/tuusuario/nombre-repo.git
   ```

2. **Crea y activa un entorno virtual.**

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

---

## 🔗 Endpoints principales

| Método | Endpoint | Descripción |
|--------|-----------|-------------|
| **GET** | `/api/planos/` | Lista todos los planos registrados |
| **POST** | `/api/planos/` | Crea un nuevo plano |
| **PUT** | `/api/planos/<id>/` | Actualiza un plano existente |
| **DELETE** | `/api/planos/<id>/` | Elimina un plano existente |
| **GET** | `/admin/` | Acceso al panel administrativo de Django |

---

## 🧰 Tecnologías utilizadas

- Python 3.11  
- Django 5.2  
- Django REST Framework  
- SQLite3  
- Postman (para pruebas de API)

---

## 📦 Estructura general del proyecto

```
IDAT_PY_MODULO_04/
│
├── backend_roles/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── planos/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│
├── usuarios/
│   ├── models.py
│   ├── views.py
│
├── venv/
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🧾 Archivo .gitignore recomendado

```
# Entorno virtual
venv/
.env/

# Archivos de Python compilados
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so

# Archivos de base de datos temporales
db.sqlite3

# Archivos del sistema
.DS_Store
Thumbs.db

# Archivos de VSCode
.vscode/

# Archivos de logs
*.log

# Archivos temporales
*.bak
*.swp
*.tmp
```

---

## 📋 Generar archivo requirements.txt

Ejecuta el siguiente comando dentro del entorno virtual:

```bash
pip freeze > requirements.txt
```

---

## 💬 Notas finales

**El proyecto acttualmente se encuentra en proceso de desarrollo**

**IDAT - 2025** 💻