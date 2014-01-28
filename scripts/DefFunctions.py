#! /usr/bin/env python
##/****************************************************************************
##**
##** Copyright (C) 2011 Andrey Kartashov .
##** All rights reserved.
##** Contact: Andrey Kartashov (porter@porter.st)
##**
##** This file is part of the global module of the genome-tools.
##**
##** GNU Lesser General Public License Usage
##** This file may be used under the terms of the GNU Lesser General Public
##** License version 2.1 as published by the Free Software Foundation and
##** appearing in the file LICENSE.LGPL included in the packaging of this
##** file. Please review the following information to ensure the GNU Lesser
##** General Public License version 2.1 requirements will be met:
##** http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
##**
##** Other Usage
##** Alternatively, this file may be used in accordance with the terms and
##** conditions contained in a signed written agreement between you and Andrey Kartashov.
##**
##****************************************************************************/

import os
import sys

import smtplib
import glob
import subprocess as s # import call
import time
import re
import random
import MySQLdb 
import warnings

error=list()
error.append('Error')
error.append('')
warning=list()
warning.append('Warning')
warning.append('')
success=list()
success.append('Success')
success.append('')

    
def send_mail(toaddrs,body):
    fromaddr='ems@ems.chmccorp.cchmc.org'
    # Add the From: and To: headers at the start!
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
           % (fromaddr,toaddrs,body))
    msg = msg + body
                                                   
    server = smtplib.SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


def error_msg(msg):
    #print """
    #	{"success": false, "message": "%s" }"""%(msg.replace('"','\\"'))
    print """ %s """%(msg)
    sys.exit()


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def check_running(fname):
    if os.path.isfile(fname):
        old_pid=file(fname, 'r').readline()
        if check_pid(int(old_pid)):
            sys.exit()
    file(fname, 'w').write(str(os.getpid()))


def file_exist(basedir,fname,extension):
    LIST=glob.glob(basedir+'/'+fname+'.'+extension)
    return LIST

def macs_data(infile):
    FRAGMENT=0
    ISLANDS=0
    FNAME=infile
    if ";" in infile:
	FNAME=infile.split(";")[0]
    for line in open(FNAME+'_macs_peaks.xls'):
        if re.match('^# d = ',line):
            FRAGMENT=int(line.split('d = ')[1])
            continue
        if re.match('^#',line):
            continue
        if line.strip() != "":
            ISLANDS=ISLANDS+1
    ISLANDS=ISLANDS-1 #header
    return [FRAGMENT,ISLANDS]


