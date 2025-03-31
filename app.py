from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import os

from game_runner import GameRunner

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Tạo đối tượng GameRunner
game = GameRunner(size=19, depth=2)


class Move(BaseModel):
    row: int
    col: int


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/1vs1", response_class=HTMLResponse)
async def game_1vs1(request: Request):
    """Trang chơi 1 vs 1"""
    return templates.TemplateResponse("1vs1.html", {"request": request})


@app.post("/1vs1/play")
async def play(request: Request, move: Move):
    """Xử lý lượt đi của người chơi."""
    try:
        # Kiểm tra giới hạn của bàn cờ
        if not (1 <= move.row <= game.size and 1 <= move.col <= game.size):
            return JSONResponse(
                content={"point": None, "win": 0, "error": "Nước đi nằm ngoài bàn cờ"}
            )

        print(f"Người chơi đi: ({move.row}, {move.col})")  # Log nước đi
        success = game.play(move.row - 1, move.col - 1)

        if not success:
            print("Nước đi không hợp lệ")  # Log lỗi
            return JSONResponse(
                content={"point": None, "win": 0, "error": "Nước đi không hợp lệ"}
            )

        # Kiểm tra nếu có người thắng
        if game.finished:
            print(f"Người chơi thắng: {game.state.winner}")  # Log kết quả
            return JSONResponse(
                content={
                    "point": int(game.state.color),
                    "win": 2 if game.state.winner == 1 else 3,
                    "win_cells": game.state.win_cells,  # Thêm vị trí của 5 quân thắng
                }
            )

        print(f"Lượt tiếp theo: {game.state.color}")  # Log lượt tiếp theo
        return JSONResponse(content={"point": int(game.state.color), "win": 0})
    except Exception as e:
        print(f"Lỗi khi xử lý nước đi: {str(e)}")  # Log lỗi
        return JSONResponse(content={"point": None, "win": 0, "error": "Có lỗi xảy ra"})


@app.post("/1vs1/ai-play")
async def ai_play():
    """Xử lý lượt đi của AI."""
    try:
        print("AI đang tính toán nước đi...")  # Log bắt đầu tính toán
        success, move = game.aiplay()

        if not success:
            print("AI không thể đi")  # Log lỗi
            return JSONResponse(content={"point": None, "win": 0})

        row, col = move
        # Chuyển đổi NumPy int64 thành Python int
        row = int(row)
        col = int(col)

        print(f"AI đi: ({row + 1}, {col + 1})")  # Log nước đi

        # Kiểm tra nếu AI thắng
        if game.finished:
            print(f"AI thắng: {game.state.winner}")  # Log kết quả
            return JSONResponse(
                content={
                    "point": int(game.state.color),
                    "win": 2 if game.state.winner == 1 else 3,
                    "win_cells": game.state.win_cells,  # Thêm vị trí của 5 quân thắng
                }
            )

        print(f"Lượt tiếp theo: {game.state.color}")  # Log lượt tiếp theo
        return JSONResponse(
            content={
                "point": int(game.state.color),
                "row": row + 1,
                "col": col + 1,
                "win": 0,
            }
        )
    except Exception as e:
        print(f"Lỗi khi AI đi: {str(e)}")  # Log lỗi
        return JSONResponse(content={"point": None, "win": 0, "error": "Có lỗi xảy ra"})


@app.get("/1vs1/status")
async def get_status():
    """Lấy trạng thái hiện tại của bàn cờ."""
    return JSONResponse(content=game.get_status())


@app.post("/1vs1/restart")
async def restart():
    """Khởi động lại ván cờ."""
    game.restart()
    return JSONResponse(content={"message": "Game restarted"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
