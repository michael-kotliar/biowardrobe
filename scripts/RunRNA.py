#! /usr/bin/env python
##
##
## Selecting data from MySQL database with respect to status downloading files from website
##
##

import os
import sys
import Arguments
import DefFunctions as d
import re
import random
import MySQLdb 
import glob
import subprocess as s # import call
import time

BOWTIE_INDEXES="/data/DATA/indexes"
ANNOTATION_BASE=BOWTIE_INDEXES+"gtf"
BASE_DIR="/data/DATA/FASTQ-DATA"

arguments = Arguments.Arguments(sys.argv)
arguments.checkArguments(2)

pidfile = "/tmp/runRNA"+str(arguments.opt.id)+".pid"

d.check_running(pidfile)

error=list()
error.append('Error')
error.append('')
warning=list()
warning.append('Warning')
warning.append('')
success=list()
success.append('Success')
success.append('')




def file_exist(basedir,fname,extension):
    LIST=glob.glob(basedir+'/'+fname+'.'+extension)
    return LIST

def make_fname(fname):
    outfname=os.path.basename(fname)
    outfname=re.sub('[^a-zA-Z0-9\.]','_',outfname)
    outfname=re.sub('\.'+extension+'','',outfname)
    return outfname

def run_tophat(infile,params):

    FL=file_exist('.',infile,'bam')
    
    if len(FL) == 1:
	success[1]='Bam file exist'
	return success

    outdir=infile+'_tophat'
    PAR='tophat2 -o '+outdir+' '+params+' '+infile+'.fastq >/dev/null 2>&1'
    RET=''
    #print PAR
    try:
	RET=s.check_output(PAR,shell=True)
	if len(file_exist('./'+outdir,'accepted_hits','bam')) != 1:
	    error[1]='accepted_hits.bam does not exist'
	    return error
	os.rename('./'+outdir+'/accepted_hits.bam','./'+infile+'.bam')
	success[1]=' Tophat finished'
	return success
    except Exception,e:
    #s.CalledProcessError,OSError,
	error[1]=str(e)
	return error

def run_fence(infile):

    FL=file_exist('.',infile,'fence')
    
    if len(FL) == 1:
	success[1]='Fence file exist'
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

def run_ribosomal(infile,db):

    suffix=''
    if 'hg' in db:
	suffix='human'
    if 'mm' in db:
	suffix='mouse'
	
    FL=file_exist('.',infile,'ribo')
    
    if len(FL) == 1:
	success[1]='Ribosomal file exist'
	return success

    PAR='bowtie -q -v 2 -m 1 --best --strata -p 24 -S '+BOWTIE_INDEXES+'/ribo_'+suffix+' '+infile+'.fastq >/dev/null 2>./'+infile+'.ribo'
    RET=''
    try:
	RET=s.Popen(PAR,shell=True)
	success[1]=' Ribosomal backgrounded'
	success.append(RET)
	return success
    except Exception,e:
	error[1]=str(e)
	return error

def run_bedgraph(infile,group,name4browser,bedformat,db):

    FL=file_exist('.',infile,'log')
    
    if len(FL) == 1:
	success[1]=' Bedgraph uploaded'
	return success
	
    PAR='bam2bedgraph -sql_table="'+infile+'" -in="'+infile+'.bam" -out="'+infile+'.out" -log="'+infile+'.log"' 
    PAR=PAR+' -bed_trackname="'+name4browser+'" -sql_grp="'+group+'" -bed_window=20 -bed_format='+bedformat+' -no-bed-file -sql_dbname='+db
    RET=''
    try:
	RET=s.check_output(PAR,shell=True)
	success[1]=' Upload to genome browser success'
	return success
    except Exception,e:
	error[1]=str(e)
	return error

def get_stat(infile):

    FL=file_exist('.',infile,'log')
    lines = 0
    
    if len(FL) == 1:
	for line in open(infile+'.fastq'):
             lines += 1
	TOTAL=lines/4
	ALIGNED=0
	RIBO=0
	for line in open(infile+'.log'):
	    if 'Aligned' in line:
		ALIGNED=int(line.split('Aligned:')[1])
		break
	for line in open(infile+'.ribo'):
	    if 'alignment' in line:
		RIBO=line.split('alignment:')[1]
		RIBO=int(RIBO.split()[0])
		break
	fp = open('./'+infile+'.stat', 'w+')
	fp.write(str((TOTAL,ALIGNED,RIBO)))
	fp.close()
	return (TOTAL,ALIGNED,RIBO)
    else:
	error[1]='Cant read stat file'
	return error


    #if [ $? -eq 0 ]; then
    #LC=`wc -l ${NA}|awk '{print $1/4}'`
    #grep 'Aligned:' ${NA}.log |awk -v tot=${LC} -F'Aligned: ' '{printf("Total: %d\nAligned: %d\nPercent: %f\n",tot,$2,$2*100/tot);}' >${NA}.stat

