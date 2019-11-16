$(function(){

    var projectName;
    var templateData;
    var templateName;
    var templateVarsName;
    var templateVarFiles;

    var varEditor = CodeMirror.fromTextArea($('#templateVars').get(0),{
        mode:  "yaml",
        lineNumbers: true,
        theme: "ambiance",
        extraKeys: {
            "F11": function(cm) {
                cm.setOption("fullScreen", !cm.getOption("fullScreen"));
            },
            "Esc": function(cm) {
                if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
            }
        }
     });
    
    var tplEditor = CodeMirror.fromTextArea($('#template').get(0),{
        mode:  "jinja2",
        lineNumbers: true,
        theme: "ambiance",
        extraKeys: {
            "F11": function(cm) {
                cm.setOption("fullScreen", !cm.getOption("fullScreen"));
            },
            "Esc": function(cm) {
                if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
            }
        }
      });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    $('#projectSelect').on('change', function(e) {
        e.preventDefault();
        $('#versionSelect :not(:first-child)').remove();
        $('#templateSelect :not(:first-child)').remove();
        $('#varFileSelect :not(:first-child)').remove();
        console.log("get templates");
        var project_path = $(this).val();
        $.ajax({
            url: '/' + project_path + '/versions',
            type: 'GET', 
            success: function (data) {
                console.log(data);
                $("#versionSelect").html(data);
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.status + ": " + xhr.responseText);
            }
         });
    });
    
    $('#templateSelect').on('change', function(e) {
        templateName = $(this).val()
        e.preventDefault();
        $('#varFileSelect :not(:first-child)').remove();
        console.log("get template");
        $.ajax({
            url: '/projects/' + projectName + '/contents' + projectData.templates_dir,
            type: 'GET', 
            data: { 
                name: templateName,
            },
            success: function (data) {
                console.log(data)
                tplEditor.setValue(data);
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.status + ": " + xhr.responseText);
            }
          });
        console.log(projectName, templateName);
        templateVarFiles = projectData.templates.find(function(tpl){
            return tpl.name === templateName
        }).var_files;
        console.log(templateVarFiles)
        $.each(templateVarFiles , function( i, val ) {
            $('#varFileSelect').append($('<option>', {
                value: val,
                text: val
            }));
        });
    });

    $('#varFileSelect').on('change', function(e) {
        templateVarsName = $(this).val()
        e.preventDefault();
        $('#varFileSelect :not(:first-child)').remove();
        console.log("get template");
        $.ajax({
            url: '/projects/' + projectName + '/contents' + projectData.vars_dir,
            type: 'GET', 
            data: { 
                name: templateVarsName,
            },
            success: function (data) {
                console.log(data)
                varEditor.setValue(data);
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.status + ": " + xhr.responseText);
            }
        });
    });

    $('#clear').on('click', function(e) {
        tplEditor.setValue('');
        varEditor.setValue('')
       /* $('#projectSelect :not(:first-child)').remove();
        $('#projectVersionSelect :not(:first-child)').remove();
        $('#templateSelect :not(:first-child)').remove();
        $('#varFileSelect :not(:first-child)').remove();*/
    });

    $('#copy').on('click', function(e) {
        console.log("copy...")
        e.preventDefault();
        tplEditor.save();
        console.log($('#template').text());
        $('#template').select();
	    document.execCommand('copy');
        // copy to clipboard
    });

    $('#save').on('click', function(e) {
        e.preventDefault();
        // save template as file
    });

    $('#convert').on('click', function(e) { 
        e.preventDefault();
        console.log("convert triggered")
        $.ajax({
            url: '/convert',
            type: 'POST', 
            data: { 
                template: tplEditor.getValue(),
                templateVars: varEditor.getValue(),
                trim_blocks: $('#trimBlocks').prop('checked'),
                lstrip_blocks: $('#lstripBlocks').prop('checked'),
                strict_undefined: $('#strictUndefined').prop('checked')
            },
            //dataType: 'json',
            success: function (data) {
                console.log(data)
                tplEditor.setValue(data)
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.responseText);
            }
          });
    });
});