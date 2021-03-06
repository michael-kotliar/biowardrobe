/****************************************************************************
 **
 ** Copyright (C) 2011-2014 Andrey Kartashov .
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


Ext.define('EMS.view.Experiment.Experiment.RPKM', {
    extend: 'Ext.Panel',

    frame: true,
    border: false,
    plain: true,
    layout: 'fit',
    title: 'RPKM list',
    iconCls: 'table2',
    alias: 'widget.experimentrpkm',

    items: [
        {
            viewConfig: {
                stripeRows: true,
                enableTextSelection: true
            },
            xtype: 'grid',
            hight: 60,
            frame: false,
            border: false,
            plain: true,
            columnLines: true,
            store: 'RPKM',
            remoteSort: true,
            features: [
                {
                    ftype: 'filters',
                    encode: true,
                    local: false
                }
            ],
            columns: [
                {   header: "RefseqId", sortable: true, filterable: true, width: 100, dataIndex: 'refseq_id', hidden: false },
                {   header: "GeneId", sortable: true, filterable: true, width: 100, dataIndex: 'gene_id' },
                {   header: 'chrom', sortable: true, filterable: true, width: 60, dataIndex: 'chrom'  },
                {   header: 'txStart', sortable: true, width: 80, dataIndex: 'txStart', align: 'right' },
                {   header: 'txEnd', sortable: true, width: 85, dataIndex: 'txEnd', align: 'right'   },
                {   header: 'strand', sortable: true, filterable: true, width: 40, dataIndex: 'strand', align: 'center'  },
                {   header: 'TOT_R', sortable: true, filterable: true, width: 85, dataIndex: 'TOT_R_0', align: 'right', hidden: true },
                {   header: 'RPKM', sortable: true, filterable: true, width: 85, dataIndex: 'RPKM_0', align: 'right' }
            ]
        }
    ],

    tbar: [
        {
            xtype: 'pagingtoolbar',
            store: 'RPKM',
            margin: '5 10 5 5',
            displayInfo: true
        },
        '-' ,
        {
            xtype: 'combobox',
            itemId: 'rpkm-group-filter',
            editable: false,
            queryMode: 'local',
            displayField: 'name',
            valueField: 'prefix',
            value: "_genes",
            width: 110,
            store: Ext.create('Ext.data.Store', {
                //autoDestroy: true,
                fields: ['prefix', 'name'],
                data: [
                    {"prefix": "_isoforms", "name": "Isoforms"},
                    {"prefix": "_genes", "name": "Genes"},
                    {"prefix": "_common_tss", "name": "Common Tss"}
                ]
            }),
            margin: "5 5 5 10"
        } ,
        {
            xtype: 'fieldcontainer',
            layout: 'hbox',

            items: [
                {
                    xtype: 'button',
                    text: 'jump',
                    itemId: 'browser-jump',
                    width: 80,
                    submitValue: false,
                    iconCls: 'genome-browser',
                    iconAlign: 'left',
                    margin: '5 10 5 10'
                } ,
                {
                    xtype: 'button',
                    //store: EMS.store.RPKM,
                    text: 'save',
                    href: '',
                    itemId: 'rpkm-save',
                    width: 80,
                    submitValue: false,
                    iconCls: 'disk',
                    margin: '5 10 5 10'
                }
            ]
        }
    ]//tbar
});


