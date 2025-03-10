queries = {
    "keys":"""SELECT d.dm_index,
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
    "order":"""SELECT CM.CUBE_ID, --ИД используется для перехода на следующую страницу (срыт)
                CM.STATUS, -- статус, должен быть img но пока не придумал как реализовать
                PO.CODE_BILL || '/' || PO.SUBCODE_BILL AS ORDER_NUM,
                PO.SHORT_NAME, -- Название ШПЗ
                (SELECT PS.ORDER_NAME || ' ' || PS.ORDER_DRAFT
        FROM PROGRAMM_SUBORDER PS
        WHERE PS.PROGRAMM_ORDER = PO.IND) AS PU_NAME -- Название платежного узла
        FROM CUBE_MAIN CM, PROGRAMM_ORDER PO
        WHERE CM.ORDER_ID = PO.IND
        AND CM.STATUS IN (0, 1)""",
}