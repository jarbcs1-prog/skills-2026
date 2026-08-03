# Trust Psychology Skill — Improvement Plan

**Status:** Proposed
**Date:** 2026-07-30
**Current version:** No version field
**Target version:** 2.0.0

---

## 1. Add Frontmatter Triggers and Version

### Changes
- Add `version: "2.0.0"` to YAML frontmatter
- Extend `description` with trigger keywords: `trust, conversion, landing page, checkout, onboarding, cart abandonment, credibility, social proof, CTA, sign-up`

### Rationale
The current description is descriptive but not trigger-rich. Adding keywords improves agent match accuracy.

---

## 2. Replace ASCII Diagrams with Structured Templates

### Changes
Convert the ASCII art diagrams into markdown tables or JSON-like templates that agents can parse:

**Current:** ASCII trust relationship flow (lines 23-46)
**Replace with:**

```markdown
## Trust-Risk Model

| User State | Driven By | Signal Needed |
|-----------|----------|---------------|
| Desire | Perceived Value exceeds Risk | More risk reduction |
| Hesitation | Perceived Risk exceeds Value | Trust signals |

**Trust signals tip the balance from hesitation to action.**
```

**Current:** Landing page trust architecture ASCII diagram (lines 156-187)
**Replace with:**

```markdown
## Landing Page Trust Sections

| Section | Trust Elements | Priority |
|---------|---------------|----------|
| Header | Logo, security badges, contact info | High |
| Hero | Value prop + social proof statement | High |
| Social Proof | Client logos, testimonials | Medium |
| Features | Proof points per feature | Medium |
| Testimonials | Detailed customer stories | Medium |
| CTA | Reassurance, guarantee, no-risk statement | Critical |
| Footer | Certifications, policies, contact | Low |
```

### Rationale
ASCII diagrams are human-readable but not machine-parseable. Tables and structured data are more useful for agent consumption and can be programmatically checked.

---

## 3. Add Trigger Conditions Section

### Changes
Add after the "When to Use This Skill" section:

```markdown
## Trigger Conditions

Activate this skill when:

- Designing a landing page, signup flow or checkout
- User reports high bounce rate or cart abandonment
- User asks "how do I build trust?" or "why aren't people converting?"
- Launching a new product or brand with low recognition
- Entering a new market or vertical

Do NOT activate when:

- The user is already seeing high conversion (trust isn't the bottleneck)
- The request is purely about visual design without a conversion goal
- The user wants a general UX audit (use a different skill)
```

### Rationale
Explicit trigger conditions help agents decide when to invoke the skill vs. skip it. Currently the skill relies solely on the description field.

---

## 4. Add Trust Signal Priority Matrix

### Changes
Add a new section after "Context-Specific Trust Strategies":

```markdown
## Trust Signal Priority Matrix

| Context | Must Have | Recommended | Nice-to-Have |
|---------|-----------|-------------|--------------|
| **New brand** | Guarantee, founder story, press mentions | Testimonials, certifications | Video testimonials, case studies |
| **B2B enterprise** | SLAs, security badges, customer logos | Case studies, team photos, API docs | Live chat, trust survey results |
| **E-commerce** | SSL, returns policy, payment logos | Reviews with counts, money-back guarantee | Live activity indicators, trust badges |
| **SaaS / Subscription** | Cancellation policy, billing transparency | Free trial, no commitment | Annual discount, roadmap public |
| **High-value service** | Credentials, portfolio/results | Guarantee, process explanation | Third-party validation, media mentions |
| **Marketplace** | User count, transaction volume | Reviews, verification badges | Dispute resolution, escrow |
```

### Rationale
The current skill describes trust signals in the abstract. A priority matrix makes it actionable for specific contexts — the user picks their context and gets a prioritized checklist.

---

## 5. Add AI Transparency Trust Signals

### Changes
Add a new trust signal category for modern contexts:

```markdown
### 5. AI Transparency Signals

| Signal | When to Use | Example |
|--------|------------|---------|
| AI disclosure | When content is AI-generated | "This page was written with AI assistance" |
| Human review badge | When content is fact-checked by humans | "Fact-checked by our editorial team" |
| Data freshness | When information freshness matters | "Last updated: July 2026" |
| Model disclosure | When AI recommendations are used | "Recommendations powered by an AI model — see how it works" |
| Human-in-the-loop | When decisions involve AI assistance | "A human reviews all output before delivery" |
```

### Rationale
AI transparency is an emerging trust dimension. Users increasingly want to know when they're interacting with AI and disclosure builds credibility rather than eroding it.

---

## 6. Add Anti-Patterns Section

### Changes
Expand the "Trust Killers" section with deeper anti-patterns:

