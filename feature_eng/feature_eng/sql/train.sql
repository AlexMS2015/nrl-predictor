CREATE OR REPLACE TABLE train AS
    SELECT
        labels.* EXCLUDE(home_win, margin),
        -- coalesce for round 1
        COALESCE(home.ladder_position, 0) AS ladder_position_home,
        COALESCE(away.ladder_position, 0) AS ladder_position_away,
        COALESCE(-1 * (home.ladder_position - away.ladder_position), 0) AS home_ladder_pos_diff,
        labels.home_win
    FROM
        labels AS labels
    LEFT JOIN
        features_team AS home
    ON
        labels.year = home.year
        AND labels.round_num - 1 = home.round_num
        AND labels.home_team = home.team
    LEFT JOIN
        features_team AS away
    ON
        labels.year = away.year
        AND labels.round_num - 1 = away.round_num
        AND labels.away_team = away.team