def upload_macsdata(conn,infile,dbexp,db,NAME,grp,share=False):
    FNAME=infile
    if ";" in infile:
	FNAME=infile.split(";")[0]

    warnings.filterwarnings('ignore', category=MySQLdb.Warning) 
    cursor=conn.cursor()

    if len(file_exist('.',FNAME+'_macs_peaks','xls')) != 1:
	error[1] = ' MACS peak file does not exist'
	return error 

    table_name=dbexp+'.'+FNAME+'_macs'
    
    cursor.execute ("DROP TABLE IF EXISTS "+table_name)
    cursor.execute ("""
       CREATE TABLE """+table_name+"""
        (
    chrom varchar(255) NOT NULL,
    start int(10) unsigned NOT NULL,
    end int(10) unsigned NOT NULL,
    length int(10) unsigned NOT NULL,
    abssummit int(10),
    pileup float, 
    log10p float,
    foldenrich float,
    log10q float,
    INDEX chrom_idx (chrom) using btree,
    INDEX start_idx (start) using btree,
    INDEX end_idx (end) using btree
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8 """)
    conn.commit()

    dbtblname=db+'.'+FNAME
    cursor.execute ("""
    CREATE OR REPLACE VIEW """ +dbtblname+"""_islands AS 
    select 0 as bin, chrom, start as chromStart, end as chromEnd,max(log10p) as name, max(log10q) as score
    from """ +table_name+"""
    group by chrom,start,end; """)
    conn.commit()


    cursor.execute ("""
    delete from """+db+""".trackDb_local where tablename like '"""+FNAME+"""_grp'; """)
    conn.commit()

    cursor.execute ("""
    insert ignore into """+db+""".trackDb_local (tablename,shortLabel,type,longLabel,visibility,priority,
    colorR,colorG,colorB,altColorR,altColorG,altColorB,useScore,private,restrictCount,restrictList,url,html,grp,canPack,settings)
    values('"""+FNAME+"""_grp','"""+NAME+"""','bed 4 +','"""+NAME+"""',
    0,10,0,0,0,0,0,0,0,0,0,'','','','"""+grp+"""',1,
    'compositeTrack on\ngroup """+grp+"""\ntrack """+FNAME+"""_grp');""")
    conn.commit()
    
    cursor.execute ("""
    delete from """+db+""".trackDb_local where tablename like '"""+FNAME+"""_islands'; """)
    conn.commit()

    cursor.execute ("""
    insert ignore into """+db+""".trackDb_local (tablename,shortLabel,type,longLabel,visibility,priority,
    colorR,colorG,colorB,altColorR,altColorG,altColorB,useScore,private,restrictCount,restrictList,url,html,grp,canPack,settings)
    values('"""+FNAME+"""_islands','"""+NAME+""" islands','bed 4 +','"""+NAME+""" islands',
    0,10,0,0,0,0,0,0,0,0,0,'','','','"""+grp+"""',1,
    'parent """+FNAME+"""_grp\ntrack """+FNAME+"""_islands\nvisibility dense'); """)
    conn.commit()

    cursor.execute ("""
    delete from """+db+""".trackDb_external where tablename like '"""+FNAME+"""_islands'; """)
    conn.commit()
    cursor.execute ("""
    delete from """+db+""".trackDb_external where tablename like '"""+FNAME+"""_grp'; """)
    conn.commit()
    
    if share:
	cursor.execute ("""
        insert ignore into """+db+""".trackDb_external (tablename,shortLabel,type,longLabel,visibility,priority,
        colorR,colorG,colorB,altColorR,altColorG,altColorB,useScore,private,restrictCount,restrictList,url,html,grp,canPack,settings)
        values('"""+FNAME+"""_grp','"""+NAME+"""','bed 4 +','"""+NAME+"""',
        0,10,0,0,0,0,0,0,0,0,0,'','','','"""+grp+"""',1,
        'compositeTrack on\ngroup """+grp+"""\ntrack """+FNAME+"""_grp');""")
        conn.commit()
	cursor.execute ("""
	insert ignore into """+db+""".trackDb_external (tablename,shortLabel,type,longLabel,visibility,priority,
	colorR,colorG,colorB,altColorR,altColorG,altColorB,useScore,private,restrictCount,restrictList,url,html,grp,canPack,settings)
	values('"""+FNAME+"""_islands','"""+NAME+""" islands','bed 4 +','"""+NAME+""" islands',
	0,10,0,0,0,0,0,0,0,0,0,'','','','"""+grp+"""',1,
	'parent """+FNAME+"""_grp\ntrack """+FNAME+"""_islands\nvisibility dense'); """)
	conn.commit()
    

    SQL="INSERT INTO "+table_name+" (chrom,start,end,length,abssummit,pileup,log10p,foldenrich,log10q) VALUES"
    SQLB="INSERT INTO "+table_name+" (chrom,start,end,length,pileup,log10p,foldenrich,log10q) VALUES"

    skip=True
    broad=False
    islands=0
    for line in open(FNAME+'_macs_peaks.xls','r'):
	if re.match('^#',line) or line.strip()=="":
	    continue
	if skip:
	    a=line.strip().split('\t')
	    broad=("pileup" in a[4])
	    skip=False
	    continue
	a=line.strip().split('\t')
	islands=islands+1
	try:
	    if broad:
		cursor.execute(SQLB+" (%s,%s,%s,%s,%s,%s,%s,%s)",(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]))
	    else:
		cursor.execute(SQL+" (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8]))
    	    conn.commit()
	except Exception, e: 
	    error[1]=line+":"+str(e) 
	    return error
	    	    
    success[1]=islands
    return success


def run_macs(infile,db,fragsize=150,fragforce=False,broad=False,force=None):
    format="BAM"
    FN=infile
    shiftsize=int(fragsize/2)
    
    if ";" in infile:
	FN=infile.split(";")[0]
	format="BAMPE"
        
    if len(file_exist('.',FN,'bam')) != 1:
	error[1]='Bam file does not exist'
	return error

    if force:
	FL=file_exist('.',FN+'_macs_peaks','xls')
	if len(FL) == 1:
	    os.unlink(FL[0])

    if len(file_exist('.',FN+'_macs_peaks','xls')) == 1:
	success[1]=' Macs analyzes done '
	return success

    G='hs'
    if 'mm' in db:
	G='mm'

    ADPAR=""
    if fragforce:
	ADPAR=ADPAR+" --nomodel "
    if broad:
    	ADPAR=ADPAR+" --broad "
    else:
	ADPAR=ADPAR+" --call-summits "

    
    PAR='macs callpeak -t '+FN+'.bam -n '+FN+'_macs -g '+G+' --format '+format+' -m 3 60  --verbose 0 --shiftsize='+str(shiftsize)+' -q 0.2 '+ADPAR+' >./'+FN+'_macs.log 2>&1'
    RET=''
    #print PAR
    try:
	RET=s.check_output(PAR,shell=True)
	success[1]=' MACS finished '
	return success
    except Exception,e:
	error[1]=str(e)+RET
	return error

def run_bedgraph(infile,group,name4browser,bedformat,db,fragment,isRNA,force=None):
    pair=False
    FN=infile
    if ";" in infile:
	pair=True
	FN=infile.split(";")[0]
        
    if force:
	FL=file_exist('.',FN,'log')
	if len(FL) == 1:
	    os.unlink(FL[0])

    if len(file_exist('.',FN,'log')) == 1:
	success[1]=' Bedgraph uploaded'
	return success

    PAR='bam2bedgraph -sql_table="'+FN+'" -in="'+FN+'.bam" -out="'+FN+'.out" -log="'+FN+'.log"'+' -bed_trackname="'+name4browser+'" -sql_grp="'+group+'" -bed_format='+bedformat+' -no-bed-file '
    PAR=PAR+' -sql_host=localhost -sql_dbname='+db
    if isRNA:	
	PAR=PAR+' -bed_type=2 -rna_seq="RNA" '
    else:
	if pair:
	    PAR=PAR+' -bed_type=2 '
	else:
	    PAR=PAR+' -bed_window='+str(fragment)+' -bed_siteshift='+str(fragment/2)
	    PAR=PAR+' -bed_type=3 '
	    
    PAR=PAR+' -bed_normalize '
    
    RET=''
    try:
	RET=s.check_output(PAR,shell=True)
	success[1]=' Upload to genome browser success'
	return success
    except Exception,e:
	error[1]=str(e)
	return error


def run_fence(infile):
    PAR=''
    if ";" in infile:
	FN=infile.split(";")
	if len(file_exist('.',FN[0],'fence')) == 1:
	    success[1]='Fence file exists'
	    return success
	PAR='fence.py --in="'+infile+'" >'+FN[0]+'.fence'
    else:	
	FL=file_exist('.',infile,'fence')
	if len(FL) == 1:
	    success[1]='Fence file exists'
	    return success
	PAR='fence.py --in=./'+infile+'.fastq >'+infile+'.fence'

    RET=''
    try:
	RET=s.Popen(PAR,shell=True)
	success[1]=' Fence backgrounded'
	return success
    except Exception,e:
	error[1]=str(e)
	return error

def run_atp(lid):

    PAR='averagedensity -avd_lid='+str(lid)+' -log="./AverageTagDensity.log" -sql_host="localhost" -sql_dbname="ems" '
    PAR=PAR+' -sam_twicechr="chrX chrY" -sam_ignorechr="chrM" -avd_window=5000 -avd_smooth=50 -plot_ext="svg" -gnuplot="/usr/local/bin/gnuplot" '

    RET=''
    try:
	RET=s.check_output(PAR,shell=True)
	success[1]=' ATP finished '
	return success
    except Exception,e:
	error[1]=str(e)+RET
	return error
