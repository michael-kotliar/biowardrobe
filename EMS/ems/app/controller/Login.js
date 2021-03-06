Ext.define('EMS.controller.Login', {
    extend: 'Ext.app.Controller',

    requires: [
        'EMS.util.MD5',
        'EMS.view.EMSViewport',
        'EMS.util.Util'
    ],

    views: [
        'Login',
        'News'
        //        'authentication.CapsLockTooltip'
    ],

    //    refs: [
    //        {
    //            ref: 'capslockTooltip',
    //            selector: 'capslocktooltip'
    //        }
    //    ],

    init: function (application) {
        this.control({
                         "login": {
                             show: this.onShow
                         },
                         "login form button#submit": {
                             click: this.onButtonClickSubmit
                         },
                         "login form button#cancel": {
                             click: this.onButtonClickCancel
                         },
                         "login form textfield": {
                             specialkey: this.onTextfielSpecialKey
                         },
                         "login form textfield[name=username]": {
                             keypress: this.onTextfielKeyPress
                         },
                         "login form textfield[name=password]": {
                             keypress: this.onTextfielKeyPress
                         },
                         "viewport button#logout": {
                             click: this.onButtonClickLogout
                         }
                     });

        Ext.apply(Ext.form.field.VTypes, {
            customPass: function(val, field) {
                return /^((?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,50})/.test(val);
            },
            customPassText: 'Not a valid password.  Length must be at least 8 characters and maximum of 20 Password must contain one digit, one letter lowercase, one letter uppercase'
        });

    },
    onShow: function (window) {
        window.down('textfield[name=username]').focus(false, 200, function () {
                        //console.log('focus');
        });
    },

    onButtonClickSubmit: function (button, e, options) {
        var formPanel = button.up('form'),
                login = button.up('login'),
                user = formPanel.down('textfield[name=username]').getValue(),
                pass = formPanel.down('textfield[name=password]').getValue();
        var me=this;

        if (formPanel.getForm().isValid()) {

            Ext.get(login.getEl()).mask("Authenticating... Please wait...", 'loading');

            Ext.Ajax.request
            ({
                 url: 'authenticate.php',
                 jsonData: Ext.encode({
                                          "username": user,
                                          "password": pass //EMS.util.MD5.encode(pass);
                                      }),
                 method: 'POST',
                 success: function (conn, response, options, eOpts) {
                     Ext.get(login.getEl()).unmask();
                     var result = EMS.util.Util.decodeJSON(conn.responseText);
                     if (result.success) {
                         login.close();
                         try {
                             Ext.ComponentQuery.query('news')[0].close();
                         } catch(e) {
                             console.log(e);
                         }
                         Ext.create('EMS.view.EMSViewport');
                     } else {
                         EMS.util.Util.showErrorMsg(result.message);
                     }
                 },
                 failure: function (conn, response, options, eOpts) {
                     Ext.get(login.getEl()).unmask();
                     EMS.util.Util.showErrorMsg(EMS.util.Util.decodeJSON(conn.responseText).message);
                 }
             });
        }
    },

    onButtonClickCancel: function (button, e, options) {
        button.up('form').getForm().reset();
        this.onShow(button.up('login'));
    },

    onTextfielSpecialKey: function (field, e, options) {
        if (e.getKey() == e.ENTER) {
            var submitBtn = field.up('form').down('button#submit');
            submitBtn.fireEvent('click', submitBtn, e, options);
        }
    },

    onTextfielKeyPress: function (field, e, options) {
        //        var charCode = e.getCharCode();
        //
        //        if ((e.shiftKey && charCode >= 97 && charCode <= 122) ||
        //            (!e.shiftKey && charCode >= 65 && charCode <= 90)) {
        //
        //            if (this.getCapslockTooltip() === undefined) {
        //                Ext.widget('capslocktooltip');
        //            }
        //
        //            this.getCapslockTooltip().show();
        //
        //        } else {
        //
        //            if (this.getCapslockTooltip() !== undefined) {
        //                this.getCapslockTooltip().hide();
        //            }
        //        }
    },

    onButtonClickLogout: function (button, e, options) {
        Ext.Ajax.request({
                             url: 'logout.php',
                             success: function (conn, response, options, eOpts) {
                                 var result = EMS.util.Util.decodeJSON(conn.responseText);

                                 if (result.success) {
                                     button.up('viewport').destroy();
                                     window.location.reload();
                                 } else {
                                     EMS.util.Util.showErrorMsg(result.message);
                                 }
                             },
                             failure: function (conn, response, options, eOpts) {
                                 EMS.util.Util.showErrorMsg(EMS.util.Util.decodeJSON(conn.responseText).message);
                             }
                         });
    }
});