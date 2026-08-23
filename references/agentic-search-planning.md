# Agentic Search 提交规划合同

## 适用范围

Agentic Search 用于异步、批量、画像式发现。单公司、精确域名、明确岗位或小范围条件优先使用 company/people waterfall，不为“更全面”而自动升级 Agentic。

国家市场调研、多个产品面、多个公司角色或 lead/competitor 双轨发现，在第一次 `POST /api/agentic/search` 前必须生成并验证 Agentic Search Plan。一个宽泛 keyword、一个产品线或一个大而全任务不能代表整个国家研究范围。

显式的一次性 Agentic 请求可以使用 direct 模式，但必须由用户明确给出单一目标和边界；direct 不得用于替代国家级覆盖计划。

## 计划来源

上层研究任务先定义：

- 国家与研究语言；
- 所有在范围内的 productFamilies；
- 所有在范围内的 roleLanes；
- sourceGoals，例如 `lead_discovery|competitor_discovery|company_enrichment`；
- 结果范围 `full|sample`、排除项和预算/并发边界。

产品、角色和技术词来自上层业务合同或 Capability Foundation。TradeWind 任务不能自行缩小为最容易描述的一条产品线，也不能把未规划的产品或角色扩入付费查询。

计划保存在研究工作区，例如：

```text
<国家>/providers/tradewind/agentic/agentic-search-plan.json
```

结构参考 [agentic-search-plan-example.json](agentic-search-plan-example.json)，并运行：

```bash
python scripts/validate_agentic_plan.py '<agentic-search-plan.json>'
```

## 覆盖矩阵

`coverageMatrix[]` 是提交清单的来源。每个适用单元至少包含 productFamily、roleLane、sourceGoal、status、taskKeys 和 reason。

- `planned`：有一个或多个任务覆盖；
- `completed`：对应任务已完成且结果边界已验收；
- `excluded`：明确不适用或不在用户范围，必须写 reason；
- 不能用未列出的“默认不查”表达遗漏。

计划中的每个 productFamily、roleLane 和 sourceGoal 必须至少在矩阵出现一次。矩阵中 planned/completed 单元引用的 taskKey 必须存在，且任务本身必须覆盖该产品、角色和意图。

## 任务拆分原则

一个 Agentic task 只有一个 intent 和一个可解释 ICP/queryBoundary：

- lead discovery 与 competitor discovery 分开；
- 采购方、实际使用方、渠道商和制造/品牌竞对不能用同一个模糊 keyword 混合；
- 产品可在买方、场景和技术关键词高度一致时合并，但必须写 coherenceReason；
- 模架、预制混凝土、装配式钢结构和 VMC 等购买链明显不同的产品面通常拆分；
- 不为每个同义词重复开任务；同义词放在同一 queryBoundary，跨任务按稳定域名和强身份去重；
- requestBody 只包含官方 Agentic schema 支持的字段，计划元数据不得混入 API body。

任务需要稳定 taskKey、requestBody、queryBoundary、phase、approvalStatus、pilotReviewStatus、dependsOn、dedupKey 和 expectedOutcome。相同 requestBody 或实质相同 queryBoundary 不得重复 submit。

## Pilot → Scale

每个 intent 至少有一个 pilot。默认先提交 pilot，并检查：

- 返回公司是否落在目标国家、产品和角色；
- 是否出现食品、招聘、零售等语义漂移；
- 公司身份和官网域名能否归一；
- 结果量、重复率和跨产品/角色覆盖；
- 计费、分页、状态接口和结果接口是否可观察；
- keyword 是否过宽、过窄或把竞对与线索混在一起。

scale 任务必须依赖 `approvalStatus=completed` 且 `pilotReviewStatus=accepted` 的 pilot。pilot 未完成、结果漂移或上游状态不可观察时，不批量提交 scale 任务。调整 keyword 后更新计划和 queryBoundary，再重新验证；不要在 trace 中临时改词后直接提交。

## 提交门禁

计划内提交使用：

```bash
python scripts/agentic_api.py search \
  --plan-file '<agentic-search-plan.json>' \
  --task-key '<approved taskKey>'
```

脚本只允许 `approvalStatus=approved_for_pilot|approved_for_submit` 的任务，并直接使用计划中的 requestBody，防止提交时漂移。

用户明确要求一次性 Agentic 任务时可使用：

```bash
python scripts/agentic_api.py search --direct \
  --direct-reason '<用户明确授权的单一边界>' \
  --body '{...}'
```

direct 是例外路径，不能用于国家调研、多个产品/角色、补漏批次或重复提交。

## 状态、结果与补漏

提交后继续遵守 acknowledgement/status/result 三阶段语义。taskId、request ID、result pagination 和 ExternalObservation 分别落盘。

结果回收后按 coverageMatrix 聚合：

- 先在任务内按强身份/稳定域名去重，再跨任务去重；
- 对跨任务标签冲突保留来源，不自动仲裁 lead/competitor；
- 统计每个覆盖单元的 resultCount、acceptedCount、driftCount 和 duplicateCount；
- 只有明确未覆盖的矩阵单元才能创建补漏任务；补漏任务同样进入计划并通过 pilot/approval；
- Agentic 结果只形成 Provider candidate/ExternalObservation，不能跳过 Web 单公司背调。

## 停止条件

- 当前计划所有非 excluded 单元已 completed；或
- 结果模式为 sample 且样本目标已达到；或
- 上游不可用、认证/余额/限流阻断；或
- 新任务只会重复既有 queryBoundary；或
- 继续扩大范围将超过用户授权或预算。

停止时回传覆盖矩阵、任务清单、taskId 状态、结果数量、跨任务去重、漂移、未覆盖单元和下一步，不用“已开一个 Agentic 任务”代表 Provider 阶段完成。
