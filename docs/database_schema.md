# FarmLink Database Schema

This document defines the relational database structure for the FarmLink platform to support authentication, user profiles, crop listings, buyer orders, KYC verification, and delivery/logistics.

## Entity Relationship Diagram (ERD)

```mermaid

erDiagram

    USERS ||--o| FARMER_PROFILES : "has profile"

    USERS ||--o| BUYER_PROFILES : "has profile"

    USERS ||--oM OTPS : "receives"

    USERS ||--oM LISTINGS : "owns (farmer)"

    USERS ||--oM ORDERS : "places (buyer)"

    USERS ||--oM DELIVERIES : "performs (driver)"

    FARMER_PROFILES ||--oM KYC_VERIFICATIONS : "undergoes"

    LISTINGS ||--oM ORDER_ITEMS : "included in"

    ORDERS ||--oM ORDER_ITEMS : "contains"

    ORDERS ||--o| PAYMENTS : "billed via"

    ORDERS ||--o| DELIVERIES : "delivered via"

    USERS {

        uuid id PK

        varchar phone_number UK

        varchar full_name

        varchar role "farmer | buyer | driver | admin"

        boolean verified "manual approval flag; defaults to false"

        timestamp created_at

        timestamp updated_at

    }

    OTPS {

        uuid id PK

        uuid user_id FK

        varchar code

        timestamp expires_at

        boolean verified

        timestamp created_at

    }

    FARMER_PROFILES {

        uuid id PK

        uuid user_id FK, UK

        varchar state

        varchar district

        varchar sub_district

        varchar village

        boolean bank_verified

        boolean identity_verified

        timestamp created_at

        timestamp updated_at

    }

    KYC_VERIFICATIONS {

        uuid id PK

        uuid farmer_profile_id FK

        varchar status "pending | approved | rejected"

        varchar document_type "aadhaar | pan | voter_id"

        varchar document_number

        varchar document_file_url

        text remarks

        timestamp created_at

        timestamp updated_at

    }

    BUYER_PROFILES {

        uuid id PK

        uuid user_id FK, UK

        text delivery_address

        varchar pin_code

        timestamp created_at

        timestamp updated_at

    }

    LISTINGS {

        uuid id PK

        uuid farmer_id FK "points to users.id"

        varchar title

        text description

        varchar category "vegetables | fruits | grains | spices | other"

        decimal price_per_kg

        decimal available_quantity_kg

        varchar status "active | sold_out | draft | inactive"

        timestamp created_at

        timestamp updated_at

    }

    ORDERS {

        uuid id PK

        uuid buyer_id FK "points to users.id"

        decimal total_amount

        varchar payment_status "pending | paid | failed"

        varchar order_status "pending | accepted | picking | shipped | delivered | cancelled"

        text delivery_address

        timestamp created_at

        timestamp updated_at

    }

    ORDER_ITEMS {

        uuid id PK

        uuid order_id FK

        uuid listing_id FK

        decimal price_per_kg

        decimal quantity_kg

    }

    PAYMENTS {

        uuid id PK

        uuid order_id FK, UK

        varchar transaction_ref UK

        varchar payment_method "upi | bank_transfer | cod"

        varchar status "pending | completed | failed | refunded"

        decimal amount

        timestamp created_at

    }

    DELIVERIES {

        uuid id PK

        uuid order_id FK, UK

        uuid driver_id FK "points to users.id"

        text pickup_address

        text dropoff_address

        decimal pickup_lat

        decimal pickup_lng

        decimal dropoff_lat

        decimal dropoff_lng

        varchar tracking_status "assigned | picked_up | in_transit | delivered"

        timestamp estimated_arrival_time

        timestamp created_at

        timestamp updated_at

    }

```

---

## SQL DDL Script (PostgreSQL dialect)

