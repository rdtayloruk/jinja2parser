$(function(){

    var cachedTemplate;

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
        var projectId = $('option:selected', this).attr('data-id');
        e.preventDefault();
        $('#versionSelect > option').remove();
        $('#templateSelect > option').remove();
        $('#varFileSelect > option').remove();
        $.ajax({
            url: '/projects/' + projectId + '/versions',
            type: 'GET', 
            success: function (data) {
                $("#versionSelect").html(data).trigger('change');
            },
            error: function (xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
         });
    });
    
    $('#versionSelect').on('change', function(e) {
        var versionId = $('option:selected', this).attr('data-id');
        e.preventDefault();
        $('#templateSelect > option').remove();
        $('#varFileSelect > option').remove();
        $.ajax({
            url: '/versions/' + versionId + '/templates',
            type: 'GET', 
            success: function (data) {
                $("#templateSelect").html(data).trigger('change');
            },
            error: function (xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
         });
    });
    
    $('#templateSelect').on('change', function(e) {
        var templateId = $('option:selected', this).attr('data-id');
        var templateUrl = $('option:selected', this).attr('data-file-url');
        e.preventDefault();
        $('#varFileSelect > option').remove();
        $.ajax({
            url: templateUrl,
            type: 'GET', 
            success: function (data) {
                tplEditor.setValue(data);
            },
            error: function (xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
        $.ajax({
            url: '/templates/' + templateId + '/varfiles',
            type: 'GET', 
            success: function (data) {
                $("#varFileSelect").html(data).trigger('change');
            },
            error: function (xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
          });
    });

    $('#varFileSelect').on('change', function(e) {
        var varFileUrl = $('option:selected', this).attr('data-file-url');
        e.preventDefault();
        $.ajax({
            url: varFileUrl,
            type: 'GET', 
            success: function (data) {
                varEditor.setValue(data);
            },
            error: function (xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    });

    $('#templateVarsClear').on('click', function(e) {
        varEditor.setValue('');
       /* $('#projectSelect :not(:first-child)').remove();
        $('#projectVersionSelect :not(:first-child)').remove();
        $('#templateSelect :not(:first-child)').remove();
        $('#varFileSelect :not(:first-child)').remove();*/
    });
    
    $('#templateVarsFullScreen').on('click', function(e) {
        varEditor.setOption("fullScreen", !varEditor.getOption("fullScreen"));
    });
    
    $('#templateVarsUndo').on('click', function(e) {
        varEditor.execCommand('undo');
    });
    
    function destroyClickedElement(event) {
            document.body.removeChild(event.target);
        };
    
    $('#templateVarsSave').on('click', function(e) {
        // your CodeMirror textarea ID
        var textToWrite = varEditor.getValue()
        var textFileAsBlob = new Blob([textToWrite], {type:'text/plain'});
        var fileNameToSaveAs = "varfile.txt";
        
        var downloadLink = document.createElement("a");
        downloadLink.download = fileNameToSaveAs;
        
        // hidden link title name
        downloadLink.innerHTML = "LINKTITLE";
        
        window.URL = window.URL || window.webkitURL;
        
        downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
        
        downloadLink.onclick = destroyClickedElement;
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        
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
        cachedTemplate = tplEditor.getValue();
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
    
    $('#undo').on('click', function(e) {
        e.preventDefault();
        tplEditor.setValue(cachedTemplate);
    });
});