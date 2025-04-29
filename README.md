# Servicios Web CRUD para revelacion de imagen

Este repositorio contiene los servicios web CRUD de la base de datos diseñada para Lienzo, además de el archivo que inicia y crea las tablas correspondientes a la base de datos. Se incluyen datos de prueba para la demostración de su funcionamiento. En caso de no necesitarlos, su eliminación no afectará el funcionamiento.

## Prerequisitos

Antes de comenzar, asegúrate de tener:

- **GitHub Codespaces** habilitado.
- **Docker** ejecutándose en tu Codespace.
- **Python 3** instalado.
- **pymssql** instalado en tu entorno Python.

### Iniciar la instancia de SQL Server en Docker

Para iniciar una instancia de **SQL Server** en un contenedor Docker, ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourPassword123!' \
   -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
```

### Instalar sqlcmd
```sh
sudo apt update
sudo apt install mssql-tools unixodbc-dev
source ~/.bashrc
```
### Usar sqlcmd para inicializar la base de datos con las tablas desde la terminal.
```sh
sqlcmd -S localhost -U sa -P YourPassword123! -i init_db.sql
```
### Para insertar datos a la base.
```sh
sqlcmd -S localhost -U sa -P YourPassword123! -i datos.sql
```
# Probar servicios web

## Prerequisitos

- Se ejecutó el comando que lee el archivo sql:
```sh
sqlcmd -S localhost -U sa -P YourPassword123! -i init_db.sql
```

### Ejecución de servidor de servicios web

Ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
cd web\ services/
python CRUDServer.py

```

