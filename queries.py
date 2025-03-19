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
    "scheme":"""SELECT PS.IND, -- ИНДЕКС ПЛАТЕЖНОГО УЗЛА ПО НЕМУ ПЕРЕХОД НА СЛЕДУЮЩУЮ СТРАНИЧКУ
                    PO.CODE_BILL || '/' || PO.SUBCODE_BILL AS ORDER_NUM, --ЩПЗ
                    PO.CONTRACT_NUM, -- № КОНТРАКТА
                    PO.CUSTOMER_NAME, -- ЗАКАЗЧИК
                    PS.ORDER_NAME || ' ' || PS.ORDER_DRAFT AS NAME_DRAFT_NUM, -- НАИМЕНОВАНИЕ, ОБОЗНАЧЕНИЕ
                    PS.NUM, -- КОЛ-ВО
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
            SELECT 
                CS.CUBE_SPECIFICATION_ID,
                CS.CUBE_ID,
                CS.STOP,
                CS.DSE_ID,
                (SELECT 
                    DM.DM_NAME || ' ' || DM.DM_DRAFT
                FROM 
                    DSE_MAIN DM
                WHERE 
                    DM.DM_INDEX = CS.DSE_ID) AS DSE_NAME,
                (SELECT 
                    (SELECT PDT.NAME FROM PROGRAMM_DSE_TYPES PDT WHERE PDT.IND = PD.TYPE_)
                FROM 
                    PROGRAMM_DSE PD
                WHERE PD.IND = CS.SPEC_ID) AS TYPE_SPEC,
                CS.NUM,
                CS.DATE_GENERAL,
                (SELECT PD.TITLE FROM PROGRAMM_DSE PD WHERE PD.IND = CS.SPEC_ID) AS TITLE

            FROM 
                CUBE_SPECIFICATION CS
            WHERE 
                CS.CUBE_ID = 1 -- Тут параметр от формы!!!
    
    """,
}