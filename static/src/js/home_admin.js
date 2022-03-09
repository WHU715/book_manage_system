var profile_content_box = document.getElementById("profile_content_box");
var profile_upd_box = document.getElementById("profile_upd_box");
var profile_content_box_mana = document.getElementById("profile_content_box_mana");
var profile_upd_box_mana = document.getElementById("profile_upd_box_mana");

var mem_list = document.getElementById("mem_list");
var mem_add_box =  document.getElementById("mem_add_box");

var profile = document.getElementById("profile");

var reader_mana = document.getElementById("reader_mana");

var profile_to_upd_btn = document.getElementById("profile_to_upd_btn");
var profile_upd_back = document.getElementById("profile_upd_back");
var profile_to_upd_btn_mana = document.getElementById("profile_to_upd_btn_mana");
var profile_upd_back_mana = document.getElementById("profile_upd_back_mana");
var mem_add_back_mana = document.getElementById("mem_add_back_mana");
var add_mem_btn = document.getElementById("add_mem_btn");

function hide_all(){
    profile_content_box.style.display="none";
    profile_upd_box.style.display="none";
    profile_content_box_mana.style.display="none";
    profile_upd_box_mana.style.display="none";

    mem_list.style.display="none";
    mem_add_box.style.display="none";
}

profile_to_upd_btn.onclick = function(){
    profile_content_box.style.display="none";
    profile_upd_box.style.display="block";
}

profile_upd_back.onclick = function(){
    profile_upd_box.style.display="none";
    profile_content_box.style.display="block";
}

profile.onclick = function(){
    hide_all();
    profile_content_box.style.display="block";

}

reader_mana.onclick = function(){
    hide_all();
    mem_list.style.display="block";
}

profile_to_upd_btn_mana.onclick = function(){
    hide_all();
    profile_upd_box_mana.style.display = "block";
}

profile_upd_back_mana.onclick = function(){
    hide_all();
    profile_content_box_mana.style.display = "block";
}

mem_add_back_mana.onclick = function(){
    hide_all();
    mem_list.style.display = "block";
}

add_mem_btn.onclick = function(){
    hide_all();
    mem_add_box.style.display = "block";
}