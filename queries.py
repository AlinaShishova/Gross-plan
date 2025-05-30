queries = {
    "key":"""SELECT d.dm_index,
               d.dm_name as dse_name,
               d.dm_draft as dse_draft_number,
               a.da_num as count_in_assembling,
               a.cn_tech_marshrut as workshop_route,
               (SELECT c.short_name FROM dse_classes c WHERE c.ind = d.dm_class_id) as class_name
        FROM 
            dse_assembling a, 
            dse_main d
        WHERE 
            d.dm_index = a.dm_index_what
            AND a.dm_index_where = :dm_index_where
            AND d.dm_class_id IN (2456, 2454, 2797, 2896)
        ORDER BY 
            d.dm_class_id, 
            d.dm_draft, 
            d.dm_name""",
    "scheme": """SELECT PS.IND, -- ИНДЕКС ПЛАТЕЖНОГО УЗЛА ПО НЕМУ ПЕРЕХОД НА СЛЕДУЮЩУЮ СТРАНИЧКУ
                    PO.CODE_BILL || '/' || PO.SUBCODE_BILL AS ORDER_NUM, --ЩПЗ
                    PO.CONTRACT_NUM, -- № КОНТРАКТА
                    PO.CUSTOMER_NAME, -- ЗАКАЗЧИК
                    PS.ORDER_NAME || ' ' || PS.ORDER_DRAFT AS NAME_DRAFT_NUM, -- НАИМЕНОВАНИЕ, ОБОЗНАЧЕНИЕ
                    (SELECT COUNT(PDL.IND)|| '/0' FROM PROGRAMM_DSE_LINK PDL WHERE PDL.PROGRAMM_SUBORDER_ID = PS.IND) AS SP_COUNT -- СП
                FROM
                    PROGRAMM_ORDER PO,
                    PROGRAMM_SUBORDER PS
                WHERE 
                    PS.PROGRAMM_ORDER = PO.IND AND 
                    UPPER(PO.CODE_BILL || '/' || PO.SUBCODE_BILL) LIKE:filter_value  -- ПАРАМЕТР ДЛЯ ФИЛЬТРАЦИ
                    AND PO.STATUS = 2
                ORDER BY 
                    PO.CODE_BILL, 
                    PO.SUBCODE_BILL,
                    PO.SHORT_NAME""",
    "spec":"""
      SELECT CS.CUBE_SPECIFICATION_ID, -- ИНДЕКС СПЕЦИФИКАЦИИ (СКРЫТ) 
                CS.STOP, -- ЗНАЧЕК В РАБОТЕ = 1 /ОСТАНОВЛЕН = 0 
                CS.DSE_ID, -- ИНДЕКС ДСЕ ДЛЯ ПЕРЕХОДА К СОСТАВУ ИЗДЕЛИЯ (СКРЫТ)
                (SELECT DM.DM_NAME || ' ' || DM.DM_DRAFT
        FROM DSE_MAIN DM
        WHERE DM.DM_INDEX = CS.DSE_ID) AS DSE_NAME, -- НАИМЕНОВАНИЕ, ОБОЗНАЧЕНИЕ
        (SELECT (SELECT PDT.NAME FROM PROGRAMM_DSE_TYPES PDT WHERE PDT.IND = PD.TYPE_)
                FROM PROGRAMM_DSE PD
                WHERE PD.IND = CS.SPEC_ID) AS TYPE_SPEC, -- ТИП
                CS.DATE_GENERAL, -- НАЧАЛО
                (SELECT PD.TITLE FROM PROGRAMM_DSE PD, programm_dse_link dsl WHERE dsl.programm_dse_id = pd.ind and  dsl.IND = CS.SPEC_ID) AS TITLE, -- ПРИМЕЧАНИЕ
                CS.SPEC_ID -- ИНДЕКС СПЕЦИФИКАЦИИ (СКРЫТ, НА ВСЯКИЙ СЛУЧАЙ)
        FROM 
            CUBE_SPECIFICATION CS
        WHERE 
            CS.SPEC_ID IN (SELECT PDL.IND
                        FROM PROGRAMM_DSE_LINK PDL
                        WHERE PDL.PROGRAMM_SUBORDER_ID = 272307) -- ПАРАМЕТРЫ ФИЛЬТРАЦИИ (ПЕРЕДАЕТСЯ ИНДЕКС ПЛАТЕЖНОГО УЗЛА)
    
    """,
    "update_status":"""
        UPDATE CUBE_SPECIFICATION 
        SET STOP = :stop 
        WHERE CUBE_SPECIFICATION_ID = :cube_specification_id
    
    """,
     
    "spec_select": """
    SELECT PDL.IND, -- СОХРАНЕНИЕ В ПОЛЕ SPEC_ID
       PD.DSE, -- СОХРАНЕНИЕ В ПОЛЕ DSE_ID
       (SELECT DM.DM_NAME || ' ' || DM.DM_DRAFT
          FROM DSE_MAIN DM
         WHERE DM.DM_INDEX = PD.DSE) AS DSE_NAME, -- НАИМЕНОВАНИЕ, ОБОЗНАЧЕНИЕ
       (SELECT PDT.NAME FROM PROGRAMM_DSE_TYPES PDT WHERE PDT.IND = PD.TYPE_) AS TYPE_SPEC, -- ТИП
       (SELECT COUNT(CS.CUBE_SPECIFICATION_ID)
          FROM CUBE_SPECIFICATION CS
         WHERE CS.SPEC_ID = PDL.IND) AS SH -- СХЕМ    
FROM PROGRAMM_DSE_LINK PDL, 
     PROGRAMM_DSE PD
WHERE PDL.PROGRAMM_DSE_ID = PD.IND AND
      PDL.PROGRAMM_SUBORDER_ID  = :pay_unit_id -- ПАРАМЕТРЫ ФИЛЬТРАЦИИ (ПЕРЕДАЕТСЯ ИНДЕКС ПЛАТЕЖНОГО УЗЛА)
    """,
    
    "insert_spec": """
    INSERT INTO CUBE_SPECIFICATION (
        DSE_ID,
        DATE_GENERAL,
        STOP,
        SPEC_ID
    )
    VALUES (
        :dse_id,
        TO_DATE(:date_general, 'YYYY-MM-DD'),
        :stop,
        :spec_id

    )
""", 
    
    "level_products": """ select d.dm_index, --0
       CASE 
         WHEN cc.cube_component_id IS NOT NULL THEN
          1
         ELSE
          0
       END AS Check_value, --1
       dc.short_name as class_name, --2
       d.dm_name as dse_name, --3
       d.dm_draft as dse_draft_number, --4
       a.cn_tech_marshrut as workshop_route,--5
       cc.date_start, --6
       cc.date_assembling, --7
       cc.date_end, --8
       a.da_index, --9
       pa.parent_da_path || '.' || a.da_index as da_path, --10
       sp.cube_specification_id, --11
       dc.seq as class_seq, --12 
       cc.cube_component_id --13
  from (select sp.cube_specification_id,
               l.programm_dse_id as prog_dse_id
          from cube_specification sp  
          left join programm_dse_link l  
            on l.ind = sp.spec_id
         where sp.cube_specification_id = :in_cube_spec_id) sp
 cross join (select pa.dm_index_what as parent_dse_id,
                    :in_parent_da_path as parent_da_path
               from dse_assembling pa 
              where pa.da_index = :in_parent_da_index
              union all
             select sp.dse_id,
                    '' as parent_da_path
               from cube_specification sp
              where sp.cube_specification_id = :in_cube_spec_id
                and (:in_parent_da_index is null)) pa
  join dse_assembling a
    on a.dm_index_where = pa.parent_dse_id
  join dse_main d
    on d.dm_index = a.dm_index_what
  join dse_classes dc
    on dc.ind = d.dm_class_id
  left join cube_components cc
    on cc.cube_specification_id = sp.cube_specification_id
   and cc.da_index = a.da_index
   and cc.da_path = pa.parent_da_path || '.' || a.da_index
  left join v_programm_dse_excludes ex
    on ex.programm_dse = sp.prog_dse_id
   and '.' || ex.exclude_path = pa.parent_da_path || '.' || a.da_index
 where a.da_class_id_what in (2456, 2454, 2797, 2896)
 union all
select d.dm_index,
       CASE
         WHEN cc.cube_component_id IS NOT NULL THEN
          1
         ELSE
          0
       END AS Check_value,
       dc.short_name as class_name,
       d.dm_name as dse_name,
       d.dm_draft as dse_draft_number,
       null as workshop_route,
       cc.date_start,
       cc.date_assembling, 
       cc.date_end,
       null as da_index,
       null as da_path,
       sp.cube_specification_id,
       dc.seq as class_seq,
       cc.cube_component_id
  from (select sp.cube_specification_id,
               sp.dse_id,
               l.programm_dse_id as prog_dse_id
          from cube_specification sp  
          left join programm_dse_link l
            on l.ind = sp.spec_id
         where sp.cube_specification_id = :in_cube_spec_id) sp
  join dse_main d
    on d.dm_index = sp.dse_id   
  join dse_classes dc
    on dc.ind = d.dm_class_id 
  left join cube_components cc
    on cc.cube_specification_id = sp.cube_specification_id
   and cc.da_index is null 
   and cc.da_path is null
 where :in_parent_da_index = 0
 order by class_seq, dse_draft_number, dse_name
 """,
 
 "check_cube_component": """
    SELECT 1 
    FROM cube_components 
    WHERE cube_component_id = :cube_component_id
"""
,

"update_cube_component": """
    UPDATE cube_components
    SET 
        cube_specification_id = :cube_specification_id,
        dse_id = :dse_id,
        date_start = TO_DATE(:date_start, 'YYYY-MM-DD'),
        date_assembling = TO_DATE(:date_assembling, 'YYYY-MM-DD'),
        date_end = TO_DATE(:date_end, 'YYYY-MM-DD'),
        da_index = :da_index,
        da_path = :da_path
    WHERE cube_component_id = :cube_component_id
"""
,
 
 
    "insert_cube_component": """
        INSERT INTO CUBE_COMPONENTS (
            cube_specification_id,
            dse_id,
            date_start,
            date_end,
            date_assembling,
            da_index,
            da_path 
        )
        VALUES (
            :cube_specification_id,
            :dse_id,
            TO_DATE(:date_start, 'YYYY-MM-DD'),
            TO_DATE(:date_end, 'YYYY-MM-DD'),
            TO_DATE(:date_assembling, 'YYYY-MM-DD'),
            :da_index,
            :da_path
        ) 
    """,
    
    'delete_cube_component': """
        DELETE FROM CUBE_COMPONENTS 
        WHERE cube_component_id = :component_id
    """
    ,
#     WITH target AS (
#   SELECT cube_component_id,
#          da_path,
#          cube_specification_id
#   FROM cube_components
#   WHERE cube_component_id = :component_id
# )
# DELETE FROM cube_components
# WHERE cube_component_id = (SELECT cube_component_id FROM target)
#    OR (da_path IS NOT NULL AND da_path LIKE '%' || da_index || '.%')
#    OR (
#         (SELECT da_path FROM target) IS NULL 
#         AND cube_specification_id = (SELECT cube_specification_id FROM target)
#       );

      
    'delete_spec': """
        DELETE FROM CUBE_SPECIFICATION
        WHERE CUBE_SPECIFICATION_ID = :spec_id
    """, 
    
    "update_spec_date":"""
        UPDATE CUBE_SPECIFICATION 
        SET DATE_GENERAL = TO_DATE(:date_start , 'YYYY-MM-DD')
        WHERE CUBE_SPECIFICATION_ID = :cube_specification_id
    
    """,
 
    
#  Для диаграммы Ганнта
"gantt": """
    SELECT 
    'S' || cc.cube_component_id AS id,
    dm.dm_name || ' ' || dm.dm_draft AS name,
    CASE 
        WHEN cc_parent.cube_component_id IS NOT NULL THEN 'S' || cc_parent.cube_component_id 
        ELSE NULL 
    END AS parent,
    TO_CHAR(cc.date_start, 'YYYY-MM-DD') AS d_start,
    TO_CHAR(cc.date_end, 'YYYY-MM-DD') AS d_end,
    0 AS progress,
    CASE 
        WHEN cc_parent.cube_component_id IS NOT NULL THEN 'S' || cc_parent.cube_component_id 
        ELSE NULL 
    END AS dependency,
    '#7cb5ec' AS color,  -- Синий — основная задача
    NULL AS milestone
FROM cube_components cc
JOIN dse_main dm ON dm.dm_index = cc.dse_id
LEFT JOIN dse_assembling da ON da.dm_index_what = cc.dse_id
LEFT JOIN cube_components cc_parent ON cc_parent.dse_id = da.dm_index_where 
    AND cc_parent.cube_specification_id = cc.cube_specification_id
WHERE cc.cube_specification_id = :node_id

UNION ALL

SELECT 
    'K' || cc.cube_component_id AS id,
    'Изготовление комплектующих' AS name,
    'S' || cc.cube_component_id AS parent,
    TO_CHAR(cc.date_start, 'YYYY-MM-DD') AS d_start,
    TO_CHAR(cc.date_assembling, 'YYYY-MM-DD') AS d_end,
    0 AS progress,
    NULL AS dependency,
    '#f7a35c' AS color,  -- Оранжевый
    NULL AS milestone
FROM cube_components cc
WHERE cc.cube_specification_id = :node_id

UNION ALL

SELECT 
    'I' || cc.cube_component_id AS id,
    'Сборка/обработка изделия' AS name,
    'S' || cc.cube_component_id AS parent,
    TO_CHAR(cc.date_assembling, 'YYYY-MM-DD') AS d_start,
    TO_CHAR(cc.date_end, 'YYYY-MM-DD') AS d_end,
    0 AS progress,
    'K' || cc.cube_component_id AS dependency,
    '#90ed7d' AS color,  -- Зеленый
    NULL AS milestone
FROM cube_components cc
WHERE cc.cube_specification_id = :node_id


    """,

# Вывод списка рабочих центров
"work_center": """
    SELECT 
        m.wc_id,
        (SELECT w.short_name FROM workshop w WHERE w.ind = m.dep_id) AS dep_name,
        m.name,
        (SELECT t.name FROM tec_types t WHERE t.ind = m.tech_type_id) AS tec_name,
        m.class_num_ws,
        m.class_num_all,
        m.model_name,
        (SELECT COUNT(p.wcp_id) FROM wc_positions p WHERE p.wc_id = m.wc_id) AS num_comp,
        m.dep_id
    FROM 
        wc_main m
    WHERE 
        m.is_deleted = 0
    ORDER BY
        dep_name,
        m.class_num_ws,
        m.class_num_all
        --dep_name,
        --tec_name,
        --m.name
""",

# Состав рабочего центра старая версия
"wc_positions": """
    SELECT 
        p.wcp_id,
        p.wc_id,
        p.worker_id,
        w.name AS worker_name,
        w.clock_number AS worker_number
    FROM 
        wc_positions p
    LEFT JOIN 
        workers w ON w.ind = p.worker_id
    WHERE
        p.is_deleted = 0 AND
        p.wc_id = :wc_id
""",

# Список цехов директора производства
"workshop_dp": """
    SELECT 
        w.ind, 
        w.short_name 
    FROM 
        workshop w 
    WHERE 
        w.ind IN (2, 3, 4, 12, 14, 29) 
    ORDER BY 
        w.short_name
""",

# Основные типы техпроцессов
"main_spec_type": """
    SELECT 
        t.ind,
        t.short_name,
        t.name,
        t.*
    FROM 
        tec_types t
    WHERE 
        t.ind NOT IN (0, 6, 7, 10, 12)
""",

# Пометка на удаление рабочего центра
"delete_wc": """
    UPDATE wc_main 
    SET is_deleted = 1
    WHERE wc_id = :wc_id
""",

# Обновление рабочего центра 
"update_wc": """
    UPDATE WC_MAIN
    SET 
        name = :name,
        dep_id = :dep_id,
        class_num_ws = :class_num_ws,
        class_num_all = :class_num_all,
        tech_type_id = :tech_type_id
    WHERE 
        wc_id = :wc_id
""",

# Создание нового рабочего центра
"insert_wc": """
    INSERT INTO WC_MAIN (
        name,
        dep_id,
        class_num_ws,
        class_num_all,
        tech_type_id
    ) VALUES (
        :name,
        :dep_id,
        :class_num_ws,
        :class_num_all,
        :tech_type_id
    )
""",

# Список бригад/рабочих цеха с чеком для выбора в состав РЦ
"wc_pos": """
SELECT 
    w.ind,
    COUNT(CASE WHEN pp.wc_id = :wc_id THEN 1 END) AS check_val,
    w.clock_number,
    w.name,
    s.name AS specialty,
    m.name AS center_name
FROM 
    workers w
LEFT JOIN 
    workers_specialty s ON s.ind = w.specialty_id
LEFT JOIN 
    wc_positions p ON p.worker_id = w.ind
LEFT JOIN 
    wc_main m ON m.wc_id = p.wc_id
LEFT JOIN 
    wc_positions pp ON pp.worker_id = w.ind AND pp.wc_id = :wc_id
WHERE 
    w.workshop = :dep_id
    AND w.del = 0
    AND w.brigade IS NULL
GROUP BY 
    w.ind, w.clock_number, w.name, s.name, m.name, w.is_brigade
ORDER BY
    check_val DESC,
    specialty,
    w.is_brigade DESC,
    w.name
""",

# Удаление рабочего из РЦ
"del_workers_wc": """
DELETE FROM wc_positions WHERE worker_id = :worker_id
""",

# Добавление рабочего в РЦ
"add_worker_wc": """
INSERT INTO wc_positions (wc_id, worker_id) VALUES (:wc_id, :worker_id)
""",

# Выборка операций по рабочему центру для обучения
"wc_oper": """
SELECT DISTINCT
       wcm.wc_id AS resource_id,
       wcm.class_num_ws AS target,
       wcm.name AS resource_name,
       dc.short_name AS dse_class,
       TO_CHAR(NVL(TRIM(mh.kind_of_hire_name), 'н/д')) AS m_name, 
       TO_CHAR(NVL(TRIM(mh.hire_height), 'н/д')) AS m_p1,  
       TO_CHAR(NVL(TRIM(mh.hire_width), 'н/д')) AS m_p2,  
       TO_CHAR(NVL(TRIM(mh.hire_length), 'н/д')) AS m_p3,
       NVL(NVL2(mh.dm_index, 
           LTRIM(RTRIM(NVL2(TRIM(mh.kind_of_hire_name), mh.kind_of_hire_name || '~', NULL) || 
                 NVL2(TRIM(mh.hire_height), mh.hire_height || '~', NULL) || 
                 NVL2(TRIM(mh.hire_width), mh.hire_width || '~', NULL) || 
                 mh.hire_length, '~ '), '~ '), NULL), 
           dc.short_name) AS material_name,
       oo.is_cnc,
       NVL(pr.name, 'н/д') AS trade,
       too.name AS oper_type,
       tg.code_t AS oper_group,
       ts.code AS tarif,
       TO_CHAR(po.code_bill) AS bill,
       pg.short_name AS product_group,
       DECODE(bu.ind, 1, 'н/д', NULL, 'н/д', bu.short_name) AS bu_name,
       ot.tec_type,
    -- p.valid_num AS dse_count,
       o.base_time,
    -- wcm.tech_type_id as wc_type,
       d.dse
       -- 
       --, DECODE(ot.tec_type, 2, tm.name, NULL) AS tool_unit_name
       --, DECODE(ot.tec_type, 2, tu.ind, NULL) AS tool_unit_id
  FROM work_order_main m
  JOIN work_order_dse d
    ON d.wom = m.ind
  JOIN work_order_operations o
    ON o.wod = d.ind
  JOIN work_order_pu p
    ON p.wod = d.ind
   AND p.ino_ind IS NULL  -- искл. межцеховые
  JOIN ort_operations oo
    ON oo.ind = o.operation_ind
  JOIN ort_technologyes ot
    ON ot.ind = oo.oper_technology
  JOIN programm_order po
    ON po.ind = p.bill_order
  LEFT JOIN production_groups pg
    ON pg.ind = po.order_group
  LEFT JOIN business_units bu
    ON bu.ind = po.business_unit
  JOIN wc_positions wcp
    ON wcp.worker_id = m.worker_ind
  JOIN wc_main wcm
    ON wcm.wc_id = wcp.wc_id
   AND wcm.dep_id = m.workshop_ind    -- цех наряда совпадает с цехом ресурса
   AND wcm.tech_type_id = ot.tec_type -- ТП операции совпадает с ТП ресурса
  JOIN dse_main dm
    ON dm.dm_index = d.dse
  JOIN dse_classes dc
    ON dc.ind = dm.dm_class_id
  LEFT JOIN mv_dse_material_hire mh
    ON mh.dm_index = dm.dm_index
  LEFT JOIN tools_operations too
    ON too.ind = o.operation_type_id
  LEFT JOIN tools_group tg
    ON tg.ind = o.tool_group
  LEFT JOIN tarif_scale ts
    ON ts.ind = o.tarif_scale
  LEFT JOIN tools_units tu
    ON tu.ind = o.tool_unit_id
  LEFT JOIN tools_models tm
    ON tm.ind = tu.model_id
  LEFT JOIN ort_trades pr
    ON (ot.is_wshop = 0 AND pr.ind || '' = oo.trade_code) 
    OR (ot.is_wshop = 1 AND pr.code = oo.trade_code)
 WHERE m.workshop_ind = :worshop_id -- ЦЕХ
   -- AND ot.tec_type = :tec_type_id -- ТИП ТП
   AND TRUNC(m.date_realization) BETWEEN '01.01.2024' AND '15.05.2025'
   AND o.base_time + o.preparation_time > 0 -- ???
   AND wcm.is_plan = 1
"""

,
"test_jobs":
    """
    select cj_id, dm.dm_name, start_job, end_job
    from cube_job_plan cjp
    join cube_jobs cj on cjp.cj_id = cj.cube_job_id
    join cube_components cc on cc.CUBE_COMPONENT_ID = cj.CUBE_COMPONENT_ID
    JOIN dse_main dm ON dm.dm_index = cc.dse_id
    where cc.cube_component_id = :cc_id 
    ORDER BY cjp.start_job
    """,

# Выборка job без рабочих центров
"job_not_wc": """
    SELECT 
        o.cube_job_id
    FROM 
        cube_job_opers o, ort_operations ort
    WHERE 
        NOT EXISTS (
            SELECT 1 
            FROM cube_job_resources r 
            WHERE r.cube_job_id = o.cube_job_id)
    AND ort.ind = o.operation_id
    AND o.count - o.count_ready >0
    AND o.dep_id  in(2, 3, 29, 4, 12, 14)
    AND ort.oper_type != 369
    
""",

# Выборка Job для предсказания рабочего центра
"pred_wc": """
SELECT 
    --wcm.wc_id as resource_id,
    --wcm.class_num_ws as target,
    --wcm.name as resource_name,
    (
        SELECT (SELECT 
                    ww.short_name 
                FROM 
                    workshop ww 
                WHERE 
                    ww.ind = w.workshop_id)
        FROM ort_operations_wshops w
        WHERE w.operation_id = (
            SELECT o.operation_id
            FROM cube_job_opers o
            WHERE o.cube_job_id = :cube_job_id
        )
        AND w.is_base = 1
    ) AS workshop,
    dc.short_name AS dse_class,
    TO_CHAR(NVL(TRIM(mh.kind_of_hire_name), 'н/д')) AS m_name, 
    TO_CHAR(NVL(TRIM(mh.hire_height), 'н/д')) AS m_p1,  
    TO_CHAR(NVL(TRIM(mh.hire_width), 'н/д')) AS m_p2,  
    TO_CHAR(NVL(TRIM(mh.hire_length), 'н/д')) AS m_p3,
    NVL(
        NVL2(mh.dm_index, 
            LTRIM(RTRIM(
                NVL2(TRIM(mh.kind_of_hire_name), mh.kind_of_hire_name || '~', NULL) || 
                NVL2(TRIM(mh.hire_height), mh.hire_height || '~', NULL) || 
                NVL2(TRIM(mh.hire_width), mh.hire_width || '~', NULL) || 
                mh.hire_length, 
                '~ '
            ), 
            '~ '
        ), 
        NULL
    ), 
    dc.short_name
    ) AS material_name,
    oo.is_cnc,
    NVL(pr.name, 'н/д') AS trade,
    too.name AS oper_type,
    tg.code_t AS oper_group,
    ts.code AS tarif,
    TO_CHAR(po.code_bill) AS bill,
    pg.short_name AS product_group,
    DECODE(bu.ind, 1, 'н/д', NULL, 'н/д', bu.short_name) AS bu_name,
    ot.tec_type,
    jo.count AS dse_count,
    jo.count_ready AS dse_count_ready,
    jo.base_time,
    -- jo.prep_time,
    -- wcm.tech_type_id as wc_type,
    ot.dse
FROM 
    cube_job_opers jo
    JOIN cube_jobs j ON j.cube_job_id = jo.cube_job_id
    JOIN cube_specification spec ON spec.cube_specification_id = j.cube_spec_id
    LEFT JOIN programm_dse_link dl ON dl.ind = spec.spec_id
    LEFT JOIN programm_dse pd ON pd.ind = dl.programm_dse_id
    JOIN ort_operations oo ON oo.ind = jo.operation_id
    JOIN ort_technologyes ot ON ot.ind = oo.oper_technology
    JOIN programm_order po ON po.ind = pd.programm_order
    LEFT JOIN production_groups pg ON pg.ind = po.order_group
    LEFT JOIN business_units bu ON bu.ind = po.business_unit
    JOIN dse_main dm ON dm.dm_index = ot.dse
    JOIN dse_classes dc ON dc.ind = dm.dm_class_id
    LEFT JOIN mv_dse_material_hire mh ON mh.dm_index = dm.dm_index
    LEFT JOIN tools_operations too ON too.ind = oo.oper_type
    LEFT JOIN tools_group tg ON tg.ind = oo.tool_group
    LEFT JOIN tarif_scale ts ON ts.ind = oo.tarif_scale
    LEFT JOIN ort_trades pr ON (ot.is_wshop = 0 AND pr.ind || '' = oo.trade_code) 
                           OR (ot.is_wshop = 1 AND pr.code = oo.trade_code)
WHERE 
    jo.cube_job_id = :cube_job_id
    --AND too.ind != 369 -- контроль качества
    --AND jo.count - jo.count_ready > 0 --проверка на выполненные операции
"""
, 
# Выбор цеха для загрузки графика работ
"select_dep":
    """
   SELECT distinct
    w.short_name AS dep_name
FROM 
    wc_main m
JOIN 
    workshop w ON w.ind = m.dep_id
        order by dep_name

"""
, 
# 
"show_dep":
    """
    SELECT 
    m.wc_id,
    w.short_name AS dep_name,
    m.name
FROM 
    wc_main m
JOIN 
    workshop w ON w.ind = m.dep_id
WHERE 
    w.short_name = :dep_id 

""",
# Все записи без ресурса с аттрибутами для предсказания на GPU
"all_jobs_not_in_res": """
SELECT 
    -- wcm.wc_id as resource_id,
    -- wcm.class_num_ws as target,
    -- wcm.name as resource_name,
    jo.cube_job_id,
    (SELECT ww.short_name FROM workshop ww WHERE ww.ind = jo.dep_id) AS workshop_name,
    dc.short_name AS dse_class,
    TO_CHAR(NVL(TRIM(mh.kind_of_hire_name), 'н/д')) AS m_name, 
    TO_CHAR(NVL(TRIM(mh.hire_height), 'н/д')) AS m_p1,
    TO_CHAR(NVL(TRIM(mh.hire_width), 'н/д')) AS m_p2,
    TO_CHAR(NVL(TRIM(mh.hire_length), 'н/д')) AS m_p3,
    NVL(
        NVL2(mh.dm_index, 
            LTRIM(RTRIM(
                NVL2(TRIM(mh.kind_of_hire_name), mh.kind_of_hire_name || '~', NULL) || 
                NVL2(TRIM(mh.hire_height), mh.hire_height || '~', NULL) || 
                NVL2(TRIM(mh.hire_width), mh.hire_width || '~', NULL) || 
                mh.hire_length, 
                '~ '
            ), 
            '~ '
        ), 
        NULL
    ), 
    dc.short_name
    ) AS material_name,
    oo.is_cnc,
    NVL(pr.name, 'н/д') AS trade,
    too.name AS oper_type,
    tg.code_t AS oper_group,
    ts.code AS tarif,
    TO_CHAR(po.code_bill) AS bill,
    pg.short_name AS product_group,
    DECODE(bu.ind, 1, 'н/д', NULL, 'н/д', bu.short_name) AS bu_name,
    ot.tec_type,
    -- jo.count AS dse_count,
    -- jo.count_ready AS dse_count_ready,
    jo.base_time,
    -- jo.prep_time,
    -- wcm.tech_type_id as wc_type,
    ot.dse
FROM 
    cube_job_opers jo
    INNER JOIN cube_jobs j ON j.cube_job_id = jo.cube_job_id
    INNER JOIN cube_specification spec ON spec.cube_specification_id = j.cube_spec_id
    LEFT JOIN programm_dse_link dl ON dl.ind = spec.spec_id
    LEFT JOIN programm_dse pd ON pd.ind = dl.programm_dse_id
    INNER JOIN ort_operations oo ON oo.ind = jo.operation_id
    INNER JOIN ort_technologyes ot ON ot.ind = oo.oper_technology
    INNER JOIN programm_order po ON po.ind = pd.programm_order
    LEFT JOIN production_groups pg ON pg.ind = po.order_group
    LEFT JOIN business_units bu ON bu.ind = po.business_unit
    INNER JOIN dse_main dm ON dm.dm_index = ot.dse
    INNER JOIN dse_classes dc ON dc.ind = dm.dm_class_id
    LEFT JOIN mv_dse_material_hire mh ON mh.dm_index = dm.dm_index
    LEFT JOIN tools_operations too ON too.ind = oo.oper_type
    LEFT JOIN tools_group tg ON tg.ind = oo.tool_group
    LEFT JOIN tarif_scale ts ON ts.ind = oo.tarif_scale
    LEFT JOIN ort_trades pr ON (ot.is_wshop = 0 AND pr.ind || '' = oo.trade_code) 
                           OR (ot.is_wshop = 1 AND pr.code = oo.trade_code)
WHERE 
    jo.count - jo.count_ready > 0
    AND jo.dep_id IN (2, 3, 29, 4, 12, 14)
    AND oo.oper_type != 369
    AND NOT EXISTS (
        SELECT 1 
        FROM cube_job_resources r 
        WHERE r.cube_job_id = jo.cube_job_id
    )
""",

# Выбор операций для предсказаний
"oper_for_predict":"""
SELECT DISTINCT 
    jo.operation_id, 
    jo.dep_id
FROM 
    cube_job_opers jo
INNER JOIN 
    ort_operations oo ON oo.ind = jo.operation_id
WHERE 
    NOT EXISTS (
        SELECT 1 
        FROM cube_job_resources r
        WHERE r.cube_job_id = jo.cube_job_id
    )
    AND oo.oper_type NOT IN(369) -- Исключения для типов операций
    AND jo.count - jo.count_ready > 0
""",
# Вставка предсказанного ресурса
"insert_resourse": """
INSERT INTO 
    cube_job_resources (cube_job_id, resource_id)
VALUES 
    (:cube_job_id, :resource_id)
""",
# Возвращает аттрибуты предсказанного ресурса
"get_res_atr": """
SELECT 
    w.wc_id
FROM 
    wc_main w
WHERE 
    w.dep_id = (
        SELECT 
            ww.ind 
        FROM 
            workshop ww 
        WHERE 
            ww.short_name = :worshop_short_name
    )
    AND w.class_num_ws = :class_num
    AND w.is_deleted = 0
"""
}