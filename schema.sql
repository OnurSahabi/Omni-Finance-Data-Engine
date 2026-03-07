CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    name TEXT,
    asset_type VARCHAR(20) NOT NULL,
    exchange VARCHAR(20),
    currency VARCHAR(10)
);

CREATE TABLE prices (
    price_id BIGSERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    price_time TIMESTAMP NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    UNIQUE (asset_id, timestamp)
);

CREATE TABLE returns (
    return_id BIGSERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    return_time TIMESTAMP NOT NULL,
    return NUMERIC,
    UNIQUE (asset_id, timestamp)
);

CREATE INDEX idx_prices_asset_time
ON prices(asset_id, price_time);

CREATE INDEX idx_returns_asset_time
ON returns(asset_id, return_time);