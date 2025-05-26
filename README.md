# lu-sales-api

![Estrutura de Diretórios](https://raw.githubusercontent.com/byDev/lu-sales-api/main/docs/estrutura-diretorios.png)

## Visão Geral

API para gestão de vendas, clientes, produtos e pedidos, com autenticação JWT, integração WhatsApp e arquitetura escalável baseada em FastAPI + SQLAlchemy.

## Tecnologias Utilizadas
- **Python 3.13**
- **FastAPI** (API REST)
- **SQLAlchemy** (ORM)
- **Alembic** (migrations)
- **Pytest** (testes)
- **Sentry** (monitoramento de erros)
- **Docker** e **Docker Compose**
- **JWT** (autenticação)
- **Pydantic v2** (validação)
- **Requests** (integração externa)

## Caso de Uso
O sistema permite:
- Cadastro e autenticação de usuários (admin/vendedor)
- Cadastro, consulta, atualização e remoção de clientes
- Cadastro, consulta, atualização e remoção de produtos
- Criação e gestão de pedidos, com controle de estoque
- Notificação automática via WhatsApp ao criar/atualizar pedidos

## Estrutura de Diretórios
```
app/
  api/v1/endpoints/   # Endpoints FastAPI (auth, client, product, order)
  core/               # Configurações, logging, database, security
  integrations/       # Integrações externas (WhatsApp)
  models/             # Modelos SQLAlchemy
  repositories/       # Regras de acesso a dados
  schemas/            # Schemas Pydantic (entrada/saída)
  main.py             # Ponto de entrada FastAPI
alembic/              # Migrations Alembic
Dockerfile            # Build da aplicação
Makefile              # Comandos úteis
README.md             # Este arquivo
```

## Endpoints Principais

### Autenticação
- `POST /api/v1/auth/login` — Login, retorna JWT
  **Exemplo:**
  ```json
  {
    "email": "usuario@exemplo.com",
    "password": "123456"
  }
  ```
- `POST /api/v1/auth/register` — Cadastro de usuário
  **Exemplo:**
  ```json
  {
    "name": "Novo Usuário",
    "email": "novo@exemplo.com",
    "phone": "11999999999",
    "access_level": "seller",
    "password": "12345678"
  }
  ```
- `POST /api/v1/auth/refresh-token` — Renova JWT
  **Header:**
  ```http
  Authorization: Bearer <token>
  ```
- `POST /api/v1/auth/logout` — Logout (simulado)

### Clientes
- `POST /api/v1/clients/` — Cria cliente
  **Exemplo:**
  ```json
  {
    "name": "Cliente 1",
    "email": "cliente1@exemplo.com",
    "phone": "11999999997",
    "cpf": "12345678901",
    "address": "Rua Teste, 123"
  }
  ```
- `GET /api/v1/clients/` — Lista clientes (filtros: nome, email, cpf)
  **Exemplo de uso:**
  `/api/v1/clients/?email=cliente1@exemplo.com`
- `GET /api/v1/clients/{id}` — Detalhe do cliente
- `PUT /api/v1/clients/{id}` — Atualiza cliente
  **Exemplo:**
  ```json
  {
    "name": "Cliente Atualizado",
    "email": "cliente1@exemplo.com",
    "phone": "11999999997",
    "cpf": "12345678901",
    "address": "Rua Nova, 456"
  }
  ```
- `DELETE /api/v1/clients/{id}` — Remove cliente

### Produtos
- `POST /api/v1/products/` — Cria produto
  **Exemplo:**
  ```json
  {
    "description": "Camiseta Preta",
    "price": 49.9,
    "barcode": "1234567890123",
    "section": "Roupas",
    "stock": 10,
    "expiration_date": "2025-12-31",
    "image": null
  }
  ```
- `GET /api/v1/products/` — Lista produtos (filtros: descrição, seção)
  **Exemplo de uso:**
  `/api/v1/products/?description=Camiseta`
- `GET /api/v1/products/{id}` — Detalhe do produto
- `PUT /api/v1/products/{id}` — Atualiza produto
  **Exemplo:**
  ```json
  {
    "description": "Camiseta Branca",
    "price": 59.9,
    "barcode": "1234567890999",
    "section": "Roupas",
    "stock": 8,
    "expiration_date": "2026-01-01",
    "image": null
  }
  ```
- `DELETE /api/v1/products/{id}` — Remove produto

### Pedidos
- `POST /api/v1/orders/` — Cria pedido (notifica WhatsApp)
  **Exemplo:**
  ```json
  {
    "client_id": 1,
    "status": "pending",
    "created_at": "2025-05-25",
    "products": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }
  ```
- `GET /api/v1/orders/` — Lista pedidos (filtros: client_id, status, data)
  **Exemplo de uso:**
  `/api/v1/orders/?client_id=1`
- `GET /api/v1/orders/{id}` — Detalhe do pedido
- `PUT /api/v1/orders/{id}` — Atualiza pedido
  **Exemplo:**
  ```json
  {
    "client_id": 1,
    "status": "processing",
    "created_at": "2025-05-25",
    "products": [
      {"product_id": 1, "quantity": 3}
    ]
  }
  ```
- `PUT /api/v1/orders/{id}/status` — Atualiza status do pedido (notifica WhatsApp)
  **Exemplo:**
  ```json
  {
    "status": "completed",
    "client_id": 1,
    "created_at": "2025-05-25"
  }
  ```
- `DELETE /api/v1/orders/{id}` — Remove pedido

## Como Executar o Projeto

1. **Clone o repositório:**
   ```zsh
   git clone <repo-url>
   cd lu-sales-api
   ```

## Serviços Docker

O projeto utiliza Docker Compose para orquestrar múltiplos serviços essenciais:

- **api**: Container principal da aplicação FastAPI.
- **db**: Banco de dados relacional (ex: PostgreSQL ou MySQL, conforme configuração do .env).
- **sentry**: Monitoramento e rastreamento de erros (Sentry Server).
- **redis**: Utilizado pelo Sentry e/ou para cache.
- **evolution (WhatsApp API)**: Utilizado para integração com WhatsApp.

Todos os serviços são definidos no arquivo `docker-compose.yml` e podem ser inicializados juntos com:

2. **Configure o arquivo `.env`** com as variáveis de ambiente necessárias (banco, JWT, Sentry, WhatsApp, etc).

3. **Suba os containers:**
   ```zsh
   docker-compose up --build
   ```

4. **Acesse a documentação interativa:**
   - [http://localhost:8000/docs](http://localhost:8000/docs)

## Migrations (Banco de Dados)
- Criar nova migration:
  ```zsh
  make migrations_create
  ```
- Aplicar migrations:
  ```zsh
  make migrations
  ```

## Executando Testes e Cobertura
- Rodar todos os testes unitários e integração:
  ```zsh
  make testes
  ```
- O comando acima executa o Pytest com cobertura de código e mostra o relatório no terminal.

## Observações
- O monitoramento de erros críticos é feito via Sentry (ver `.env` para configuração do DSN).
- O projeto segue boas práticas de logging, rollback de transações e tratamento de exceções.
- Para integração WhatsApp, configure as variáveis de ambiente de API e instância.

---

> Projeto desenvolvido por byMario.dev para gestão de vendas e integração omnichannel (WhatsApp).