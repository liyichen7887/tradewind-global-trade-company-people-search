# Provider Observation 采纳合同

## 主体候选

公司和人员搜索结果只形成候选观察。每条候选记录：

```json
{
  "identityDecision": "accepted|rejected|unresolved",
  "decisionReasons": [],
  "queryCountry": "MX",
  "observedCountry": null,
  "matchedAnchors": [],
  "conflictingAnchors": []
}
```

- `S.R.L.`、`S.A. de C.V.`、LLC、Ltd 及阿拉伯语通用法律词不构成名称锚点。
- queryCountry 只表示请求条件。记录没有返回国家/地址字段时，`observedCountry=null`，不能声称国家过滤已生效。
- 法定名、RFC、注册号或稳定官网域名有冲突时使用 rejected；只有名称相似且没有强锚点时使用 unresolved。
- People 记录必须同时归一人员身份和任职公司；公司候选被拒绝时，人员不能桥接到目标 Company。

## 覆盖与上游状态

- `coverageStatus=not_exhaustive` 或 warning=`pagination_metadata_inconsistent` 表示分页元数据不能证明穷尽覆盖。
- `providerStatus=upstream_unavailable`、warning=`invalid_upstream_payload` 表示上游返回应用堆栈或错误载荷；其中的 success、记录数和伪数据不进入 ExternalObservation.data。
- 精确查询返回 0 只说明该 queryBoundary 无命中。

## Agentic 任务观察

- 国家级、多产品或多角色 Agentic 查询必须能回溯到已验证计划的 planId、taskKey、coverage cell 和 queryBoundary；缺计划的 Provider 结果只能作为孤立的 bounded observation，不能宣称国家或产品覆盖完成。
- 一个 Agentic task 只证明其 taskKey 对应的产品、角色和 intent 边界。跨任务聚合后按稳定域名、强身份和任务标签去重；标签冲突不自动升级 lead/competitor。
- submit 成功消息、taskId 和计费元数据只构成 `submission_acknowledged_unconfirmed`；不能据此写入 queued、running、completed 或 no_result。
- 状态接口明确返回 completed 后才读取结果。错误载荷、HTTP 500、认证失败、限流和余额不足分别保留原状态，不进入结果数据。
- 相同 taskId 每轮只查询一次；已有 taskId 不重新 submit 相同 queryBoundary。需要重新提交时必须先确认原任务不可恢复并取得用户授权。
- 结果分页保存请求页码/offset、limit、返回条数和去重键。分页元数据与实测不一致时，以可复现的请求结果确定边界并标记 warning。

## 联系人邮箱桥接

邮箱验证只支持邮箱自身的可投递性：

```json
{
  "name": "",
  "jobTitle": null,
  "buyingRole": null,
  "workEmail": "person@example.com",
  "verificationStatus": "email_only",
  "evidence": [{
    "sourceType": "provider",
    "relation": "context",
    "verificationScope": ["workEmail.deliverability"],
    "note": "Mailbox deliverability only; does not verify employment, title, authority, or buying role."
  }]
}
```

任职、职位、授权和采购角色分别需要公司官网、人员公开职业页或多源一致证据。精确域名/法定名称锚定、完整姓名和 Provider 联系方式可以支持 Provider 范围内的联系人记录；姓名掩码或雇主身份 unresolved 时不进入 `contacts[]`。
