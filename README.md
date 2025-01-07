## Tech Stack

- **UI**: ShadCN & Tailwind CSS
- **Frontend**: Next.js
- **Backend**: Django
- **Database**: SQLite (or MSSQL in production)
- **API Communication**: REST

## Pre-requisites

1. **Docker**
2. **ODBC Driver for SQL Connection**: [Microsoft ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Docker Commands

If the frontend container fails, you might need to install dependencies:

```bash
npm install next
```

### 1. **Run Both Backend and Frontend Containers**

```bash
docker-compose up --build
```

Ensure dependencies are listed in `requirements.txt` for Django.

### 2. **Run Backend Container**

```bash
docker-compose run backend
```

Make sure to include dependencies in `requirements.txt` for Django.

### 3. **Run Frontend Container**

```bash
docker-compose run frontend
```

## Development Directories

- **Frontend (Next.js)**:

  ```bash
  cd sunshine_frontend
  ```

- **Backend (Django)**:

  ```bash
  cd sunshine_backend
  ```

## Database (MSSQL)

- **Connect to the Database Using**:

  ```bash
  sqlcmd -S tcp:sunshine-web-db-server.database.windows.net,1433 -d sunshine -U sunshine_admin -P Minh@sit -N -C -l 30
  ```

- **For Windows (Installation of `sqlcmd`)**:

  ```bash
  winget install sqlcmd
  ```

---
