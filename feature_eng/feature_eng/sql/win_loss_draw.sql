CREATE OR REPLACE TABLE win_loss_draw AS
    WITH base AS (
        SELECT
            year,
            round_num,
            Home AS home_team,
            Home_Score AS home_score,
            Away AS away_team,
            Away_Score AS away_score
        FROM
            df
    )

    SELECT
        year,
        round_num,
        home_team AS team,
        home_score AS pts_for,
        away_score AS pts_against,
        IF(home_score > away_score, 1, 0) AS win,
        IF(home_score = away_score, 1, 0) AS draw,
        IF(home_score < away_score, 1, 0) AS loss
    FROM
        base

    UNION ALL

    SELECT
        year,
        round_num,
        away_team AS team,
        away_score AS pts_for,
        home_score AS pts_against,
        IF(away_score > home_score, 1, 0) AS win,
        IF(away_score = home_score, 1, 0) AS draw,
        IF(away_score < home_score, 1, 0) AS loss
    FROM
        base
