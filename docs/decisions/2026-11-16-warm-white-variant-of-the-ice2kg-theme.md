# Warm-White Variant Of The ice2kg Theme

**Status:** Accepted
**Date:** 16 November, 2026
**Deciders:** Youpele Michael (with Claude Code)

## Decision

`apps/web` uses ice2kg's theme (`apps/web/src/styles.css`: navy ink `#023d6b`, Manrope, shadcn base-nova)
with warmer whites and neutrals. Inks, primary and destructive colours are unchanged.

| Token | ice2kg | DEMATELab |
| --- | --- | --- |
| `--background` | `#f9fafb` | `#faf8f4` |
| `--card`, `--popover`, `--primary-foreground` | `#ffffff` | `#fffdf9` |
| `--secondary`, `--muted`, `--accent` | `#f3f4f6` | `#f4f1ea` |
| `--soft-2` | `#eceef2` | `#eeeae1` |
| `--border`, `--input` | `#e5e7eb` | `#e8e3d9` |
| `--line-strong` | `#d1d5db` | `#d6cfc2` |
| `--muted-foreground` | `#6b7280` | `#6f6a60` |
| `--ring`, `--placeholder` | `#9ca3af` | `#a39d91` |
| `--sidebar` | `oklch(0.985 0 0)` | `oklch(0.985 0.006 85)` |
| body gradient | `#ffffff` / `#fafafa` / `#f3f4f6` | `#fffdf9` / `#fbf9f5` / `#f4f1ea` |

Domain tokens for cause/effect badges were darkened (lightness only) to pass WCAG AA with their light
foregrounds: `--cause #3f7c52` (4.70:1), `--effect #b65105` (4.64:1). The chart hues rendered by the API
stay Qt's `#4e9965` / `#f97816`. `--cell-edited: #eef4f8`.

## Context

The owner asked for ice2kg's colours with a warmer white. Ink on every surface measures 9.29–10.98:1 and
muted text 4.77–5.29:1. The placeholder colour (`#a39d91`, 2.65:1 on cards) is below AA; it is only used
for placeholder text, as in ice2kg.

## Alternatives Considered

- **ice2kg unchanged:** rejected by the owner (whites too cool).
- **Qt's teal palette:** not requested; the web app follows the ice2kg family look.

## Consequences

- Theme changes go through this table; a failed contrast check may change lightness only.

## Related Work

- Plan: [Rebuild The DEMATELab UI In TanStack Start](../plans/2026-11-16-rebuild-ui-in-tanstack-start-plan.md)
