// $(function()
// {
//     $('[data-toggle="tooltip"]').tooltip()
// })
//
// $(document).ready(function(){
//     document.getElementById('toggle_btn_off').hidden=true
//
//     $("#toggle_btn_on").click(function(){
//         $("#sidenav").animate({"width": "0"}, 'fast').hide();
//         $("#main_div").animate({"margin-left": "0"}, 'slow');
//
//         $("#toggle_btn_on").hide();
//         document.getElementById('toggle_btn_on').hidden=true;
//
//         $("#toggle_btn_off").show();
//         document.getElementById('toggle_btn_off').hidden=false;
//     });
//
//     $("#toggle_btn_off").click(function(){
//         $("#sidenav").animate({"width": "260px"}, 'slow').show();
//         $("#main_div").animate({"margin-left": "260"}, 'fast');
//
//         $("#toggle_btn_off").hide();
//         document.getElementById('toggle_btn_off').hidden=true;
//
//         $("#toggle_btn_on").show();
//         document.getElementById('toggle_btn_on').hidden=false;
//     });
// });
//
// $(function()
// {
//     var Accordion = function(el, multiple)
//     {
//         this.el = el || {};
//         this.multiple = multiple || false;
//         // Variables privadas
//         var links = this.el.find('.link');
//         // Evento
//         links.on('click', {el: this.el, multiple: this.multiple}, this.dropdown)
//     }
//
//     Accordion.prototype.dropdown = function(e)
//     {
//         var $el = e.data.el;
//         $this = $(this);
//         $next = $this.next();
//         $next.slideToggle();
//         $this.parent().toggleClass('open');
//
//         if(!e.data.multiple)
//         {
//             $el.find('.submenu').not($next).slideUp().parent().removeClass('open');
//         }
//     }
//     var accordion = new Accordion($('#accordion'), false);
// });