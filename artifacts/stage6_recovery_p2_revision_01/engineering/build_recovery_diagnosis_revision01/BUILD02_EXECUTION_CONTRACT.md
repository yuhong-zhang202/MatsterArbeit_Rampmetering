# BUILD02：启动环境诊断与独立构建契约

状态：待独立审查；本包尚未启动任何新的 netconvert。用户新指令“排查原因，尝试直到成功”授权有根据的后续排查和构建，不能解释为修改科学设计或盲目重复。原 BUILD01、原批准卡和旧回执永久保留。

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

1. 复核旧BUILD01输出/receipt的hash；BUILD02目标目录必须不存在。复核新卡全部bindings，原五个源文件hash一致、离线不变量178项回执仍绑定。
2. 经工具独立的sandbox escalation审核，使用卡中精确wrapper argv和SUMO_HOME启动；wrapper只允许一个BUILD02。在Popen前原子占用BUILD02并fsync reservation。任何claim均消耗，崩溃不自动重跑。
3. 若启动2秒后仍存活，由父代理另行读取started.json并使用记录的PID进行一次 `/usr/bin/sample PID 1 1 -file <BUILD02>/startup.sample.txt`，工具自身最多5秒；执行前确认PID仍是本次netconvert并属于其新进程组。若已完成则跳过。禁止对复用PID或其它应用采样。sample输出必须计入该attempt的目录大小。采样失败只记录，不能启动替代netconvert。watchdog独立运行，不因采样停顿。
4. 30秒仍未完成则停止并保留。stdout、stderr不得过滤。终态后确认进程组无残留；若组存活或身份不确定，停止后续尝试并人工检查，不杀可能复用的PID。
5. 构建成功要求returncode0、该attempt绑定network文件存在且非空、XML根为net，且没有资源/完整性异常。即使达到成功条件，还须独立完成compiled几何/连接/权限/城市TLS/储存/检测器/路线核验；不能把进程成功当作科学通过。不得修改compiled XML。
6. BUILD02成功即停止构建尝试，进入只读编译核验。失败则分析新日志/栈/系统证据；若仍无新证据，报告无法安全推进，不重复同一命令。

## 有限治理

本卡只实现一次BUILD02：netconvert1、retry0、SUMO/TraCI/GUI0。30s和100,000,000B仍是观察触发线，不是硬实时/硬配额；无法给出有限最大超调，失败证据不删除。

建议本轮恢复诊断最多3个新的独立netconvert attempts（BUILD02及最多两个证据驱动后继），合计90个监测预算秒、300,000,000B观察预算；这些是工程治理上限而非必须跑满，也不开放自动循环。每个后继都须新假设、新卡、独立审查，前次完整计账；这不要求重复索取已授权范围内的用户批准。若到上限仍未知、需要改网络/科学参数、增加资源，或权限审核拒绝，停止并向父代理报告具体阻碍。当前仅BUILD02包有可执行定义，BUILD03/04未授权给任何执行器。

## 保留的因果限制

若BUILD02成功，只能支持“原失败与执行环境/短暂启动状态有关”的工程解释；同时加入verbose且时间发生变化，不能把一次成功严格归因于kern.bootargs拒绝。若需要更细根因证据，复用日志和采样，不为了因果洁癖再构建。若仍超时，应依据采样区分加载初始化、配置解析、文件/网络等待或计算，不猜测具体原因。
