CREATE OR REPLACE TABLE labels AS
    SELECT
        year,
        round_num,
        Home AS home_team,
        Away AS away_team,
        CAST(Home_Score - Away_Score AS INT) AS margin,
        IF(Home_Score > Away_Score, 1, 0) AS home_win
    FROM
        df
