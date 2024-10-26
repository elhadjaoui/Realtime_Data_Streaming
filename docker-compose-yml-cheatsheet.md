# Detailed Docker Compose YAML File Cheat Sheet

## Basic Structure

```yaml
version: '3'  # Specifies the version of Docker Compose file format
services:     # Defines the containers that should be created
  service_name:  # Name of your service
    # service configuration
volumes:      # Defines named volumes that can be reused across multiple services
  # volume configuration
networks:     # Defines custom networks for your services
  # network configuration
```

## Service Configuration Options

### Image and Build

```yaml
services:
  service_name:
    image: nginx:latest  # Use a pre-built image from a registry
    # OR
    build:  # Build a custom image
      context: ./dir  # The build context (usually the directory containing the Dockerfile)
      dockerfile: Dockerfile  # The name of the Dockerfile to use
      args:  # Build arguments to pass to the Dockerfile
        buildno: 1
```
Description: Specifies the image to use for the container. You can either use a pre-built image from a registry or build a custom image using a Dockerfile.

### Container Name and Hostname

```yaml
services:
  service_name:
    container_name: my-web-container  # Sets a custom name for the container
    hostname: my-web-host  # Sets the hostname inside the container
```
Description: Allows you to set a custom name for the container and specify its internal hostname.

### Port Mapping

```yaml
services:
  service_name:
    ports:
      - "8080:80"  # Maps host port 8080 to container port 80
      - "9000-9100:9000-9100"  # Maps a range of ports
```
Description: Maps ports from the host to the container, allowing external access to services running inside the container.

### Environment Variables

```yaml
services:
  service_name:
    environment:  # Set environment variables directly
      - RACK_ENV=development
    # OR
    env_file:  # Load environment variables from files
      - ./common.env
      - ./apps/web.env
```
Description: Sets environment variables for the container, either directly in the compose file or by loading from external files.

### Volumes

```yaml
services:
  service_name:
    volumes:
      - /var/lib/mysql  # Creates an anonymous volume
      - data:/var/lib/mysql  # Uses a named volume
      - ./cache:/tmp/cache  # Binds a host directory to a container path
```
Description: Mounts volumes to the container, allowing data persistence and sharing between the host and containers.

### Networks

```yaml
services:
  service_name:
    networks:
      - frontend  # Connects the service to the 'frontend' network
      - backend   # Connects the service to the 'backend' network
```
Description: Specifies which custom networks the service should join, allowing controlled communication between services.

### Dependencies

```yaml
services:
  service_name:
    depends_on:
      - db  # This service depends on the 'db' service
      - redis  # This service also depends on the 'redis' service
```
Description: Expresses dependency between services, ensuring that dependent services are started before this service.

### Restart Policy

```yaml
services:
  service_name:
    restart: always  # Always restart the container if it stops
    # Other options: "no", "on-failure", "unless-stopped"
```
Description: Configures how the container should be restarted if it exits or the Docker daemon restarts.

### Resource Limits

```yaml
services:
  service_name:
    deploy:
      resources:
        limits:
          cpus: '0.50'  # Limit CPU usage to 50% of a core
          memory: 50M   # Limit memory usage to 50 megabytes
        reservations:
          cpus: '0.25'  # Reserve 25% of a CPU core
          memory: 20M   # Reserve 20 megabytes of memory
```
Description: Sets resource constraints for the service, limiting or reserving CPU and memory.

### Healthcheck

```yaml
services:
  service_name:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]  # The command to run to check health
      interval: 1m30s  # Time between health checks
      timeout: 10s     # Time to wait for a response
      retries: 3       # Number of consecutive failures needed to consider unhealthy
      start_period: 40s  # Initial delay before starting health checks
```
Description: Configures a health check for the service, allowing Docker to monitor its status and restart if necessary.

### Logging

```yaml
services:
  service_name:
    logging:
      driver: "json-file"  # The logging driver to use
      options:
        max-size: "200k"   # Maximum size of log files
        max-file: "10"     # Maximum number of log files
```
Description: Configures logging for the service, specifying the logging driver and any associated options.

### User and Working Directory

```yaml
services:
  service_name:
    user: "1000:1000"  # The user:group to run the container as
    working_dir: /code  # The working directory inside the container
```
Description: Specifies the user and working directory for the container, affecting permissions and the default directory for commands.

### Command and Entrypoint

```yaml
services:
  service_name:
    command: bundle exec thin -p 3000  # The command to run when the container starts
    entrypoint: /code/entrypoint.sh  # The entrypoint script to run
```
Description: Overrides the default command and entrypoint of the container image.

## Volume Configuration

```yaml
volumes:
  data:
    driver: local  # The volume driver to use
    driver_opts:  # Driver-specific options
      type: "nfs"
      o: "addr=10.40.0.199,nolock,soft,rw"
      device: ":/docker/example"
```
Description: Defines named volumes that can be used by services, specifying the driver and any driver-specific options.

## Network Configuration

```yaml
networks:
  frontend:
    driver: bridge  # The network driver to use
    ipam:  # IP Address Management
      driver: default
      config:
        - subnet: 172.16.238.0/24  # The subnet to use for this network
```
Description: Defines custom networks for services, specifying the network driver and IP address management configuration.

## Advanced Features

### Extends

```yaml
services:
  web:
    extends:
      file: common-services.yml  # The file to extend from
      service: webapp  # The service to extend
```
Description: Allows sharing of common configurations between services, potentially across multiple compose files.

### Configs

```yaml
services:
  service_name:
    configs:
      - source: my_config  # The name of the config
        target: /redis_config  # Where to mount the config in the container
        uid: '103'  # The user ID to own the config file
        gid: '103'  # The group ID to own the config file
        mode: 0440  # The permissions of the config file
configs:
  my_config:
    file: ./my_config.txt  # The file to use as the config
```
Description: Allows services to access configuration files, providing a way to manage configuration separately from image content.

### Secrets

```yaml
services:
  service_name:
    secrets:
      - db_password  # The name of the secret to use
secrets:
  db_password:
    file: ./db_password.txt  # The file containing the secret
```
Description: Provides a way to manage sensitive data, such as passwords or API keys, separately from the service definition.

### Profiles

```yaml
services:
  frontend:
    image: frontend
    profiles: ["frontend", "debug"]  # This service is part of these profiles

  phpmyadmin:
    image: phpmyadmin
    profiles: ["debug"]  # This service is only part of the debug profile
```
Description: Allows grouping of services into different profiles, enabling selective service startup based on the current use case or environment.

