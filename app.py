from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import os

app = FastAPI()

# Gán thư mục chứa file tĩnh
app.mount("/static", StaticFiles(directory="static"), name="static")

# Đọc nội dung của index.html và trả về
@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = Path("templates/index.html")
    return index_path.read_text(encoding="utf-8")

@app.get("/1vs1", response_class=HTMLResponse)
async def read_1vs1(request: Request):
    client_ip = request.client.host if request.client else "unknown"  # Lấy địa chỉ IP
    history_dir = Path("history")
    history_dir.mkdir(exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

    history_file = history_dir / f"{client_ip}.txt"  # Tạo file theo IP
    history_file.write_text("")  # Xóa nội dung file hoặc tạo file mới

    # Trả về trang 1vs1.html
    index_path = Path("templates/1vs1.html")
    return index_path.read_text(encoding="utf-8")

class Move(BaseModel):
    row: int
    col: int

def get_history_file(client_ip):
    return f"history/{client_ip}.txt"  # Thay đổi để lưu trong thư mục history

def load_board_from_file(client_ip):
    """Đọc lại file lịch sử để khôi phục bàn cờ và lượt chơi."""
    history_file = get_history_file(client_ip)

    if not os.path.exists(history_file):
        return [[""] * 10 for _ in range(10)], "X"

    board = [[""] * 10 for _ in range(10)]
    last_turn = "O"

    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            turn, r, c = line.strip().split(",")
            board[int(r) - 1][int(c) - 1] = turn
            last_turn = turn

    next_turn = "O" if last_turn == "X" else "X"
    return board, next_turn

@app.post("/1vs1/play")
async def play(request: Request, move: Move):
    client_ip = request.client.host
    history_file = get_history_file(client_ip)

    # Đảm bảo thư mục `history/` tồn tại trước khi ghi file
    Path("history").mkdir(parents=True, exist_ok=True)

    board, current_turn = load_board_from_file(client_ip)

    if board[move.row - 1][move.col - 1]:
        return JSONResponse(content={"point": None, "win": 0})

    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{current_turn},{move.row},{move.col}\n")

    board[move.row - 1][move.col - 1] = current_turn

    win_cells, direction = check_win(board, move.row - 1, move.col - 1, current_turn)
    if win_cells:
        return JSONResponse(content={"point": current_turn, "win": 2 if current_turn == "X" else 3, "win_cells": win_cells, "direction": direction})

    return JSONResponse(content={"point": current_turn, "win": 0})

def check_win(board, row, col, player):
    directions = {
        "horizontal": (0, 1),
        "vertical": (1, 0),
        "diagonal": (1, 1),
        "anti-diagonal": (1, -1)
    }

    for direction, (dr, dc) in directions.items():
        cells = [(row, col)]  

        for d in (-1, 1):
            r, c = row + dr * d, col + dc * d
            while 0 <= r < 10 and 0 <= c < 10 and board[r][c] == player:
                if d == -1:
                    cells.insert(0, (r, c))
                else:
                    cells.append((r, c))
                r += dr * d
                c += dc * d

        if len(cells) >= 5:
            win_cells = [(r + 1, c + 1) for r, c in cells[:5]]  # +1 để chuyển từ 0-based thành 1-based
            return win_cells, direction  

    return None, None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
