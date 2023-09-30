
(function($){
    $.fn.multiEmails = function(options) {
        var settings = $.extend({
            color: "#343a40",
            textColor: "#000000",
            fontAwesome: false,
        }, options );

            var keynum;
            var emailList = [];
            var hiddenField = $(this);
            const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

            $(this)
            .after(
                '<input type="text" class="'+hiddenField.attr("class")+'" id="email">'
                ).hide()/*.before(
                    '<span class="email-format">Emails be must sepereted by a comma character (,)</span>'
                    )*/;
    
            function uniqueEmails(emails) {
                let uniqueEmails = [];
                $.each(emailList, function(i, el){
                    if($.inArray(el, uniqueEmails) === -1) uniqueEmails.push(el);
                });
    
                return uniqueEmails;
            }
            
            $(document).on('keyup', '#email', function(e) {
                $('.email-error').remove();
                if(window.event){ // IE
                    keynum = e.keyCode;
                }
                else if(e.which){ // Netscape/Firefox/Opera
                    keynum = e.which;
                }
                if (keynum == 188){
                    
                    let email = $('#email').val().replace(',','');
                    if (re.test(String(email).toLowerCase())){
                        emailList.push(email);
                        let displayList = '';
                        
                        uniqueEmails(emailList).forEach((value, ind) => {
                            displayList += "<li style='background-color:"+hexToRgbA(settings.color)+";border-left: 3px solid"+settings.color+"'>"+value+"<span class='float-right remove' data-index="+ind+">"+((settings.fontAwesome === true)?'<i class=\"fas fa-times\"></i>':'X')+"</span></li>"
                        } )
                        let buildEmailList = '<div id="show-emails"><ul style="color:'+settings.textColor+'">'+displayList+'</ul></div>'
                        if($("#show-emails").length){
                            $("#show-emails").replaceWith(buildEmailList);
                        }else{
                            $('#email').parent().after(buildEmailList);
                        }
                        hiddenField.val(JSON.stringify(uniqueEmails(emailList)));
                        $('#email').val('');
                    }else{
                        let errrMessage = "<div class='email-error'>Please enter a valid email address</div>";
                        if($("#show-emails").length){
                            $("#show-emails").after(errrMessage);
                        }else{
                            $('#email').parent().after(errrMessage);
                            console.log($('#email').parent());
                        }
                    }
                }
            })

            $(document).on('click', ".remove", function () {
                let index = $(this).data("index");
                emailList.splice(index, 1);
                let displayList = '';
                uniqueEmails(emailList).forEach((value, ind) => {
                    displayList += "<li style='background-color:"+hexToRgbA(settings.color)+";border-left: 3px solid"+settings.color+"'>"+value+"<span class='float-right remove' data-index="+ind+">"+((settings.fontAwesome === true)?'<i class=\"fas fa-times\"></i>':'X')+"</span></li>"
                } )
                hiddenField.val(uniqueEmails(emailList));
                $("#show-emails ul").html(displayList);
            })

            function hexToRgbA(hex){
                var c;
                if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
                    c= hex.substring(1).split('');
                    if(c.length== 3){
                        c= [c[0], c[0], c[1], c[1], c[2], c[2]];
                    }
                    c= '0x'+c.join('');
                    return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+',0.08)';
                }
                throw new Error('Bad Hex');
            }
     
    };
}(jQuery))