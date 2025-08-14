# ⚓️🛥️ BattleShip — Multiplayer (2-player) over TCP

## 📌 Mô tả ngắn:
BattleShip là game chiến thuật 2 người chơi, mỗi phòng tối đa 2 người, chạy online qua TCP. Server quản lý nhiều phòng độc lập và lưu trạng thái bàn cùng lượt chơi. Dữ liệu trao đổi dùng JSON line (kết thúc \n) để dễ parse và mở rộng. Client hỗ trợ console ASCII (colorama) hoặc Pygame. Trò chơi gồm chế độ cổ điển (đặt tàu, bắn theo lượt, hit/miss/sunk, xử lý disconnect) và có thể mở rộng thêm Radar, Double Shot, Shield, Salvo mode, tàu đặc biệt.

## 📌 Tính năng chính:
- Nhiều phòng (room), mỗi phòng tối đa 2 players.
- Đặt tàu, bắn theo lượt, thông báo hit / miss / sunk.
- Luật: bắn tiếp nếu trúng; hết tàu → thua.
- Xử lý rớt kết nối (thông báo đối phương thắng hoặc cho phép reconnect).
- Biến thể tùy chọn: Salvo, Radar (3×3), Double Shot, Shield, shapes khác (L-shape).

## Kiến trúc tổng quan:
- Server: TCP listener, map room_id -> GameRoom, mỗi client 1 thread, Lock khi chỉnh dữ liệu chung.
- Client: 2 luồng (recv + input), hiển thị 2 bảng (own/enemy).

## 🚹 Trạng thái phòng (State):
- waiting — chưa đủ 2 người
- placing — cả 2 đang place ships
- playing — luân phiên bắn
- finished — game over, gửi winner

## 🎮 Luồng chơi (flow):
1. Player A connect → join/create room.
2. Player B join same room → server gửi game_start + chỉ định lượt ngẫu nhiên.
3. Cả 2 gửi place_ships.
4. Khi cả 2 đã place → playing.
5. Player có lượt gửi shoot → server trả shot_result và broadcast.
6. Nếu tất cả tàu 1 bên chìm → finished.

## Cách chạy nhanh (Quick start):
**Server**
```sh
python server.py
```
***Client***
```sh
python client.py --host 127.0.0.1 --port 5000 --name "Player1"
```
