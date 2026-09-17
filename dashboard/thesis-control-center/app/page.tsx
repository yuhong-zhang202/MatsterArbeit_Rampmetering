"use client";

import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";
import initialDashboardData from "../data/thesis-dashboard.json";

type TaskStatus = "todo" | "doing" | "blocked" | "done";
type BoardStatus = "todo" | "doing" | "done";
type Priority = "high" | "medium" | "low";
type ReferenceStatus = "todo" | "reading" | "using" | "done";

type Chapter = { id: string; number: string; title: string; subtitle: string; goal: string; sections: string[]; status: string };
type Task = { id: string; chapterId: string; title: string; status: TaskStatus; priority: Priority; type: string; due: string; subtasks?: string[]; boardOrder?: number; referenceId?: string };
type Reference = { id: string; key: string; authors: string; year: string; title: string; status: ReferenceStatus; chapterIds: string[]; url: string; note: string; taskId?: string };
type Feedback = { id: string; date: string; author: string; summary: string; action: string; status: string; chapterIds: string[]; source: string };
type Experiment = { id: string; code: string; rq: string; title: string; status: string; next: string; taskIds: string[] };
type Decision = { id: string; date: string; title: string; detail: string; status: string };
type DashboardData = {
  meta: {
    title: string; degree: string; currentPhase: string; updatedAt: string;
    nextMilestone: string; researchQuestion: string; supervisors: { name: string; role: string }[];
  };
  chapters: Chapter[]; tasks: Task[]; references: Reference[]; feedback: Feedback[];
  experiments: Experiment[]; decisions: Decision[]; pendingConfirmations: { id: string; title: string }[];
};
type View = "overview" | "structure" | "tasks" | "references" | "feedback" | "experiments";
type LocalFileHandle = {
  getFile: () => Promise<File>;
  createWritable: () => Promise<{ write: (data: string) => Promise<void>; close: () => Promise<void> }>;
  queryPermission?: (options?: { mode: "readwrite" }) => Promise<PermissionState>;
  requestPermission?: (options?: { mode: "readwrite" }) => Promise<PermissionState>;
};

