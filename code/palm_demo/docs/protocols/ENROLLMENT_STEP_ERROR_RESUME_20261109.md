# 自动录入步骤失败后的恢复 — 2026-11-09，X

## 源码缺口

页面在 `/api/demo/enroll/start` 已取得 token 后，如果首个或后续 `/api/demo/enroll/step` 请求失败，异常分支只显示错误。`enrollmentToken` 仍存在，但 `enrollmentPaused` 为 false，故“继续采集”隐藏；用户只能取消同一会话，丢弃已缓存的候选。已暂停后的手动继续若再次失败，也会发生同样的状态。

## 改动

两处采集异常分支在仍持有 token 时保留暂停状态，提示预览就绪后手动继续或取消。恢复仍使用同一个 token；相机和 ROI READY、忙碌保护由原有 `resumeEnrollment` 判断，不修改服务端会话、八选五和质量门槛。

## 验证

`node tests/test_demo_page.cjs` 通过。新增一个交互场景模拟首次 step 的传输失败、第一次手动继续再次失败、第二次手动继续成功返回 NO_HAND；每次继续请求均使用同一个 token，取消后继续按钮隐藏。`git diff --check -- demo_page.py tests/test_demo_page.cjs` 通过。

## 边界

这是页面模拟测试，未连接相机或真人。若服务端会话已过 120 秒或 token 被撤销，继续请求仍会失败；这项改动只修复临时步骤请求错误时的页面恢复入口。
