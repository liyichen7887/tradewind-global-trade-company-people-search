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

任职、职位、授权和采购角色分别需要公司官网、人员公开职业页或多源一致证据。
