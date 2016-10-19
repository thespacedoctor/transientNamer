CREATE TABLE IF NOT EXISTS `TNS_spectra` (
  `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
  `TNSId` varchar(45) NOT NULL,
  `TNSuser` varchar(45) DEFAULT NULL,
  `dateCreated` datetime DEFAULT CURRENT_TIMESTAMP,
  `exptime` double DEFAULT NULL,
  `obsdate` datetime DEFAULT NULL,
  `reportAddedDate` datetime DEFAULT NULL,
  `specType` varchar(100) DEFAULT NULL,
  `survey` varchar(100) DEFAULT NULL,
  `telescope` varchar(100) DEFAULT NULL,
  `transRedshift` double DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateLastModified` datetime DEFAULT NULL,
  `remarks` VARCHAR(800) NULL DEFAULT NULL,
  `sourceComment` VARCHAR(800) NULL DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  UNIQUE KEY `tnsid_survey_obsdate` (`TNSId`,`survey`,`obsdate`)
) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
            
INSERT INTO `TNS_spectra` (`TNSId`,`TNSuser`,`exptime`,`obsdate`,`reportAddedDate`,`specType`,`survey`,`telescope`,`transRedshift`) VALUES ("2016asf" ,"DAO_OTS" ,"8300" ,"2016-03-08 07:46:14" ,"2016-03-08 20:17:56" ,"SN Ia" ,"DAO_OTS" ,"Plaskett Telescope_Plaskett" ,"0.021")  ON DUPLICATE KEY UPDATE  `TNSId`="2016asf", `TNSuser`="DAO_OTS", `exptime`="8300", `obsdate`="2016-03-08 07:46:14", `reportAddedDate`="2016-03-08 20:17:56", `specType`="SN Ia", `survey`="DAO_OTS", `telescope`="Plaskett Telescope_Plaskett", `transRedshift`="0.021", updated=IF( `TNSId`="2016asf" AND  `TNSuser`="DAO_OTS" AND  `exptime`="8300" AND  `obsdate`="2016-03-08 07:46:14" AND  `reportAddedDate`="2016-03-08 20:17:56" AND  `specType`="SN Ia" AND  `survey`="DAO_OTS" AND  `telescope`="Plaskett Telescope_Plaskett" AND  `transRedshift`="0.021", 0, 1), dateLastModified=IF( `TNSId`="2016asf" AND  `TNSuser`="DAO_OTS" AND  `exptime`="8300" AND  `obsdate`="2016-03-08 07:46:14" AND  `reportAddedDate`="2016-03-08 20:17:56" AND  `specType`="SN Ia" AND  `survey`="DAO_OTS" AND  `telescope`="Plaskett Telescope_Plaskett" AND  `transRedshift`="0.021", dateLastModified, NOW()) ;
