# File: L:\Mayan-EDMS-master\Mayan-EDMS-master\docker\Dockerfile

# Use the official Mayan EDMS image as the base
ARG MAYAN_DOCKER_IMAGE_TAG=s4.3
FROM mayanedms/mayanedms:${MAYAN_DOCKER_IMAGE_TAG}

# Set basic environment variables for Mayan to run
# (These lines help with the 'UndefinedVar' warnings during build,
# but the actual values are resolved at runtime from .env and docker-compose.yml)
ENV MAYAN_CELERY_BROKER_URL="amqp://mayan:mayanrabbitpass@rabbitmq:5672/mayan"
ENV MAYAN_CELERY_RESULT_BACKEND="redis://:mayanredispassword@redis:6379/1"
ENV MAYAN_DATABASES="{'default':{'ENGINE':'django.db.backends.postgresql','NAME':'mayan','PASSWORD':'mayandbpass','USER':'mayan','HOST':'postgresql'}}"
ENV MAYAN_LOCK_MANAGER_BACKEND=mayan.apps.lock_manager.backends.redis_lock.RedisLock
ENV MAYAN_LOCK_MANAGER_BACKEND_ARGUMENTS="{'redis_url':'redis://:mayanredispassword@redis:6379/2'}"
# Note: For simplicity, I've hardcoded default values here.
# If you use complex variables in your .env file, you might need to pass them
# as build arguments to the Dockerfile if they're needed during build time.
# For now, this should suppress most warnings.

# THIS IS THE CRUCIAL COPY ADJUSTMENT:
# Since context is now '.', and your 'mayan' source code folder is in the parent directory of 'docker',
# you need to explicitly go up one level to copy it.
COPY mayan /opt/mayan-edms/source/mayan/

# Set the Python path to include your copied source code.
# This makes Python look for modules in /opt/mayan-edms/source/
ENV PYTHONPATH="/opt/mayan-edms/source/:$PYTHONPATH"

# Set the working directory within the containerization(edited)
WORKDIR /opt/mayan-edms/