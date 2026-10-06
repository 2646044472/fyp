# Fast-CC 掌紋 ROI 兩人先導測試分析報告

日期：2026-09-22  
平台：Raspberry Pi 5 + Camera NoIR v2 + 動態掌心 ROI  
演算法：Fast-CC  
ROI：128×128 灰階影像  
判定規則：Fast-CC distance 越低越相似；本次暫用既有門檻 0.28

## 1. 實驗目的

本次先導測試回答兩個最基本問題：

1. 同一隻手重複放置時，ROI 經過正規化後是否仍能保持相似，讓 Fast-CC 穩定接受？
2. 換成另一個人的手（Bankey）時，Fast-CC 是否能穩定拒絕？

這不是完整的準確率或安全性驗證。它是小規模的工程診斷，用於判斷目前主要風險來自 ROI 重複性、Fast-CC 分數分離能力、既有門檻，或三者的組合。

## 2. 資料與測試協議

所有比較共用同一張參考影像，避免因更換 reference 而令兩組結果不可直接比較：

- Reference：`20260916T201834Z/sample_001/roi_128.png`
- 同手 probes：`20260916T201834Z/sample_002–010/roi_128.png`，共 9 張
- 異手 probes：`20260916T202013Z/sample_002–010/roi_128.png`，全部屬於 Bankey，共 9 張

每張樣本都有：

- `raw.png`：原始相機影像
- `roi_128.png`：實際送入 matcher 的 128×128 ROI
- `metadata.json`：ROI 四邊形、對比度、清晰度、追蹤狀態和相機設定

本次使用固定 reference 對每張 probe 計算一次 Fast-CC distance。門檻 0.28 來自現有 demo 的 provisional setting，並非由這 18 次比較重新調校。這可避免用測試資料反過來選擇最有利的門檻。

## 3. 主要結果

| 指標 | 同一隻手 | Bankey 異手 |
|---|---:|---:|
| Probe 數量 | 9 | 9 |
| 平均 distance | 0.2822 | 0.3403 |
| 中位數 | 0.3065 | 0.3389 |
| 標準差 | 0.0742 | 0.0489 |
| 最低 distance | 0.1784 | 0.2792 |
| 最高 distance | 0.3958 | 0.4041 |
| 門檻 0.28 下接受 | 4/9 | 1/9 |
| 門檻 0.28 下拒絕 | 5/9 | 8/9 |

以「同手應接受、異手應拒絕」計算，混淆矩陣如下：

| 真實身分 | 系統接受 | 系統拒絕 |
|---|---:|---:|
| 同一隻手 | 4（正確接受） | 5（錯誤拒絕） |
| Bankey 異手 | 1（錯誤接受） | 8（正確拒絕） |

因此，在這個很小的 pilot 中：

- True Accept Rate：44.4%
- False Reject Rate：55.6%
- True Reject Rate：88.9%
- False Accept Rate：11.1%
- Balanced Accuracy：66.7%

以上百分比只描述這 18 次比較，不能外推為系統整體的 FAR、FRR 或識別準確率。

## 4. 逐張 Fast-CC 結果

### 4.1 同一隻手

| Probe | Distance | 0.28 判定 | 解讀 |
|---|---:|---|---|
| sample_002 | 0.1886 | ACCEPT | 穩定、明顯低於門檻 |
| sample_003 | 0.3065 | REJECT | 錯誤拒絕 |
| sample_004 | 0.3448 | REJECT | 錯誤拒絕 |
| sample_005 | 0.3560 | REJECT | 錯誤拒絕 |
| sample_006 | 0.2558 | ACCEPT | 接受，但距離較 sample_002 高 |
| sample_007 | 0.3075 | REJECT | 錯誤拒絕 |
| sample_008 | 0.3958 | REJECT | 最嚴重的同手失敗 |
| sample_009 | 0.2063 | ACCEPT | 穩定 |
| sample_010 | 0.1784 | ACCEPT | 本組最低 distance |

同一隻手的 distance 從 0.1784 到 0.3958，跨度為 0.2174。這個跨度大於兩組平均值之間的差距，顯示重複放手引起的變化足以蓋過部分身分差異。

### 4.2 Bankey 異手

