# C visual-only FCD replay

状态：仅创建和静态验证；Codex未启动sumo、sumo-gui、TraCI或netconvert。原科学卡5/5已耗尽，不因本包重置。正式协议仍未冻结。

## 用户手动启动

```bash
env SUMO_HOME=/Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/share/sumo /Library/Frameworks/EclipseSUMO.framework/Versions/1.26.0/EclipseSUMO/bin/sumo-gui -c /Users/yuhongzhang/Desktop/Masterarbeit-Ramp-Metering/artifacts/stage6_targeted_validation_20260920_v1/visual_replay/visual.sumocfg
```

该命令启动一个新的SUMO GUI视觉回放进程，默认暂停。点击播放后GUI时钟推进0–2700秒，步长1秒、seed17。它使用既有C的FCD轨迹驱动车辆，不加载原研究需求flows，不重新生成原研究条件下的交通行为，不配置任何科学输出。本机图形显示环境仍须可用；本包未启动GUI验证。

**不是历史state快照，也不是无仿真引擎的播放器。** 原生FCDReplay内部使用libsumo的moveToXY和setSpeed及SUMO时步；其位置/速度强制来自存档，不能用回放重新判断跟驰、让行、容量、碰撞或控制收益。无外部TraCI会话。GUI可能保存自身界面偏好。

**绝不要以原`engineering/inputs/TV_C_S17_attempt1/scenario.sumocfg`启动观察**：原配置和additional引用不可变data/raw输出。也不要给此回放额外加载原demand.rou.xml或vehroute.xml；回放器会从FCD创建车辆，重复输入可能产生重复身份。

## 文件与输入

- `types.rou.xml`：仅technical_passenger的原vType；无flow、vehicle、route。
- `visual.add.xml`：仅原C的WAUT/wautJunction，选中C_STRONG；无检测器、timedEvent或输出文件。
- `visual.sumocfg`：引用原compiled network与原FCD作为只读输入，引用本地两个sidecar；无output节、log、error-log或科学输出选项。
- `source_hash_manifest.json`：源配置、net、FCD、binary、XSD与本包内容的SHA256。
- `static_validation_receipt.json`：本地XML/XSD及安全不变量检查结果；不是运行验收。

C_STRONG为12G/3y/45r、offset0。原network同时保留urban_tls及其他预装meter程序，本sidecar只选择C。没有复制或改写network/FCD；config中的data/raw路径唯一用途是**读取既有FCD**。

## 暂停与时间限制

预设GUI断点：45、46、399、400、402、403、1739、1740、2699。1.26源码中breakpoint B仍执行B步骤再暂停；内部时钟成为B+1，GUI显示减去1，因此显示B。无需加减1。

这个映射只保证GUI显示标签。**FCDReplay初始化与显示帧的位置/时间对齐没有实测。** 首次观察须先单步检查显示0、1，必要时2，与原FCD同ID的lane/pos/speed核对；若不匹配，停止把显示帧解释为精确历史时刻，不自行假定修正偏移。FCD只有1Hz/0.01m格式精度，不能恢复采样之间轨迹。最后记录2699不是2700位置快照；未完成车辆不是已到达。

## 空间定位

在Locate菜单按Edge/Junction/Vehicle ID定位；打开内部edge/junction显示。选中道路后右键Show Parameter核实lane；可启用连接线与ID显示。

- `shared_approach_0`末端约(1001.60,642.80)：城市侧储存参考边界。
- `:urban_diverge_1_0`：113.08m内部连接；其后`ramp_storage_0`为204.49m，合计317.57m仅几何参考。
- `ramp_storage_0`末端约(1220.78,863.61)：meter stopline，ramp_mid信号；节点中心坐标不等于停止线。
- `freeway_merge`：三股入口分别进入不同lane；横向并入发生在`merge_section_0 → merge_section_1`。
- `merge_section`长294.51m；`merge_end`接main_down。

可观察R_flow.71在399–414、R_flow.190/R_flow.191在1739–1741，以及末帧R_flow.252–299。只使用定位、缩放、显示参数、暂停和单步；不要切信号、关闭lane、调车辆速度或Scale Traffic。

## 依据与限制

- https://sumo.dlr.de/docs/Simulation/FCDReplay.html
- https://sumo.dlr.de/docs/sumo-gui.html#breakpoints
- 官方v1_26_0 MSDevice_FCDReplay.cpp只读核查SHA：fe3891ac16ec7112149120edc2d477cb8fa90675ad9fefd58efb4a64ec102048；这是版本标签源代码，不是声称本机binary可复现构建。
- GUIRunThread.cpp的断点处理与GUIApplicationWindow.cpp的updateTimeLCD减去DELTA_T共同支持显示标签换算。

置信度：绑定与静态结构High；实际GUI显示、回放对齐、末帧保留均未测试。本包不更新任何科研结论。父代理负责PROJECT_STATE/WORKLOG的必要事实记录；本目录之外没有文件被本任务修改。
