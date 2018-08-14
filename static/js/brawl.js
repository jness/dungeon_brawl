
function subtract(id) {
  element = document.getElementById(id);
  element.innerHTML -= 1;
}

function add(id) {
  element = document.getElementById(id);
  element.innerHTML ++;
}

// function roll(monsters) {
//
//   for (i = 0; i < monsters.length; i++) {
//     var monster = monsters[i];
//
//     var mod = monster['dexterity_mod'];
//     var roll_result = Math.round(Math.random() * 19 + 1);
//
//     var result = eval(roll_result.toString() + mod);
//
//     element = document.getElementById(monster['unique_id'] + '_dexterity_mod');
//     element.innerHTML = result;
//
//   }
//
// }
