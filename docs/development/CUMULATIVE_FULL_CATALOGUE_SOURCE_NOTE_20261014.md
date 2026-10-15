# 累计放行技术诊断：官方资料及适用边界

2026-10-14。此资料核查服务于执行器技术调查，不更改正式研究设计、车辆模型、相位、安全检查或验收条件。

## SUMO 信号接口

SUMO 官方 [Traffic Lights](https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html) 与 [TraCI Change Traffic Lights State](https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html) 说明：外部控制可通过 `setPhase` 切换已定义相位，由信号程序执行后续黄灯／红灯；`setPhaseDuration` 修改的是当前相位剩余时长，不是以后周期的永久参数；`setProgram` 切换程序时不会自动重置相位索引。

这支持复用现有程序、明确控制切换并回读实际状态的技术路线，也解释了为什么仅记录所发指令不足以证明实际 G→y→r 连续执行。本项目继续逐步核对 TLS、ACK、转相时刻和实际车辆，不从“接口受支持”推出安全。

以上为访问时的在线文档，不是固定 SUMO 1.26 二进制证明。版本特有行为仍以项目已有的 1.26 源码、环境绑定及实际日志为准；没有重新声称安装二进制与官方源码编译等价。

## 放行率与每周期车辆数

FHWA [Ramp Management and Control Handbook, Chapter 10](https://ops.fhwa.dot.gov/publications/ramp_mgmt_handbook/manual/manual/10_1.htm) 将单车放行和每绿灯两／三车的成组放行区分，并给出不同方式的实际容量讨论。其单车示例中900 veh/h对应4秒周期，示例为红2.5秒、绿1.5秒；这是该手册情境中的说明。

该例没有包含当前项目相同的 G/y/r 最小时长、车辆动力学和保守检查，因此**不能直接移植其配时、容量或将两车名义值当作当前实测能力**。本项目请求积分C、完整周期计划E、独立实测N必须分开；完整包欠放时不能靠继续累计追债假装跟上请求。

## 本轮使用范围

此次资料只支持明确的接口操作和容量核账思路。完整 T8…24 目录与 T10 例外来自已存在且可追溯的项目实现；新的750运行检验该目录下的真实混合轨迹。资料没有证明新轨迹安全、保证N=2或授权正式实验，也没有据此增加新配时或放宽门槛。
