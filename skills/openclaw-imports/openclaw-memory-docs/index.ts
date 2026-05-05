import path from "node:path";
import os from "node:os";

import {
  DefaultRedactor,
  HashEmbedder,
  JsonlMemoryStore,
  uuid,
  type MemoryItem,
} from "@elvatis_com/openclaw-memory-core";

function expandHome(p: string): string {
  if (!p) return p;
  if (p === "~") return os.homedir();
  if (p.startsWith("~/")) return path.join(os.homedir(), p.slice(2));
  return p;
}

export default function register(api: any) {
  const cfg = (api.pluginConfig ?? {}) as {
    enabled?: boolean;
    storePath?: string;
    dims?: number;
    redactSecrets?: boolean;
    defaultTags?: string[];
  };

  if (cfg.enabled === false) return;

  const storePath = expandHome(cfg.storePath ?? "~/.openclaw/workspace/memory/docs-memory.jsonl");
  const embedder = new HashEmbedder(cfg.dims ?? 256);
  const store = new JsonlMemoryStore({ filePath: storePath, embedder });
  const redactor = new DefaultRedactor();
  const defaultTags = cfg.defaultTags ?? ["docs"];
  const redactSecrets = cfg.redactSecrets !== false;

  api.logger?.info?.(`[memory-docs] enabled. store=${storePath}`);

  // Command: /remember-doc <text>
  api.registerCommand({
    name: "remember-doc",
    description: "Save a documentation memory item (explicit capture)",
    requireAuth: false,
    acceptsArgs: true,
    handler: async (ctx: any) => {
      const text = String(ctx?.args ?? "").trim();
      if (!text) {
        return { text: "Usage: /remember-doc <text>" };
      }

      const r = redactSecrets ? redactor.redact(text) : { redactedText: text, hadSecrets: false, matches: [] };
      const item: MemoryItem = {
        id: uuid(),
        kind: "doc",
        text: r.redactedText,
        createdAt: new Date().toISOString(),
        tags: defaultTags,
        source: {
          channel: ctx?.channel,
          from: ctx?.from,
          conversationId: ctx?.conversationId,
          messageId: ctx?.messageId,
        },
        meta: r.hadSecrets ? { redaction: { hadSecrets: true, matches: r.matches } } : undefined,
      };

      await store.add(item);

      const note = r.hadSecrets
        ? " (note: secrets were redacted)"
        : "";
      return { text: `Saved docs memory.${note}` };
    },
  });

  // Tool: docs_memory_search
  api.registerTool({
    name: "docs_memory_search",
    description: "Search documentation memory items (local JSONL store)",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        query: { type: "string" },
        limit: { type: "number", minimum: 1, maximum: 20, default: 5 },
      },
      required: ["query"],
    },
    handler: async (params: any) => {
      const q = String(params.query ?? "").trim();
      const limit = Number(params.limit ?? 5);
      if (!q) return { hits: [] };

      const hits = await store.search(q, { limit });
      return {
        storePath,
        hits: hits.map((h) => ({
          score: h.score,
          id: h.item.id,
          createdAt: h.item.createdAt,
          tags: h.item.tags,
          text: h.item.text,
        })),
      };
    },
  });
}
