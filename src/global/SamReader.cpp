/****************************************************************************
**
** Copyright (C) 2011 Andrey Kartashov .
** All rights reserved.
** Contact: Andrey Kartashov (porter@porter.st)
**
** This file is part of the global module of the genome-tools.
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
//GLOBALCALL{
// Arguments::addArg("sam_siteshift","sam_siteshift","SAM/SITESHIFT",QVariant::Int,"default siteshift",0);
// Arguments::addArg("sam_twicechr","sam_twicechr","SAM/TWICECHR",QVariant::String,"Which chromosome to double",QString(""));// chrX chrY
// Arguments::addArg("sam_ignorechr","sam_ignorechr","SAM/IGNORECHR",QVariant::String,"Which chromosome to ignore",QString(""));//chrM
// return 0;
//}();

/****************************************************************************************************************************
    desctructor, close bam files
****************************************************************************************************************************/
template <class Storage>
SamReader<Storage>::~SamReader()
{
    reader.Close();
}


/****************************************************************************************************************************

****************************************************************************************************************************/
template <class Storage>
SamReader<Storage>::SamReader( Storage* o, QObject *):
    output(o)
{
    inFile=gArgs().getArgs("in").toString();
    initialize();
}

/****************************************************************************************************************************

****************************************************************************************************************************/
template <class Storage>
SamReader<Storage>::SamReader(QString fn, Storage* o, QObject *):
    inFile(fn),
    output(o)
{
    initialize();
}

/****************************************************************************************************************************

****************************************************************************************************************************/
template <class Storage>
void SamReader<Storage>::initialize()
{

    QString twicechr=gArgs().getArgs("sam_twicechr").toString();
    QString ignorechr=gArgs().getArgs("sam_ignorechr").toString();

    vector<string> fn;
    fn.push_back(inFile.toStdString());
    if ( !reader.Open(fn) ) {
        qDebug() << "Could not open input BAM files.";
        throw "Could not open input BAM files";
    }

    header = reader.GetHeader();
    references = reader.GetReferenceData();

    for(int RefID=0;RefID < (int)references.size();RefID++) {

        if(ignorechr.contains(references[RefID].RefName.c_str())) {
            i_tids<<RefID;
            continue;
        }
        if(twicechr.contains(references[RefID].RefName.c_str())) {
            tids<<RefID;
        }
        //qDebug() <<inFile<< " refname:" << references[RefID].RefName.c_str()<<"reflen:"<<references[RefID].RefLength;
        output->setLength(QChar('+'),references[RefID].RefName.c_str(),references[RefID].RefLength);
        output->setLength(QChar('-'),references[RefID].RefName.c_str(),references[RefID].RefLength);
        output->tot_len+=references[RefID].RefLength;
    }

    qDebug()<<inFile<<": Total genome length:"<<output->tot_len;// -hr.name, hr.len

}



/****************************************************************************************************************************

****************************************************************************************************************************/
template <class Storage>
void SamReader<Storage>::Load(void)
{
    int siteshift=gArgs().getArgs("sam_siteshift").toInt();
    int ignored=0,mapped=gArgs().getArgs("sam_mapped_limit").toInt();
    int u=0, l=0;
    QStringList border=gArgs().split("sam_frag_filtr",'-');
    if(border.size()==2) {
        l=border[0].toInt();
        u=border[1].toInt();
    }


    BamAlignment al;
    while ( reader.GetNextAlignment(al) ) {
        output->total++;
        if(i_tids.contains(al.RefID)) { ignored++; continue; }

        //        if(c-->0)
        //        {
        //            qDebug()<<"Name:"<<al.Name.c_str()<< " Maped:"<<al.IsMapped() <<" fM:"<<al.IsFirstMate()<<
        //                   " Mate"<<al.IsMateMapped()<<" strand:"<<(al.IsReverseStrand()?"-":"+")<<" flg:"<<al.AlignmentFlag
        //                   <<" mrf:"<<al.MateRefID;
        //        }
        if(al.IsMapped()) {
            int num=1;
            if(tids.contains(al.RefID)) { num=2; output->total++;}

            if(mapped==1) { break;}
            if(mapped>1)  mapped--;


//                        qDebug()<<"Name:"<<al.Name.c_str()<<"Seq:"<<al.QueryBases.c_str();
//                        qDebug()<<"+++++"<<" Position:["<<references[al.RefID].RefName.c_str()<<":"<<al.Position+1<<"-"<<al.GetEndPosition()<<"] "
//                               <<"Len:"<<al.Length<<" InsSize:"<<abs(al.InsertSize)<<" strand:"<<(al.IsReverseStrand()?"-":"+");


            QChar strnd=QChar('+');
            int shift=siteshift;
            int position_b = al.Position+1;
            int position_e = al.GetEndPosition();

            if(al.IsReverseStrand()) {// - strand
                strnd= QChar('-');
                shift= -siteshift;
            }

            if(al.IsMateMapped() && al.IsFirstMate()) { //pair-end reads
                int length=abs(al.InsertSize);
                if( (u|l)>0 && !(l<=length && length<=u) ) { //fragment length filter, for pair ends
                    output->notAligned+=num;
                    continue;
                }
                if(al.IsReverseStrand()) {
                    position_b= position_e-length+1;
                } else {
                    position_e= position_b+length-1;
                }
            } else  if(al.IsMateMapped() && al.IsSecondMate()) {
                continue;
            }

            genome::read_representation rp;

            //QString _out;
            const vector<CigarOp>& cigarData = al.CigarData;
            if (! cigarData.empty() && cigarData.size()>1) {
                vector<CigarOp>::const_iterator cigarIter = cigarData.begin();
                for ( ; cigarIter != cigarData.end(); ++cigarIter ) {
                    if(QString(cigarIter->Type)=="M") {
                        rp.add(genome::interval_type::closed(position_b,position_b+cigarIter->Length-1));
                        position_b+=cigarIter->Length;
                    }
                    if(QString(cigarIter->Type)=="N") {
                        position_b+=cigarIter->Length;
                    }
                    //_out+=QString("[Len=%1,Type=%2]").arg(cigarIter->Length).arg(cigarIter->Type);
                }
            }
            else {
                rp.add(genome::interval_type::closed(position_b+shift,position_e+shift));
            }

            output->setGene(strnd,
                            references[al.RefID].RefName.c_str(),
                            rp,num);

            //                        for(genome::read_representation::iterator it=rp.begin();it!=rp.end();it++){
            //                            genome::read_representation::interval_type itv = bicl::key_value<genome::read_representation>(it);
            //                            qDebug()<<"["<<itv.lower()<<":"<<itv.upper()<<"]";
            //                        }

            //                        qDebug()<<"+++++"<<" Position:["<<references[al.RefID].RefName.c_str()<<":"<<position_b<<"-"<<position_e<<"] " <<
            //                                  " strand:"<<strnd <<" Cigar"<<_out<<"cigar size:"<<cigarData.size()<<"  shift:"<<shift;

        } else {
            output->notAligned++;
        }
    }

    qDebug()<<inFile<<": Total:"<<output->total;
    qDebug()<<inFile<<": Not aligned:"<<output->notAligned;
    qDebug()<<inFile<<": Aligned:"<<output->total-output->notAligned;
    qDebug()<<inFile<<": Ignored:"<<ignored;
    qDebug()<<inFile<<": Total aligned %:"<<((output->total-output->notAligned)*100/output->total);
}
