counter = 0;
total = 0;

function clear_dice() {
  dice_result = document.getElementById("dice_result");
  dice_result.innerHTML = "";
  dice_total = document.getElementById("dice_total");
  dice_total.innerHTML = "";
  total = 0;
  counter = 0;
}

function roll_dice(number) {
  roll = Math.floor(Math.random() * number) + 1;
  total += roll;
  counter += 1;
  dice_result = document.getElementById("dice_result");
  dice_result.innerHTML = dice_result.innerHTML + "<small>[" + counter + "]</small> <strong>d" + number + "</strong> rolled a <strong>" + roll + "</strong><br>";
  dice_total = document.getElementById("dice_total");
  dice_total.innerHTML = "<br><strong>Total</strong>: " + total;
}
