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

Ext.define('EMS.view.toolbar.EMSMenu', {
    extend: 'Ext.toolbar.Toolbar',
    alias: 'widget.EMSMenu',
    style: 'border-bottom: 1px solid #4c72a4;',
    items: [
        {
            text: 'Data & Analysis',
            tooltip: '',
            menu: [
                { text: 'Experiments', action: 'LabData', tooltip: 'List of experiments', iconCls: 'form-blue-edit' },
                { text: 'Analyzes', action: 'ProjectDesigner2', tooltip: 'Project designer', iconCls: 'analysis' },
                { text: 'Folders', action: 'ExperimentGroups', tooltip: 'Experiment groupping', iconCls: 'magazine-folder' }
            ],
            iconCls: 'form-blue'
        } ,
        {
            text: 'Catalogs',
            tooltip: '',
            menu: [
                { text: 'Antibodies', action: 'Antibodies', tooltip: 'List of antibodies', iconCls: 'battery-green'},
                { text: 'Crosslink type', action: 'CrossType', tooltip: 'List of crosslink types', iconCls: 'atom' },
                { text: 'Fragmentation type', action: 'FragmentType', tooltip: 'List of fragmentation types', iconCls: 'army-knife' }
                //{ text: 'Experiment type', action: 'ExpType', tooltip: 'List of experiment types', iconCls: 'bottle-pills' },
                //{ text: 'Spikeins', action: 'Spikeins', tooltip: 'List of spikeins controls', iconCls: 'surveillance-camera' }
            ],
            iconCls: 'folder-document'
        },
        {
            text: 'Tools',
            tooltip: '',
            menu: [
                { text: 'Sequence cutter', action: 'SeqCut', tooltip: 'Tool to cutting sequence into pieces and align them to the genome', iconCls: 'cut' },
            ],
            iconCls: 'wrench'
        },
        {
            text: 'Notes for supplemental',
            tooltip: '',
            menu: [
                { text: 'Notes', action: 'SuppInfo', tooltip: 'Notes about pipelines for supplemental material', iconCls: 'notebook-edit' }
            ],
            iconCls: 'notebook-edit'
        },
        '->',
        {
            text: 'Help',
            tooltip: '',
            menu: [
                { text: 'Help', action: 'Help', tooltip: 'Wardrobe Help', iconCls: 'help' },
                { text: 'About', action: 'About', tooltip: 'About', iconCls: 'about' }
            ],
            iconCls: 'question_and_answer'
        }
    ]
})
;
