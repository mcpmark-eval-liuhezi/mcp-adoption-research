# MCP Adoption Digest — Model Context Protocol Readiness Briefing

**Prepared for:** Friday architecture review — internal agent platform
**Date compiled:** 2026-10-22 (HKT)
**Verdict:** **ADOPT MCP for the agent platform, with an explicit security hardening workstream** — weighted adoption-readiness score **4.15 / 5.00** (see [scoring](#adoption-readiness-score) below; computed by [`mcp_score.py`](./mcp_score.py)).

---

## 1. What MCP is, and the organization behind it

- **What it is:** "MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems." AI applications (e.g., Claude, ChatGPT) connect via MCP to data sources (local files, databases), tools (search engines, calculators) and workflows (specialized prompts). The official docs describe it as *"like a USB-C port for AI applications."*
  Source: [What is the Model Context Protocol (MCP)? — official docs](https://modelcontextprotocol.io/docs/getting-started/intro)
- **The specification:** "Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools… This specification defines the authoritative protocol requirements, based on the TypeScript schema in schema.ts," with BCP 14 / RFC-2119 requirement keywords (MUST, SHOULD, MAY).
  Source: [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
- **Origin and stewardship:** MCP was created and open-sourced by **Anthropic** (November 2024). In December 2025 Anthropic **donated MCP to the Linux Foundation's new Agentic AI Foundation (AAIF)**, co-founded with Block and OpenAI, with support from Google, Microsoft, AWS, Cloudflare and Bloomberg. AAIF platinum members: AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, OpenAI. MCP's governance model is unchanged; maintainers continue to prioritize community input.
  Sources: [Anthropic — Donating MCP to the Agentic AI Foundation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation) · [Linux Foundation press release](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) · [MCP blog — MCP joins the Agentic AI Foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/) · [GitHub Blog](https://github.blog/open-source/maintainers/mcp-joins-the-linux-foundation-what-this-means-for-developers-building-the-next-era-of-ai-tools-and-agents/)
- **Design lineage:** "MCP takes some inspiration from the Language Server Protocol, which standardizes how to add support for programming languages across a whole ecosystem of development tools."
  Source: [MCP Specification — Overview](https://modelcontextprotocol.io/specification/2026-07-28)

## 2. Client/server architecture

From the official [Architecture overview](https://modelcontextprotocol.io/docs/concepts/architecture):

- **MCP follows a client-server architecture** where an **MCP host** — an AI application like Claude Code or Claude Desktop — establishes connections to one or more **MCP servers**, creating **one MCP client per server**, each maintaining a dedicated connection.
- **Participants:**
  - **MCP Host:** the AI application that coordinates and manages one or multiple MCP clients
  - **MCP Client:** a component that maintains a connection to an MCP server and obtains context from it for the host
  - **MCP Server:** a program that provides context to MCP clients
- **Local vs. remote:** Local servers using STDIO typically serve a single MCP client; remote servers using Streamable HTTP typically serve many MCP clients. Example given in docs: VS Code (host) instantiates a client object per server (e.g., the remote Sentry MCP server, a local filesystem server).
- **Two layers:** the **data layer** (JSON-RPC based protocol for client-server communication, including capability and version discovery, and core primitives) and the **transport layer** (communication mechanisms/channels, connection establishment, message framing, and authorization).

## 3. Core capability primitives

From the [MCP Specification](https://modelcontextprotocol.io/specification/2026-07-28) and [Tools](https://modelcontextprotocol.io/docs/concepts/tools) / [Resources](https://modelcontextprotocol.io/docs/concepts/resources) concept pages:

**Server-side primitives (servers offer to clients):**
- **Resources** — context and data, for the user or the AI model to use
- **Prompts** — templated messages and workflows for users
- **Tools** — functions for the AI model to execute (model-controlled: the LLM can discover and invoke tools automatically based on contextual understanding and user prompts; the protocol does not mandate a specific user interaction model)

**Client-side primitives (clients offer to servers):**
- **Elicitation** — server-initiated requests for additional information from users

**Utilities:** configuration, progress tracking, cancellation, error reporting; notifications for real-time updates. Note: **Sampling is deprecated as of protocol version 2026-07-28** (architecture overview).

**Extensions (opt-in, negotiated):** **Tasks** (async long-running operations with polling, mid-flight input, durable handles), **Skills over MCP** (rich structured instructions for agent workflows), **MCP Apps** (interactive UI elements — charts, forms, video players — rendered inline in conversations).

**Base protocol details (2026-07-28):** JSON-RPC message format; stateless, self-contained requests; per-request capability negotiation. Tool lists "MUST NOT vary per-connection," "SHOULD return tools in a deterministic order" (improves client caching and LLM prompt cache hit rates), and may vary by authorization scopes since "credentials are per-request input, not connection state."

## 4. Transports

From the [Architecture overview](https://modelcontextprotocol.io/docs/concepts/architecture):

1. **Stdio transport** — standard input/output streams for direct process communication between local processes on the same machine; "optimal performance with no network overhead."
2. **Streamable HTTP transport** — HTTP POST for client-to-server messages with optional Server-Sent Events for streaming; enables remote server communication and supports standard HTTP authentication (bearer tokens, API keys, custom headers). **MCP recommends OAuth to obtain authentication tokens.**

The transport layer abstracts communication details from the protocol layer, enabling the same JSON-RPC 2.0 message format across transports. Notable: the 2026-07-28 revision **removed protocol-level sessions and the `Mcp-Session-Id` header** from Streamable HTTP, made MCP stateless (removed the `initialize` handshake — version/capabilities now travel per-request in `_meta`), and removed SSE stream resumability. Source: [2026-07-28 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog).

## 5. Current specification version and release cadence

- **Current protocol version: `2026-07-28`** — marked as a **stable release**. Verified two ways: the [official GitHub release](https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28) (published 2026-07-28T16:47:49Z: "This release marks the stable release of the `2026-07-28` revision of the Model Context Protocol") and the [Versioning page](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning.md): "The current protocol version is 2026-07-28."
- **Version identifiers** are date-based (`YYYY-MM-DD`, indicating the last date of backwards-incompatible changes); versions are not incremented for backwards-compatible changes. Revision states: **Draft / Current / Final**. Deprecated features keep a documented migration path and remain in the spec for at least twelve months (or 90 days under expedited removal) before removal eligibility.
- **Version negotiation:** every request declares its protocol version via `io.modelcontextprotocol/protocolVersion` in `_meta` (also `MCP-Protocol-Version` header on Streamable HTTP); `server/discover` is a mandatory RPC that returns supported versions, capabilities, and identity.
- Previous revisions documented on site: `2025-11-25`, `2025-06-18` (per the site's [llms.txt index](https://modelcontextprotocol.io/llms.txt)).

## 6. Security and authorization model

From [Understanding Authorization in MCP](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization.md) and [Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices.md):

- **Authorization follows OAuth 2.1** conventions (authorization code + PKCE), with RFC 8414 (AS metadata discovery), RFC 7591 (Dynamic Client Registration), RFC 9728 (Protected Resource Metadata), and RFC 8707 (Resource Indicators). 401 + Protected Resource Metadata in the `WWW-Authenticate` header kicks off the flow; access tokens in the `Authorization` header; the `aud` claim is validated against the MCP server URI.
- **Local stdio servers** can use environment-based or library-provided credentials instead of browser OAuth flows.
- **The spec's own security principles:** user consent and control; data privacy (hosts must obtain explicit consent before exposing user data); tool safety (tools are arbitrary code execution; tool descriptions/annotations are untrusted unless from a trusted server).
- **Critically:** "While MCP itself cannot enforce these security principles at the protocol level, implementors SHOULD…" — i.e., security is largely an implementor obligation, not a protocol guarantee.
- **Documented attack vectors:** the **confused deputy problem** (MCP proxy servers using a static client ID with a third-party authorization server + dynamic client registration + consent cookies allow attackers to obtain authorization codes without user consent; mitigated by per-client consent **MUST**), plus token audience validation, treating `Mcp-Session-Id` as untrusted, and RFC 9700 OAuth 2.0 best practices.

**Recent third-party security findings:**
- Ars Technica (2026-10-05): "Vulnerability in agents from Google and others exposes structural flaw in MCP" — over five months, Google and four other organizations acknowledged vulnerabilities that "exploit one agent inside a targeted network to spread harmful instructions to other internal agents" — a prompt-injection variant targeting specific agents rather than the LLM, often leading to SSRF; "MCP is new and is already everywhere before it has been sufficiently tested and hardened." Google's case was rated severity 8. Rapid7's director of vulnerability intelligence: "AI agents give attackers a fresh set of connections to walk across."
  Source: [Ars Technica](https://arstechnica.com/security/2026/10/vulnerability-in-agents-from-google-and-others-exposes-structural-flaw-in-mcp/) · [CCTest summary with severity scores](https://cctest.ai/en/articles/mcp-s-trust-chain-lets-malicious-instructions-travel-between-ai-agents)
- Stacklok's December 2025 software-industry survey: **64% named security concerns and requirements as their top obstacle to MCP adoption**. Source: [State of MCP in Software 2026](https://stacklok.com/resources/state-of-mcp-in-software-2026/) (via [Supermetrics summary](https://supermetrics.com/blog/mcp-marketing))
- Radware (2026-10-14) launched **MCP Server Protection** for the agentic-AI integration layer — evidence of an emerging security-products market around MCP. Source: [Radware press release via Markets Insider](https://markets.businessinsider.com/news/stocks/radware-introduces-model-context-protocol-mcp-server-protection-to-help-secure-the-integration-layer-of-agentic-ai-1036624834)

## 7. Ecosystem, adoption, and tooling

- **Official SDKs (10 languages), tiered:** Tier 1 — TypeScript, Python, C#, Go, Rust, Ruby. Tier 2 — Java. Tier 3 — Swift, PHP, Kotlin. All SDKs support building servers exposing tools/resources/prompts, clients connecting to any server, local and remote transports, and typed protocol compliance.
  Source: [SDKs page](https://modelcontextprotocol.io/docs/2026-07-28/sdk.md)
- **Developer tools:** the **MCP Inspector** (interactive testing/debugging in browser, CLI, and TUI, with OAuth and protocol-era negotiation docs) plus reference server implementations. Source: [MCP Inspector](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector.md)
- **Client/host adoption:** per the intro page, Claude and ChatGPT, plus development tools Visual Studio Code, Cursor, MCPJam and others support MCP. Anthropic reported adoption across ChatGPT, Gemini, Microsoft Copilot, VS Code, Cursor by December 2025 (via [eWeek guide](https://www.eweek.com/artificial-intelligence/model-context-protocol/)).
- **Production usage (survey):** Stacklok's *State of Model Context Protocol in Software 2026*: **nearly half of software companies use MCP in production, 19% in broad production**; **49% tagged MCP adoption as a top-5 company-level initiative** (highest of any industry surveyed). Retail: 40%+ in production. Financial services lags: 3% broad production, 12% formal pilots, security top obstacle at 58%.
  Sources: [Software](https://stacklok.com/resources/state-of-mcp-in-software-2026/) · [Retail](https://stacklok.com/resources/state-of-mcp-in-retail-2026/) · [Financial Services](https://stacklok.com/resources/state-of-mcp-in-financial-services-2026/)
- **Ecosystem milestone (2026-10-20):** Figma announced **20 new MCP partners** — Amp, ClickUp, Dia, Junie by JetBrains, Linear, Meta Muse, Mistral, Notion, OpenCode, Sarvam Agents — with an updated MCP server offering faster performance, more product coverage, and agents that can create code layers, edit specs, and generate images. Figma co-founder/CEO **Dylan Field**: MCP "is not a perfect protocol," has "tons of room for improvement," and is "advantaged more to frontier labs"; more exposed data means more abuse risk. Useful counter-signal on maturity, but note Figma is *expanding* MCP support regardless.
  Sources: [TechCrunch](https://techcrunch.com/2026/10/20/figma-co-founder-dylan-field-thinks-mcp-is-not-a-perfect-protocol/) · [CryptoBriefing summary](https://cryptobriefing.com/figma-model-context-protocol-20-partners/)
- **New market entries (2026-10-21):** Notified opened an **MCP beta program for PR and IR data**, targeting Microsoft Teams/Copilot first (already security-approved), then ChatGPT, Claude, Gemini. Source: [GlobeNewswire](https://globenewswire.com/news-release/2026/10/21/3385795/0/en/notified-opens-model-context-protocol-mcp-beta-program-for-pr-and-ir-data-and-services.html)
- **Practitioner production reports (Ask HN, 2026):** teams run user-facing production services over MCP hosts (ChatGPT, Claude, Grok, Perplexity, Mistral interfaces) — "MCP is the backbone behind the product and enables regular users to do things without knowing anything about it"; a niche CRM credits MCP with LLM-specific tool descriptions, OAuth handling, and non-technical-user reach; cybersecurity teams report integrations/playbooks "amazingly easy"; recurring cautions: many third-party MCP servers are worse than direct API access, determinism limits (non-deterministic workflows can't replace dashboards), and multi-tenant auth patterns are still maturing.
  Source: [Ask HN: Who is using MCP in production?](https://news.ycombinator.com/item?id=49548600) · [r/mcp: One Month in MCP](https://www.reddit.com/r/mcp/comments/1mub6g6/one_month_in_mcp_what_i_learned_the_hard_way/) · [Towards AI: running stateful AI agents safely in an enterprise](https://pub.towardsai.net/beyond-the-mcp-demo-running-stateful-ai-agents-safely-in-an-enterprise-87ad6bd998d1)
- **Tutorial video:** [MCP Complete Explanation (YouTube, 15:22)](https://www.youtube.com/watch?v=_fzpnqt39jQ); also [Model Context Protocol Clearly Explained | MCP Beyond the Hype (15:04)](https://www.youtube.com/watch?v=tzrwxLNHtRY) and [How Model Context Protocol (MCP) actually works (7:58)](https://www.youtube.com/watch?v=cGuyrANVi4A).

## 8. Documentation freshness notes

Page-level "last updated" estimates were checked via HTTP headers/page metadata (Jina date-guessing, confidence 92 where noted). All official MCP documentation pages returned the same site-wide deployment timestamp, so treat freshness as **site-level, ~9 months old at time of writing (2026-10-22), predating the 2026-07-28 stable spec release in deployment terms**:

| Page | Last updated (est.) | Confidence |
| --- | --- | --- |
| [What is MCP? (intro)](https://modelcontextprotocol.io/docs/getting-started/intro) | 2026-01-30 | 92 |
| [Architecture overview](https://modelcontextprotocol.io/docs/concepts/architecture) | 2026-01-30 | 92 |
| [Transports](https://modelcontextprotocol.io/docs/concepts/transports) | 2026-01-30 | 92 |
| [Tools](https://modelcontextprotocol.io/docs/concepts/tools) | 2026-01-30 | 92 |
| [Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28) | 2026-01-30 | 92 |
| [Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices.md) | 2026-01-30 | 92 |
| [SDKs](https://modelcontextprotocol.io/docs/2026-07-28/sdk.md) | 2026-01-30 | 92 |

The GitHub release metadata is independently verifiable and fresher: the `2026-07-28` tag was published **2026-07-28T16:47:49Z** ([release](https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28)). Docs content is version-pinned (`/docs/2026-07-28/...`) and clearly describes the stable revision, so substance is current even though the site's page timestamps lag.

---

## 9. Adoption-readiness score

Ratings 1–5 (5 = strongly favors adopting). Weights: protocol maturity 0.30, ecosystem and tooling 0.25, documentation quality 0.20, security story 0.15, integration effort 0.10. Computed by [`mcp_score.py`](./mcp_score.py) — **run it to reproduce: the weighted total is 4.15**.

| Criterion | Weight | Rating | Weighted | Rationale (evidence-linked) |
| --- | --- | --- | --- | --- |
| Protocol maturity | 0.30 | 4 | 1.20 | Stable `2026-07-28` spec ([release](https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28)) under Linux Foundation/AAIF stewardship ([LF press](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)) with a documented deprecation policy ([versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning.md)). But the stable revision is a large breaking rewrite ([changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)) and Figma's CEO calls it "not a perfect protocol" ([TechCrunch](https://techcrunch.com/2026/10/20/figma-co-founder-dylan-field-thinks-mcp-is-not-a-perfect-protocol/)). |
| Ecosystem and tooling | 0.25 | 5 | 1.25 | 10 official SDKs, six Tier-1 ([SDKs](https://modelcontextprotocol.io/docs/2026-07-28/sdk.md)); Inspector tooling; broad host adoption (ChatGPT, VS Code, Cursor); ~half of software companies in production ([Stacklok](https://stacklok.com/resources/state-of-mcp-in-software-2026/)); Figma + 20 partners Oct 2026 ([TechCrunch](https://techcrunch.com/2026/10/20/figma-co-founder-dylan-field-thinks-mcp-is-not-a-perfect-protocol/)). |
| Documentation quality | 0.20 | 5 | 1.00 | Versioned docs with authoritative spec, RFC-2119 keywords, changelogs, versioning/deprecation policy, security tutorials with attack diagrams, llms.txt index ([spec](https://modelcontextprotocol.io/specification/2026-07-28), [llms.txt](https://modelcontextprotocol.io/llms.txt)). Freshness: page timestamps 2026-01-30, ~9 months old but content version-pinned to the current spec. |
| Security story | 0.15 | 2 | 0.30 | OAuth 2.1 + PKCE with RFC-compliant extension guidance exists ([authorization](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization.md)), and attack vectors are documented ([best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices.md)). But the spec states MCP "cannot enforce these security principles at the protocol level"; Oct 2026 structural-flaw reporting ([Ars Technica](https://arstechnica.com/security/2026/10/vulnerability-in-agents-from-google-and-others-exposes-structural-flaw-in-mcp/)); 64% cite security as top adoption obstacle ([Stacklok](https://stacklok.com/resources/state-of-mcp-in-software-2026/)). |
| Integration effort | 0.10 | 4 | 0.40 | Uniform cross-language SDKs, Inspector for debugging, remote Streamable HTTP transport with OAuth; positive production reports ([Ask HN](https://news.ycombinator.com/item?id=49548600)); offset by multi-tenant auth patterns still maturing ([r/mcp](https://www.reddit.com/r/mcp/comments/1mub6g6/one_month_in_mcp_what_i_learned_the_hard_way/)). |
| **TOTAL** | **1.00** | | **4.15** | |

**Verdict: ADOPT — with an explicit security hardening workstream.** The protocol is stable, vendor-neutrally governed, and the ecosystem/tooling/documentation are strong. The weakest dimension by far is security (0.30 weighted contribution from the lowest-rated criterion): treat MCP as a trust boundary that provides zero security guarantees by itself, and plan per-agent identity, per-tool authorization, audit logging, and prompt-injection defenses above the protocol. Reassess quarterly — spec revisions are date-versioned and moving quickly.

---

## 10. Recommendations for the platform team

1. **Adopt MCP as the integration layer** for tools/context; align to the `2026-07-28` stable revision and rely on Tier-1 SDKs (TypeScript/Python/Go/Rust/C#/Ruby).
2. **Do not depend on protocol-level security.** Layer per-agent identity and per-tool authorization outside the protocol; the spec explicitly cannot enforce its security principles, and current reporting shows cross-agent trust exploitation.
3. **Track breaking changes.** The 2026-07-28 revision removed sessions/handshakes and moved tasks to an extension — monitor the changelog and SDK releases each quarter.
4. **Pilot first with a low-risk remote server** (Streamable HTTP + OAuth 2.1/PKCE), then expand; mirror the pattern of software companies now ~half in production.
