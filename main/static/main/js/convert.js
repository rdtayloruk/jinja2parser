$(function(){

    var repo; 

    var varEditor = CodeMirror.fromTextArea($('#templateVars').get(0),{
        mode:  "yaml",
        lineNumbers: true
      });
    
    var tplEditor = CodeMirror.fromTextArea($('#template').get(0),{
        mode:  "jinja2",
        lineNumbers: true
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

    $('#repoSelect').on('change', function(e) {
        e.preventDefault();
        $('#templateSelect :not(:first-child)').remove();
        $('#varsSelect :not(:first-child)').remove();
        console.log("get templates")
        $.ajax({
            url: '/repos/' + $(this).val() + '/templates',
            type: 'GET', 
            success: function (data) {
                console.log(data)
                repo = data
                $.each( repo.templates, function( i, val ) {
                    $('#templateSelect').append($('<option>', {
                        value: val.name,
                        text: val.name
                    }));
                });
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.status + ": " + xhr.responseText);
            }
          });
    });
    
    $('#templateSelect').on('change', function(e) {
        e.preventDefault();
        $('#varsSelect :not(:first-child)').remove();
        console.log("get template");
        $.ajax({
            url: '/repos/' + $('#repoSelect').val() + '/contents' + repo.templates_dir,
            type: 'GET', 
            data: { 
                name: $(this).val(),
            },
            success: function (data) {
                console.log(data)
                tplEditor.setValue(data);
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.status + ": " + xhr.responseText);
            }
          });
        console.log($(this).prop('selectedIndex'));
        //repo.templates[$(this).prop('selectedIndex'))].template_vars;
        /*$.each( , function( i, val ) {
            $('#varsSelect').append($('<option>', {
                value: val.name,
                text: val.name
            }));
        });*/
    });

    $('#clear').on('click', function(e) {
        tplEditor.setValue('');
        varEditor.setValue('')
        $('#repoSelect :not(:first-child)').remove();
        $('#repoBranchSelect :not(:first-child)').remove();
        $('#templateSelect :not(:first-child)').remove();
        $('#varsSelect :not(:first-child)').remove();
    });

    $('#copy').on('click', function(e) {
        e.preventDefault();
        tplEditor.focus();
        tplEditor.select();
	    document.execCommand('copy')
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
            success: function (data) {
                tplEditor.setValue(data)
            },
            error: function (xhr,errmsg,err) {
                alert(xhr.status + ": " + xhr.responseText);
            }
          });
    });
});