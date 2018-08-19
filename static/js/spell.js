
// This function will bold the text 'At Higher Levels.'
function highlight_at_higher_levels() {

  paragraphs = document.getElementById("description").getElementsByTagName("p");

  for (i = 0; i < paragraphs.length; i++) {
    paragraphs[i].innerHTML = paragraphs[i].innerHTML.replace(
      "At Higher Levels.",
      "<strong>At Higher Levels.</strong>"
    );
  }

}

// This function will bold the text 'This spell's damage increases'
function highlight_damage_increases() {

  paragraphs = document.getElementById('description').getElementsByTagName('p');

  for (i = 0; i < paragraphs.length; i++) {
    paragraphs[i].innerHTML = paragraphs[i].innerHTML.replace(
      "This spell's damage increases when you reach higher levels",
      "<strong>This spell's damage increases when you reach higher levels</strong>"
    );
  }

}

// execute on page load
$(window).on('load',function(){
    highlight_at_higher_levels();
    highlight_damage_increases();
});
