# UNEP KMaP Platform

## Table of Contents

-  [Quick Docker Start](#quick-docker-start)
-  [Start your server using Docker](#start-your-server-using-docker)
-  [Run the instance in development mode](#run-the-instance-in-development-mode)
-  [Run the instance on a public site](#run-the-instance-on-a-public-site)
-  [Stop the Docker Images](#stop-the-docker-images)
-  [Backup and Restore from Docker Images](#backup-and-restore-the-docker-images)

## Quick Docker Start

  ```bash
    python create-envfile.py 
  ```
`create-envfile.py` accepts the following arguments:

- `--https`: Enable SSL. It's disabled by default
- `--env_type`: 
   - When set to `prod` `DEBUG` is disabled and the creation of a valid `SSL` is requested to Letsencrypt's ACME server
   - When set to `test`  `DEBUG` is disabled and a test `SSL` certificate is generated for local testing
   - When set to `dev`  `DEBUG` is enabled and no `SSL` certificate is generated
- `--hostname`: The URL that whill serve GeoNode (`localhost` by default)
- `--email`: The administrator's email. Notice that a real email and a valid SMPT configurations are required if  `--env_type` is seto to `prod`. Letsencrypt uses to email for issuing the SSL certificate 
- `--geonodepwd`: GeoNode's administrator password. A random value is set if left empty
- `--geoserverpwd`: GeoNode's administrator password. A random value is set if left empty
- `--pgpwd`: PostgreSQL's administrator password. A random value is set if left empty
- `--dbpwd`: GeoNode DB user role's password. A random value is set if left empty
- `--geodbpwd`: GeoNode data DB user role's password. A random value is set if left empty
- `--clientid`: Client id of Geoserver's GeoNode Oauth2 client. A random value is set if left empty
- `--clientsecret`: Client secret of Geoserver's GeoNode Oauth2 client. A random value is set if left empty
```bash
  docker compose build
  docker compose up -d
```

### Start your server using Docker

You need Docker 1.12 or higher, get the latest stable official release for your platform.
Once you have the project configured run the following command from the root folder of the project.

1. Run `docker-compose` to start it up (get a cup of coffee or tea while you wait)

    ```bash
    docker-compose build --no-cache
    docker-compose up -d
    ```

    ```bash
    set COMPOSE_CONVERT_WINDOWS_PATHS=1
    ```

    before running `docker-compose up`

2. Access the site on http://localhost/

## Run the instance in development mode

### Use dedicated docker-compose files while developing

**NOTE**: In this example we are going to keep localhost as the target IP for GeoNode

  ```bash
  docker-compose -f docker-compose.development.yml -f docker-compose.development.override.yml up
  ```

## Run the instance on a public site

### Preparation of the image (First time only)

**NOTE**: In this example we are going to publish to the public IP http://123.456.789.111

```bash
vim .env
  --> replace localhost with 123.456.789.111 everywhere
```

### Startup the image

```bash
docker-compose up --build -d
```

### Stop the Docker Images

```bash
docker-compose stop
```

### Fully Wipe-out the Docker Images

**WARNING**: This will wipe out all the repositories created until now.

**NOTE**: The images must be stopped first

```bash
docker system prune -a
```

## Backup and Restore from Docker Images

### Run a Backup

```bash
SOURCE_URL=$SOURCE_URL TARGET_URL=$TARGET_URL ./infomapnode/br/backup.sh $BKP_FOLDER_NAME
```

- BKP_FOLDER_NAME:
  Default value = backup_restore
  Shared Backup Folder name.
  The scripts assume it is located on "root" e.g.: /$BKP_FOLDER_NAME/

- SOURCE_URL:
  Source Server URL, the one generating the "backup" file.

- TARGET_URL:
  Target Server URL, the one which must be synched.

e.g.:

```bash
docker exec -it django4infomapnode sh -c 'SOURCE_URL=$SOURCE_URL TARGET_URL=$TARGET_URL ./infomapnode/br/backup.sh $BKP_FOLDER_NAME'
```

### Run a Restore

```bash
SOURCE_URL=$SOURCE_URL TARGET_URL=$TARGET_URL ./infomapnode/br/restore.sh $BKP_FOLDER_NAME
```

- BKP_FOLDER_NAME:
  Default value = backup_restore
  Shared Backup Folder name.
  The scripts assume it is located on "root" e.g.: /$BKP_FOLDER_NAME/

- SOURCE_URL:
  Source Server URL, the one generating the "backup" file.

- TARGET_URL:
  Target Server URL, the one which must be synched.

e.g.:

```bash
docker exec -it django4infomapnode sh -c 'SOURCE_URL=$SOURCE_URL TARGET_URL=$TARGET_URL ./infomapnode/br/restore.sh $BKP_FOLDER_NAME'
```


## Test project generation and Docker swarm build on vagrant

What vagrant does:

Starts a vm for test on docker swarm:
    - configures a GeoNode project from template every time from your working directory (so you can develop directly on geonode-project).
    - exposes service on localhost port 8888
    - rebuilds everytime everything with cache [1] to avoid banning from docker hub with no login.
    - starts, reboots to check if docker services come up correctly after reboot.

To test on a docker swarm enable vagrant box:

```bash
vagrant up
VAGRANT_VAGRANTFILE=Vagrantfile.stack vagrant up
# check services are up upon reboot
VAGRANT_VAGRANTFILE=Vagrantfile.stack vagrant ssh geonode-compose -c 'docker service ls'
```

Test geonode on [http://localhost:8888/](http://localhost:8888/)
Again, to clean up things and delete the vagrant box:

```bash
VAGRANT_VAGRANTFILE=Vagrantfile.stack vagrant destroy -f
```

for direct deveolpment on geonode-project after first `vagrant up` to rebuild after changes to project, you can do `vagrant reload` like this:

```bash
vagrant up
```

What vagrant does (swarm or comnpose cases):

Starts a vm for test on plain docker service with docker-compose:
    - configures a GeoNode project from template every time from your working directory (so you can develop directly on geonode-project).
    - rebuilds everytime everything with cache [1] to avoid banning from docker hub with no login.
    - starts, reboots.

[1] to achieve `docker-compose build --no-cache` just destroy vagrant boxes `vagrant destroy -f`

