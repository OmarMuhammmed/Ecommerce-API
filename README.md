# E-Commerce API

A robust, scalable, and high-performance RESTful API for e-commerce platforms built with Django and Django Rest Framework.

## Features

- **Complete E-Commerce Functionality**: Products, categories, orders, payments, user profiles, shopping carts, and more
- **High Performance**: Optimized database queries, caching strategies, and asynchronous task processing and Postgres Full Text Search for products 
- **Scalability**: Docker containerization for easy deployment and scaling
- **Authentication & Authorization**: JWT-based secure authentication system with role-based permissions
- **Background Processing**: Celery for handling resource-intensive tasks asynchronously
- **Caching**: Redis for fast data retrieval and session management
- **Database Optimization**: PostgreSQL with optimized queries and indexing strategies
- **API Documentation**: Comprehensive Swagger/OpenAPI documentation

## Technology Stack

- **Backend Framework**: Django  / Django Rest Framework 
- **Database**: PostgreSQL 
- **Caching & Message Broker**: Redis
- **Task Queue**: Celery 
- **Containerization**: Docker & Docker Compose
- **Documentation**: drf-spectacular (Swagger/OpenAPI)

## Architecture

This project follows a clean, modular architecture separating concerns:

```
ecommerce_api/
├── /config                # Configuration files
├── accounts/              # Userauthentication and profiles
├── products/              # Product catalog functionality
├── orders/                # Order processing and management
├── payments/              # Payment processing integrations
```

## Database Optimization Strategies

- Strategic indexing on frequently queried fields
- Denormalization where appropriate for read-heavy operations
- Database connection pooling
- Query optimization and proper use of select_related/prefetch_related

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/OmarMuhammmed/Ecommerce-API
cd Ecommerce-API
```

2. Configure environment variables (copy from example):
```bash
cp .env.example .env
```

3. Build and start the containers:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec api python manage.py migrate
```

5. Create a superuser:
```bash
docker-compose exec api python manage.py createsuperuser
```

6. Load sample data (optional):
```bash
docker-compose exec api python manage.py loaddata sample_data
```

The API will be available at http://127.0.0.1:8000/
API documentation will be available at http://127.0.0.1:8000/


## License

This project is licensed under the MIT License - see the LICENSE file for details.