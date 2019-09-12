$(function(){
    var varEditor = CodeMirror.fromTextArea($('#templateVars').get(0),{
        mode:  "yaml",
        lineNumbers: true
      });
    
    var tplEditor = CodeMirror.fromTextArea($('#template').get(0),{
        mode:  "jinja2",
        lineNumbers: true
      });
    
    $('#clear').click(function() {
        $('#template').val('');
        $('#templateVars').val('');
    });

    $("#convertForm").on('submit', function(e) { 
        e.preventDefault();
        console.log("convert template called")
        console.log($(this).serialize()),
        $.ajax({
            url: '/convert',
            type: 'POST', 
            data: $(this).serialize(),
            success: function (data) {
                $('#template').val(data)
            },
            error: function (xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
                console.log(errmsg);
            }
          });
    });
});