**低功耗 sentinel 决定何时唤醒昂贵传感器，但没有唤醒的样本本身不会被观察，系统因此不知道自己漏掉了什么。能否用很小、概率已知的 audit budget，估计并控制 no-wake safety risk?**

低功耗 sentinel 不触发时，系统并非真的“知道没事”，而是选择了不观察。预留小 audit budget，例如即使 ToF 未触发，也按已知概率唤醒 RGB/NIR；据此估计 `P(intrusion | no-wake, context)`。若风险上界超标，系统扩大 wake 区域、提高 audit rate 或输出 `uncertain`。

风险审计式 Cascade Sensing
简单说：
低功耗 sensor 先观察，只有可疑时才启动昂贵 sensor；但系统还要估计“没有启动时，自己可能漏掉了什么”。

例子：

- ToF/PIR 常开；
- 检测到可疑距离才启动 RGB/NIR；
- 少量没有触发的时间段也随机抽查；
- 如果抽查发现 no-wake 漏报率太高，就提高触发灵敏度、增加 audit，或输出 uncertain。
  研究重点不是“如何唤醒相机”，而是：
  在省电的同时，能否知道自己有没有因为不观察而漏掉危险事件？

主要指标是完整时间段中的 missed event、false permit、能耗、延迟和 audit 成本。
这个方向故事清楚、edge 关联强，比较适合 FYP。





**共因退化下的独立证据 Acquisition?**
简单说：
多个 sensor 同意，不代表它们真的提供了独立证据。

例如：

- 强光同时影响 RGB 和 NIR；
- 反光材质同时让 RGB 误判、ToF 测距失败；
- 共享时钟或标定错误让多个 sensor 一起出错。
  普通 fusion 可能看到“RGB 和 NIR 都说安全”，于是提高 confidence。但研究系统要先判断：
  第二个 sensor 是真的提供了新信息，还是只是重复了同一个错误？

系统可以选择启动第三个 sensor、重新采集，或者直接拒绝自动判断。
研究重点是降低：

- false consensus；
- false permit；
- 高置信度错误。
  这个方向比第一个更有研究味，但需要真实的反光、遮挡、距离、低光和同步故障数据，硬件和实验要求更高。
  简单排序：
- E1：较稳、较容易验证
- E3：研究意义更强，但风险和实验成本更高
