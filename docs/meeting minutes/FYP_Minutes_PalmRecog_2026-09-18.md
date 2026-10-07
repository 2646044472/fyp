# FYP_Minutes_PalmRecog_2026-09-18.md

**Group:** Biometric: Palm Recognition
**Supervisor:** Bob Zhang
**Date:** September 18, 2026
**Attendee:** Stephen, Bankey

目前進度：已完成掌紋辨識及支付系統的初步實作，正在改善 ROI 提取的一致性，尚未完成完整的 end-to-end 性能驗證。

## 1. 已完成的工作

硬件與影像採集

已實作

使用 Raspberry Pi 4 搭配 NoIR Camera V2，已能採集手掌影像。目前測試使用環境光，尚未加入額外的 850 nm IR 補光。

Automatic Palm ROI

已實作

已整合 MediaPipe Palm Detector ONNX 模型，透過 wrist 和 MCP 關鍵點計算掌心中心、方向和尺度，再將 ROI 對齊並轉換成 128×128 灰階影像。

57c7561b-1d57-4bfa-a712-b4747e1833c8.py

57c7561b-1d57-4bfa-a712-b4747e1833c8.py

Recognition

初步整合

已有 DoN 和 Fast-CC 兩種辨識實作。不過，目前 dynamic ROI debug UI 使用 DoN，而 Fast-CC CLI 仍使用固定比例裁切，尚未整合成統一的辨識流程。



Palm Payment

功能原型

已建立包含 1:N 身份搜尋、金額確認、短效 server token 和 SQLite 原子支付的流程，並設計了未知身份、ROI 未就緒及餘額不足時的拒絕路徑。

目前仍需確認支付 demo 使用的辨識引擎及 ROI 版本，並完成完整流程測試。

## 2. 最近的主要研究進展：ROI Stability Investigation



我們發現，即使系統顯示 ROI tracking 成功，同一隻手的掌紋在不同樣本中仍然存在位置和尺度差異。

因此，我們對現有 `palm-detector-mcp-v2` 進行了程式分析及十張 ROI 的離線幾何重建。

## 主要實驗結果

# 10/10

樣本觸發 boundary fitting

# 0.546–0.932

ROI 縮放係數範圍

00.250.50.751

十張現有 ROI metadata 的離線重建結果。數值越小，代表原始 ROI 被縮小得越多。



發現的問題：

目前 ROI 的寬度和高度均設定為 MCP span 的兩倍。當 ROI 超出相機畫面，程式會自動縮小整個裁切區域，再重新 resize 成 128×128。

因此，手掌在畫面中的位置不同，可能導致最後 ROI 的掌紋比例不同。這是一個已確認存在的幾何一致性問題。



但目前尚未證明這是辨識錯誤的唯一原因，亦未量化其對 Fast-CC 準確率的影響。

另外，調查發現現有 quality gate 能檢查單次拍攝內的穩定性，卻不能保證不同次拍攝的 ROI 尺度一致。



## 3. 下一步工作



Step 1 — 改善 ROI 一致性

利用已保存的十張原圖與 detector keypoints，離線比較目前 2.0×2.0 ROI 與較小的裁切尺寸。

分析哪些參數能減少 boundary fitting，同時保留足夠的掌紋資訊。先不修改正式 pipeline。

Step 2 — 統一 Recognition Pipeline

將改善後的 dynamic ROI 接入 Fast-CC，確保 enrollment 和 verification 使用相同的影像預處理及辨識方法。

隨後測試 genuine / impostor score 分布、FAR 和 FRR。

Step 3 — 完成 NIR 與系統測試

加入 850 nm IR 補光，檢查不同光照下的 ROI 品質和辨識表現。

再測試掌紋辨識到支付完成的整條 pipeline，包括陌生使用者、錯誤辨識與支付失敗等情況。

