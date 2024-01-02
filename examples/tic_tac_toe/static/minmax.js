//Code for each symbol
let X = "h1 fas fa-times";
let O = "h1 far fa-circle";
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
    $("#cell-" + cell + " i").addClass(symbol);
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
            if (player == BOT) {
                return WIN;
            } else {
                return LOSE;
            }
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
    for (cells of win_conds) {
        win = evaluteCondition(cells, board);
        if (win) {
            if (current_player == PLAYER) {
                $("#prompt").html("Ganhaste.");
            } else {
                $("#prompt").html("Ganhei :-)");
            }
            game_over = true;
            return null;
        }
    }
    if (isFull(board)) {
        $("#prompt").html("Empate");
        //end the game
        game_over = true;
    }
}

//update the game based on the board
function updateGameState(grid) {
    let i;
    for (i = 0; i < 9; i++) {
        if (grid[i] == "x") {
            updateCell(i + 1, X);
        } else if (grid[i] == "o") {
            updateCell(i + 1, O);
        }
    }
    isGameOver();
}

function clearBoard() {
    current_player = null;
    $(".grid-cell i").removeClass(X);
    $(".grid-cell i").removeClass(O);
    board = ["", "", "", "", "", "", "", "", ""];
    game_over = false;
}
//Function that registers player's moves

function getPlayerMove() {
    if (current_player != PLAYER || game_over) return null;
    cell = parseInt($(this).data("cell-index"));
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
    let i;
    for (i = 0; i < 9; i++) {
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
    $("#prompt").html("Pensando...");
    getBotMove();
    updateGameState(board);
    if (!game_over) {
        current_player = PLAYER;
        $("#prompt").html("Tua vez.");
    }
}

//Function that starts the game loop
function startGame(startingPlayer) {
    current_player = startingPlayer;
    //Add event listener to the grid
    $(".grid-cell").on("click", getPlayerMove);
    $("#player-text").html("Eu recomeço");
    $("#bot-text").html("Tu recomeças");
    //Check whose is starts game
    if (startingPlayer == BOT) {
        BOT.symbol = "x";
        PLAYER.symbol = "o";
        startBotTurn();
    } else {
        PLAYER.symbol = "x";
        BOT.symbol = "o";
        $("#prompt").html("Tua vez.");
    }
}

$(document).ready(function () {
    //Add event listener to start option
    $("#player-option").on("click", function () {
        if (current_player != null) clearBoard();
        startGame(PLAYER);
    });

    $("#bot-option").on("click", function () {
        if (current_player != null) clearBoard();
        startGame(BOT);
    });
});
