# Usage Guide

This guide shows how to run the API and use common endpoints with concrete examples.

## Run Locally (Docker)
1. Copy `.env.example` to `.env` and adjust if needed.
2. Start services:
```bash
docker compose up --build
```
3. Run migrations:
```bash
docker compose exec api alembic upgrade head
```
4. Seed data (basic):
```bash
docker compose exec api python seed_data.py --force
```
5. Seed data (behavioral MCMC):
```bash
docker compose exec api python mcmc_seed.py --force --sessions 5000
```

API docs:
```
http://localhost:8000/api/v1/docs
```

## Auth
Register:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","username":"user1","password":"Password123!","full_name":"User One"}'
```

Login (OAuth2 form):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user1&password=Password123!"
```

Refresh:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh>"}'
```

Logout:
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access>" \
  -d '{"refresh_token":"<refresh>"}'
```

## Products
List with filters:
```bash
curl "http://localhost:8000/api/v1/products/?query=shoe&min_price=20&max_price=150&sort=price_asc&page=1&size=20"
```

Get by id:
```bash
curl http://localhost:8000/api/v1/products/1
```

Create product (seller/admin):
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Running Shoe","description":"Lightweight runner","price":89.99,"stock":50,"sku":"SKU-1234-ABCD","category_id":1,"tag_ids":[1,2],"image_urls":["https://example.com/img1.jpg"]}'
```

## Cart
Get my cart:
```bash
curl -H "Authorization: Bearer <access>" http://localhost:8000/api/v1/cart/
```

Add item:
```bash
curl -X POST http://localhost:8000/api/v1/cart/items \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

Guest cart flow:
```bash
curl -X POST http://localhost:8000/api/v1/cart/guest
curl -X POST http://localhost:8000/api/v1/cart/guest/<guest_id>/items \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":1}'
```

## Orders
Create order from cart:
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer <access>"
```

List my orders:
```bash
curl -H "Authorization: Bearer <access>" http://localhost:8000/api/v1/orders/
```

Cancel order:
```bash
curl -X POST http://localhost:8000/api/v1/orders/1/cancel \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Changed my mind"}'
```

## Payments (Simulated)
Pay for order:
```bash
curl -X POST http://localhost:8000/api/v1/payments/pay/1 \
  -H "Authorization: Bearer <access>"
```

Webhook:
```bash
curl -X POST "http://localhost:8000/api/v1/payments/webhook?reference=PAY-xxx&success=true"
```

## Reviews
Add review after delivery:
```bash
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"rating":5,"comment":"Great product"}'
```

## Admin
Dashboard:
```bash
curl -H "Authorization: Bearer <access>" http://localhost:8000/api/v1/admin/dashboard
```

## Health and Metrics
Health:
```bash
curl http://localhost:8000/health
```

Metrics:
```bash
curl http://localhost:8000/metrics
```
