# Database Relationships and Data Population

This document explains how the database tables relate to each other and how they are populated in this project.

## ER Overview (Conceptual)
```
User (1) ── (0..1) Cart ── (1..N) CartItem ── (N) Product ── (1) Category
   │                         │
   │                         └── Product has many ProductImage
   │
   ├── (1..N) Product (as seller)
   ├── (1..N) Order ── (1..N) OrderItem ── (N) Product
   └── (1..N) Review ── (1) Product

Product (N) ── (N) Tag  via product_tags
TokenBlacklist stores revoked JWT JTIs
```

## Tables and Relationships

### `users`
Primary actor table.
- One user can be a **customer**, **seller**, or **admin** (`role`).
- A user can have **many products** (if seller/admin).
- A user can have **many orders**.
- A user can have **many reviews**.
- A user can have **one cart** (`carts.user_id` unique).

### `categories`
Product classification.
- A category has **many products**.

### `products`
Core catalog items.
- Each product belongs to **one category**.
- Each product belongs to **one seller** (`users.id`).
- Each product can have **many images**.
- Each product can have **many tags** (many-to-many).
- Each product can have **many reviews**.
- `is_deleted` + `deleted_at` for soft deletes.

### `product_images`
Stores image URLs for a product.
- Many images belong to one product.

### `tags` and `product_tags`
Tag taxonomy.
- Many-to-many between products and tags via `product_tags`.

### `carts`
Shopping cart container.
- **One cart per user** (unique `user_id`).
- Can also be a **guest cart** (`guest_id`), which is unique when not null.

### `cart_items`
Cart line items.
- Each cart item references a cart and a product.
- `(cart_id, product_id)` is unique to prevent duplicate rows for same product.

### `orders`
Represents a purchase attempt.
- Each order belongs to one user.
- Order status is tracked (`pending`, `confirmed`, `shipped`, `delivered`, `cancelled`).

### `order_items`
Line items for an order.
- Each order item references an order and a product.
- Stores price at purchase time (`unit_price`, `total_price`).

### `reviews`
User feedback on products.
- Unique constraint `(user_id, product_id)` ensures one review per user per product.
- Only created after **delivered** orders in the app logic.

### `token_blacklist`
Stores revoked JWT token JTIs for logout / invalidation.

## How Data Is Populated

### 1) `seed_data.py` (Basic Seed)
Creates deterministic fake data:
- Users (mix of customer/seller/admin)
- Categories
- Tags
- Products with images + tags
- Carts and cart items
- Orders and order items
- Reviews for delivered orders

This script is fast and designed for simple demo data.

### 2) `mcmc_seed.py` (Behavioral Seed)
Populates data using **Markov Chain Monte Carlo** simulation of realistic user behavior:
- Generates users, categories, tags, products (same as basic seed).
- Simulates thousands of sessions using a Markov chain:
  - Most sessions abandon early.
  - Only a small fraction convert to purchase.
  - Reviews are generated only after purchase.
- Behavior varies by user persona (impulse / researcher / window‑shopper).

The result is **non‑uniform, realistic distributions** across:
- cart creation
- order creation
- order status progression
- review creation

## Constraints & Indexes
- `users.email`, `users.username` are unique.
- `products.sku` is unique.
- `cart_items` has unique `(cart_id, product_id)`.
- `carts.user_id` unique (one cart per user).
- `carts.guest_id` uses a **filtered unique index** (`guest_id IS NOT NULL`).
- `reviews` unique `(user_id, product_id)`.

## Notes on Integrity
- Stock is decremented on order creation.
- Stock is restored on order cancellation.
- Reviews are only allowed after delivery.
- Soft deletes prevent products from disappearing from historical data.