const views: { id: View; label: string; short: string }[] = [
  { id: "overview", label: "总览", short: "总" },
  { id: "structure", label: "论文结构", short: "章" },
  { id: "tasks", label: "任务", short: "任" },
  { id: "references", label: "参考文献", short: "文" },
  { id: "feedback", label: "导师意见", short: "师" },
  { id: "experiments", label: "实验与数据", short: "实" },
];
const statusLabel: Record<string, string> = {
  todo: "待开始", doing: "进行中", blocked: "待确认", done: "已完成", open: "待处理",
  accepted: "已采纳", confirmed: "已确认", reading: "阅读中", using: "使用中",
};
const priorityLabel: Record<Priority, string> = { high: "高", medium: "中", low: "低" };
const boardColumns: { status: BoardStatus; title: string; note: string }[] = [
  { status: "todo", title: "待开始", note: "尚未进入当前工作" },
  { status: "doing", title: "进行中", note: "现在正在推进" },
  { status: "done", title: "已完成", note: "保留完成记录" },
];
const boardStatusOf = (task: Task): BoardStatus => task.status === "blocked" ? "todo" : task.status;
const referenceStatusFromTask = (status: TaskStatus): ReferenceStatus => status === "done" ? "done" : status === "doing" ? "reading" : "todo";
const taskStatusFromReference = (status: ReferenceStatus): TaskStatus => status === "done" ? "done" : status === "reading" || status === "using" ? "doing" : "todo";
const normalizedLiteratureTitle = (title: string) => title.toLocaleLowerCase().replace(/^阅读文献[：:]\s*/, "").replace(/^阅读\s*/, "").replace(/[。.]$/, "").trim();
const priorityRank: Record<Priority, number> = { high: 0, medium: 1, low: 2 };
const sortBoardTasks = (tasks: Task[]) => {
  const hasManualOrder = tasks.some((task) => Number.isFinite(task.boardOrder));
  return [...tasks].sort((left, right) => {
    if (hasManualOrder) {
      const orderDifference = (left.boardOrder ?? Number.MAX_SAFE_INTEGER) - (right.boardOrder ?? Number.MAX_SAFE_INTEGER);
      if (orderDifference !== 0) return orderDifference;
    }
    return priorityRank[left.priority] - priorityRank[right.priority];
  });
};
const formatDate = () => new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium" }).format(new Date());
const makeId = (prefix: string) => `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

function localHandleDb() {
  return new Promise<IDBDatabase>((resolve, reject) => {
    const request = indexedDB.open("thesis-control-center", 1);
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains("settings")) request.result.createObjectStore("settings");
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
async function rememberHandle(handle: LocalFileHandle) {
  const db = await localHandleDb();
  await new Promise<void>((resolve, reject) => {
    const transaction = db.transaction("settings", "readwrite");
    transaction.objectStore("settings").put(handle, "dashboard-file");
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
  db.close();
}
async function recalledHandle() {
  const db = await localHandleDb();
  const handle = await new Promise<LocalFileHandle | undefined>((resolve, reject) => {
    const request = db.transaction("settings", "readonly").objectStore("settings").get("dashboard-file");
    request.onsuccess = () => resolve(request.result as LocalFileHandle | undefined);
    request.onerror = () => reject(request.error);
  });
  db.close();
  return handle;
}

function StatusPill({ status }: { status: string }) {
  return <span className={`status status-${status}`}>{statusLabel[status] ?? status}</span>;
}
function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  return <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
    <section className="modal" role="dialog" aria-modal="true" aria-label={title} onMouseDown={(event) => event.stopPropagation()}>
      <header className="modal-header"><div><p className="eyebrow">论文研究控制台</p><h2>{title}</h2></div><button className="icon-button" onClick={onClose} aria-label="关闭">×</button></header>
      {children}
    </section>
  </div>;
}

export default function Home() {
  const [data, setData] = useState<DashboardData>(initialDashboardData as DashboardData);
  const [view, setView] = useState<View>("overview");
  const [fileHandle, setFileHandle] = useState<LocalFileHandle | null>(null);
  const [fileState, setFileState] = useState<"unlinked" | "linked" | "saving" | "saved" | "error">("unlinked");
  const [modal, setModal] = useState<"task" | "reference" | "feedback" | null>(null);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const activeTasks = data.tasks.filter((task) => task.status === "doing");
  const blockedTasks = data.tasks.filter((task) => task.status === "blocked");
  const openTasks = data.tasks.filter((task) => task.status !== "done");

  const writeFile = async (nextData: DashboardData, handle = fileHandle) => {
    if (!handle) return;
    setFileState("saving");
    try {
      const writable = await handle.createWritable();
      await writable.write(`${JSON.stringify(nextData, null, 2)}\n`);
      await writable.close();
      setFileState("saved");
    } catch { setFileState("error"); }
  };
  const updateData = (updater: (current: DashboardData) => DashboardData) => {
    setData((current) => {
      const next = updater(current);
      next.meta.updatedAt = formatDate();
      if (saveTimer.current) clearTimeout(saveTimer.current);
      if (fileHandle) saveTimer.current = setTimeout(() => void writeFile(next), 280);
      return next;
    });
  };
  const loadFromHandle = async (handle: LocalFileHandle, askPermission = false) => {
    try {
      let permission = handle.queryPermission ? await handle.queryPermission({ mode: "readwrite" }) : "granted";
      if (permission !== "granted" && askPermission && handle.requestPermission) permission = await handle.requestPermission({ mode: "readwrite" });
      if (permission !== "granted") return;
      const file = await handle.getFile();
      setData(JSON.parse(await file.text()) as DashboardData);
      setFileHandle(handle);
      setFileState("linked");
      await rememberHandle(handle);
    } catch { setFileState("error"); }
  };
  useEffect(() => {
    void recalledHandle().then((handle) => { if (handle) void loadFromHandle(handle, false); }).catch(() => undefined);
  }, []);
  const openDataFile = async () => {
    const picker = (window as unknown as { showOpenFilePicker?: (options: object) => Promise<LocalFileHandle[]> }).showOpenFilePicker;
    if (!picker) { alert("请使用最新版 Chrome 或 Edge 连接本地 JSON。你仍然可以导出 JSON 备份。"); return; }
    try {
      const [handle] = await picker({ multiple: false, types: [{ description: "论文控制台数据", accept: { "application/json": [".json"] } }] });
      await loadFromHandle(handle, true);
    } catch { /* The user cancelled the picker. */ }
  };
  const createDataFile = async () => {
    const picker = (window as unknown as { showSaveFilePicker?: (options: object) => Promise<LocalFileHandle> }).showSaveFilePicker;
    if (!picker) { downloadBackup(); return; }
    try {
      const handle = await picker({ suggestedName: "thesis-dashboard.json", types: [{ description: "论文控制台数据", accept: { "application/json": [".json"] } }] });
      setFileHandle(handle); await rememberHandle(handle); await writeFile(data, handle); setFileState("linked");
    } catch { /* The user cancelled the picker. */ }
  };
  const reloadFile = async () => { if (fileHandle) await loadFromHandle(fileHandle, true); };
  const downloadBackup = () => {
    const blob = new Blob([`${JSON.stringify(data, null, 2)}\n`], { type: "application/json" });
    const url = URL.createObjectURL(blob); const anchor = document.createElement("a");
    anchor.href = url; anchor.download = `thesis-dashboard-${new Date().toISOString().slice(0, 10)}.json`; anchor.click(); URL.revokeObjectURL(url);
  };
  const addTask = (task: Task) => updateData((current) => {
    if (task.type !== "literature") return { ...current, tasks: [...current.tasks, task] };
    const existingReference = current.references.find((reference) => !reference.taskId && normalizedLiteratureTitle(reference.title) === normalizedLiteratureTitle(task.title));
    if (existingReference) {
      const linkedTask = { ...task, referenceId: existingReference.id };
      return {
        ...current,
        tasks: [...current.tasks, linkedTask],
        references: current.references.map((reference) => reference.id === existingReference.id
          ? { ...reference, taskId: task.id, status: referenceStatusFromTask(task.status) }
          : reference),
      };
    }
    const referenceId = makeId("ref");
    return {
      ...current,
      tasks: [...current.tasks, { ...task, referenceId }],
      references: [...current.references, {
        id: referenceId,
        taskId: task.id,
        key: `TaskRef-${task.id.slice(-5)}`,
        authors: "",
        year: "",
        title: task.title,
        status: referenceStatusFromTask(task.status),
        chapterIds: task.chapterId ? [task.chapterId] : [],
        url: "",
        note: "由任务看板同步创建；书目信息待补充。",
      }],
    };
  });
  const addReference = (reference: Reference) => updateData((current) => {
    const existingTask = current.tasks.find((task) => task.type === "literature" && !task.referenceId && normalizedLiteratureTitle(task.title) === normalizedLiteratureTitle(reference.title));
    if (existingTask) {
      const linkedReference = { ...reference, taskId: existingTask.id };
      return {
        ...current,
        references: [...current.references, linkedReference],
        tasks: current.tasks.map((task) => task.id === existingTask.id
          ? { ...task, referenceId: reference.id, status: taskStatusFromReference(reference.status) }
          : task),
      };
    }
    const taskId = makeId("task");
    return {
      ...current,
      references: [...current.references, { ...reference, taskId }],
      tasks: [...current.tasks, {
        id: taskId,
        referenceId: reference.id,
        chapterId: reference.chapterIds[0] ?? "",
        title: reference.title,
        status: taskStatusFromReference(reference.status),
        priority: "medium",
        type: "literature",
        due: "",
      }],
    };
  });
  const setReferenceStatus = (referenceId: string, status: ReferenceStatus) => updateData((current) => {
    const reference = current.references.find((item) => item.id === referenceId);
    if (!reference) return current;
    return {
      ...current,
      references: current.references.map((item) => item.id === referenceId ? { ...item, status } : item),
      tasks: current.tasks.map((task) => task.id === reference.taskId || task.referenceId === referenceId
        ? { ...task, status: taskStatusFromReference(status) }
        : task),
    };
  });
  const updateTask = (updatedTask: Task) => updateData((current) => {
    const previousTask = current.tasks.find((task) => task.id === updatedTask.id);
    if (!previousTask) return current;
    if (previousTask.referenceId) {
      const linkedTask = { ...updatedTask, type: "literature", referenceId: previousTask.referenceId };
      return {
        ...current,
        tasks: current.tasks.map((task) => task.id === linkedTask.id ? linkedTask : task),
        references: current.references.map((reference) => reference.id === previousTask.referenceId
          ? { ...reference, title: linkedTask.title, status: referenceStatusFromTask(linkedTask.status), chapterIds: linkedTask.chapterId ? [linkedTask.chapterId] : [] }
          : reference),
      };
    }
    if (updatedTask.type !== "literature") {
      return { ...current, tasks: current.tasks.map((task) => task.id === updatedTask.id ? updatedTask : task) };
    }
    const referenceId = makeId("ref");
    return {
      ...current,
      tasks: current.tasks.map((task) => task.id === updatedTask.id ? { ...updatedTask, referenceId } : task),
      references: [...current.references, {
        id: referenceId,
        taskId: updatedTask.id,
        key: `TaskRef-${updatedTask.id.slice(-5)}`,
        authors: "",
        year: "",
        title: updatedTask.title,
        status: referenceStatusFromTask(updatedTask.status),
        chapterIds: updatedTask.chapterId ? [updatedTask.chapterId] : [],
        url: "",
        note: "由任务看板同步创建；书目信息待补充。",
      }],
    };
  });
  const deleteTask = (task: Task) => updateData((current) => ({
    ...current,
    tasks: current.tasks.filter((item) => item.id !== task.id),
    references: task.referenceId ? current.references.filter((reference) => reference.id !== task.referenceId) : current.references,
    experiments: current.experiments.map((experiment) => ({ ...experiment, taskIds: experiment.taskIds.filter((taskId) => taskId !== task.id) })),
  }));
  const reorderTask = (taskId: string, targetStatus: BoardStatus, targetTaskId: string | null, placement: "before" | "after" | "end") => updateData((current) => {
    const draggedTask = current.tasks.find((task) => task.id === taskId);
    if (!draggedTask) return current;
    const sourceStatus = boardStatusOf(draggedTask);
    const sourceLane = sortBoardTasks(current.tasks.filter((task) => task.id !== taskId && boardStatusOf(task) === sourceStatus));
    const targetLane = sourceStatus === targetStatus
      ? sourceLane
      : sortBoardTasks(current.tasks.filter((task) => task.id !== taskId && boardStatusOf(task) === targetStatus));
    let insertionIndex = targetLane.length;
    if (targetTaskId) {
      const targetIndex = targetLane.findIndex((task) => task.id === targetTaskId);
      if (targetIndex >= 0) insertionIndex = targetIndex + (placement === "after" ? 1 : 0);
    }
    targetLane.splice(insertionIndex, 0, { ...draggedTask, status: targetStatus });
    const nextOrder = new Map<string, number>();
    if (sourceStatus !== targetStatus) sourceLane.forEach((task, index) => nextOrder.set(task.id, index));
    targetLane.forEach((task, index) => nextOrder.set(task.id, index));
    const tasks = current.tasks.map((task) => task.id === taskId
      ? { ...task, status: targetStatus, boardOrder: nextOrder.get(task.id) }
      : nextOrder.has(task.id) ? { ...task, boardOrder: nextOrder.get(task.id) } : task);
    return {
      ...current,
      tasks,
      references: draggedTask.referenceId ? current.references.map((reference) => reference.id === draggedTask.referenceId
        ? { ...reference, status: referenceStatusFromTask(targetStatus) }
        : reference) : current.references,
    };
  });
  const chapterName = (chapterId: string) => data.chapters.find((chapter) => chapter.id === chapterId)?.title ?? "未分配";

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">S</span><div><strong>Sweet Spot</strong><span>论文研究控制台</span></div></div>
      <nav className="nav-list" aria-label="主导航">
        {views.map((item) => <button key={item.id} className={view === item.id ? "nav-item active" : "nav-item"} onClick={() => setView(item.id)}>
          <span className="nav-glyph">{item.short}</span>{item.label}
          {item.id === "tasks" && <em>{openTasks.length}</em>}
          {item.id === "feedback" && <em>{data.feedback.filter((entry) => entry.status === "open").length}</em>}
        </button>)}
      </nav>
      <div className="sidebar-foot"><div className="phase-summary"><span>当前阶段</span><strong>{data.meta.currentPhase}</strong></div><p>以阶段状态为准，不按初步章节 Todo 计算完成率。</p></div>
    </aside>

    <section className="workspace">
      <header className="topbar">
        <div><p className="eyebrow">TU Berlin · Masterarbeit</p><h1>{data.meta.title}</h1></div>
        <div className="top-actions">
          <div className={`file-indicator file-${fileState}`}><span />{fileHandle ? (fileState === "saving" ? "正在保存" : fileState === "error" ? "保存失败" : "已连接本地数据") : "尚未连接数据文件"}</div>
          {fileHandle ? <button className="button secondary" onClick={reloadFile}>从文件重载</button> : <button className="button secondary" onClick={openDataFile}>连接数据文件</button>}
          <button className="button ghost" onClick={fileHandle ? () => void writeFile(data) : createDataFile}>{fileHandle ? "立即保存" : "新建数据文件"}</button>
        </div>
      </header>
      {!fileHandle && <div className="connect-banner"><div className="connect-icon">↔</div><div><strong>连接同一份 JSON，网页和 AI 才能同步更新</strong><p>选择项目中的 <code>data/thesis-dashboard.json</code>。网页编辑会自动写回，Codex 修改后点击“从文件重载”即可看到变化。</p></div><button className="button primary" onClick={openDataFile}>现在连接</button></div>}
      {view === "overview" && <Overview data={data} activeTasks={activeTasks} blockedTasks={blockedTasks} onOpenChapter={(chapterId) => { setSelectedChapter(chapterId); setView("structure"); }} onNavigate={setView} />}
      {view === "structure" && <StructureView data={data} selectedChapter={selectedChapter} setSelectedChapter={setSelectedChapter} updateData={updateData} />}
      {view === "tasks" && <TasksView data={data} search={search} setSearch={setSearch} chapterName={chapterName} onReorder={reorderTask} onAdd={() => { setEditingTask(null); setModal("task"); }} onEdit={(task) => { setEditingTask(task); setModal("task"); }} onDelete={setTaskToDelete} />}
      {view === "references" && <ReferencesView data={data} chapterName={chapterName} onAdd={() => setModal("reference")} onStatus={setReferenceStatus} />}
      {view === "feedback" && <FeedbackView data={data} chapterName={chapterName} onAdd={() => setModal("feedback")} />}
      {view === "experiments" && <ExperimentsView data={data} />}
    </section>

    {modal === "task" && <TaskModal chapters={data.chapters} initialTask={editingTask} onClose={() => { setModal(null); setEditingTask(null); }} onSave={(task) => { if (editingTask) updateTask(task); else addTask(task); setModal(null); setEditingTask(null); }} />}
    {modal === "reference" && <ReferenceModal chapters={data.chapters} onClose={() => setModal(null)} onSave={(reference) => { addReference(reference); setModal(null); }} />}
    {modal === "feedback" && <FeedbackModal chapters={data.chapters} onClose={() => setModal(null)} onSave={(feedback) => { updateData((current) => ({ ...current, feedback: [feedback, ...current.feedback] })); setModal(null); }} />}
    {taskToDelete && <DeleteTaskModal task={taskToDelete} onClose={() => setTaskToDelete(null)} onConfirm={() => { deleteTask(taskToDelete); setTaskToDelete(null); }} />}
  </main>;
}

function Overview({ data, activeTasks, blockedTasks, onOpenChapter, onNavigate }: {
  data: DashboardData; activeTasks: Task[]; blockedTasks: Task[];
  onOpenChapter: (id: string) => void; onNavigate: (view: View) => void;
}) {
  return <div className="view-content">
    <section className="overview-hero"><div className="phase-marker" aria-hidden="true">准备</div><div className="hero-progress"><div><p className="eyebrow">当前阶段</p><h2>{data.meta.currentPhase}</h2><p>当前推进项目自建场景与探索性无控制基线；正式研究范围和实验协议仍待确认。</p></div></div><div className="milestone-card"><span>当前里程碑</span><strong>{data.meta.nextMilestone}</strong><small>最后更新 · {data.meta.updatedAt}</small></div></section>
    <section className="metric-grid">
      <button className="metric-card" onClick={() => onNavigate("structure")}><span>初步章节</span><strong>{data.chapters.length}</strong><small>全部尚未确认</small></button>
      <button className="metric-card" onClick={() => onNavigate("tasks")}><span>未完成任务</span><strong>{data.tasks.filter((task) => task.status !== "done").length}</strong><small>{activeTasks.length} 项进行中 · 已完成不计入</small></button>
      <button className="metric-card" onClick={() => onNavigate("references")}><span>参考文献</span><strong>{data.references.length}</strong><small>{data.references.filter((ref) => ref.status === "reading").length} 篇阅读中</small></button>
      <button className="metric-card warning" onClick={() => onNavigate("feedback")}><span>等待确认</span><strong>{data.pendingConfirmations.length}</strong><small>暂不转化为执行任务</small></button>
    </section>
    <section className="dashboard-grid">
      <article className="panel chapters-panel"><header className="panel-header"><div><p className="eyebrow">Thesis outline</p><h2>初步章节结构</h2></div><button className="text-button" onClick={() => onNavigate("structure")}>查看完整结构 →</button></header>
        <div className="chapter-list">{data.chapters.map((chapter) => <button className="chapter-row" key={chapter.id} onClick={() => onOpenChapter(chapter.id)}><span className="chapter-number">{chapter.number}</span><span className="chapter-name"><strong>{chapter.title}</strong><small>{chapter.subtitle}</small></span><span className="provisional-label">{chapter.status}</span></button>)}</div>
      </article>
      <div className="right-stack">
        <article className="panel focus-panel"><header className="panel-header"><div><p className="eyebrow">Now</p><h2>当前执行</h2></div></header>{activeTasks.map((task) => <div className="focus-task" key={task.id}><div><strong>{task.title}</strong><StatusPill status={task.status} /></div><ol>{task.subtasks?.map((subtask) => <li key={subtask}>{subtask}</li>)}</ol></div>)}</article>
        <article className="panel decision-panel"><header className="panel-header"><div><p className="eyebrow">Pending confirmation</p><h2>等待确认</h2></div></header><div className="waiting-task"><strong>{blockedTasks[0]?.title}</strong><StatusPill status="blocked" /></div><ul className="confirmation-list">{data.pendingConfirmations.map((item) => <li key={item.id}>{item.title}</li>)}</ul></article>
      </div>
    </section>
  </div>;
}

function StructureView({ data, selectedChapter, setSelectedChapter, updateData }: {
  data: DashboardData; selectedChapter: string | null; setSelectedChapter: (id: string | null) => void;
  updateData: (updater: (current: DashboardData) => DashboardData) => void;
}) {
  const selected = data.chapters.find((chapter) => chapter.id === selectedChapter) ?? null;
  const [newSection, setNewSection] = useState("");
  const updateChapter = (chapterId: string, patch: Partial<Chapter>) => updateData((current) => ({ ...current, chapters: current.chapters.map((chapter) => chapter.id === chapterId ? { ...chapter, ...patch } : chapter) }));
  return <div className="view-content">
    <header className="view-header"><div><p className="eyebrow">Thesis outline</p><h2>论文结构</h2><p>七章仅作为初步导航，不生成 Todo，也不参与完成率计算。</p></div></header>
    <section className="outline-grid">{data.chapters.map((chapter) => <button className="outline-card" key={chapter.id} onClick={() => setSelectedChapter(chapter.id)}><div className="outline-top"><span>{chapter.number}</span><b className="provisional-label">{chapter.status}</b></div><h3>{chapter.title}</h3><small>{chapter.subtitle}</small><p>{chapter.goal}</p><div className="section-preview">{chapter.sections.slice(0, 3).map((section) => <span key={section}>{section}</span>)}</div></button>)}</section>
    {selected && <div className="drawer-backdrop" onMouseDown={() => setSelectedChapter(null)}><aside className="drawer" onMouseDown={(event) => event.stopPropagation()}><header className="drawer-header"><span className="chapter-number large">{selected.number}</span><div><p className="eyebrow">章节详情</p><h2>{selected.title}</h2></div><button className="icon-button" onClick={() => setSelectedChapter(null)}>×</button></header><div className="drawer-content">
      <label className="field"><span>章节标题</span><input value={selected.title} onChange={(event) => updateChapter(selected.id, { title: event.target.value })} /></label>
      <label className="field"><span>英文副标题</span><input value={selected.subtitle} onChange={(event) => updateChapter(selected.id, { subtitle: event.target.value })} /></label>
      <label className="field"><span>本章目标</span><textarea rows={3} value={selected.goal} onChange={(event) => updateChapter(selected.id, { goal: event.target.value })} /></label>
      <section className="drawer-section"><div className="drawer-section-title"><h3>小节结构</h3><span>{selected.sections.length} 节</span></div><div className="editable-sections">{selected.sections.map((section, index) => <div key={`${selected.id}-${index}`}><span>{selected.number}.{index + 1}</span><input value={section} onChange={(event) => { const sections = [...selected.sections]; sections[index] = event.target.value; updateChapter(selected.id, { sections }); }} /><button onClick={() => updateChapter(selected.id, { sections: selected.sections.filter((_, itemIndex) => itemIndex !== index) })} aria-label="删除小节">×</button></div>)}<form onSubmit={(event) => { event.preventDefault(); if (!newSection.trim()) return; updateChapter(selected.id, { sections: [...selected.sections, newSection.trim()] }); setNewSection(""); }} className="add-section"><input placeholder="添加新小节" value={newSection} onChange={(event) => setNewSection(event.target.value)} /><button className="button secondary">添加</button></form></div></section>
      <section className="drawer-section provisional-note"><strong>{selected.status}</strong><p>本章不自动生成任务；正式结构需等待 Robert 确认。</p></section>
      <section className="drawer-section related-counts"><div><strong>{data.references.filter((ref) => ref.chapterIds.includes(selected.id)).length}</strong><span>相关文献</span></div><div><strong>{data.feedback.filter((entry) => entry.chapterIds.includes(selected.id)).length}</strong><span>导师意见</span></div><div><strong>{data.experiments.filter((experiment) => experiment.taskIds.some((taskId) => data.tasks.find((task) => task.id === taskId)?.chapterId === selected.id)).length}</strong><span>关联实验</span></div></section>
    </div></aside></div>}
  </div>;
}

function TasksView({ data, search, setSearch, chapterName, onReorder, onAdd, onEdit, onDelete }: {
  data: DashboardData; search: string; setSearch: (value: string) => void;
  chapterName: (id: string) => string;
  onReorder: (taskId: string, status: BoardStatus, targetTaskId: string | null, placement: "before" | "after" | "end") => void;
  onAdd: () => void; onEdit: (task: Task) => void; onDelete: (task: Task) => void;
}) {
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [dropTarget, setDropTarget] = useState<{ status: BoardStatus; taskId: string | null; placement: "before" | "after" | "end" } | null>(null);
  const filtered = data.tasks.filter((task) => task.title.toLowerCase().includes(search.toLowerCase()));
  const moveTask = (taskId: string, status: BoardStatus) => {
    onReorder(taskId, status, null, "end");
    setDraggedTaskId(null);
    setDropTarget(null);
  };
  useEffect(() => {
    if (!draggedTaskId) return;
    const targetAt = (x: number, y: number) => {
      const element = document.elementFromPoint(x, y);
      const status = element?.closest<HTMLElement>(".kanban-column")?.dataset.status as BoardStatus | undefined;
      if (!status) return null;
      const card = element?.closest<HTMLElement>(".kanban-card");
      if (!card || card.dataset.taskId === draggedTaskId) return { status, taskId: null, placement: "end" as const };
      const bounds = card.getBoundingClientRect();
      return { status, taskId: card.dataset.taskId ?? null, placement: y < bounds.top + bounds.height / 2 ? "before" as const : "after" as const };
    };
    const handlePointerMove = (event: PointerEvent) => setDropTarget(targetAt(event.clientX, event.clientY));
    const handlePointerUp = (event: PointerEvent) => {
      const target = targetAt(event.clientX, event.clientY);
      if (target) onReorder(draggedTaskId, target.status, target.taskId, target.placement);
      setDraggedTaskId(null);
      setDropTarget(null);
    };
    document.addEventListener("pointermove", handlePointerMove);
    document.addEventListener("pointerup", handlePointerUp, { once: true });
    return () => {
      document.removeEventListener("pointermove", handlePointerMove);
      document.removeEventListener("pointerup", handlePointerUp);
    };
  }, [draggedTaskId, onReorder]);
  return <div className="view-content"><header className="view-header actions-header"><div><p className="eyebrow">Task board</p><h2>任务看板</h2><p>默认按优先级排列；拖动卡片可调整列内顺序或切换状态。</p></div><button className="button primary" onClick={onAdd}>＋ 添加任务</button></header>
    <div className="kanban-toolbar"><div><span className="board-dot" />共 {data.tasks.filter((task) => task.status !== "done").length} 项未完成任务 <small>已完成不计入 · 高 → 中 → 低 · 拖动后保存自定义顺序</small></div><input className="search-input" placeholder="搜索任务…" value={search} onChange={(event) => setSearch(event.target.value)} /></div>
    <section className="kanban-board" aria-label="任务状态看板">
      {boardColumns.map((column, columnIndex) => {
        const tasks = sortBoardTasks(filtered.filter((task) => boardStatusOf(task) === column.status));
        return <section
          className={`kanban-column kanban-${column.status}${dropTarget?.status === column.status ? " is-drag-over" : ""}`}
          data-status={column.status}
          key={column.status}
          aria-label={`${column.title}，${tasks.length} 项任务`}
        >
          <header className="kanban-column-header"><div><span className="column-signal" /><h3>{column.title}</h3><b>{tasks.length}</b></div><p>{column.note}</p></header>
          <div className="kanban-stack">
            {tasks.map((task) => <article
              className={`kanban-card${draggedTaskId === task.id ? " is-dragging" : ""}${dropTarget?.taskId === task.id ? ` is-drop-${dropTarget.placement}` : ""}`}
              data-task-id={task.id}
              key={task.id}
              onPointerDown={(event) => {
                if ((event.target as HTMLElement).closest("button, summary, .card-menu")) return;
                event.preventDefault();
                setDraggedTaskId(task.id);
              }}
            >
              <details className="card-menu"><summary aria-label={`打开“${task.title}”的操作菜单`}>•••</summary><div role="menu"><button type="button" role="menuitem" onClick={() => onEdit(task)}>编辑卡片</button><button type="button" role="menuitem" className="danger" onClick={() => onDelete(task)}>删除卡片</button></div></details>
              <div className="kanban-card-tags"><span className={`priority-tag priority-tag-${task.priority}`}>{priorityLabel[task.priority]}优先级</span>{task.type === "confirmation" && <span className="confirmation-tag">等待确认</span>}{task.referenceId && <span className="reference-sync-tag">↔ 参考文献</span>}</div>
              <h4>{task.title}</h4>
              <p>{task.chapterId ? chapterName(task.chapterId) : "当前阶段"} · {task.type}</p>
              {task.subtasks && <ol className="kanban-checklist">{task.subtasks.map((subtask) => <li key={subtask}>{subtask}</li>)}</ol>}
              <footer><span>{task.subtasks ? `${task.subtasks.length} 个子步骤` : "顶层事项"}</span><div className="card-move-actions">{columnIndex > 0 && <button type="button" onClick={() => moveTask(task.id, boardColumns[columnIndex - 1].status)} aria-label={`将“${task.title}”移至${boardColumns[columnIndex - 1].title}`}>←</button>}{columnIndex < boardColumns.length - 1 && <button type="button" onClick={() => moveTask(task.id, boardColumns[columnIndex + 1].status)} aria-label={`将“${task.title}”移至${boardColumns[columnIndex + 1].title}`}>→</button>}</div></footer>
            </article>)}
            {tasks.length === 0 && <div className="kanban-empty">把任务拖到这里</div>}
          </div>
        </section>;
      })}
    </section>
  </div>;
}

function ReferencesView({ data, chapterName, onAdd, onStatus }: { data: DashboardData; chapterName: (id: string) => string; onAdd: () => void; onStatus: (id: string, status: ReferenceStatus) => void }) {
  return <div className="view-content"><header className="view-header actions-header"><div><p className="eyebrow">Evidence library</p><h2>参考文献</h2><p>文献状态与任务看板双向同步；待读、阅读中和已完成分别对应三个任务列。</p></div><button className="button primary" onClick={onAdd}>＋ 添加文献</button></header><section className="reference-grid">{data.references.map((reference) => <article className="reference-card" key={reference.id}><div className="reference-top"><div className="reference-id"><code>{reference.key}</code>{reference.taskId && <span className="reference-sync-tag">↔ 已同步任务</span>}</div><select value={reference.status} onChange={(event) => onStatus(reference.id, event.target.value as ReferenceStatus)}><option value="todo">待读</option><option value="reading">阅读中</option><option value="using">使用中</option><option value="done">已完成</option></select></div><h3>{reference.title}</h3><p>{reference.authors || "作者待补充"} · {reference.year || "年份待补充"}</p><blockquote>{reference.note}</blockquote><div className="tag-row">{reference.chapterIds.map((chapterId) => <span key={chapterId}>{chapterName(chapterId)}</span>)}</div>{reference.url && <a href={reference.url} target="_blank" rel="noreferrer">打开来源 ↗</a>}</article>)}</section></div>;
}

function FeedbackView({ data, chapterName, onAdd }: { data: DashboardData; chapterName: (id: string) => string; onAdd: () => void }) {
  return <div className="view-content"><header className="view-header actions-header"><div><p className="eyebrow">Supervisor log</p><h2>导师意见与研究决策</h2><p>保留原始意见、行动项和落实状态，避免只记住结论。</p></div><button className="button primary" onClick={onAdd}>＋ 记录新意见</button></header><section className="feedback-layout"><div className="timeline">{data.feedback.map((entry) => <article className="timeline-item" key={entry.id}><div className="timeline-dot" /><div className="timeline-card"><header><div><strong>{entry.author}</strong><span>{entry.date} · {entry.source}</span></div><StatusPill status={entry.status} /></header><p>{entry.summary}</p><div className="action-note"><span>下一步</span>{entry.action}</div><div className="tag-row">{entry.chapterIds.map((chapterId) => <span key={chapterId}>{chapterName(chapterId)}</span>)}</div></div></article>)}</div><aside className="panel decisions-list"><header className="panel-header"><div><p className="eyebrow">Decision log</p><h2>关键决策</h2></div></header>{data.decisions.map((decision) => <div className="decision-log" key={decision.id}><div><span>{decision.date}</span><StatusPill status={decision.status} /></div><strong>{decision.title}</strong><p>{decision.detail}</p></div>)}</aside></section></div>;
}

function ExperimentsView({ data }: { data: DashboardData }) {
  return <div className="view-content"><header className="view-header"><div><p className="eyebrow">Simulation pipeline</p><h2>环境与最小示例</h2><p>这里只展示当前准备阶段；正式实验需在研究范围确认后另行规划。</p></div></header><section className="experiment-flow">{data.experiments.map((experiment, index) => { const tasks = data.tasks.filter((task) => experiment.taskIds.includes(task.id)); return <article className="experiment-card" key={experiment.id}><div className="experiment-index"><span>{experiment.code}</span>{index < data.experiments.length - 1 && <i />}</div><div className="experiment-content"><header><div><small>{experiment.rq}</small><h3>{experiment.title}</h3></div><StatusPill status={experiment.status} /></header><div className="experiment-meta"><span>阶段状态：{statusLabel[experiment.status] ?? experiment.status}</span><span>当前动作：{experiment.next}</span></div><div className="experiment-tasks">{tasks.map((task) => <span key={task.id}>{task.title}</span>)}</div></div></article>; })}</section></div>;
}

function TaskModal({ chapters, initialTask, onClose, onSave }: { chapters: Chapter[]; initialTask?: Task | null; onClose: () => void; onSave: (task: Task) => void }) {
  const [form, setForm] = useState({
    title: initialTask?.title ?? "",
    chapterId: initialTask?.chapterId ?? chapters[0]?.id ?? "",
    priority: initialTask?.priority ?? "medium" as Priority,
    status: initialTask ? boardStatusOf(initialTask) : "todo" as TaskStatus,
    type: initialTask?.type ?? "writing",
    subtasksText: initialTask?.subtasks?.join("\n") ?? "",
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!form.title.trim()) return;
    const subtasks = form.subtasksText.split("\n").map((item) => item.trim()).filter(Boolean);
    onSave({
      ...(initialTask ?? { id: makeId("task"), due: "" }),
      title: form.title.trim(), chapterId: form.chapterId, priority: form.priority,
      status: form.status, type: initialTask?.referenceId ? "literature" : form.type,
      subtasks: subtasks.length ? subtasks : undefined,
    });
  };
  return <Modal title={initialTask ? "编辑任务" : "添加任务"} onClose={onClose}><form className="modal-form" onSubmit={submit}><label className="field full"><span>任务内容</span><input autoFocus required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} placeholder="例如：核验 ALINEA 控制参数" /></label><label className="field"><span>对应章节</span><select value={form.chapterId} onChange={(event) => setForm({ ...form, chapterId: event.target.value })}>{chapters.map((chapter) => <option value={chapter.id} key={chapter.id}>{chapter.number} {chapter.title}</option>)}</select></label><label className="field"><span>类型</span><select value={form.type} disabled={Boolean(initialTask?.referenceId)} onChange={(event) => setForm({ ...form, type: event.target.value })}><option value="writing">写作</option><option value="literature">文献</option><option value="simulation">仿真</option><option value="analysis">分析</option><option value="decision">决策</option><option value="environment">配置</option><option value="confirmation">等待确认</option></select></label>{form.type === "literature" && <p className="sync-hint">{initialTask?.referenceId ? "此任务已关联参考文献；标题、章节和阅读状态会同步更新。" : "保存后会同步创建参考文献条目，后续阅读状态将在两个 Tab 中保持一致。"}</p>}<label className="field"><span>优先级</span><select value={form.priority} onChange={(event) => setForm({ ...form, priority: event.target.value as Priority })}><option value="high">高</option><option value="medium">中</option><option value="low">低</option></select></label><label className="field"><span>状态</span><select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as TaskStatus })}><option value="todo">待开始</option><option value="doing">进行中</option><option value="done">已完成</option></select></label><label className="field full"><span>子步骤（每行一项）</span><textarea rows={4} value={form.subtasksText} onChange={(event) => setForm({ ...form, subtasksText: event.target.value })} placeholder="可选，例如：检查配置文件" /></label><div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>取消</button><button className="button primary">{initialTask ? "保存修改" : "保存任务"}</button></div></form></Modal>;
}
function DeleteTaskModal({ task, onClose, onConfirm }: { task: Task; onClose: () => void; onConfirm: () => void }) {
  return <Modal title="删除任务" onClose={onClose}><div className="delete-confirm"><p>确定删除“{task.title}”吗？</p>{task.referenceId && <p className="delete-warning">关联的参考文献条目也会一并删除，以保持两个 Tab 的数据一致。</p>}<div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>取消</button><button type="button" className="button danger-button" onClick={onConfirm}>确认删除</button></div></div></Modal>;
}
function ReferenceModal({ chapters, onClose, onSave }: { chapters: Chapter[]; onClose: () => void; onSave: (reference: Reference) => void }) {
  const [form, setForm] = useState({ key: "", authors: "", year: "", title: "", status: "todo" as ReferenceStatus, chapterIds: [] as string[], url: "", note: "" });
  const submit = (event: FormEvent) => { event.preventDefault(); if (form.title.trim()) onSave({ id: makeId("ref"), ...form, key: form.key || `Ref${new Date().getFullYear()}` }); };
  return <Modal title="添加参考文献" onClose={onClose}><form className="modal-form" onSubmit={submit}><label className="field full"><span>文献标题</span><input autoFocus required value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} /></label><label className="field"><span>Citation key</span><input value={form.key} onChange={(event) => setForm({ ...form, key: event.target.value })} placeholder="Author2026" /></label><label className="field"><span>年份</span><input value={form.year} onChange={(event) => setForm({ ...form, year: event.target.value })} /></label><label className="field full"><span>作者</span><input value={form.authors} onChange={(event) => setForm({ ...form, authors: event.target.value })} /></label><label className="field full"><span>链接 / DOI</span><input value={form.url} onChange={(event) => setForm({ ...form, url: event.target.value })} /></label><label className="field full"><span>用途或支持的论点</span><textarea rows={3} value={form.note} onChange={(event) => setForm({ ...form, note: event.target.value })} /></label><ChapterChecks chapters={chapters} selected={form.chapterIds} onChange={(chapterIds) => setForm({ ...form, chapterIds })} /><div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>取消</button><button className="button primary">保存文献</button></div></form></Modal>;
}
function FeedbackModal({ chapters, onClose, onSave }: { chapters: Chapter[]; onClose: () => void; onSave: (feedback: Feedback) => void }) {
  const [form, setForm] = useState({ date: new Date().toISOString().slice(0, 10), author: "Robert Hilbrich", summary: "", action: "", status: "open", chapterIds: [] as string[], source: "会谈" });
  const submit = (event: FormEvent) => { event.preventDefault(); if (form.summary.trim()) onSave({ id: makeId("feedback"), ...form }); };
  return <Modal title="记录导师意见" onClose={onClose}><form className="modal-form" onSubmit={submit}><label className="field"><span>日期</span><input type="date" value={form.date} onChange={(event) => setForm({ ...form, date: event.target.value })} /></label><label className="field"><span>提出者</span><input value={form.author} onChange={(event) => setForm({ ...form, author: event.target.value })} /></label><label className="field full"><span>原始意见或准确摘要</span><textarea autoFocus required rows={4} value={form.summary} onChange={(event) => setForm({ ...form, summary: event.target.value })} /></label><label className="field full"><span>需要采取的行动</span><textarea rows={3} value={form.action} onChange={(event) => setForm({ ...form, action: event.target.value })} /></label><label className="field"><span>来源</span><select value={form.source} onChange={(event) => setForm({ ...form, source: event.target.value })}><option>会谈</option><option>邮件</option><option>批注</option><option>汇报反馈</option></select></label><label className="field"><span>状态</span><select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}><option value="open">待处理</option><option value="doing">落实中</option><option value="accepted">已采纳</option><option value="done">已完成</option></select></label><ChapterChecks chapters={chapters} selected={form.chapterIds} onChange={(chapterIds) => setForm({ ...form, chapterIds })} /><div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>取消</button><button className="button primary">保存意见</button></div></form></Modal>;
}
function ChapterChecks({ chapters, selected, onChange }: { chapters: Chapter[]; selected: string[]; onChange: (ids: string[]) => void }) {
  return <fieldset className="field full checkbox-field"><legend>关联章节</legend>{chapters.map((chapter) => <label key={chapter.id}><input type="checkbox" checked={selected.includes(chapter.id)} onChange={() => onChange(selected.includes(chapter.id) ? selected.filter((item) => item !== chapter.id) : [...selected, chapter.id])} />{chapter.number} {chapter.title}</label>)}</fieldset>;
}
