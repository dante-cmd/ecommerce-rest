# MCMC Seed Simulator (mcmc_seed.py)

This document explains how the Markov Chain Monte Carlo (MCMC) simulator works and how it populates realistic e-commerce behavioral data.

## Goals
- Simulate **realistic session behavior** (browse → view → cart → checkout → purchase/abandon).
- Generate **non‑uniform data** where most users abandon early.
- Reflect **industry benchmarks** (cart abandonment, add‑to‑cart rates, checkout completion).
- Support multiple **personas** to diversify behavior.

## States (9 Required)
The simulator models a first‑order Markov chain with these states:
1. `HOMEPAGE_BROWSE`  
2. `PRODUCT_LIST`  
3. `PRODUCT_DETAIL`  
4. `ADD_TO_CART`  
5. `VIEW_CART`  
6. `PROCEED_CHECKOUT`  
7. `PURCHASE` (absorbing)  
8. `ABANDON` (absorbing)  
9. `POST_PURCHASE_REVIEW` (absorbing; only after purchase)

The **memoryless property** applies: the next state depends only on the current state.

## Transition Matrix
`build_base_matrix()` defines a 9×9 matrix where each row sums to 1.  
It is calibrated to key funnel benchmarks:
- Cart abandonment ≈ **70.2%**
- Product‑view → add‑to‑cart ≈ **6–8%**
- Cart → checkout ≈ **40–50%**
- Checkout → purchase ≈ **55–60%**
- Overall conversion ≈ **2–3%**

These values are encoded in the matrix rows and normalized.

## Personas
Three personas are applied by scaling specific transitions:
- **Impulse buyer (30%)**: higher add‑to‑cart and purchase
- **Researcher (40%)**: more list/detail browsing, lower conversion
- **Window‑shopper (30%)**: higher abandonment

`apply_persona()` multiplies selected transition probabilities then re‑normalizes the row.

## Monte Carlo Session Simulation
For each session:
1. Start in `HOMEPAGE_BROWSE`
2. Sample the next state using `np.random.choice` and the transition matrix
3. Continue until an absorbing state is reached or a max step count is hit

This yields a full **trajectory** for the session.

## Absorption Probabilities
`absorption_probabilities()` computes the probability of ending in:
- `PURCHASE`
- `ABANDON`
- `POST_PURCHASE_REVIEW`

It uses absorbing Markov chain mathematics (Q/R matrices and the fundamental matrix).

## How Sessions Populate Data
Each session:
- Selects a **persona‑specific matrix**
- Simulates transitions
- Uses transitions to create domain objects:
  - `ADD_TO_CART` → add cart item
  - `PROCEED_CHECKOUT` → merge guest cart into user cart
  - `PURCHASE` → create order, update stock, set order status
  - `POST_PURCHASE_REVIEW` → create reviews for purchased items

Orders are assigned realistic statuses:
- `confirmed`, `shipped`, `delivered` weighted by probabilities

## Session Timing
`random_delay_seconds()` adds stochastic time gaps between transitions to emulate real session durations.

## Scheduler
Run on a schedule with APScheduler:
```bash
python mcmc_seed.py --interval-minutes 60
```

## Usage Examples
One‑off run:
```bash
python mcmc_seed.py --force --sessions 5000
```

Larger run:
```bash
python mcmc_seed.py --force --sessions 20000
```

## File Reference
- Script: `mcmc_seed.py`

