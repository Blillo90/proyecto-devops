# Visión general
El objetivo del proyecto es construir un sistema web altamente disponible, escalable y automatizado aplicando principios DevOps

- Infraestructura como Código (IaC) con Ansible
- Orquestación de contenedores (K3s / Kubernetes (k8s))
- Despliegue continuo con posibilidad de mejoras futuras
- Servicios web fiables, con persistencia

La plataforma consiste en:

- Una aplicación web Flask, basada en un gestor de incidencias similar al que tenemos en Accenture / Airbus
- Una base de datos PostgreSQL con persistencia para la aplicación
- Un Ingress Controller (Traefik) actuando como reverse proxy
- Un clúster k3s con 3 nodos
- Despliegue automatizado con Ansible

## Arquitectura física

El clúster está formado por 3 máquinas Ubuntu Server:

- k8s-master --> Control + nodo de control Ansible --> 192.168.56.10
- k8s-worker1 --> Worker --> 192.168.56.11
- k8s-worker2 --> Worker --> 192.168.56.12

Red configurada en VirtualBox:

- NAT --> enp0s3 --> Salida a internet
- Host-only --> 192.168.56.0/24 --> Para comunicación interna entre nodos

El nodo actúa como máquina control, donde se ejecuta Ansible

### Arquitectura lógica (Kubernetes)

El sistema se despliega en un namespace dedicado (produccion)

Componentes dentro del namespace:

1. Deployment de aplicación web

- Imagen Docker de Flask
- 2 réplicas por defecto
- Probes de liveness/readiness mediante /health
- Variables de entorno apuntando a PostgreSQL

2. Service de la aplicación

- Tipo: ClusterIP
- Expone puerto interno 5000
- Balanceo de réplicas del Deployment

3. Base de datos PostgreSQL

- Deployment de 1 réplica
- PVC de 2 Gb para persistencia
- Service interno accesible sólo desde el cluster

4. PersistentVolumeClaim (PVC)

- Garantiza almacenamiento duradero en '/var/lib/postresql/data'

5. Ingress

- Gestionado por Traefik (incluído en k3s)
- Expone app mediante dominio interno gestor.local
- Hace de reverse proxy con servicio 'app'


#### Diagrama de Arquitectura

                        ┌──────────────────────────┐
                        │     Usuario / Cliente    │
                        └──────────────┬───────────┘
                                       │ HTTP
                                       ▼
                         ┌────────────────────────┐
                         │   Ingress (Traefik)    │
                         └───────────┬────────────┘
                                     │
                     ┌───────────────┼──────────────────┐
                     ▼                                  ▼
           ┌────────────────────┐           ┌──────────────────────┐
           │  Service: app      │           │  Service: postgres   │
           │  (ClusterIP)       │           │  (ClusterIP)         │
           └─────────┬──────────┘           └──────────┬───────────┘
                     │                                 │            
         ┌───────────▼───────────┐         ┌───────────▼────────────┐
         │ Deployment: app       │         │ Deployment: postgres   │
         │ 2–3 pods (réplicas)   │         │ 1 pod + PVC persistente│
         └───────────────────────┘         └────────────────────────┘

##### Arquitectura de despliegue (Ansible)

El aprovisionamiento del cluster se realiza totalmente desde Ansible de forma automatizada

Playbook principal: k3s_install.yml

Realiza:

1. Preparación de nodos

- Actualización de paquetes
- Instalación de utilidades básicas
- Desactivación de memoria SWAP
- Limpieza de '/etc/fstab'

2. Instalación de k3s Server (en master)

- Instala y habilita 'k3s.service'
- Extrae el token del master para unir workers

3. Instalación de k3s Agent (en workers)

- Unen los workers automáticamente con 'K3S_URL + K3S_TOKEN'
- Inician 'k3s-agent.service'

Permite levantar el cluster completo con un solo comando:

'ansible-playbook -i inventory.ini k3s_install.yml'

###### Flujo de funcionamiento

1. El usuario accede a 'http://gestor.local'
2. El Ingress recibe la petición
3. Traefik reenvía al Service app
4. El service balancea entre los pods del Deployment
5. El pod Flask procesa la petición
6. Si necesita datos, consulta el Service postgres
7. PostgreSQL responde y la app devuelve respuesta al usuario

####### Alta disponibilidad y escalabilidad

- Kubernetes reinicia pods automáticamente en caso que fallen
- Replicasets garantiza que siempre haya N pods activos
- Se puede escalar fácilmente la app cambiando:
	
	spec:
	 replicas: 3

- Se pueden añadir nuevos workers solo ejecutando Ansible

######## Seguridad

- La base de datos no está expluesta al exterior
- Comunicación app-DB por ClusterIP
- Contenedores separados en namespace aislado
- El uso de probes minimiza fallos silenciosos
- Permisos mínimos en usuario PostgreSQL
+ En un futuro podría añadirse TLS, Secrets, Resource Limits...

######### Pruebas de rendimiento

- Pruebas con av (ApacheBench)
- Comparativa 1 réplica vs 3 réplicas
- Métricas
