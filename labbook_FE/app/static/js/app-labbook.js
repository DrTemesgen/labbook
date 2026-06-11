/* javascript functions for labbook project */
var disconnect_page = "/disconnect" ;
var page_timeout    = 0 ;

function tempAlert(msg, id_elem)
{
let w_page  = $("#page").width() / 2 - 80 ; // -80 for better center

let pos_elem = $("#" +id_elem).position();
let x = pos_elem.left;
let y = pos_elem.top - 80; // -80 for raise up a bit

if ( y < 120 ) y = 120 ; // less than 100 it's non visible beacuse hide by menu

$(".toast").css({ top: y }) ;
$(".toast").css({ left: w_page + 'px' }) ;

$("#toast-msg").html(msg) ;

$(".toast").toast('show') ;
}

// Return formatted record number
function fmt_num_rec( num_rec, fmt, period )
{
let ret = num_rec ;

    if ( fmt == 1072 ) // short format
    {
        if ( period == 1070 ) // month period
        ret = Number( (num_rec.toString()).substr(6,4) ) ; // convert number to take off front zero
        else
        ret = Number( (num_rec.toString()).substr(4,6) ) ;
    }

return ret ; 
}

/* AlC DESACT 26/12/2023 */
// Return period for record number
/*
function per_num_rec( num_rec, fmt, period )
{
let ret = "" ;

    if ( period == 1070 && fmt == 1072 ) // month period and short format
    ret = (num_rec.toString()).substr(4,2) + "/" + (num_rec.toString()).substr(0,4) ;

return ret ;
}
*/
function per_num_rec( rec_date, lang )
{
let ret = "" ;

ret = moment(rec_date, "YYYY-MM-DD") ;
ret = ret.toDate();

    if ( lang == "US" ) 
    ret = moment(ret).format("MM/DD/YYYY") ;
    else
    ret = moment(ret).format("DD/MM/YYYY") ;

return ret ;
}

function status_rec( id_stat, with_det )
{
let res = '' ;

    if ( id_stat == 182 )
    res = '<span class="icon stat-A">A</span>' ;
    else if ( id_stat == 253 )
    res = '<span class="icon stat-A">I</span>' ;
    else if ( id_stat == 254 )
    res = '<span class="icon stat-T">T</span>' ;
    else if ( id_stat == 255 )
    res = '<span class="icon stat-T">I</span>' ;
    else if ( id_stat == 256 )
    res = '<span class="icon stat-B">B</span>' ;

return res ;
}

function status_res( id_stat )
{
let res = '' ;

    if ( id_stat == 250 )
    res = '<span class="icon stat-A">A</span>' ;
    else if ( id_stat == 251 )
    res = '<span class="icon stat-T">T</span>' ;
    else if ( id_stat == 252 )
    res = '<span class="icon stat-B">B</span>' ;

return res ;
}

function emer( flag_emer )
{
let res = '' ;

    if ( flag_emer == "O" || flag_emer == 4 )
    res = '<span class="emer">&nbsp;</span>' ;

return res ;
}

function init_timeOut( url_server, logout_time )
{
let disconnect_time = logout_time * 60000 ; // convert minutes to milliseconds
disconnect_page = url_server + disconnect_page ;
page_timeout = window.setTimeout( disconnect, disconnect_time ) ;
}

function reboot_timeOut( logout_time )
{
clearTimeout( page_timeout ) ;
let disconnect_time = logout_time * 60000 ; // convert minutes to milliseconds
page_timeout = window.setTimeout( disconnect, disconnect_time ) ;
}

function disconnect() 
{
location.href = disconnect_page ;
}

