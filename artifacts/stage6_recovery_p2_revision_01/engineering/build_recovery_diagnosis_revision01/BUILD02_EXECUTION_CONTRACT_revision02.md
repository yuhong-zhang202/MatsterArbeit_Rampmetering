# BUILD02：启动环境诊断与独立构建契约

状态：revision02，修正独立审查要求，待终审；本包尚未启动任何新的 netconvert。用户新指令“排查原因，尝试直到成功”授权有根据的后续排查和构建，不能解释为修改科学设计或盲目重复。原 BUILD01、原批准卡和旧回执永久保留。

## 已证实与未知

BUILD01 的 PID 为21722，2026-09-19 19:32:26.423573 UTC 启动。精确时间窗的系统日志在21:32:26.899947+0200记录 `Sandbox: netconvert(21722) deny(1) sysctl-read kern.bootargs`，约在启动后0.476秒。该记录证明该PID发生了sandbox拒绝；它**不能证明拒绝引起了30秒停滞**。没有留存调用栈、CPU或系统调用跟踪，根因仍Unknown。

二进制为arm64 Mach-O，直接引用的7个非系统动态库均存在且可读并已绑定哈希；不能把静态可读等同于成功动态加载。主二进制无xattr记录；签名描述可以读取，但未声称Gatekeeper完整验证通过。系统库可能来自dyld共享缓存，不能以普通路径不存在判缺库。系统日志最初在sandbox内读取被拒，随后获工具权限后仅导出该PID/二进制对应45秒窗口。

## 最小下一尝试

BUILD02检验“启动sandbox干扰参与了停滞”这一具体假设。保持原二进制及五个输入文件字节、科学网络参数、SUMO_HOME和干净子进程环境不变，通过受支持的 `require_escalated` 工具权限通道启动独立wrapper。不得暗中绕过工具审核；若工具拒绝，本次不启动netconvert，报告权限阻碍。

唯一netconvert argv差异是追加 `--output-file <工程目录>/build_attempts/BUILD02/network.net.xml --verbose true`：前者隔离输出，后者增加诊断信息。原netccfg仍逐字保留，其BUILD01输出项由CLI明确覆盖。SUMO官方参数处理代码显示配置载入后会再次解析命令行；这里没有修改几何、lane、connection、TLS或车辆行为。参考：[OptionsIO官方代码](https://sumo.dlr.de/doxygen/da/d3e/_options_i_o_8cpp_source.html)。该网页为当前文档，不声称它是本机二进制逐字源码。

新wrapper由原绑定 `build01_executor.py` 窄范围复制：BUILD01身份改为BUILD02；绑定argv增加上述两个选项；原config输出项仍核对BUILD01路径以防静默改源。其余reservation、进程组、日志、50ms watchdog、30s触发线、100MB观测停机线及失败保留机制不变。精确差异见 `build01_to_build02_executor.diff`。

## 批准与审查绑定

原revision03卡绝不修改或重用。新卡保留approved=false、authorized_starts=0；父代理在本次独立审查通过后，可依据用户持续授权创建专属BUILD02 sidecar，填入本卡SHA、BUILD02 scope和原文“排查原因，尝试直到成功”。必须明确这是**持续授权下的具体工程实现**，不是声称用户逐字确认了后来生成的SHA。将科学审查结果、来源与hash写入sidecar附加provenance。未创建sidecar，或输入/binary/script/hash发生变化则fail closed。

## 顺序和停止门

1. BUILD01目录必须保留，复核其全部输出与receipt哈希；其中build_receipt.json SHA必须仍为902956e03e04e516da3e43725205d220fa8a4b6249572782339e4c728ee7e7f3。BUILD02目标目录必须不存在。复核新卡全部bindings，原五个源文件hash一致、离线不变量178项回执仍绑定。
2. 经工具独立的sandbox escalation审核，使用卡中精确wrapper argv和SUMO_HOME启动；wrapper只允许一个BUILD02。在Popen前原子占用BUILD02并fsync reservation。任何claim均消耗，崩溃不自动重跑。
3. 若启动2秒后仍存活，由父代理另行读取started.json并使用记录的PID进行一次 `/usr/bin/sample PID 1 1 -file <BUILD02>/startup.sample.txt`，工具自身最多5秒；执行前确认PID仍是本次netconvert并属于其新进程组。若已完成则跳过。禁止对复用PID或其它应用采样。sample输出必须计入该attempt的目录大小。采样由独立进程组运行，记录其PID、启动/结束时间、退出码、stdout/stderr；等待最多5秒，超时先TERM等最多1秒、再KILL等最多1秒并确认退出。采样失败只记录，不能启动替代netconvert。watchdog独立运行，不因采样停顿。
4. 30秒仍未完成则停止并保留。stdout、stderr不得过滤。终态后确认进程组无残留；若组存活或身份不确定，停止后续尝试并人工检查，不杀可能复用的PID。
5. **收尾屏障：** wrapper退出后，不得立即宣布最终字节数/哈希封存。先等待上述sample进程终态或确认超时终止；若未启动则显式记skip。确认netconvert与sample均已停止写入后，重新遍历全部attempt文件（含sample、其日志、wrapper receipt）计算准确字节数和每文件SHA，写独立closeout。原build_receipt不可改写；其字节快照只是wrapper时点值，最终统计以sample结束后的closeout为准。若最终完整目录超过100,000,000B，closeout必须记录资源失败，不能沿用wrapper成功状态；若sample无法确认终止，closeout为terminal_unknown且停止后续工作。closeout自身/manifest也计入最终目录统计，采用最后一次全目录复算记录，保留超量证据。
6. 构建成功要求returncode0、该attempt绑定network文件存在且非空、XML根为net，且没有资源/完整性异常。即使达到成功条件，还须独立完成compiled几何/连接/权限/城市TLS/储存/检测器/路线核验；不能把进程成功当作科学通过。不得修改compiled XML。
7. BUILD02成功即停止构建尝试，进入只读编译核验。失败则分析新日志/栈/系统证据；若仍无新证据，报告无法安全推进，不重复同一命令。

## 有限治理

本卡只实现一次BUILD02：netconvert1、retry0、SUMO/TraCI/GUI0。30s和100,000,000B仍是观察触发线，不是硬实时/硬配额；无法给出有限最大超调，失败证据不删除。

用户授权是持续的“排查原因，尝试直到成功”，不能把任意三次当作该授权终点。有限资源治理落实到**每个独立attempt**：本卡仅BUILD02一次、30秒观察超时、100,000,000B观察停机线；每次结束都先核账再决定下一步。此卡不开放自动循环或未定义的后继启动。失败后若有新证据和具体区分性假设，可在同一持续授权下制定新的隔离卡、独立审查、预算和claim，再由父代理执行，无需重复向用户索取相同范围的授权。维护跨attempt累计次数、实测时间和字节账，不能把历史消耗清零。若无新证据、需要改变科学网络/参数，或权限/资源控制不能成立，停止并报告具体阻碍；不是盲目运行到某个次数，也不通过自动增加timeout规避未知根因。

## 保留的因果限制

若BUILD02成功，只能支持“原失败与执行环境/短暂启动状态有关”的工程解释；同时加入verbose且时间发生变化，不能把一次成功严格归因于kern.bootargs拒绝。若需要更细根因证据，复用日志和采样，不为了因果洁癖再构建。若仍超时，应依据采样区分加载初始化、配置解析、文件/网络等待或计算，不猜测具体原因。
