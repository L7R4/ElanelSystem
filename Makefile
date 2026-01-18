COMPOSE ?= docker compose
SERVICE ?= web


up: ## Levanta el entorno (db + web) y sigue logs
	$(COMPOSE) up --build

down: ## Baja servicios
	$(COMPOSE) down

restart: ## Reinicia servicios
	$(COMPOSE) down
	$(COMPOSE) up --build

ps: ## Estado de contenedores
	$(COMPOSE) ps

shell: ## Abre shell Django dentro del contenedor
	$(COMPOSE) exec $(SERVICE) python elanelsystem/manage.py shell

bash: ## Abre una terminal en el contenedor
	$(COMPOSE) exec $(SERVICE) sh

migrate: ## Ejecuta migraciones
	$(COMPOSE) exec $(SERVICE) python elanelsystem/manage.py migrate

makemigrations: ## Crea migraciones (solo cuando cambias models)
	$(COMPOSE) exec $(SERVICE) python elanelsystem/manage.py makemigrations

seed: ## Corre el seed (crea datos iniciales + usuario)
	$(COMPOSE) exec $(SERVICE) python elanelsystem/manage.py seed

superuser: ## Crea un superusuario de Django (manual)
	$(COMPOSE) exec $(SERVICE) python elanelsystem/manage.py createsuperuser