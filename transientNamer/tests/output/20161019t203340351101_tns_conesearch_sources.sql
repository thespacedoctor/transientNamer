CREATE TABLE IF NOT EXISTS `TNS_sources` (
  `primaryId` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'An internal counter',
  `TNSId` varchar(20) NOT NULL,
  `TNSName` varchar(20) DEFAULT NULL,
  `dateCreated` datetime DEFAULT NULL,
  `decDeg` double DEFAULT NULL,
  `decSex` varchar(45) DEFAULT NULL,
  `discDate` datetime DEFAULT NULL,
  `discMag` double DEFAULT NULL,
  `discMagFilter` varchar(45) DEFAULT NULL,
  `discSurvey` varchar(100) DEFAULT NULL,
  `discoveryName` varchar(100) DEFAULT NULL,
  `objectUrl` varchar(200) DEFAULT NULL,
  `raDeg` double DEFAULT NULL,
  `raSex` varchar(45) DEFAULT NULL,
  `specType` varchar(100) DEFAULT NULL,
  `transRedshift` double DEFAULT NULL,
  `updated` tinyint(4) DEFAULT '0',
  `dateLastModified` datetime DEFAULT NULL,
  `hostName` VARCHAR(100) NULL DEFAULT NULL,
  `hostRedshift` DOUBLE NULL DEFAULT NULL, 
  `survey` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`primaryId`),
  UNIQUE KEY `tnsid` (`TNSId`)
) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
            
INSERT INTO `TNS_sources` (`TNSId`,`TNSName`,`decDeg`,`decSex`,`discDate`,`discMag`,`discMagFilter`,`discSurvey`,`discoveryName`,`hostName`,`hostRedshift`,`objectUrl`,`raDeg`,`raSex`,`separationArcsec`,`separationEastArcsec`,`separationNorthArcsec`,`specType`,`transRedshift`) VALUES ("2016asf" ,"SN2016asf" ,"31.1126" ,"+31:06:45.36" ,"2016-03-06 08:09:36" ,"17.1" ,"V-Johnson" ,"ASAS-SN" ,"ASASSN-16cs" ,"KUG 0647+311" ,null ,"http://wis-tns.weizmann.ac.il/object/2016asf" ,"102.653041667" ,"06:50:36.73" ,"0.66" ,"-0.13" ,"0.65" ,"SN Ia" ,"0.021")  ON DUPLICATE KEY UPDATE  `TNSId`="2016asf", `TNSName`="SN2016asf", `decDeg`="31.1126", `decSex`="+31:06:45.36", `discDate`="2016-03-06 08:09:36", `discMag`="17.1", `discMagFilter`="V-Johnson", `discSurvey`="ASAS-SN", `discoveryName`="ASASSN-16cs", `hostName`="KUG 0647+311", `hostRedshift`=null, `objectUrl`="http://wis-tns.weizmann.ac.il/object/2016asf", `raDeg`="102.653041667", `raSex`="06:50:36.73", `separationArcsec`="0.66", `separationEastArcsec`="-0.13", `separationNorthArcsec`="0.65", `specType`="SN Ia", `transRedshift`="0.021", updated=IF( `TNSId`="2016asf" AND  `TNSName`="SN2016asf" AND  `decDeg`="31.1126" AND  `decSex`="+31:06:45.36" AND  `discDate`="2016-03-06 08:09:36" AND  `discMag`="17.1" AND  `discMagFilter`="V-Johnson" AND  `discSurvey`="ASAS-SN" AND  `discoveryName`="ASASSN-16cs" AND  `hostName`="KUG 0647+311" AND  `hostRedshift` is null AND  `objectUrl`="http://wis-tns.weizmann.ac.il/object/2016asf" AND  `raDeg`="102.653041667" AND  `raSex`="06:50:36.73" AND  `separationArcsec`="0.66" AND  `separationEastArcsec`="-0.13" AND  `separationNorthArcsec`="0.65" AND  `specType`="SN Ia" AND  `transRedshift`="0.021", 0, 1), dateLastModified=IF( `TNSId`="2016asf" AND  `TNSName`="SN2016asf" AND  `decDeg`="31.1126" AND  `decSex`="+31:06:45.36" AND  `discDate`="2016-03-06 08:09:36" AND  `discMag`="17.1" AND  `discMagFilter`="V-Johnson" AND  `discSurvey`="ASAS-SN" AND  `discoveryName`="ASASSN-16cs" AND  `hostName`="KUG 0647+311" AND  `hostRedshift` is null AND  `objectUrl`="http://wis-tns.weizmann.ac.il/object/2016asf" AND  `raDeg`="102.653041667" AND  `raSex`="06:50:36.73" AND  `separationArcsec`="0.66" AND  `separationEastArcsec`="-0.13" AND  `separationNorthArcsec`="0.65" AND  `specType`="SN Ia" AND  `transRedshift`="0.021", dateLastModified, NOW()) ;
