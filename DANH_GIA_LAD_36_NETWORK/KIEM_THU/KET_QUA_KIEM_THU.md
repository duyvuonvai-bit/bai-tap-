# Kết quả mô hình quét độc lập

Ngày 11/10/2026: 31/31 nhóm ca đạt; 0 lỗi kiểm thử.

Phạm vi: Python mô phỏng thứ tự quét và TON; không phải TIA/PLCSIM. Các ca cho bản gốc gồm việc tái hiện đúng lỗi bước bất hợp lệ; PASS không có nghĩa bản gốc không thiếu bảo vệ.

| Ca / nhóm ca | Kết quả |
|---|---|
| original36: all 1440 minutes | PASS |
| original36: every second of 24-hour day | PASS |
| revised26: all 1440 minutes | PASS |
| revised26: every second of 24-hour day | PASS |
| original36: startup AUTO cannot self-start | PASS |
| revised26: startup AUTO cannot self-start | PASS |
| original36: 2 cycles, masks, no early transition, scan 1ms | PASS |
| original36: 2 cycles, masks, no early transition, scan 10ms | PASS |
| original36: 2 cycles, masks, no early transition, scan 37ms | PASS |
| revised26: 2 cycles, masks, no early transition, scan 1ms | PASS |
| revised26: 2 cycles, masks, no early transition, scan 10ms | PASS |
| revised26: 2 cycles, masks, no early transition, scan 37ms | PASS |
| original36: four stop inputs at all five steps | PASS |
| revised26: four stop inputs at all five steps | PASS |
| original36: held RESET through recovery | PASS |
| revised26: held RESET through recovery | PASS |
| original36: normal OFF/ON | PASS |
| revised26: normal OFF/ON | PASS |
| original36: automatic next scheduled shift | PASS |
| revised26: automatic next scheduled shift | PASS |
| original36: RTC error and recovery policy | PASS |
| revised26: RTC error and recovery policy | PASS |
| original36: invalid-step injection and diagnosis | PASS |
| revised26: invalid-step injection and diagnosis | PASS |
| original36: STOP at timer expiry | PASS |
| revised26: STOP at timer expiry | PASS |
| RD_LOC_T success status 1 with DST | PASS |
| revised26: DTL field bounds | PASS |
| revised26: first-scan edge suppression | PASS |
| original36: randomized scan invariants | PASS |
| revised26: randomized scan invariants | PASS |

Lịch được thử đủ 86.400 giây/ngày cho mỗi phiên bản. Chu trình thử với scan1,10,37ms. Dừng4đầu vào tại5bước; giữ RESET; startup; RTC; random seed cố định. Xem JSON để đọc các giá trị chứng cứ.

Chạy lại: `python test_lad_model.py` (Python3.10+, thư viện chuẩn).
