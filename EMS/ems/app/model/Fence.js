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

Ext.define('EMS.model.Fence', {
               extend: 'Ext.data.Model',

               fields: [
                   {name: 'id', type: 'int'},
                   {name: 'A', type: 'int'},
                   {name: 'C', type: 'int'},
                   {name: 'T', type: 'int'},
                   {name: 'G', type: 'int'},
                   {name: 'N', type: 'int'},
                   {name: 'min', type: 'float'},
                   {name: 'max', type: 'float'},
                   {name: 'mean', type: 'float'},
                   {name: 'Q1', type: 'float'},
                   {name: 'med', type: 'float'},
                   {name: 'Q3', type: 'float'},
                   {name: 'IQR', type: 'float'},
                   {name: 'lW', type: 'float'},
                   {name: 'rW', type: 'float'}
               ]
           }
);
