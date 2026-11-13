# London Reception Admissions Skill

**`london-reception-admissions` turns school policies, supplementary forms, correspondence and tour notes into an actionable application plan and clear English/Chinese communication.**

## Background

The skill grew out of a real London state-primary application preparation. The family lived in a different borough from the school, needed the right entry year and CAF/SIF routes, contacted the office, prepared clergy evidence and attended a school visit.

The observed process reached preparation and the visit. CAF/SIF submission and an admission offer were not verified. This is a preparation and verification workflow, not a claimed admission success story. The published case is anonymised.

## Who can use it

- Parents preparing a London state-primary Reception application, particularly recent arrivals or families needing English-language support.
- Families applying across borough boundaries or interpreting faith-school supplementary evidence.
- Codex, Claude Code, Hermes, OpenClaw and other agents that support `SKILL.md`.

Independent-school, in-year, EHCP and out-of-year applications require their own procedures; the normal Reception route must not be applied automatically.

## What it solves

| Problem | Approach |
|---|---|
| Unclear home-borough versus school-borough route | Verify the residence authority and official application portal |
| CAF, SIF and clergy letter confused | Check purpose, signer, destination, deadline and receipt separately |
| A tour mistaken for an interview | Establish the visit's purpose from the policy and distinguish EAL support |
| Transcript dates or spoken categories conflict with written rules | Record the conflict and verify the year's policy |
| Preparation mistaken for submission or an offer | Track drafts, bookings, visits, submissions, receipts and offers separately |

Outputs include an application brief, actions, concise enquiry/call/follow-up drafts, visit questions and Chinese explanations. Dates and eligibility are checked afresh for the relevant academic year.

## Example

```text
Use $london-reception-admissions to prepare next September's Reception application.
We live in Brent and the school is in Westminster. I have its policy and SIF.
Verify the application routes and deadlines, and draft a concise English enquiry.
```

```text
Use $london-reception-admissions to review this school-tour transcript.
Separate official rules, reported statements and unresolved questions;
produce next actions in English and Chinese.
```

The agent needs web research and file-reading tools. Sending correspondence or submitting an application also needs a suitable connection and explicit user authorization. The skill neither guarantees admission nor automatically contacts a school.

- [Agent instructions](SKILL.md)
- [Anonymised process and lessons](references/case-lessons.md)
- [Application brief template](assets/application-brief.md)
- [中文介绍](README.zh-CN.md)