| Probe | Distance | 0.28 判定 | 解讀 |
|---|---:|---|---|
| sample_002 | 0.3389 | REJECT | 正確拒絕 |
| sample_003 | 0.3885 | REJECT | 正確拒絕；影像品質偏低 |
| sample_004 | 0.2802 | REJECT | 極接近門檻，只高 0.0002 |
| sample_005 | 0.3135 | REJECT | 正確拒絕 |
| sample_006 | 0.3730 | REJECT | 正確拒絕 |
| sample_007 | 0.3975 | REJECT | 正確拒絕 |
| sample_008 | 0.2792 | ACCEPT | 錯誤接受，只低於門檻 0.0008 |
| sample_009 | 0.2881 | REJECT | 接近門檻 |
| sample_010 | 0.4041 | REJECT | 本組最高 distance |

Bankey 的 sample_008 被錯誤接受。sample_004、sample_008 和 sample_009 都位於門檻附近，代表結果對門檻的微小變動十分敏感。

## 5. 分數分離能力

同手平均 distance 為 0.2822，異手平均為 0.3403，平均差只有 0.0582。異手分數通常較高，方向符合預期，但兩組分布重疊嚴重：

- 同手範圍：0.1784–0.3958
- 異手範圍：0.2792–0.4041
- 重疊區間：0.2792–0.3958

9 個同手 probes 中有 5 個落入異手分數範圍。以「隨機抽取一個異手和一個同手，異手 distance 較高」計算，觀察到的排序 AUC 約為 0.716。這代表系統有一些區分訊號，但遠未達到穩定分離。

兩組平均值的標準化差異 Cohen's d 約為 0.87。這個值顯示平均上有差異，但不能抵消個別分數的大量重疊。生物辨識系統需要在個別決策層面可靠分離，而不只是兩組平均值不同。

在這 18 個已觀察分數上，若把門檻降到約 0.2558，可以令本批 Bankey probes 全部被拒絕，但同手仍只有 4/9 被接受。也就是說，單純降低門檻只能減少錯誤接受，不能修復同手重複性。提高門檻則會接受更多同手樣本，同時增加 Bankey 被接受的風險。

## 6. ROI 與影像品質診斷

### 6.1 同手最大失敗：sample_008

Reference 的 ROI 四邊形約為 189×189 px，中心約在 `(304.9, 136.3)`。同手 sample_008 的 ROI 約為 260×260 px，中心約在 `(256.1, 188.6)`：

- ROI 邊長增加約 37%
- 中心水平移動約 49 px
- 中心垂直移動約 52 px
- Fast-CC distance 為 0.3958，是同手組最高值

這說明目前的 ROI 雖然都被輸出成 128×128，但正規化前所涵蓋的掌心範圍、尺度和位置仍可大幅改變。縮放到相同像素大小不等於掌紋結構已被對齊。

同手 sample_005 也有明顯水平中心位移，distance 為 0.3560。不過 sample_010 在 ROI 尺度和中心也與 reference 有差異，distance 卻只有 0.1784。因此，幾何偏移是重要因素，但不能單獨解釋全部分數變化；旋轉、掌面姿勢、照明、局部紋理涵蓋範圍，以及 Fast-CC 的特徵敏感度也可能參與。

### 6.2 Bankey 錯誤接受：sample_008

Bankey sample_008 的 contrast 為 46.70、sharpness 為 32.83，均明顯高於目前品質門檻（contrast 12、sharpness 2）。它不是一張明顯模糊或低對比的 ROI，卻得到 0.2792 並被接受。

這個案例不能簡單歸類為「影像品質差導致錯誤」。它更可能反映：

1. Fast-CC 在目前 ROI 內容下對兩隻手產生相近的二值特徵；
2. ROI 涵蓋的有效掌紋區域不足或不一致，使身分特徵被弱化；
3. provisional threshold 0.28 位於兩組分布的重疊區；
4. 以上因素共同作用。

Bankey sample_003 的 contrast 只有 13.05、sharpness 6.00，接近目前最低品質要求，而且 ROI 視覺上有明顯不均勻紋理。它仍通過 `READY`，表示現有 quality gate 只保證最低可處理條件，不保證生物辨識品質。

## 7. 可以支持的結論

本次資料支持以下工程結論：