```markdown
## Anti-Patterns

### Trust Theater
Adding trust signals that don't map to real protections. Example: "Trusted by 10,000+ companies" with no names or security badges for a service that doesn't handle payments.
**Fix:** Every trust signal should be verifiable. If a claim can't be substantiated, remove it — unverifiable trust signals destroy trust faster than no trust signals at all.

### Trust Overloading
Too many trust signals competing for attention. Example: 5 security badges + 3 testimonials + a guarantee + certifications all crammed above the fold.
**Fix:** Prioritize 2-3 signals per section. Trust signals lose impact when they become noise rather than cues.

### Trust Asymmetry
Claiming trustworthiness in some areas while being opaque in others. Example: "100% secure" with no privacy policy link or "5-star reviews" with no way to verify them.
**Fix:** If you claim trust, provide mechanisms for verification. Links, references and specific numbers are better than vague superlatives.

### Social Proof Fabrication
Fake reviews, purchased testimonials or stock photo "customers." Once discovered, this destroys all trust permanently.
**Fix:** Only use verifiable social proof. Even a small number of real testimonials beats a large number of fake ones.

### Guarantee Without Teeth
A money-back guarantee that buries return terms in 10 pages of legal jargon or requires the customer to jump through hoops.
**Fix:** Make guarantees easy to understand and easy to use. The friction of claiming should be lower than the friction of not converting.
```

### Rationale
The current "Trust Killers" section covers technical and content issues but misses behavioral and meta-level anti-patterns. Anti-patterns help agents and users avoid subtle trust-building mistakes.

---

## 7. Expand Measurement with Actionable Diagnostics

### Changes
Enhance the measurement section:

```markdown
## Measurement Approaches

### Diagnostic Decision Tree

| Metric | What It Tells You | Next Action |
|--------|-------------------|-------------|
| High bounce + high time on page | Trust signals present but not convincing at decision point | Strengthen CTA trust signals (guarantee, social proof near submit) |
| High bounce + low time on page | Trust signals absent or unconvincing from first impression | Add trust indicators in header and hero section |
| Low bounce + high cart abandonment | Initial trust works, checkout trust failing | Add security signals, payment logos and guarantee near checkout |
| Low bounce + low conversions | Trust signals present, but value proposition unclear | Revisit the value proposition — trust isn't always the bottleneck |
| High support inquiries about trust | Specific trust concerns not addressed on the page | Audit and add the specific missing signals (see Trust Audit Template) |

### Quantitative Metrics

| Metric | What It Indicates | Target |
|--------|-------------------|--------|
| Conversion rate | Overall trust sufficiency | Baseline → +10% after trust improvements |
| Bounce rate | Initial trust impression | < 40% for landing pages |
| Cart abandonment rate | Checkout trust issues | < 70% for e-commerce |
| Time to conversion | Trust-building effectiveness | Decreasing trend |
| Support inquiries | Unaddressed trust concerns | Decreasing trend |

### Qualitative Methods
- Exit surveys on non-converters
- User interviews about hesitations
- Session recordings for friction points
- A/B testing trust signal variations
```

### Rationale
The current measurement section lists metrics without diagnostic guidance. Adding a decision tree makes the data actionable — users can look at their metrics and immediately know what trust signals to adjust.

---

## 8. Add Cross-Skill References and Integration

### Changes
Add a "Related Skills" section:

```markdown
## Related Skills

- **frontend-design** — Trust signals are implemented through UI; use this skill for visual design patterns
- **design-md** — Document trust architecture decisions for the product team
- **prompt-engineering** — Ensure AI-generated content includes trust signals
- **ai-self-reflection** — After a conversion experiment, reflect on what trust signals worked and why
```

### Rationale
Trust Psychology currently operates in isolation. Cross-referencing connects it to the broader skill ecosystem.

---

## 9. Add Modern Trust Contexts

### Changes
Add a new context section:

```markdown
### Regulated Industries

For finance, healthcare and legal contexts:
- Regulatory compliance badges (SOC 2, HIPAA, FINRA)
- License numbers and registration details
- Data handling certifications
- Clear opt-in/opt-out mechanisms

Key message: "We comply with the rules so you don't have to worry."

### Open-Source / Community Trust

- Public roadmap and issue tracker
- Contribution guidelines and code of conduct
- Transparent changelog
- Community governance model

Key message: "We're open about what we do, how we do it and where we're going."

### Sustainability / Social Responsibility

- Carbon-neutral badges
- DEI commitments
- Ethical sourcing statements
- Community impact metrics

Key message: "We stand for something beyond profit."
```

### Rationale
Trust signals have evolved beyond security and social proof. Modern contexts require broader trust dimensions that the current skill doesn't cover.

---

## 10. Version All Sections with Change Management

### Changes
Add version tracking to the SKILL.md:

- At the bottom of each major section, add a `<!-- Last updated: 2026-07-30 | version: 2.0.0 -->` comment
- Maintain a `## Changelog` at the end of the file

### Rationale
Long-lived skills accumulate changes over time. A changelog helps agents know what was added and when and enables rollback if a change causes issues.

---

## Implementation Order

1. Frontmatter triggers + version (trivial edit)
2. Replace ASCII diagrams with structured templates (restructure existing sections)
3. Add trigger conditions section
4. Add trust signal priority matrix (new section)
5. Add AI transparency trust signals (new section)
6. Add anti-patterns section (expand existing trust killers)
7. Expand measurement with diagnostic decision tree
8. Add cross-skill references
9. Add modern trust contexts (regulated, open-source, sustainability)
10. Add changelog + version tracking in sections

### Verification
After implementing:
- All ASCII diagrams should be replaced with parseable tables or JSON
- SKILL.md should have explicit trigger conditions and an exit path
- Every trust signal category should have a modern context (AI, sustainability, etc.)
- The diagnostic decision tree should allow an agent to look at a metric and get a specific action
- Anti-patterns should have "Fix" instructions for each