```sql

-- Enable UUID extension

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table

CREATE TABLE users (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    phone_number VARCHAR(15) UNIQUE NOT NULL,

    full_name VARCHAR(100) NOT NULL,

    role VARCHAR(20) NOT NULL CHECK (role IN ('farmer', 'buyer', 'driver', 'admin')),

    verified BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 2. OTPs Table (Auth log)

CREATE TABLE otps (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    code VARCHAR(6) NOT NULL,

    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 3. Farmer Profiles Table

CREATE TABLE farmer_profiles (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    state VARCHAR(50) NOT NULL,

    district VARCHAR(50) NOT NULL,

    sub_district VARCHAR(50) NOT NULL,

    village VARCHAR(50) NOT NULL,

    bank_verified BOOLEAN DEFAULT FALSE,

    identity_verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 4. KYC Verifications Table

CREATE TABLE kyc_verifications (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    farmer_profile_id UUID NOT NULL REFERENCES farmer_profiles(id) ON DELETE CASCADE,

    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),

    document_type VARCHAR(20) NOT NULL CHECK (document_type IN ('aadhaar', 'pan', 'voter_id')),

    document_number VARCHAR(50) NOT NULL,

    document_file_url VARCHAR(255) NOT NULL,

    remarks TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 5. Buyer Profiles Table

CREATE TABLE buyer_profiles (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    delivery_address TEXT NOT NULL,

    pin_code VARCHAR(10) NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 6. Crop Listings Table

CREATE TABLE listings (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    farmer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    title VARCHAR(150) NOT NULL,

    description TEXT,

    category VARCHAR(30) NOT NULL CHECK (category IN ('vegetables', 'fruits', 'grains', 'spices', 'other')),

    price_per_kg NUMERIC(10, 2) NOT NULL CHECK (price_per_kg >= 0),

    available_quantity_kg NUMERIC(10, 2) NOT NULL CHECK (available_quantity_kg >= 0),

    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'sold_out', 'draft', 'inactive')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 7. Orders Table

CREATE TABLE orders (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    buyer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,

    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),

    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed')),

    order_status VARCHAR(20) DEFAULT 'pending' CHECK (order_status IN ('pending', 'accepted', 'picking', 'shipped', 'delivered', 'cancelled')),

    delivery_address TEXT NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 8. Order Items Table

CREATE TABLE order_items (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,

    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE RESTRICT,

    price_per_kg NUMERIC(10, 2) NOT NULL CHECK (price_per_kg >= 0),

    quantity_kg NUMERIC(10, 2) NOT NULL CHECK (quantity_kg > 0)

);

-- 9. Payments Table

CREATE TABLE payments (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    order_id UUID UNIQUE NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,

    transaction_ref VARCHAR(100) UNIQUE NOT NULL,

    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('upi', 'bank_transfer', 'cod')),

    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),

    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- 10. Deliveries Table (Logistics/Route Tracking)

CREATE TABLE deliveries (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    order_id UUID UNIQUE NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,

    driver_id UUID REFERENCES users(id) ON DELETE SET NULL,

    pickup_address TEXT NOT NULL,

    dropoff_address TEXT NOT NULL,

    pickup_lat NUMERIC(9, 6) NOT NULL,

    pickup_lng NUMERIC(9, 6) NOT NULL,

    dropoff_lat NUMERIC(9, 6) NOT NULL,

    dropoff_lng NUMERIC(9, 6) NOT NULL,

    tracking_status VARCHAR(20) DEFAULT 'assigned' CHECK (tracking_status IN ('assigned', 'picked_up', 'in_transit', 'delivered')),

    estimated_arrival_time TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

);

-- Indices for performance optimization

CREATE INDEX idx_listings_farmer ON listings(farmer_id);

CREATE INDEX idx_listings_category ON listings(category);

CREATE INDEX idx_orders_buyer ON orders(buyer_id);

CREATE INDEX idx_order_items_order ON order_items(order_id);

CREATE INDEX idx_deliveries_driver ON deliveries(driver_id);

```