function calc( id_rec, ref_ana, id_res, num_var )
{
//console.log("####################### DEBUG-TRACE CALC ###################");
//console.log("DEBUG-TRACE ref_ana=" + ref_ana + " | id_res=" + id_res + " | num_var=" + num_var) ;

// start by evaluate this var
eval_value( id_rec, ref_ana, id_res ) ;

    // search formula for this var
    $(".formula-" + id_rec + "-" + ref_ana ).each( function(i, elem)
    {
    let id_tot  = $(this).attr("id").substr(8) ; 
    let f1      = $(this).val() ;

        // EVAL f1
        if ( f1.search("_"+num_var) >= 0 )
        {
        //console.log("DEBUG-TRACE calc num_var found in f1") ;

        // GET current value for all var in this formula
        // NOTE: if var num greater than 9 ???
        let l_var   = [];
        let k_var_p = 0;

        // Get var number for this formula
        let k = 0;
            while (k < f1.length)
            {
            const pos = f1.indexOf("_", k);

              // Stop when no more "_" is found
                if (pos === -1) { break; }

                const k_var = pos + 1;

                // Stop rotate
                if (k_var <= k_var_p) { break; }

                if (k_var < f1.length) {
                    l_var.push(f1.substr(k_var, 1));
                    k_var_p = k_var;

                    // Continue scanning after the extracted variable
                    k = k_var + 1;
                } else { break; }
            }

         //console.log("DEBUG-TRACE f1 l_var="+l_var) ;

         let l_value = [] ;

            // Get id_res for each var
            for ( let k = 0; k < l_var.length; k++ )
            {
            let val_tmp = "" ;

                $(".num_var-" + id_rec + "-" + ref_ana + "-" + l_var[k]).each( function(j, elem)
                {
                let id_res_var = $(this).attr("id") ;

                    // if no value we try to getting one
                    if ( val_tmp == null || val_tmp == "" )
                    {
                    val_tmp = $("#res_"+id_res_var).val() ;

                        if ( val_tmp != null && val_tmp != "" )
                        {
                        l_value.push( val_tmp ) ;
                        }
                    }

                } ) ;
            }
        
         //console.log("DEBUG-TRACE f1 l_value="+l_value) ;

            // Calculation
            if ( l_var.length == l_value.length )
            {
                for ( let k = 0; k < l_var.length; k++ )
                {
                f1 = f1.replace("$_"+l_var[k], l_value[k]) ;
                }

            //console.log("DEBUG-TRACE formule f1 avant eval : " + f1);
            let total = eval(f1) ;

            //console.log("DEBUG-TRACE TOTAL VIA f1="+total) ;
            let accu = $("#accu_"+id_tot).val() ;

            //console.log("DEBUG-TRACE accu="+accu) ;

                if ( accu == null || accu == "" )
                accu = 2 ;

            //console.log("DEBUG-TRACE #res_" + id_tot + " = " + Number(total).toFixed( accu ) ) ;

            $("#res_"+id_tot).val( Number(total).toFixed( accu ) ) ;
            }
        }
    } ) ;
}

function eval_value( id_rec, ref_ana, num_var, id_res )
{
//console.log("DEBUG-TRACE EVAL_VALUE -------------------------------------");
let val  = $( "#res_"+id_res ).val()  ;

    if ( val == null || val == "" )
    return "";

//console.log("------------------------------------------------------");
}

function conv_val( formula2, accu2, val )
{
console.log("####################### DEBUG-TRACE CONV_VAL ###################");

    // start by evaluate this value
    if ( val == null || val == "" )
    return "" ;

// search formula for this var
formula2 = formula2.replace("$", val) ;

console.log("DEBUG-TRACE conv formula2 = " + formula2 ) ;

let total = eval(formula2) ;

console.log("DEBUG-TRACE total : " + total);

console.log("DEBUG-TRACE accu2="+accu2) ;

    if ( accu2 == null || accu2 == "" )
    accu2 = 2 ;

console.log("DEBUG-TRACE conv_val = " + Number(total).toFixed( accu2 ) ) ;

return Number(total).toFixed( accu2 ) ;
}

function check_min_max(id_res, min, max)
{
let val = $( "#res_"+id_res ).val() ;

    if ( (min != '' && val <= Number.parseFloat(min)) || (max != '' && val >= Number.parseFloat(max)) )
    {
        $("#limit_"+id_res).addClass('show') ;
        $("#limit_"+id_res).removeClass('d-none') ;
    }
    else
    {
        $("#limit_"+id_res).addClass('d-none') ;
        $("#limit_"+id_res).removeClass('show') ;
    }
}

function check_min(id_res, min)
{
let val = $( "#res_"+id_res ).val() ;

    if ( min != '' && val <= Number.parseFloat(min) )
    {
        $("#limit_"+id_res).addClass('show') ;
        $("#limit_"+id_res).removeClass('d-none') ;
    }
    else
    {
        $("#limit_"+id_res).addClass('d-none') ;
        $("#limit_"+id_res).removeClass('show') ;
    }
}

function check_max(id_res, max)
{
let val = $( "#res_"+id_res ).val() ;

    if ( max != '' && val >= Number.parseFloat(max) )
    {
        $("#limit_"+id_res).addClass('show') ;
        $("#limit_"+id_res).removeClass('d-none') ;
    }
    else
    {
        $("#limit_"+id_res).addClass('d-none') ;
        $("#limit_"+id_res).removeClass('show') ;
    }
}

