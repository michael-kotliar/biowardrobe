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

try {
    $data = json_decode(file_get_contents('php://input'));
} catch (Exception $e) {
    $res->print_error("Cant read input" . $e);
}
//logmsg(print_r($_REQUEST,true));
//logmsg(print_r($data,true));


$V = $data->filters[0];

if (!isset($V->name) || !isset($V->conditions) || !isset($data->uuid) || !isset($data->project_id))
    $res->print_error("no data");
/**************************************************************
 ***************************************************************/
function get_field($f)
{
    global $res;
    switch ($f) {
        case 1:
            return array("name" => "RPKM", "field" => "RPKM_0");
        case 2:
            return array("name" => "Chromosome", "field" => "chrom");
    }
    $res->print_error("Error field");
}

$con = def_connect();
$con->select_db($db_name_ems);
$con->autocommit(FALSE);

$tablenames = array();

$c = 0;

check_val($data->uuid);

$WHERE = "0=0 ";
$WHEREC = "";
$FNAME = $V->name;
$EXT = get_extention(intval($V->annottype));
$UUID = $data->uuid;
$tbname = str_replace('-', '', $UUID);
check_val($data->project_id);
$project_id = $data->project_id;

$READABLE = $EXT['name'] . " were used <br>";
$FROM = "";
$RPKMS = "";
$gblink = "";
$retdata = array();

foreach ($V->conditions as $k2 => $val) {
    check_val($val->table);

    if (!isset($tablenames[$val->table])) {
        $tn = get_table_name($val->table);
        if (!$tn)
            $res->print_error("no tablename data");
        $tablenames[$val->table] = array("table" => $tn[0]['tableName'], "alias" => "a$c", "name" => $tn[0]['name']);
        if ($c > 0) {
            $WHEREC = $WHEREC . " and a" . ($c - 1) . ".refseq_id=a" . $c . ".refseq_id";
            $WHEREC = $WHEREC . " and a" . ($c - 1) . ".chrom=a" . $c . ".chrom";
            $WHEREC = $WHEREC . " and a" . ($c - 1) . ".txStart=a" . $c . ".txStart";
            $WHEREC = $WHEREC . " and a" . ($c - 1) . ".txEnd=a" . $c . ".txEnd";
            $WHEREC = $WHEREC . " and a" . ($c - 1) . ".strand=a" . $c . ".strand";
            $FROM = $FROM . "," . $db_name_experiments . "." . $tablenames[$val->table]['table'] . $EXT['ext'] . " " . $tablenames[$val->table]['alias'];
            $RPKMS = $RPKMS . "," . $tablenames[$val->table]['alias'] . "." . "RPKM_0 as `RPKM " . $tablenames[$val->table]['name'] . "`";
            $gblink = $gblink . "&" . $tn[0]['gblink'];
        } else {
            $FROM = $db_name_experiments . "." . $tablenames[$val->table]['table'] . $EXT['ext'] . " " . $tablenames[$val->table]['alias'];
            $RPKMS = $tablenames[$val->table]['alias'] . "." . "RPKM_0 as `RPKM " . $tablenames[$val->table]['name'] . "`";
            $gblink = $tn[0]['gblink'];
        }
        $c++;
    }
    $exp = get_expression(intval($val->condition));
    $field = get_field(intval($val->field));
    $op = get_operand(intval($val->operand));

    if (intval($val->field) == 2) { //chrom
        $WHERE = $WHERE . " $op " . $val->bracketl . $tablenames[$val->table]['alias'] . "." . $field['field'] . " " . $exp['exp'] . " '" . $val->value . "'" . $val->bracketr; //replace potentioal injection !
    } else {
        $WHERE = $WHERE . " $op " . $val->bracketl . $tablenames[$val->table]['alias'] . "." . $field['field'] . " " . $exp['exp'] . " " . floatval($val->value) . "" . $val->bracketr;
    }

    $READABLE = $READABLE . "$op $val->bracketl'" . $tablenames[$val->table]['name'] . "' " . $field['name'] . " " . $exp['name'] . " " . floatval($val->value) . "$val->bracketr<br>\n";
}

$SQL = "CREATE VIEW " . $db_name_experiments . "." . $tbname . " AS " .
    "select a0.refseq_id as refseq_id," .
    "a0.gene_id AS gene_id," .
    "a0.chrom AS chrom," .
    "a0.txStart AS txStart," .
    "a0.txEnd AS txEnd," .
    "a0.strand AS strand," .
    $RPKMS .
    " FROM " . $FROM . " WHERE $WHERE $WHEREC ";
execSQL($con, $SQL, array(), true);

execSQL($con, "insert into " . $db_name_ems . ".genelist (id,name,project_id,leaf,db,`type`,tableName,gblink,conditions,rtype_id) values(?,?,?,1,?,2,?,?,?)",
    array("sssssss", $UUID, $V->name, $project_id, $db_name_experiments, $tbname, $gblink, $READABLE, $EXT['id']), true);

if (!$con->commit()) {
    $res->print_error("Cant commit");
}

$con->close();


$res->success = true;
$res->message = "Data loaded";
$res->total = 1;
$res->data = array("id" => $UUID, "conditions" => $READABLE, "gblink" => $gblink);
print_r($res->to_json());

?>
