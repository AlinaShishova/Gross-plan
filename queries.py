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
                (SELECT PD.TITLE FROM PROGRAMM_DSE PD WHERE PD.IND = CS.SPEC_ID) AS TITLE, -- ПРИМЕЧАНИЕ
                CS.SPEC_ID -- ИНДЕКС СПЕЦИФИКАЦИИ (СКРЫТ, НА ВСЯКИЙ СЛУЧАЙ)
        FROM 
            CUBE_SPECIFICATION CS
        WHERE 
            CS.SPEC_ID IN (SELECT PDL.IND
                        FROM PROGRAMM_DSE_LINK PDL
                        WHERE PDL.PROGRAMM_SUBORDER_ID = :ps_ind) -- ПАРАМЕТРЫ ФИЛЬТРАЦИИ (ПЕРЕДАЕТСЯ ИНДЕКС ПЛАТЕЖНОГО УЗЛА)
    
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
        "STOP",
        SPEC_ID,
    )
    VALUES (
        :dse_id,
        TO_DATE(:date_general, 'YYYY-MM-DD'),
        :stop,
        :spec_id,

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
}