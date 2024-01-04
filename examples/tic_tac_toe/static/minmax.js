//Code for each symbol
let X = "uil:times";
let O = "uil:circle";
//Player symbol
let PLAYER = { id: "PLAYER", symbol: null };
let BOT = { id: "BOT", symbol: null };

let board = ["", "", "", "", "", "", "", "", ""];

//Scores to measure the value of
//each move
WIN = 10;
LOSE = -10;
DRAW = 0;

//Different win conditions
win_conds = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
];

//Keeps track of whose turn it is
let current_player = null;
//Tracks if game is over
let game_over = false;

//Function that updates a cell with
//the given symbol
function updateCell(cell, symbol) {
    const cellEl = document.querySelector(`#cell-${cell} iconify-icon`);
    cellEl.setAttribute("icon", symbol);
    cellEl.classList.remove("d-none");
}

//Check the board for the win conditions
function evaluteCondition(cells, grid) {
    if (grid[cells[0]] == "" || grid[cells[1]] == "" || grid[cells[2]] == "") {
        return false;
    }

    if (grid[cells[0]] == grid[cells[1]] && grid[cells[0]] == grid[cells[2]]) {
        return true;
    }
    return false;
}

//Checks if board is full
function isFull(grid) {
    let i;
    for (i = 0; i < 9; i++) {
        if (grid[i] == "") return false;
    }
    return true;
}

function getScore(grid, player) {
    //Check conditions
    let win = false;
    for (cells of win_conds) {
        win = evaluteCondition(cells, grid);
        if (win) {
            return player == BOT ? WIN : LOSE;
        }
    }
    if (isFull(grid)) {
        return 0;
    }
    return null;
}

function isGameOver() {
    //Check conditions
    let win = false;
    const game_prompt = document.querySelector("#prompt");
    for (cells of win_conds) {
        win = evaluteCondition(cells, board);
        if (win) {
            game_prompt.innerHTML =
                current_player == PLAYER ? "Ganhaste." : "Ganhei :-)";
            game_over = true;
        }
    }
    if (isFull(board)) {
        game_prompt.innerHTML = "Empate";
        //end the game
        game_over = true;
    }
}

//update the game based on the board
function updateGameState(grid) {
    for (let i = 0; i < 9; i++) {
        if (grid[i] == "") {
            continue;
        }
        updateCell(i + 1, grid[i] == "x" ? X : O);
    }
    isGameOver();
}

function clearBoard() {
    current_player = null;
    const gridCellsIcons = document.querySelectorAll(".grid-cell iconify-icon");

    gridCellsIcons.forEach((iconEl) => {
        iconEl.setAttribute("icon", "");
        iconEl.classList.add("d-none");
    });

    board = ["", "", "", "", "", "", "", "", ""];
    game_over = false;
}
//Function that registers player's moves

function getPlayerMove(event) {
    if (current_player != PLAYER || game_over) return null;
    const cellNum = event.target.dataset.cellIndex;
    cell = parseInt(cellNum);
    if (board[cell] == "") {
        board[cell] = PLAYER.symbol;
        updateGameState(board);
        if (!game_over) {
            startBotTurn();
        }
    }
}

//Functions that uses minimax
//to get the next optimal move
//for the bot player
function minimax(grid, player) {
    if (getScore(grid, player) != null) {
        return getScore(grid, player);
    } else {
        let turn_player;
        if (player == BOT) turn_player = PLAYER;
        else turn_player = BOT;
        let scores = [];
        let i;
        for (i = 0; i < 9; i++) {
            if (grid[i] == "") {
                grid[i] = turn_player.symbol;
                scores.push(minimax(grid, turn_player));
                grid[i] = "";
            }
        }
        if (turn_player == BOT) {
            return Math.max(...scores);
        } else {
            return Math.min(...scores);
        }
    }
}

function getBotMove() {
    let scores = [];
    let moves = [];

    for (let i = 0; i < 9; i++) {
        if (board[i] == "") {
            board[i] = BOT.symbol;
            scores.push(minimax(board, BOT));
            moves.push(i);
            board[i] = "";
        }
    }
    let choice = moves[scores.indexOf(Math.max(...scores))];
    board[choice] = BOT.symbol;
}

function startBotTurn() {
    current_player = BOT;
    const gamePrompt = document.querySelector("#prompt");
    gamePrompt.innerHTML = "Pensando...";
    getBotMove();
    updateGameState(board);
    if (!game_over) {
        current_player = PLAYER;
        gamePrompt.innerHTML = "Tua vez.";
    }
}

function startGame(startingPlayer) {
    current_player = startingPlayer;
    //Add event listener to the grid
    //
    document
        .querySelectorAll(".grid-cell")
        .forEach((cell) => cell.addEventListener("click", getPlayerMove));
    document.querySelector("#player-text").innerHTML = "Eu recomeço";
    document.querySelector("#bot-text").innerHTML = "Tu recomeças";
    //Check whose is starts game
    if (startingPlayer == BOT) {
        BOT.symbol = "x";
        PLAYER.symbol = "o";
        startBotTurn();
    } else {
        PLAYER.symbol = "x";
        BOT.symbol = "o";
        document.querySelector("#prompt").innerHTML = "Tua vez.";
    }
}

window.addEventListener("load", () => {
    alert("hello world");
    //Add event listener to start option
    document.querySelector("#player-option").addEventListener("click", () => {
        if (current_player != null) clearBoard();
        startGame(PLAYER);
    });

    document.querySelector("#bot-option").addEventListener("click", () => {
        if (current_player != null) clearBoard();
        startGame(BOT);
    });
});
