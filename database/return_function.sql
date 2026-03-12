CREATE OR REPLACE FUNCTION update_returns()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_last_return_time date;
    v_start_time date;
BEGIN
    SELECT MAX(return_time)::date
    INTO v_last_return_time
    FROM returns;

    IF v_last_return_time IS NULL THEN
        v_start_time := NULL;
    ELSE
        v_start_time := v_last_return_time - INTERVAL '1 day';
    END IF;

    INSERT INTO returns (asset_id, return_time, simple_return, log_return)
    SELECT
        q.asset_id,
        q.price_time::date,
        (q.close / NULLIF(q.prev_close, 0) - 1) AS simple_return,
        LN(q.close / NULLIF(q.prev_close, 0))   AS log_return
    FROM (
        SELECT
            p.asset_id,
            p.price_time,
            p.close,
            LAG(p.close) OVER (
                PARTITION BY p.asset_id
                ORDER BY p.price_time
            ) AS prev_close
        FROM prices p
        WHERE v_start_time IS NULL
           OR p.price_time::date >= v_start_time
    ) q
    -- Hem önceki gün boş olmamalı, hem de logaritma çökmesin diye fiyatlar > 0 olmalı
    WHERE q.prev_close IS NOT NULL
      AND q.prev_close > 0
      AND q.close > 0
      AND (
            v_last_return_time IS NULL
            OR q.price_time::date > v_last_return_time
          )
    ORDER BY q.price_time, q.asset_id
    ON CONFLICT (asset_id, return_time) DO NOTHING;

END;
$$;