-- ============================================================
-- FarmLink Database Schema
-- PostgreSQL
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE users (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
phone_number VARCHAR(15) NOT NULL UNIQUE,
full_name VARCHAR(100) NOT NULL,
role VARCHAR(20) NOT NULL
CHECK (role IN ('farmer', 'buyer', 'driver', 'admin')),
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. OTPs
-- Store a hashed OTP in production rather than the raw code.
-- ============================================================
CREATE TABLE otps (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
code VARCHAR(255) NOT NULL,
expires_at TIMESTAMPTZ NOT NULL,
verified BOOLEAN NOT NULL DEFAULT FALSE,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otps_user_id ON otps(user_id);
CREATE INDEX idx_otps_expires_at ON otps(expires_at);

-- ============================================================
-- 3. FARMER PROFILES
-- ============================================================
CREATE TABLE farmer_profiles (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
state VARCHAR(50) NOT NULL,
district VARCHAR(50) NOT NULL,
sub_district VARCHAR(50) NOT NULL,
village VARCHAR(100) NOT NULL,
bank_verified BOOLEAN NOT NULL DEFAULT FALSE,
identity_verified BOOLEAN NOT NULL DEFAULT FALSE,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_farmer_profiles_location
ON farmer_profiles(state, district, sub_district);

-- ============================================================
-- 4. KYC VERIFICATIONS
-- ============================================================
CREATE TABLE kyc_verifications (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
farmer_profile_id UUID NOT NULL
REFERENCES farmer_profiles(id) ON DELETE CASCADE,
status VARCHAR(20) NOT NULL DEFAULT 'pending'
CHECK (status IN ('pending', 'approved', 'rejected')),
document_type VARCHAR(20) NOT NULL
CHECK (document_type IN ('aadhaar', 'pan', 'voter_id')),
document_number VARCHAR(100) NOT NULL,
document_file_url TEXT NOT NULL,
remarks TEXT,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_farmer_profile ON kyc_verifications(farmer_profile_id);
CREATE INDEX idx_kyc_status ON kyc_verifications(status);

-- ============================================================
-- 5. BUYER PROFILES
-- ============================================================
CREATE TABLE buyer_profiles (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
delivery_address TEXT NOT NULL,
pin_code VARCHAR(10) NOT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_buyer_profiles_pin_code ON buyer_profiles(pin_code);

-- ============================================================
-- 6. CROP LISTINGS
-- ============================================================
CREATE TABLE listings (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
farmer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
title VARCHAR(150) NOT NULL,
description TEXT,
category VARCHAR(30) NOT NULL
CHECK (category IN ('vegetables', 'fruits', 'grains', 'spices', 'other')),
price_per_kg NUMERIC(10, 2) NOT NULL
CHECK (price_per_kg > 0),
available_quantity_kg NUMERIC(12, 2) NOT NULL
CHECK (available_quantity_kg >= 0),
status VARCHAR(20) NOT NULL DEFAULT 'active'
CHECK (status IN ('active', 'sold_out', 'draft', 'inactive')),
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_listings_farmer ON listings(farmer_id);
CREATE INDEX idx_listings_category ON listings(category);
CREATE INDEX idx_listings_status ON listings(status);

-- ============================================================
-- 7. ORDERS
-- ============================================================
CREATE TABLE orders (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
buyer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
total_amount NUMERIC(12, 2) NOT NULL
CHECK (total_amount >= 0),
payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'
CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
order_status VARCHAR(20) NOT NULL DEFAULT 'pending'
CHECK (
order_status IN (
'pending',
'accepted',
'picking',
'shipped',
'delivered',
'cancelled'
)
),
delivery_address TEXT NOT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);

-- ============================================================
-- 8. ORDER ITEMS
-- ============================================================
CREATE TABLE order_items (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE RESTRICT,
price_per_kg NUMERIC(10, 2) NOT NULL
CHECK (price_per_kg > 0),
quantity_kg NUMERIC(12, 2) NOT NULL
CHECK (quantity_kg > 0)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_listing ON order_items(listing_id);

-- ============================================================
-- 9. PAYMENTS
-- transaction_ref is nullable because COD may not have one.
-- ============================================================
CREATE TABLE payments (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
order_id UUID NOT NULL UNIQUE
REFERENCES orders(id) ON DELETE RESTRICT,
transaction_ref VARCHAR(150) UNIQUE,
payment_method VARCHAR(20) NOT NULL
CHECK (payment_method IN ('upi', 'bank_transfer', 'cod')),
status VARCHAR(20) NOT NULL DEFAULT 'pending'
CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
amount NUMERIC(12, 2) NOT NULL
CHECK (amount >= 0),
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT cod_transaction_ref_check
        CHECK (
            payment_method = 'cod'
            OR transaction_ref IS NOT NULL
        )

);

CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_transaction_ref ON payments(transaction_ref);

-- ============================================================
-- 10. DELIVERIES
-- ============================================================
CREATE TABLE deliveries (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
order_id UUID NOT NULL UNIQUE
REFERENCES orders(id) ON DELETE RESTRICT,
driver_id UUID REFERENCES users(id) ON DELETE SET NULL,
pickup_address TEXT NOT NULL,
dropoff_address TEXT NOT NULL,
pickup_lat NUMERIC(9, 6) NOT NULL
CHECK (pickup_lat BETWEEN -90 AND 90),
pickup_lng NUMERIC(9, 6) NOT NULL
CHECK (pickup_lng BETWEEN -180 AND 180),
dropoff_lat NUMERIC(9, 6) NOT NULL
CHECK (dropoff_lat BETWEEN -90 AND 90),
dropoff_lng NUMERIC(9, 6) NOT NULL
CHECK (dropoff_lng BETWEEN -180 AND 180),
tracking_status VARCHAR(20) NOT NULL DEFAULT 'assigned'
CHECK (
tracking_status IN (
'assigned',
'picked_up',
'in_transit',
'delivered'
)
),
estimated_arrival_time TIMESTAMPTZ,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deliveries_driver ON deliveries(driver_id);
CREATE INDEX idx_deliveries_status ON deliveries(tracking_status);

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;

$$
LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_farmer_profiles_updated_at
BEFORE UPDATE ON farmer_profiles
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_kyc_verifications_updated_at
BEFORE UPDATE ON kyc_verifications
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_buyer_profiles_updated_at
BEFORE UPDATE ON buyer_profiles
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_listings_updated_at
BEFORE UPDATE ON listings
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_orders_updated_at
BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_deliveries_updated_at
BEFORE UPDATE ON deliveries
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
$$
