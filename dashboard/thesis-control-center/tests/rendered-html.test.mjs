import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("renders the thesis control center metadata", async () => {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  const response = await worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );

  assert.equal(response.status, 200);
  assert.match(
    response.headers.get("content-type") ?? "",
    /^text\/html\b/i,
  );
  assert.match(await response.text(), /<title>论文研究控制台<\/title>/i);
});

test("keeps the dashboard phase-first with a three-column task board", async () => {
  const data = JSON.parse(
    await readFile(new URL("../data/thesis-dashboard.json", import.meta.url), "utf8"),
  );

  assert.equal(data.meta.currentPhase, "探索验证已结项；进入正式实验方案设计");
  assert.equal(
    data.meta.nextMilestone,
    "设计并审查正式实验协议；批准冻结后再运行",
  );
  assert.equal(
    data.tasks.find((task) => task.id === "stage-one-observation-instrumentation")?.status,
    "done",
  );
  assert.equal(
    data.tasks.find((task) => task.id === "task-1787503668452-ce9ys")?.status,
    "done",
  );
  assert.equal(
    data.tasks.find((task) => task.id === "exploratory-uncontrolled-grid")?.status,
    "done",
  );
  assert.equal(data.experiments.find((item) => item.id === "e1")?.status, "done");
  assert.equal(data.experiments.find((item) => item.id === "formal-design")?.status, "todo");
  assert.equal(data.tasks.find((item) => item.id === "formal-experiment-design")?.status, "todo");
  assert.equal(data.tasks.find((item) => item.id === "stage6-standard-metering-validation")?.status, "done");
  assert.ok(data.tasks.length >= 2);
  assert.ok(data.tasks.every((task) => ["todo", "doing", "blocked", "done"].includes(task.status)));
  assert.equal(data.chapters.length, 7);
  assert.ok(
    data.chapters.every(
      (chapter) => chapter.status === "Provisional / 初步结构，尚未确认",
    ),
  );
  assert.deepEqual(
    data.pendingConfirmations.map((item) => item.title),
    [
      "请 Robert 确认 Sweet Spot 可接受区域定义",
      "请 Robert 确认主研究问题、子问题与评价导向范围",
      "确认英文写作规则与中期汇报确切日期",
      "正式指标、需求范围、seeds 与统计规则",
      "城市路网、qUrban 与匝道储存的正式角色",
    ],
  );
  assert.equal(
    data.tasks.find((task) => task.id === "minimal-uncontrolled-scenario")?.status,
    "done",
  );

  const pageSource = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(pageSource, /progressOf|overallProgress|chapterProgress|总体完成/);
  assert.match(pageSource, /const boardColumns/);
  assert.match(pageSource, /const priorityRank/);
  assert.match(pageSource, /const sortBoardTasks/);
  assert.match(pageSource, /boardOrder/);
  assert.match(pageSource, /onPointerDown=/);
  assert.match(pageSource, /addEventListener\("pointerup"/);
  assert.match(pageSource, /待开始/);
  assert.match(pageSource, /进行中/);
  assert.match(pageSource, /已完成/);
});

test("keeps literature tasks and references linked in both directions", async () => {
  const data = JSON.parse(
    await readFile(new URL("../data/thesis-dashboard.json", import.meta.url), "utf8"),
  );
  const taskById = new Map(data.tasks.map((task) => [task.id, task]));
  const referenceById = new Map(data.references.map((reference) => [reference.id, reference]));
  const taskStatusFromReference = (status) => status === "done" ? "done" : status === "reading" || status === "using" ? "doing" : "todo";

  const literatureTasks = data.tasks.filter((task) => task.type === "literature");
  assert.ok(literatureTasks.length > 0);
  assert.ok(literatureTasks.every((task) => task.referenceId && referenceById.get(task.referenceId)?.taskId === task.id));
  assert.ok(data.references.every((reference) => reference.taskId && taskById.get(reference.taskId)?.referenceId === reference.id));
  assert.ok(data.references.every((reference) => taskById.get(reference.taskId)?.status === taskStatusFromReference(reference.status)));

  const pageSource = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.match(pageSource, /referenceStatusFromTask/);
  assert.match(pageSource, /taskStatusFromReference/);
  assert.match(pageSource, /setReferenceStatus/);
  assert.match(pageSource, /↔ 已同步任务/);
});

test("provides editable and deletable task card menus", async () => {
  const pageSource = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.match(pageSource, /className="card-menu"/);
  assert.match(pageSource, /编辑卡片/);
  assert.match(pageSource, /删除卡片/);
  assert.match(pageSource, /const updateTask/);
  assert.match(pageSource, /const deleteTask/);
  assert.match(pageSource, /DeleteTaskModal/);
  assert.match(pageSource, /子步骤（每行一项）/);
  assert.match(pageSource, /关联的参考文献条目也会一并删除/);
  assert.match(pageSource, /共 \{data\.tasks\.filter\(\(task\) => task\.status !== "done"\)\.length\} 项未完成任务/);
  assert.match(pageSource, /已完成不计入/);
});
