-- acore_world. Run by hand to remove mod-retail-library's rows. The module's own ids: creature
-- displays 200000-399999 (200000 + a retail display id) and creature models 200000-209999.
-- Remove the two client patches from the realm's patch list as well, or players keep the files.
DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN 200000 AND 399999;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` BETWEEN 200000 AND 399999;
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` BETWEEN 200000 AND 209999;