1. ROI pipeline 可以在每次 capture 中產生完整的 128×128 ROI，並保存可追溯的原圖與 metadata。
2. 同一隻手重複放置時，Fast-CC distance 不穩定；以 0.28 門檻計算，5/9 probes 被錯誤拒絕。
3. Bankey 的大部分 probes 能被拒絕，但出現 1/9 錯誤接受，另有兩張非常接近門檻。
4. 同手與異手分數分布重疊，現階段不能只靠調整單一門檻取得可靠結果。
5. ROI 幾何不一致是同手失敗的一個具體來源，但 Bankey sample_008 顯示 matcher／threshold 端也需要檢查。
6. 現有 `READY` quality gate 不等於「足以可靠辨識」；它目前只是最低影像與追蹤條件。

## 8. 本次不能支持的結論

本次只有兩個人、每組 9 個 probes，而且只有一張固定 reference，因此不能據此宣稱：

- 系統的正式 FAR、FRR、EER 或準確率
- Fast-CC 本身一定不適合本項目
- ROI 演算法是唯一失敗原因
- 0.28 是有效或最佳門檻
- 系統能抵抗 spoofing 或提供支付級安全性
- 結果可泛化到不同使用者、相機距離、旋轉、光線或日期

## 9. 下一輪測試建議

### 第一階段：確認 ROI 重複性

先對同一隻手收集 30 次真正獨立放置。每次必須完全移開再放回，保存原圖、ROI 和 metadata。分析項目包括：

- ROI 中心、尺度和旋轉角的變異
- 與 reference 的 Fast-CC distance
- contrast、sharpness 與 distance 的關聯
- 高 distance 樣本的並排視覺檢查

### 第二階段：固定 ROI 後測 matcher

若 ROI 視覺和幾何已穩定，但同手 distance 仍大幅波動，才把重點移到 Fast-CC：

- 使用多張 enrollment ROI，而非單張 reference
- 比較 median gallery score、minimum score 和 template fusion
- 使用獨立 development data 選門檻
- 保留測試資料作最終評估，避免用同一批資料調參又報告結果

### 第三階段：異手與條件變化

在同手基本穩定後，再依序加入：

1. Bankey 30 次獨立放置
2. 左右旋轉 15°、30°
3. 不同相機距離
4. 更多參與者
5. 不同日期的重測

每個變因應獨立成組，避免同時改變角度、距離與光線後無法定位原因。

## 10. 建議的故障判定規則

| 現象 | 優先檢查 |
|---|---|
| 同手高 distance，ROI 中心／尺度／角度明顯不同 | ROI 幾何與正規化 |
| 同手高 distance，ROI 幾何正常但模糊或曝光異常 | Quality gate 與相機設定 |
| 同手高 distance，ROI 幾何與品質都正常 | Fast-CC 特徵與 gallery 策略 |
| 異手低 distance，ROI 品質正常 | Matcher 分離能力與 threshold |
| 異手低 distance，ROI 截取區域錯誤或缺少掌紋 | ROI 演算法 |

## 11. 報告用簡短解讀

這次 pilot 用同一張 reference 分別比較 9 張同手 ROI 和 9 張 Bankey 異手 ROI。Fast-CC 的異手平均 distance 較高，表示系統有一定的身分區分訊號；但是兩組分數嚴重重疊。在 provisional threshold 0.28 下，同手只有 4/9 被接受，Bankey 則有 1/9 被錯誤接受。最嚴重的同手錯誤伴隨 ROI 尺度增加約 37% 和明顯中心位移，證明 ROI 正規化仍不穩定；另一方面，Bankey 的錯誤接受影像具有良好 contrast 和 sharpness，表示問題不只來自影像品質，也涉及 matcher 和 threshold。現階段最合理的結論是：pipeline 已能穩定產生 ROI，但尚未達到可靠辨識，下一步應先量化和改善 ROI 對齊，再用獨立資料重新評估 Fast-CC 與門檻。

## 12. 相關輸出

- 逐筆數據：`code/palm_demo/runtime/debug_capture/two_hand_comparison.csv`
- 同手並排圖：`code/palm_demo/runtime/debug_capture/20260916T201834Z/repeatability_report/comparison_01.png`
- 同手摘要：`code/palm_demo/runtime/debug_capture/20260916T201834Z/repeatability_report/summary.json`
- Bankey 原始樣本：`code/palm_demo/runtime/debug_capture/20260916T202013Z/sample_002–010/`

注意：本報告的 Bankey 分數全部使用 `201834Z/sample_001` 作共同 reference，以 `two_hand_comparison.csv` 為準。`202013Z/repeatability_report` 是較早使用該 session 自身 sample_001 計算的診斷輸出，不屬於本報告的共同-reference protocol。
