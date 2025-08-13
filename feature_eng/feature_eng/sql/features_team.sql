CREATE OR REPLACE TABLE features_team AS
    WITH ladder AS (
        SELECT
            year,
            round_num,
            team,
            COALESCE(SUM(bye) OVER (
                PARTITION BY
                    year,
                    team
                ORDER BY
                    round_num
            ), 0) AS byes,
            COALESCE(SUM(win) OVER (
                PARTITION BY
                    year,
                    team
                ORDER BY
                    round_num
            ), 0) AS wins,
            COALESCE(SUM(draw) OVER (
                PARTITION BY
                    year,
                    team
                ORDER BY
                    round_num
            ), 0) AS draws,
            COALESCE(SUM(loss) OVER (
                PARTITION BY
                    year,
                    team
                ORDER BY
                    round_num
            ), 0) AS losses,
            COALESCE(SUM(pts_for) OVER (
                PARTITION BY
                    year,
                    team
                ORDER BY
                    round_num
            ), 0) AS pts_for,
            COALESCE(SUM(pts_against) OVER (
                PARTITION BY
                    year,
                    team
                ORDER BY
                    round_num
            ), 0) AS pts_against
        FROM win_loss_draw_full
    ),

    ladder_final AS (
        SELECT
            year,
            round_num,
            team,
            CAST(round_num - byes AS INT) AS played,
            CAST(byes AS INT) AS byes,
            CAST(wins AS INT) AS wins,
            CAST(draws AS INT) AS draws,
            CAST(losses AS INT) AS losses,
            CAST(2*wins + 2*byes + 1*draws AS INT) AS points,
            CAST(pts_for AS INT) AS pts_for,
            CAST(pts_against AS INT) AS pts_against,
            CAST(pts_for - pts_against AS INT) AS pts_diff
        FROM ladder
    )

    SELECT
        *,
        RANK() OVER (
            PARTITION BY
                year,
                round_num
            ORDER BY
                points DESC,
                pts_diff DESC
        ) AS ladder_position
    FROM ladder_final