/* ------------------------------------------------------------------ */
/* Click feedback + loading spinner                                    */
/* When the user clicks an action/submit button that talks to the      */
/* server, THAT button immediately dims and shows its own little       */
/* spinner and becomes un-clickable (so it can't be tapped twice), and */
/* a light overlay covers the page while the server works. It is       */
/* triggered ONLY by an AJAX call that closely follows a real click,   */
/* so the background polls (unread messages, backup status) never make */
/* it flash; quick actions skip the page overlay via a short delay.    */
/* ------------------------------------------------------------------ */
(function ()
{
var LBK_DELAY    = 350 ;    // ms before the page overlay appears (quick actions skip it)
var LBK_CLICK_MS = 1500 ;   // an AJAX starting within this window of a click = a user action
var lbk_timer    = null ;
var lbk_click_t  = 0 ;
var lbk_$btn     = null ;
var lbk_pending  = 0 ;
var LBK_SEL = "button, input[type=submit], input[type=button], .btn, a.btn, [onclick]" ;

    $(function ()
    {
        if ( !document.getElementById("lbk-spin-style") )
        {
        var css =
            "#lbk-spin-overlay{position:fixed;top:0;left:0;width:100%;height:100%;z-index:13000;" +
            "display:none;align-items:center;justify-content:center;background:rgba(255,255,255,.2);cursor:wait}" +
            "#lbk-spin-overlay .lbk-spin{width:46px;height:46px;border-radius:50%;" +
            "border:4px solid rgba(58,125,52,.2);border-top-color:#3a7d34;background:rgba(255,255,255,.65);" +
            "box-shadow:0 2px 10px rgba(0,0,0,.15);animation:lbk-spin .8s linear infinite}" +
            "@keyframes lbk-spin{to{transform:rotate(360deg)}}" +
            ".btn:active{transform:scale(.97)}" +
            ".lbk-busy{position:relative !important;opacity:.6 !important;pointer-events:none !important}" +
            ".lbk-busy::after{content:'';position:absolute;top:50%;left:50%;width:16px;height:16px;" +
            "margin:-8px 0 0 -8px;border-radius:50%;border:2px solid rgba(0,0,0,.15);" +
            "border-top-color:#3a7d34;animation:lbk-spin .7s linear infinite}" ;

        var st = document.createElement("style") ;
        st.id  = "lbk-spin-style" ;
        st.appendChild( document.createTextNode(css) ) ;
        document.head.appendChild(st) ;
        }

        if ( !document.getElementById("lbk-spin-overlay") )
        $("body").append('<div id="lbk-spin-overlay"><div class="lbk-spin"></div></div>') ;
    } ) ;

    // remember the last action element the user pressed
    $(document).on("mousedown", LBK_SEL, function () { lbk_click_t = Date.now() ; lbk_$btn = $(this) ; } ) ;

function lbk_show_overlay() { $("#lbk-spin-overlay").css("display", "flex") ; }

function lbk_done()
{
lbk_pending = 0 ;
clearTimeout(lbk_timer) ;
$("#lbk-spin-overlay").hide() ;
$(".lbk-busy").removeClass("lbk-busy") ;   // clear any busy button(s)
lbk_$btn = null ;
}

    // Count ONLY the AJAX calls that closely follow a real click (ignores the
    // background polls). ajaxSend/ajaxComplete fire per-request, so this stays
    // correct even if a poll overlaps a user action.
    $(document).ajaxSend( function (e, xhr)
    {
        if ( Date.now() - lbk_click_t > LBK_CLICK_MS ) return ;   // background poll, not a click
        xhr._lbk = true ;                                        // tag it as a user action
        if ( lbk_$btn ) lbk_$btn.addClass("lbk-busy") ;          // per-button: dim + spinner + lock
        lbk_pending++ ;
        if ( lbk_pending === 1 ) lbk_timer = setTimeout(lbk_show_overlay, LBK_DELAY) ;
    } ) ;

    $(document).ajaxComplete( function (e, xhr)
    {
        if ( !xhr || !xhr._lbk ) return ;
        lbk_pending = Math.max(0, lbk_pending - 1) ;
        if ( lbk_pending === 0 ) lbk_done() ;
    } ) ;

    $(window).on("beforeunload", lbk_done) ;
})() ;
