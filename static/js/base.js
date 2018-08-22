
function roll_dice(number) {
  roll = Math.floor(Math.random() * number) + 1;
  dice_result = document.getElementById("dice_result");
  dice_result.innerHTML = "The result of the <strong>d" + number + "</strong> was a <strong>" + roll + "</strong>";
}
