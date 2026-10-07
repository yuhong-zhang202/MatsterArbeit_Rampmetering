# Issue #2 最终独立科学审查

日期：2026-10-07。审查者：`/root/issue2_science`；全程只读，未启动仿真、修改文件或作出研究决策。由主代理按审查者最终回复保存。

**Disposition：PASS_FOR_BOUNDED_TECHNICAL_INVESTIGATION_DELIVERY。**

建议交付状态为“实现完成，待审查”，准确限定为技术调查完成，保留2008论文全文访问限制。此结论不表示A/B执行器已经实现、实际900 veh/h已经合格、用户已经验收或正式实验已经获批。

## 1. 上下文与审查范围

已读取AGENTS、角色说明、PROJECT_STATE、DECISIONS、0B/unfrozen EXPERIMENT_PROTOCOL、相关WORKLOG、Issue #2快照及工程/数据/来源/调查报告。PR1基线`e8bf608a15cf4c4484914467c5550d041c017a62`，D-018结项保持，D-019开发完成/服务不合格。STATE过时段落已标历史，初始冲突解决。没有新SUMO场景；A/B实际安全和服务资格尚未取得。

## 2. 独立核查

- 初次核对28个raw/gate/table绑定和2个工程测试源码哈希；修订后增加published service CSV绑定。
- 逐一核对11个受保护文件SHA-256，均与基线一致。
- 独立汇总72窗口：指令4905.0891784446385，过线3331，丢弃1572.0036676489306，边界余额增加2.0855107957079424；守恒残差约−9.77e−15辆等价额度。
- 独立读取唯一PASS的R750/S23/T1原始300行[2100,2400)：指令46.529768362114375、43个唯一过线ID、误差7.586043%。
- 独立核对43,200控制秒credit跨行连续及12初始余额0。
- 12历史权威gate保留NOT_QUALIFIED和PASS_V15_FCD_SERVICE；不混用被替代的stopped-only sampled_service.json。
- 阅读新合同/10项测试源码，没有重复运行工程测试；receipt源码绑定相符。
- 独立打开2008出版社摘要和SUMO官方文档；L2分层、四policy和detector声明在摘要内有依据，未取得全文。
- 最终数据脚本SHA256：`98a3c43408d00b2f06e8c9ad8a082bb6e8e151c3fc5acbe685bb3b58c024fd81`。

## 3. 五项测量检查

| 检查 | 判定 | 证据与限制 |
|---|---|---|
| 测量目标 | Passed | 最终指令积分/credit/meter过线；veh/h与辆等价额度明确；[600,4200)与72窗口分开，不重新估全路线/源等待/未完成成本 |
| 实际覆盖 | Passed，限本轮用途 | 全12A03日志/权威gate纳入，停止线/入口版本绑定；新A/B runtime覆盖/安全/服务Not verified |
| 遗漏/重复 | Passed | 50,400行/43,200控制秒/72唯一窗口/逐秒连续/过线唯一/credit守恒；优先级遮蔽明确，拒绝秒数不相加为损失辆数 |
| 独立核对 | Passed | 独立汇总四表和唯一PASS原窗口，与receipt/历史窗口一致；物理FCD安全沿用原审计，不假称重验 |
| 回归保护 | Passed，限调查工具 | 离散周期误差/900不可达反例/拒绝额度/headway/非法输入；数据连续性/初始0/防静默覆盖；没有新TLS/yellow/gap runtime测试，列入下一任务 |

执行成功、测量完整及科学资格不能合并为“全部通过”。

## 4. Issue七项回答

1. FIX02短缺：守恒闭合，纯整数误差不足解释短缺，安全/receiver约束和cap丢弃组合成立；没有推断可恢复因果车辆数。
2. 来源映射：支持/本地推断/边界分列。2008仅摘要层核查，不能写全文完成。
3. A优先：基于phase/service可审计性，不以交通效果筛选，保持Proposed。
4. 300–900：A需T_min≤4n且n实际合格，B需足够gap与可持续≤4s安全headway；数学覆盖不等于actual。
5. 安全：保留nativeCF/lanechange/red/入口/receiver/transition/warning/collision；立即红专用互锁需新安全合同替代审查，不能直接移除或当通用定理。
6. 下一任务：单一A actor、跨灯色ledger、phase/service资格卡；不自动重跑或正式矩阵。
7. Fallback：条件备选未触发；研究对象改变须用户/Robert。

## 5. Findings

未发现未处理的Blocker、Major或必须修改的Minor。

Observation：2008全文未取得。影响是不能据未读全文选timings、capacity或policy优越性；当前报告没有这样归因，不阻塞有界调查交付。PR保留摘要/全文限制；下一任务若需具体timing再补合法全文。保留限制不需新批准，具体timing仍需下一个工程/方法审查。

## 6. 剩余问题与交接

A/B实际服务、相位安全、每cycle真实n、gap预测和变动command runtime未验证。停止本轮调查交用户/Chat审查新DraftPR；不为把调查写成qualified actuator追加仿真。推荐A及相位参数/卡片/资源/正式实验各需后续授权。

主代理可同步报告§9与状态，不能据此改变数据/审查范围。

## 7. 审查快照与后续状态同步

审查者记录的SHA256：
- 主报告：`5fd5f2534db25812906b15c7150a3bce5ad706eac6da7546be10bbe4deb27cfe`
- source ledger：`320d1b2d7d17049a1176b5e3424802bf7178e5a6d1e4931ed4c6faaf3b105452`
- data receipt：`b2e35922f1f804f3d69f0cf934ef711a2710999e64688b38877d40f6b083b810`
- engineering receipt：`50ed331bf96cd33b818f1561e58a7d90bec68692570d1b3af3474406f36f5ff1`

主代理随后仅同步主报告审查结论/精确离线命令及PROJECT_STATE/WORKLOG交接状态；交付现版hash另由DELIVERY_VALIDATION.json记录。无实现、数据或候选范围改变。
