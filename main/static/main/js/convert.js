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
    
    // Toolbars
    
    function copyToClipboard(textToCopy) {
        var $temp = $("<textarea>");
        $("body").append($temp);
        $temp.val(textToCopy).select();
        document.execCommand("copy");
        $temp.remove();
    }
    
    function destroyClickedElement(event) {
        document.body.removeChild(event.target);
    };
        
    function saveFile(textToWrite) {
        var textFileAsBlob = new Blob([textToWrite], {type:'text/plain'});
        
        var downloadLink = document.createElement("a");
        downloadLink.download = "myfile.txt";
        
        downloadLink.innerHTML = "LINKTITLE";
        
        window.URL = window.URL || window.webkitURL;
        
        downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
        
        downloadLink.onclick = destroyClickedElement;
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
    };
    
    $('#templateVarsCopy').on('click', function(e) {
        var textToCopy = varEditor.getValue();
        copyToClipboard(textToCopy);
    });

    $('#templateVarsClear').on('click', function(e) {
        varEditor.setValue('');
    });
    
    $('#templateVarsFullScreen').on('click', function(e) {
        varEditor.setOption("fullScreen", !varEditor.getOption("fullScreen"));
    });
    
    $('#templateVarsUndo').on('click', function(e) {
        varEditor.execCommand('undo');
    });
    
    $('#templateVarsSave').on('click', function(e) {
        var textToWrite = varEditor.getValue()
        saveFile(textToWrite)
    });
    
    $('#templateCopy').on('click', function(e) {
        var textToCopy = tplEditor.getValue();
        copyToClipboard(textToCopy);
    });

    $('#templateClear').on('click', function(e) {
        tplEditor.setValue('');
    });
    
    $('#templateFullScreen').on('click', function(e) {
        tplEditor.setOption("fullScreen", !tplEditor.getOption("fullScreen"));
    });
    
    $('#templateUndo').on('click', function(e) {
        tplEditor.execCommand('undo');
    });
    
    $('#templateSave').on('click', function(e) {
        var textToWrite = tplEditor.getValue()
        saveFile(textToWrite)
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