CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    name TEXT,
    asset_type VARCHAR(20) NOT NULL,
    currency VARCHAR(10)
);

CREATE TABLE prices (
    price_id BIGSERIAL PRIMARY KEY,
    asset_id INT NOT NULL REFERENCES assets(asset_id),
    price_time DATE NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    UNIQUE (asset_id, price_time)
);

CREATE TABLE returns (
    return_id BIGSERIAL PRIMARY KEY,
    asset_id INT NOT NULL REFERENCES assets(asset_id),
    return_time DATE NOT NULL,
    simple_return DOUBLE PRECISION,
    log_return DOUBLE PRECISION,
    UNIQUE (asset_id, return_time)
);
