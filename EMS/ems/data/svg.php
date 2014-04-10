<?php
/****************************************************************************
**
** Copyright (C) 2011 Andrey Kartashov .
** All rights reserved.
** Contact: Andrey Kartashov (porter@porter.st)
**
** This file is part of the EMS web interface module of the genome-tools.
**
** GNU Lesser General Public License Usage
** This file may be used under the terms of the GNU Lesser General Public
** License version 2.1 as published by the Free Software Foundation and
** appearing in the file LICENSE.LGPL included in the packaging of this
** file. Please review the following information to ensure the GNU Lesser
** General Public License version 2.1 requirements will be met:
** http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** Other Usage
** Alternatively, this file may be used in accordance with the terms and
** conditions contained in a signed written agreement between you and Andrey Kartashov.
**
****************************************************************************/

require("common.php");
require_once('response.php');
require_once('def_vars.php');
require_once('database_connection.php');

//logmsg(__FILE__);
//logmsg(print_r($_REQUEST,true));

$tablename="";
if(isset($_REQUEST['id']))
    $tablename = $_REQUEST['id'];
else
    $res->print_error('Not enough required parameters.');
$type="";
if(isset($_REQUEST['type']))
    $type = $_REQUEST['type'];
else
    $res->print_error('Not enough required parameters.');

if(!isset($_REQUEST['svg']))
    $res->print_error('Not enough required parameters.');

header("Content-type: image/svg+xml");
header("Content-Disposition: attachment; filename=$tablename.svg");
header("Pragma: no-cache");
header("Expires: 0");

$dom = new DOMDocument;
$dom->preserveWhiteSpace = FALSE;
$dom->loadXML($_REQUEST['svg']);
$dom->formatOutput = TRUE;


$outstream = fopen("php://output", 'w');
fwrite($outstream,str_replace(", sans-serif","",$dom->saveXml()));
$outstream->close();
?>
