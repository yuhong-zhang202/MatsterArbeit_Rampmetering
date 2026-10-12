# Candidate A：四档技术预算与三个原生信号周期核查

日期：2026-10-12（Europe/Berlin）。本轮用户目标是分别检验5、6、7、8分钟预算，观察首次受控黄转红、几个完整周期及实际放行数量。最新指令“技术问题自行解决然后推进”支持审查通过后顺序执行技术测试；不是正式论文实验或执行器资格认定。

## 范围与设计依据

沿用当前网络、车辆模型、需求M3600/R900/U360/X180veh/h、seed17、1s步长、名义指令300veh/h及G3/y3/r18、24s原生周期。四组的模拟终点统一为1272s，仅技术最大允许时间分别为300/360/420/480s；完成终点即可结束，不为凑满现实时间继续仿真。相同seed的四组不是四个独立随机重复。

原SMOKE04卡片仍保留1207s终止。本轮另建身份与版本，1207s必须核查、保存并fsync检查点，只有当前ACK、相位、核账和监测均明确通过才在同次运行内继续。该时刻日志仅为连续已捕获的provisional证据，关闭进程后的最终EOF绑定仍必须完成。

三个完整周期为[1200,1224)、[1224,1248)、[1248,1272)：各3s绿、3s黄、18s红。首次黄灯1203、红灯1206；其后黄灯1227/1251、红灯1230/1254。1272s前核账三个完整周期，停止在第四次原生转绿事件尚未执行的边界。

旧adapter仍预测红灯后继为self-loop2，而当前XML后继已为0。新版本只纠正这一观察与周期核账缺口；1224/1248步进前可以仍读到原生红灯且nextSwitch等于当前时刻。必须按官方事件顺序预测有效运动信号，随后对实际相位回读核对，不能强制setPhase重置掩盖问题。每次原生自动转绿前重新核查身份、车辆覆盖、内部车道及接收空间；未知或不足即停止，不依靠更长预算继续放行。

[工程设计与源码依据](../../artifacts/candidate_a_native_budget_cycles_20261012_v1/design/TECHNICAL_DESIGN_V1.md)；[设计科学审查](../../artifacts/candidate_a_native_budget_cycles_20261012_v1/design/SCIENTIFIC_DESIGN_REVIEW_V1.md)。设计允许最小实现，尚未代表实现或真实运行通过。

## 放行与安全证据

N定义为R车辆前端从storage进入受控内部lane的唯一ID数，按每一步(t,t+1]、G/y/r和周期分类并全局去重。内部lane长81.98m，大于受检1s推进上限约58.16m；在模型、速度、路线与步长门持续成立时，可防止整个内部lane被一步跳过而漏数。现有E1位于freeway/merge，不是meter停止线计数。

原生FCD每个t标签为运动后的状态，对应ACKt+1；控制期前态用FCDt-1。实际审计必须再次核对ID/lane时序，逐步重建新增内部ID，并与主N账逐车一致。名义C/E可为每周期2、三周期6，实际N不必相同；不以N=6制造通过。不完整或缺测的周期/window分别标partial/unobserved，完全未观测的量保持null。

全部既有制动、碰撞、teleport、红灯过线、身份、模型、接收空间、相位、日志和资源门保留。追加记录实际制动覆盖：速度差检查的before∩after IDs、after加速度IDs及arrived exclusions；已退出车辆末次运动没有同等覆盖，不能宣称全网每车全过程均无异常。父Python CLI输出与四路原生日志的现有范围保持如实披露，兼容性提示不屏蔽。任意安全异常或未知不能被解释为预算不足。

## 执行顺序及验收

先完成新namespace最小实现，离线测试覆盖1207检查点、1224/1248到期原生事件、接收拒绝、1272终止、异常/未知停止及null/partial/实测零；工程→独立数据→科学审查通过并绑定源、卡片与用户目标后，才释放第一组。每组结束后完成工程、独立数据和科学复核，再运行下一预算；保留全部失败和技术修复记录。技术故障须查明后新身份、复审再尝试，禁止盲目重启、放宽安全规则或结果驱动改参数。

每组记录实际启动及总运行耗时、1207检查点、已完成周期、阶段相位、监测覆盖、实际N/FCD对账、输出/日志EOF及退出原因。选择“这次已测最小可完成预算”，不宣称普遍最佳时间、各负载均可靠完成、速率合格或正式sweet spot。

共同资源保留startup60s、output300MB、每次启动和运行中至少free5GB、0.2s采样watchdog；各组独立原始目录不覆盖旧证据。预算不是整个CLI/审查的硬实时上界。旧STOP3、A1UNRESOLVED、CandidateANNOT_QUALIFIED、Stage6结项及0B未冻结正式协议不改变。

## 当前结果

最小实现工程审查完成：[ENGINEERING_REVIEW_V1](../../artifacts/candidate_a_native_budget_cycles_20261012_v1/engineering/ENGINEERING_REVIEW_V1.md)。11项新V3离线测试通过，工程59文件绑定SHA `4fb432812bc954dfe77d01f53d4ec991ebb4d6650ce0bfd35e166a5da587ce4d`。原V1一项接收未知停止时刻的错误预期与失败日志、源码前像保留；V2九项通过的源码为明确披露的重建，不伪称当时已保存哈希；当前V3十一项对应冻结实现与新卡片。

独立数据预审与5项小型测量测试V2通过，14文件绑定SHA `0b00430172b215262896d341733961e513c625c450a89e7e2902b53e166e9311`；[数据预审](../../data/processed/candidate_a_native_budget_cycles_20261012_v1/offline/FINAL_DATA_REVIEW_V1.md)、[只读实际输出核账工具](../../data/processed/candidate_a_native_budget_cycles_20261012_v1/analysis_tools/audit_run.py)。真实--raw审计尚未执行，公共预审通过不代表真实计数已验证。四个身份均未运行，[scientific预启动释放审查](../../artifacts/candidate_a_native_budget_cycles_20261012_v1/PRELAUNCH_SCIENTIFIC_REVIEW_V1.md)通过：PASS_FOR_BOUNDED_THREE_CYCLE_SERIES_PRELAUNCH_ONLY，无阻止首W300运行的必修问题。真实放行/安全/周期/性能未验证，须记录当前提交及单组授权后启动；每组实际核账与科学复审后再下一组。

| 身份后缀 | 最大wall预算 | 卡片SHA-256 |
|---|---:|---|
| CYCLES_W300_01 |300s|25dccfa39d3ff716823f6ce7ceee18eba1c0b8c6393ae464b6db1d2b61c70386|
| CYCLES_W360_01 |360s|1289b33f53f54e2cdf4bcd504fc0774c4c4923c7ae1f9c31d5bf34c9ca848090|
| CYCLES_W420_01 |420s|624f774f5308aa00ff69d42f4436e9ffcc41a462e4cce1b8d0462c051fc799c1|
| CYCLES_W480_01 |480s|3ce1e92e7a21ea4b78aaccbcdaca19136cf67fb917d860a71f820b6de97799b3|

完整ID均以`CA_NATIVE_PHASE_R300_S17_`开头；卡片保存于新engineering/packages对应目录。
