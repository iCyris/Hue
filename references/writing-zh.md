# Writing Rules: Chinese Requirement Documents

Loaded when the generated document is Chinese. These rules govern prose quality; the gate
(`scripts/check.py`) enforces the mechanical subset. Everything here serves one goal: a
document a busy teammate reads once and understands completely.

## Voice

- Write like an engineer explaining to a colleague, not like a report generator. Plain,
  direct, concrete. First person plural (我们) is fine when stating decisions.
- Describe behavior the reader can observe: 用户看到什么、能点什么、系统回应什么。
  Not wishes about internals ("系统应该具备良好的扩展性" is not a requirement).
- One idea per paragraph. If a paragraph needs 此外 to continue, it is two paragraphs.
- Terms are consistent: pick one name per concept (用户/会员, 订单/单据) and never vary it.

## Structure

- Title: concrete and short (≤ 20 chars preferred), names the thing, not the theme.
  NO: 关于订单履约体验优化的若干思考  OK: 订单页增加物流实时跟踪
- Lead: two sentences max — what this requirement is, why it exists now.
- Sections follow the need: 背景与目标 / 范围 / 功能描述 / 交互细节 / 边界与异常 / 验收标准.
  Do not invent ceremonial sections (前言, 意义, 总结) to look complete.
- Acceptance criteria are testable: each item can be verified true or false.
  NO: 响应速度较快  OK: 列表页首屏加载不超过 2 秒(4G 网络,100 条数据)

## Banned patterns (deterministic)

These are AI-tone fingerprints in Chinese. Never produce them; rewrite when editing.

1. **段末总结句**: a closing sentence that restates the paragraph (总之, 综上所述, 由此可见,
   总的来说). The paragraph already said it.
2. **升华句**: ending that inflates meaning (为业务赋能, 打造极致体验, 助力数字化转型,
   开启新篇章). A requirement ends when the behavior is described.
3. **对比框架**: 不是……而是…… used for rhythm rather than real contrast.
4. **提示语**: 值得注意的是, 众所周知, 毫无疑问, 不得不说. Say the thing itself.
5. **报告腔**: 高度重视, 深入贯彻, 扎实推进, 有效提升. Replace with the concrete action.
6. **形式感连接词**: 首先/其次/再次/最后 as decoration when the items have no real order.
   A list without 首先 is still a list.
7. **三段式排比**: three parallel clauses marching in lockstep (更快速、更便捷、更智能).
   One precise claim beats three vague ones.
8. **空泛形容词**: 极致, 卓越, 完美, 强大, 丰富. Numbers, states, and examples instead.

## Punctuation and format (gate-enforced subset marked ✓)

- Full-width punctuation in Chinese text: ,。、;:!?「」() — never half-width next to
  CJK characters. ✓
- One half-width space between CJK and Latin/digits: 支持 Markdown 语法, 最多 100 条. ✓
  (--fix repairs this case automatically.)
- No em-dash (—— or —) anywhere; restructure with a comma, colon, or parentheses. ✓
- Numbers carry units and conditions: 不超过 2 秒(4G 网络), not 很快.
- List items are parallel in form and complete without the lead-in sentence.

## Demo captions

One sentence: what to try, or what the interaction proves. NO: 下面这个演示非常直观.
OK: 拖动滑块,观察右侧数值与提交按钮状态的变化。
