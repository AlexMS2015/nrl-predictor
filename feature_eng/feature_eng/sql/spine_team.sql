-- will include all teams even in the finals rounds
-- but won't matter as it won't join to anything in the train_df

CREATE OR REPLACE TABLE spine_team AS

    WITH year_team AS (
        SELECT DISTINCT
            year,
            team
        FROM win_loss_draw
    ),

    year_round AS (
        SELECT DISTINCT
            year,
            round_num
        FROM win_loss_draw
    )

    SELECT
        yr.year,
        yr.round_num,
        yt.team
    FROM
        year_round AS yr
    LEFT JOIN
        year_team AS yt
    ON
        yr.year = yt.year