######################################################
try:
    conn = MySQLdb.connect (host = arguments.readString("SQLE/HOST"),user = arguments.readString("SQLE/USER"), passwd=arguments.readPass("SQLE/PASS"), db=arguments.readString("SQLE/DB"))
    conn.set_character_set('utf8')
    cursor = conn.cursor ()
except Exception, e: 
    Error_str=str(e)
    error_msg("Error database connection"+Error_str)


cursor.execute("update labdata set libstatustxt='ready for process',libstatus=10 where libstatus=2 and experimenttype_id in (select id from experimenttype where etype like 'RNA%')")




while True:
    row=[]
    cursor.execute ("select e.etype,l.name4browser,g.db,g.findex,g.annotation,filename,w.worker,w.worker,l.id "
    " from labdata l,experimenttype e,genome g,worker w "
    " where e.id=experimenttype_id and g.id=genome_id and w.id=worker_id and e.etype like 'RNA%' and libstatus in (10,1010) order by dateadd limit 1")
    row = cursor.fetchone()
    if not row:
	break

    PAIR=('pair' in row[0])
    DUTP=('dUTP' in row[0])
    FNAME=''
    if not PAIR:
	FNAME=row[5]
    DB=row[2]
    FINDEX=row[3]
    ANNOTATION=row[4]
    GROUP=row[7]
    LID=row[8]
    NAME=row[1]
    SUBDIR='/RNA'
    BEDFORMAT='4'
    ADD_TOPHAT=" -T "
    #ADD_TOPHAT=''
    if DUTP:
        ADD_TOPHAT=" --library-type fr-firststrand " #DUTP
	BEDFORMAT='8'
        

    ADD_TOPHAT=" -g 1 --no-novel-juncs "+ADD_TOPHAT

    basedir=BASE_DIR+'/'+row[6].upper()+SUBDIR    


    ANN_BASE=BOWTIE_INDEXES+'/gtf/'+ANNOTATION
    TRANSCRIPTOME=' --transcriptome-index '+ANN_BASE+' '
    GFT_FILE='-G '+ANN_BASE+'.gtf '
    
    TOPHAT_PARAM=' --num-threads 24 '+GFT_FILE+ADD_TOPHAT+TRANSCRIPTOME+BOWTIE_INDEXES+'/'+FINDEX+' '


    os.chdir(basedir)
    FL=file_exist('.',FNAME,'fastq')

    cursor.execute("update labdata set libstatustxt='processing',libstatus=11 where id=%s",LID)
    conn.commit()

    if not PAIR and len(FL) == 1:
	run_fence(FNAME)
	a=run_ribosomal(FNAME,DB)
	if 'Error' in a[0]:
	    cursor.execute("update labdata set libstatustxt=%s,libstatus=2010 where id=%s",(a[0]+": "+a[1],LID))
	    conn.commit()
	    continue
	PID=0
	if len(a)==3:
	    PID=a[2].pid
		
	a=run_tophat(FNAME,TOPHAT_PARAM)
	if 'Error' in a[0]:
	    cursor.execute("update labdata set libstatustxt=%s,libstatus=2010 where id=%s",(a[0]+": "+a[1],LID))
	    conn.commit()
	    continue
	if 'Warning' in a[0]:
	    cursor.execute("update labdata set libstatustxt=%s,libstatus=1010 where id=%s",(a[0]+": "+a[1],LID))
	    conn.commit()
	    continue

	cursor.execute("update labdata set libstatustxt=%s,libstatus=11 where id=%s",(a[0]+": "+a[1],LID))
	conn.commit()

        a=run_bedgraph(FNAME,GROUP,NAME,BEDFORMAT,DB)
	if 'Error' in a[0]:
	    cursor.execute("update labdata set libstatustxt=%s,libstatus=2010 where id=%s",(a[0]+": "+a[1],LID))
	    conn.commit()
	    continue

	cursor.execute("update labdata set libstatustxt=%s,libstatus=11 where id=%s",(a[0]+": "+a[1],LID))
	conn.commit()
	try:	
	    os.waitpid(PID,0)
	    time.sleep(5)
	except:
	    pass
	a=get_stat(FNAME)
        cursor.execute("update labdata set libstatustxt='Complete',libstatus=12,tagstotal=%s,tagsmapped=%s,tagsribo=%s where id=%s",(a[0],a[1],a[2],LID))
	conn.commit()

    #cursor.execute("update labdata set libstatustxt='processing',libstatus=10 where id=%s",LID)
    #conn.commit()    
    #('RNA-Seq dUTP', 'Activated_rested CD4', 'hg19', 'hg19c', 'hg19_refsec_genes_control', 'run0140_lane5_read1_index10_ABYR14', 'yrina')
    
    
    