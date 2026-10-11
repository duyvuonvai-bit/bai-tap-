# Bảng alias dùng trong hình LAD

Alias chỉ rút gọn để đọc hình. Chọn tag thực bằng TIA; không tạo biến trùng I/O. DB thực trong ảnh là `daiphunnuoc`. CSV kèm theo là bảng tra, không phải file import TIA đã kiểm chứng.

| Alias | Tag / instance thực | Kiểu | Start | Ghi chú |
|---|---|---|---|---|
| AutoSelected | "chon auto" / %I0.0 | Bool | I/O | 1=AUTO |
| WaterOK | "du nuoc" / %I0.1 | Bool | I/O | 1=du nuoc |
| ResetButton | "nut reset" / %I0.2 | Bool | I/O | 1=nhan, NO |
| EStopOK | "dung khan ok" / %I0.3 | Bool | I/O | 1=binh thuong |
| OverloadOK | "qua tai" / %I0.4 | Bool | I/O | 1=khong trip; doi comment *_OK |
| StopOK | "stop" / %I0.5 | Bool | I/O | 1=chua nhan STOP, NC |
| Pump | "bom nuoc" / %Q0.0 | Bool | I/O | Lenh bom |
| Valve1 | "van 1" / %Q0.1 | Bool | I/O | Lenh van1 |
| Valve2 | "van 2" / %Q0.2 | Bool | I/O | Lenh van2 |
| Valve3 | "van 3" / %Q0.3 | Bool | I/O | Lenh van3 |
| Valve4 | "van 4" / %Q0.4 | Bool | I/O | Lenh van4 |
| Alarm | "den bao loi" / %Q0.5 | Bool | I/O | Den loi |
| PLC_LocalTime | "daiphunnuoc"."gio plc" | DTL | DTL default | Truong hien co |
| RTC_Status | "daiphunnuoc"."trangthai rtc" | Int | 0 | Truong hien co |
| RTC_OK | "daiphunnuoc"."rtc_ok" | Bool | FALSE | Truong hien co |
| Morning | "daiphunnuoc"."ca_sang" | Bool | FALSE | Truong hien co |
| Evening | "daiphunnuoc"."ca_toi" | Bool | FALSE | Truong hien co |
| InSchedule | "daiphunnuoc"."trong_gio" | Bool | FALSE | Truong hien co |
| Safe | "daiphunnuoc"."an_toan" | Bool | FALSE | Truong hien co |
| FaultNow | "daiphunnuoc"."loi_hientai" | Bool | FALSE | Truong hien co |
| FaultLatched | "daiphunnuoc"."nho_loi" | Bool | FALSE | Truong hien co |
| StopLatched | "daiphunnuoc"."nho_stop" | Bool | FALSE | Truong hien co |
| ResetEdge | "daiphunnuoc"."xung_reset" | Bool | FALSE | Truong hien co |
| AutoEdge | "daiphunnuoc"."xung_auto" | Bool | FALSE | Truong hien co |
| OffSeen | "daiphunnuoc"."da_gat_tat" | Bool | FALSE | Truong hien co |
| CancelAuto | "daiphunnuoc"."huy_phep_chay" | Bool | FALSE | Truong hien co |
| AutoArmed | "daiphunnuoc"."cho_phep_auto" | Bool | FALSE | Truong hien co |
| Run | "daiphunnuoc"."tu_dong_chay" | Bool | FALSE | Truong hien co |
| CurrentStep | "daiphunnuoc"."buoc_hientai" | Int | 0 | Truong hien co |
| NextStep | "daiphunnuoc"."buoc_tieptheo" | Int | 0 | Truong hien co |
| FirstScan | "daiphunnuoc".vong_quet_dau | Bool | FALSE | Them cho ban26 |
| InitPending | "daiphunnuoc".khoi_tao_cho | Bool | TRUE | Them cho ban26 |
| BadStep | "daiphunnuoc".loi_buoc | Bool | FALSE | Them cho ban26 |
| Ack | "daiphunnuoc".xac_nhan_loi | Bool | FALSE | Them cho ban26 |
| OutputEnable | "daiphunnuoc".cho_phep_ngo_ra | Bool | FALSE | Them cho ban26 |
| ResetTrigger | Instance do TIA tao rieng / Static multi-instance | R_TRIG | Mac dinh instance | Khong dung chung instance; goi moi scan |
| AutoTrigger | Instance do TIA tao rieng / Static multi-instance | R_TRIG | Mac dinh instance | Khong dung chung instance; goi moi scan |
| Timer1 | Instance do TIA tao rieng / Static multi-instance | TON | Mac dinh instance | Khong dung chung instance; goi moi scan |
| Timer2 | Instance do TIA tao rieng / Static multi-instance | TON | Mac dinh instance | Khong dung chung instance; goi moi scan |
| Timer3 | Instance do TIA tao rieng / Static multi-instance | TON | Mac dinh instance | Khong dung chung instance; goi moi scan |
| Timer4 | Instance do TIA tao rieng / Static multi-instance | TON | Mac dinh instance | Khong dung chung instance; goi moi scan |
| Timer5 | Instance do TIA tao rieng / Static multi-instance | TON | Mac dinh instance | Khong dung chung instance; goi moi scan |

`PLC_LocalTime.HOUR/MINUTE/SECOND` là các thành phần USInt của DTL `"daiphunnuoc"."gio plc"`. SR gắn operand Bool ở trên khối: `FaultLatched`, `StopLatched`, `AutoArmed`; đây không phải ba FB cần instance riêng. R1 của SR ưu tiên RESET.

Timer1.Q/ResetTrigger.Q là Q của instance được TIA tạo. Hình thể hiện giá trị đầu ra; không tạo một tag I/O mới trùng tên instance. Có thể nối Q vào Bool trung gian rồi dùng Bool đó nếu cách dựng LAD của dự án yêu cầu.

Không Retain trạng thái điều khiển/timer/trigger. Start TRUE của InitPending bổ sung OB100 SET để bảo đảm scan đầu được nhận diện. NW01 copy sang FirstScan; chỉ NW26 RESET InitPending.

Các cờ xong_buoc1…5, co_van_mo và M0.0/M0.1 có thể bỏ sau kiểm tra Cross-reference khi chuyển bản26. Giữ huy_phep_chay để ánh xạ CancelAuto như hình NW14.
