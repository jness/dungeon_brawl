
// This function will bold the text within description blocks
function highlight_description() {

  paragraphs = document.getElementsByClassName("description");

  for (i = 0; i < paragraphs.length; i++) {

    paragraphs[i].innerHTML = paragraphs[i].innerHTML.replace(
      "At Higher Levels.",
      "<strong>At Higher Levels.</strong>"
    );

    paragraphs[i].innerHTML = paragraphs[i].innerHTML.replace(
      "This spell's damage increases when you reach higher levels",
      "<strong>This spell's damage increases when you reach higher levels</strong>"
    );

  }

}

// execute on page load
$(window).on('load',function(){
    highlight_description();
});
