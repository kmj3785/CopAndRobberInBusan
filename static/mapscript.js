const turn = document.getElementById('turn text');
const robberElement = document.getElementById('robber turn');

function changeByjQuery(node) {
    turn.innerHTML = parseInt(turn.innerHTML) + 1;
    robberElement.style.display = 'none';
    console.log(node);
    // robberElement.style.display = 'block';
}