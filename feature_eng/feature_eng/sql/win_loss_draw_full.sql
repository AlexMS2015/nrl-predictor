CREATE OR REPLACE TABLE win_loss_draw_full AS
    SELECT
        s.year,
        s.round_num,
        s.team,
        IF(w.team IS NULL, 1, 0) AS bye,
        COALESCE(w.pts_for, 0) AS pts_for,
        COALESCE(w.pts_against, 0) AS pts_against,
        COALESCE(w.win, 0) AS win,
        COALESCE(w.draw, 0) AS draw,
        COALESCE(w.loss, 0) AS loss
    FROM
        spine_team AS s
    LEFT JOIN
        win_loss_draw AS w
    ON
        s.year = w.year
        AND s.round_num = w.round_num
        AND s.team = w.team
