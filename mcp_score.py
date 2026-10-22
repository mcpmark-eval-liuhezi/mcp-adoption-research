#!/usr/bin/env python3
"""
mcp_score.py — MCP adoption-readiness scoring for the internal agent platform.

Rates five weighted criteria (1-5, 5 = strongly favors adopting) and prints an
auditable weighted total. Ratings are justified in mcp_adoption_digest.md; each
rating maps to evidence linked there.

Weights: protocol maturity 0.30, ecosystem & tooling 0.25, documentation
quality 0.20, security story 0.15, integration effort 0.10 (sum = 1.00).

Run: python3 mcp_score.py
"""

CRITERIA = [
    # (criterion, weight, rating, key evidence pointer)
    ("Protocol maturity", 0.30, 4,
     "Stable 2026-07-28 spec under Linux Foundation governance, but major "
     "breaking changes (stateless rewrite, sessions removed) and 'not a "
     "perfect protocol' feedback from Figma's CEO"),
    ("Ecosystem and tooling", 0.25, 5,
     "10 official SDKs, 6 Tier-1; adopted by ChatGPT/Gemini/Copilot/VS Code/"
     "Cursor; Figma + 20 partners (Oct 2026); ~half of software cos in "
     "production per Stacklok 2026 survey"),
    ("Documentation quality", 0.20, 5,
     "Versioned docs w/ full spec, RFC-2119 keywords, changelogs, security "
     "tutorials w/ attack diagrams; llms.txt index; freshness 2026-01-30"),
    ("Security story", 0.15, 2,
     "OAuth 2.1 + PKCE + RFC-compliant docs exist, BUT spec itself says MCP "
     "cannot enforce security at protocol level; Oct 2026 Ars Technica "
     "structural-flaw report; 64% of leaders cite security as top obstacle"),
    ("Integration effort", 0.10, 4,
     "Uniform SDKs across languages, MCP Inspector, remote Streamable HTTP "
     "transport; production HN reports positive; multi-tenant auth patterns "
     "still maturing"),
]


def weighted_total(pairs):
    """Return sum(weight * rating). Raises if weights don't sum to 1.0."""
    total_weight = sum(w for _, w, _, _ in pairs)
    assert abs(total_weight - 1.0) < 1e-9, f"weights must sum to 1.0, got {total_weight}"
    return sum(w * r for _, w, r, _ in pairs)


def main():
    print("MCP Adoption-Readiness Score")
    print("=" * 76)
    print(f"{'Criterion':<24}{'Weight':>8}{'Rating':>8}{'Weighted':>10}")
    print("-" * 76)
    for name, weight, rating, _ in CRITERIA:
        print(f"{name:<24}{weight:>8.2f}{rating:>8d}{weight * rating:>10.2f}")
    print("-" * 76)
    total = weighted_total(CRITERIA)
    print(f"{'TOTAL':<24}{'1.00':>8}{'':>8}{total:>10.2f}")
    print("=" * 76)
    print(f"\nComputed weighted adoption-readiness score: {total:.2f} / 5.00")
    if total >= 4.0:
        verdict = "ADOPT (with security controls)"
    elif total >= 3.0:
        verdict = "PILOT"
    else:
        verdict = "HOLD"
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
