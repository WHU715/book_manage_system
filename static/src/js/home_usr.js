var profile_content_box = document.getElementById("profile_content_box");
var profile_upd_box = document.getElementById("profile_upd_box");

var book_list = document.getElementById("book_list");


var profile = document.getElementById("profile");
var my_book = document.getElementById("my_book");

var profile_to_upd_btn = document.getElementById("profile_to_upd_btn");
var profile_upd_back = document.getElementById("profile_upd_back");

function hide_all(){
    profile_content_box.style.display="none";
    profile_upd_box.style.display="none";
    book_list.style.display="none";
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

my_book.onclick = function(){
    hide_all();
    book_list.style.display="block";
}
