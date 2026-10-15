# PRB-003 — 接收拒绝、条件等待与技术预算收敛

- **日期／阶段：**2026-10-12；独立原生信号最小诊断，非正式实验。
- **现象：**旧CYCLES_W300_01在1201s以POST_GREEN_RECEIVER_DENIED停止，耗时126.18s，小于300s预算；只实际放行1辆，未到1207／黄转红／完整周期。早期180s停止与该接收拒绝须分开，不能用加预算绕过拒绝。
- **证据与版本：**[原停止科学复核](../../artifacts/candidate_a_native_budget_cycles_20261012_v1/runs/CA_NATIVE_PHASE_R300_S17_CYCLES_W300_01/FINAL_SCIENTIFIC_REVIEW_V1.md)、[WAIT最小实现及实际诊断](../development/CANDIDATE_A_NATIVE_WAIT_DIAGNOSTIC_20261012.md)、[预算结项](../development/CANDIDATE_A_NATIVE_BUDGET_SUFFICIENCY_CLOSEOUT_20261012.md)。新卡c6f857…为WAIT_DIAG01_V2，未提交源快照绑定baseline 20e5e83…，不能声称baseline已测试新源码。原始输出仍在独立工作区；主目录摘要／哈希不冒充完整raw在线访问。
- **科研影响：**必须分清技术预算耗尽、合同拒绝与未知；零告警只限日志／监测覆盖。恢复周期运行不是服务资格或普遍安全通过。
- **根因：**旧接收查询用v+a×1s的假设推进；下一辆静止车不满足该谓词，读数和车辆绑定真实。新actual-speed查询不同，不把旧available=False改为True，也不认定静止队列危险。
- **采取的方案及效果：**独立WAIT仅在身份／模式／时间／路线／覆盖／当前间距完整绑定且通过时允许原生继续；未知或拒绝仍STOP，fresh-cycle准入保持。进入车辆before拒绝×after通过的漏STOP已修复，旧反例FAIL／新11项PASS保留。300／360s各一次到1272，1207检查点及三周期完成；监控清理144.848700／135.124102s，whole CLI145.409144／135.392720s。420／480按用户收敛SKIPPED_BY_USER_CONVERGENCE，未启动，不补零。
- **最终状态／停止条件：**MITIGATED，限暂时等待导致整轮终止的工程问题；预算子问题已CLOSED：300s为已测足够最小预算，不是绝对最优或可靠性保证。两run相同seed／共同核心，不是随机独立重复，速度差不归因预算。每run C=applied C=E6、N3仍不合格；退出车辆末步制动覆盖和父CLI提示范围限制保留。任何未知／异常继续STOP，旧证据不覆盖。
- **下一链接：**[PRB-004](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)追踪服务缺额；[Issue #12](https://github.com/yuhong-zhang202/MatsterArbeit_Rampmetering/issues/12)。此归档不修改生产guard、协议或运行权限。

**主要来源快照 SHA-256：** `d2326198719eb413672832d9852e997d252dce7995dfaa53859b6f8fc78549ab`（CANDIDATE_A_NATIVE_WAIT_DIAGNOSTIC_20261012.md；归档时校验，不替代该报告引用的原始证据）。

---

2026-10-15补记：后续G5/Y3、累计纠偏与新154动态／真实闭环见[PRB-004](PRB-004_NOMINAL_TWO_CAR_DISCHARGE.md)。不以它们重写旧E6/N3。后续单独获批取消固定输出字节门及同600秒监控账均按各卡，不把旧300MB／300秒参考视作所有后续运行的统一上限。
