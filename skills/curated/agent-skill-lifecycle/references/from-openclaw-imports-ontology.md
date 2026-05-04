# Demoted legacy skill: `openclaw-imports/ontology`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "ontology",
  "installedVersion": "0.1.2",
  "installedAt": 1772274814652
}

```


## `SKILL.md`

````
---
name: ontology
description: Typed knowledge graph for structured agent memory and composable skills. Use when creating/querying entities (Person, Project, Task, Event, Document), linking related objects, enforcing constraints, planning multi-step actions as graph transformations, or when skills need to share state. Trigger on "remember", "what do I know about", "link X to Y", "show dependencies", entity CRUD, or cross-skill data access.
---

# Ontology

A typed vocabulary + constraint system for representing knowledge as a verifiable graph.

## Core Concept

Everything is an **entity** with a **type**, **properties**, and **relations** to other entities. Every mutation is validated against type constraints before committing.

```
Entity: { id, type, properties, relations, created, updated }
Relation: { from_id, relation_type, to_id, properties }
```

## When to Use

| Trigger | Action |
|---------|--------|
| "Remember that..." | Create/update entity |
| "What do I know about X?" | Query graph |
| "Link X to Y" | Create relation |
| "Show all tasks for project Z" | Graph traversal |
| "What depends on X?" | Dependency query |
| Planning multi-step work | Model as graph transformations |
| Skill needs shared state | Read/write ontology objects |

## Core Types

```yaml
# Agents & People
Person: { name, email?, phone?, notes? }
Organization: { name, type?, members[] }

# Work
Project: { name, status, goals[], owner? }
Task: { title, status, due?, priority?, assignee?, blockers[] }
Goal: { description, target_date?, metrics[] }

# Time & Place
Event: { title, start, end?, location?, attendees[], recurrence? }
Location: { name, address?, coordinates? }

# Information
Document: { title, path?, url?, summary? }
Message: { content, sender, recipients[], thread? }
Thread: { subject, participants[], messages[] }
Note: { content, tags[], refs[] }

# Resources
Account: { service, username, credential_ref? }
Device: { name, type, identifiers[] }
Credential: { service, secret_ref }  # Never store secrets directly

# Meta
Action: { type, target, timestamp, outcome? }
Policy: { scope, rule, enforcement }
```

## Storage

Default: `memory/ontology/graph.jsonl`

```jsonl
{"op":"create","entity":{"id":"p_001","type":"Person","properties":{"name":"Alice"}}}
{"op":"create","entity":{"id":"proj_001","type":"Project","properties":{"name":"Website Redesign","status":"active"}}}
{"op":"relate","from":"proj_001","rel":"has_owner","to":"p_001"}
```

Query via scripts or direct file ops. For complex graphs, migrate to SQLite.

### Append-Only Rule

When working with existing ontology data or schema, **append/merge** changes instead of overwriting files. This preserves history and avoids clobbering prior definitions.

## Workflows

### Create Entity

```bash
python3 scripts/ontology.py create --type Person --props '{"name":"Alice","email":"alice@example.com"}'
```

### Query

```bash
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'
python3 scripts/ontology.py get --id task_001
python3 scripts/ontology.py related --id proj_001 --rel has_task
```

### Link Entities

```bash
python3 scripts/ontology.py relate --from proj_001 --rel has_task --to task_001
```

### Validate

```bash
python3 scripts/ontology.py validate  # Check all constraints
```

## Constraints

Define in `memory/ontology/schema.yaml`:

```yaml
types:
  Task:
    required: [title, status]
    status_enum: [open, in_progress, blocked, done]
  
  Event:
    required: [title, start]
    validate: "end >= start if end exists"

  Credential:
    required: [service, secret_ref]
    forbidden_properties: [password, secret, token]  # Force indirection

relations:
  has_owner:
    from_types: [Project, Task]
    to_types: [Person]
    cardinality: many_to_one
  
  blocks:
    from_types: [Task]
    to_types: [Task]
    acyclic: true  # No circular dependencies
```

## Skill Contract

Skills that use ontology should declare:

```yaml
# In SKILL.md frontmatter or header
ontology:
  reads: [Task, Project, Person]
  writes: [Task, Action]
  preconditions:
    - "Task.assignee must exist"
  postconditions:
    - "Created Task has status=open"
```

## Planning as Graph Transformation

Model multi-step plans as a sequence of graph operations:

```
Plan: "Schedule team meeting and create follow-up tasks"

1. CREATE Event { title: "Team Sync", attendees: [p_001, p_002] }
2. RELATE Event -> has_project -> proj_001
3. CREATE Task { title: "Prepare agenda", assignee: p_001 }
4. RELATE Task -> for_event -> event_001
5. CREATE Task { title: "Send summary", assignee: p_001, blockers: [task_001] }
```

Each step is validated before execution. Rollback on constraint violation.

## Integration Patterns

### With Causal Inference

Log ontology mutations as causal actions:

```python
# When creating/updating entities, also log to causal action log
action = {
    "action": "create_entity",
    "domain": "ontology", 
    "context": {"type": "Task", "project": "proj_001"},
    "outcome": "created"
}
```

### Cross-Skill Communication

```python
# Email skill creates commitment
commitment = ontology.create("Commitment", {
    "source_message": msg_id,
    "description": "Send report by Friday",
    "due": "2026-01-31"
})

# Task skill picks it up
tasks = ontology.query("Commitment", {"status": "pending"})
for c in tasks:
    ontology.create("Task", {
        "title": c.description,
        "due": c.due,
        "source": c.id
    })
```

## Quick Start

```bash
# Initialize ontology storage
mkdir -p memory/ontology
touch memory/ontology/graph.jsonl

# Create schema (optional but recommended)
python3 scripts/ontology.py schema-append --data '{
  "types": {
    "Task": { "required": ["title", "status"] },
    "Project": { "required": ["name"] },
    "Person": { "required": ["name"] }
  }
}'

# Start using
python3 scripts/ontology.py create --type Person --props '{"name":"Alice"}'
python3 scripts/ontology.py list --type Person
```

## References

- `references/schema.md` — Full type definitions and constraint patterns
- `references/queries.md` — Query language and traversal examples

## Instruction Scope

Runtime instructions operate on local files (`memory/ontology/graph.jsonl` and `memory/ontology/schema.yaml`) and provide CLI usage for create/query/relate/validate; this is within scope. The skill reads/writes workspace files and will create the `memory/ontology` directory when used. Validation includes property/enum/forbidden checks, relation type/cardinality validation, acyclicity for relations marked `acyclic: true`, and Event `end >= start` checks; other higher-level constraints may still be documentation-only unless implemented in code.

````


## `_meta.json`

```
{
  "ownerId": "kn72dv4fm7ss7swbq47nnpad9x7zy2jh",
  "slug": "ontology",
  "version": "0.1.2",
  "publishedAt": 1770990793271
}
```


## `references/queries.md`

````
# Query Reference

Query patterns and graph traversal examples.

## Basic Queries

### Get by ID

```bash
python3 scripts/ontology.py get --id task_001
```

### List by Type

```bash
# All tasks
python3 scripts/ontology.py list --type Task

# All people
python3 scripts/ontology.py list --type Person
```

### Filter by Properties

```bash
# Open tasks
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'

# High priority tasks
python3 scripts/ontology.py query --type Task --where '{"priority":"high"}'

# Tasks assigned to specific person (by property)
python3 scripts/ontology.py query --type Task --where '{"assignee":"p_001"}'
```

## Relation Queries

### Get Related Entities

```bash
# Tasks belonging to a project (outgoing)
python3 scripts/ontology.py related --id proj_001 --rel has_task

# What projects does this task belong to (incoming)
python3 scripts/ontology.py related --id task_001 --rel part_of --dir incoming

# All relations for an entity (both directions)
python3 scripts/ontology.py related --id p_001 --dir both
```

### Common Patterns

```bash
# Who owns this project?
python3 scripts/ontology.py related --id proj_001 --rel has_owner

# What events is this person attending?
python3 scripts/ontology.py related --id p_001 --rel attendee_of --dir outgoing

# What's blocking this task?
python3 scripts/ontology.py related --id task_001 --rel blocked_by --dir incoming
```

## Programmatic Queries

### Python API

```python
from scripts.ontology import load_graph, query_entities, get_related

# Load the graph
entities, relations = load_graph("memory/ontology/graph.jsonl")

# Query entities
open_tasks = query_entities("Task", {"status": "open"}, "memory/ontology/graph.jsonl")

# Get related
project_tasks = get_related("proj_001", "has_task", "memory/ontology/graph.jsonl")
```

### Complex Queries

```python
# Find all tasks blocked by incomplete dependencies
def find_blocked_tasks(graph_path):
    entities, relations = load_graph(graph_path)
    blocked = []
    
    for entity in entities.values():
        if entity["type"] != "Task":
            continue
        if entity["properties"].get("status") == "blocked":
            # Find what's blocking it
            blockers = get_related(entity["id"], "blocked_by", graph_path, "incoming")
            incomplete_blockers = [
                b for b in blockers 
                if b["entity"]["properties"].get("status") != "done"
            ]
            if incomplete_blockers:
                blocked.append({
                    "task": entity,
                    "blockers": incomplete_blockers
                })
    
    return blocked
```

### Path Queries

```python
# Find path between two entities
def find_path(from_id, to_id, graph_path, max_depth=5):
    entities, relations = load_graph(graph_path)
    
    visited = set()
    queue = [(from_id, [])]
    
    while queue:
        current, path = queue.pop(0)
        
        if current == to_id:
            return path
        
        if current in visited or len(path) >= max_depth:
            continue
        
        visited.add(current)
        
        for rel in relations:
            if rel["from"] == current and rel["to"] not in visited:
                queue.append((rel["to"], path + [rel]))
            if rel["to"] == current and rel["from"] not in visited:
                queue.append((rel["from"], path + [{**rel, "direction": "incoming"}]))
    
    return None  # No path found
```

## Query Patterns by Use Case

### Task Management

```bash
# All my open tasks
python3 scripts/ontology.py query --type Task --where '{"status":"open","assignee":"p_me"}'

# Overdue tasks (requires custom script for date comparison)
# See references/schema.md for date handling

# Tasks with no blockers
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'
# Then filter in code for those with no incoming "blocks" relations
```

### Project Overview

```bash
# All tasks in project
python3 scripts/ontology.py related --id proj_001 --rel has_task

# Project team members
python3 scripts/ontology.py related --id proj_001 --rel has_member

# Project goals
python3 scripts/ontology.py related --id proj_001 --rel has_goal
```

### People & Contacts

```bash
# All people
python3 scripts/ontology.py list --type Person

# People in an organization
python3 scripts/ontology.py related --id org_001 --rel has_member

# What's assigned to this person
python3 scripts/ontology.py related --id p_001 --rel assigned_to --dir incoming
```

### Events & Calendar

```bash
# All events
python3 scripts/ontology.py list --type Event

# Events at a location
python3 scripts/ontology.py related --id loc_001 --rel located_at --dir incoming

# Event attendees
python3 scripts/ontology.py related --id event_001 --rel attendee_of --dir incoming
```

## Aggregations

For complex aggregations, use Python:

```python
from collections import Counter

def task_status_summary(project_id, graph_path):
    """Count tasks by status for a project."""
    tasks = get_related(project_id, "has_task", graph_path)
    statuses = Counter(t["entity"]["properties"].get("status", "unknown") for t in tasks)
    return dict(statuses)

def workload_by_person(graph_path):
    """Count open tasks per person."""
    open_tasks = query_entities("Task", {"status": "open"}, graph_path)
    workload = Counter(t["properties"].get("assignee") for t in open_tasks)
    return dict(workload)
```

````


## `references/schema.md`

````
# Ontology Schema Reference

Full type definitions and constraint patterns for the ontology graph.

## Core Types

### Agents & People

```yaml
Person:
  required: [name]
  properties:
    name: string
    email: string?
    phone: string?
    organization: ref(Organization)?
    notes: string?
    tags: string[]?

Organization:
  required: [name]
  properties:
    name: string
    type: enum(company, team, community, government, other)?
    website: url?
    members: ref(Person)[]?
```

### Work Management

```yaml
Project:
  required: [name]
  properties:
    name: string
    description: string?
    status: enum(planning, active, paused, completed, archived)
    owner: ref(Person)?
    team: ref(Person)[]?
    goals: ref(Goal)[]?
    start_date: date?
    end_date: date?
    tags: string[]?

Task:
  required: [title, status]
  properties:
    title: string
    description: string?
    status: enum(open, in_progress, blocked, done, cancelled)
    priority: enum(low, medium, high, urgent)?
    assignee: ref(Person)?
    project: ref(Project)?
    due: datetime?
    estimate_hours: number?
    blockers: ref(Task)[]?
    tags: string[]?

Goal:
  required: [description]
  properties:
    description: string
    target_date: date?
    status: enum(active, achieved, abandoned)?
    metrics: object[]?
    key_results: string[]?
```

### Time & Location

```yaml
Event:
  required: [title, start]
  properties:
    title: string
    description: string?
    start: datetime
    end: datetime?
    location: ref(Location)?
    attendees: ref(Person)[]?
    recurrence: object?  # iCal RRULE format
    status: enum(confirmed, tentative, cancelled)?
    reminders: object[]?

Location:
  required: [name]
  properties:
    name: string
    address: string?
    city: string?
    country: string?
    coordinates: object?  # {lat, lng}
    timezone: string?
```

### Information

```yaml
Document:
  required: [title]
  properties:
    title: string
    path: string?  # Local file path
    url: url?      # Remote URL
    mime_type: string?
    summary: string?
    content_hash: string?
    tags: string[]?

Message:
  required: [content, sender]
  properties:
    content: string
    sender: ref(Person)
    recipients: ref(Person)[]
    thread: ref(Thread)?
    timestamp: datetime
    platform: string?  # email, slack, whatsapp, etc.
    external_id: string?

Thread:
  required: [subject]
  properties:
    subject: string
    participants: ref(Person)[]
    messages: ref(Message)[]
    status: enum(active, archived)?
    last_activity: datetime?

Note:
  required: [content]
  properties:
    content: string
    title: string?
    tags: string[]?
    refs: ref(Entity)[]?  # Links to any entity
    created: datetime
```

### Resources

```yaml
Account:
  required: [service, username]
  properties:
    service: string  # github, gmail, aws, etc.
    username: string
    url: url?
    credential_ref: ref(Credential)?

Device:
  required: [name, type]
  properties:
    name: string
    type: enum(computer, phone, tablet, server, iot, other)
    os: string?
    identifiers: object?  # {mac, serial, etc.}
    owner: ref(Person)?

Credential:
  required: [service, secret_ref]
  forbidden_properties: [password, secret, token, key, api_key]
  properties:
    service: string
    secret_ref: string  # Reference to secret store (e.g., "keychain:github-token")
    expires: datetime?
    scope: string[]?
```

### Meta

```yaml
Action:
  required: [type, target, timestamp]
  properties:
    type: string  # create, update, delete, send, etc.
    target: ref(Entity)
    timestamp: datetime
    actor: ref(Person|Agent)?
    outcome: enum(success, failure, pending)?
    details: object?

Policy:
  required: [scope, rule]
  properties:
    scope: string  # What this policy applies to
    rule: string   # The constraint in natural language or code
    enforcement: enum(block, warn, log)
    enabled: boolean
```

## Relation Types

### Ownership & Assignment

```yaml
owns:
  from_types: [Person, Organization]
  to_types: [Account, Device, Document, Project]
  cardinality: one_to_many

has_owner:
  from_types: [Project, Task, Document]
  to_types: [Person]
  cardinality: many_to_one

assigned_to:
  from_types: [Task]
  to_types: [Person]
  cardinality: many_to_one
```

### Hierarchy & Containment

```yaml
has_task:
  from_types: [Project]
  to_types: [Task]
  cardinality: one_to_many

has_goal:
  from_types: [Project]
  to_types: [Goal]
  cardinality: one_to_many

member_of:
  from_types: [Person]
  to_types: [Organization]
  cardinality: many_to_many

part_of:
  from_types: [Task, Document, Event]
  to_types: [Project]
  cardinality: many_to_one
```

### Dependencies

```yaml
blocks:
  from_types: [Task]
  to_types: [Task]
  acyclic: true  # Prevents circular dependencies
  cardinality: many_to_many

depends_on:
  from_types: [Task, Project]
  to_types: [Task, Project, Event]
  acyclic: true
  cardinality: many_to_many

requires:
  from_types: [Action]
  to_types: [Credential, Policy]
  cardinality: many_to_many
```

### References

```yaml
mentions:
  from_types: [Document, Message, Note]
  to_types: [Person, Project, Task, Event]
  cardinality: many_to_many

references:
  from_types: [Document, Note]
  to_types: [Document, Note]
  cardinality: many_to_many

follows_up:
  from_types: [Task, Event]
  to_types: [Event, Message]
  cardinality: many_to_one
```

### Events

```yaml
attendee_of:
  from_types: [Person]
  to_types: [Event]
  cardinality: many_to_many
  properties:
    status: enum(accepted, declined, tentative, pending)

located_at:
  from_types: [Event, Person, Device]
  to_types: [Location]
  cardinality: many_to_one
```

## Global Constraints

```yaml
constraints:
  # Credentials must never store secrets directly
  - type: Credential
    rule: "forbidden_properties: [password, secret, token]"
    message: "Credentials must use secret_ref to reference external secret storage"

  # Tasks must have valid status transitions
  - type: Task
    rule: "status transitions: open -> in_progress -> (done|blocked) -> done"
    enforcement: warn

  # Events must have end >= start
  - type: Event
    rule: "if end exists: end >= start"
    message: "Event end time must be after start time"

  # No orphan tasks (should belong to a project or have explicit owner)
  - type: Task
    rule: "has_relation(part_of, Project) OR has_property(owner)"
    enforcement: warn
    message: "Task should belong to a project or have an explicit owner"

  # Circular dependency prevention
  - relation: blocks
    rule: "acyclic"
    message: "Circular task dependencies are not allowed"
```

````


## `scripts/ontology.py`

```
#!/usr/bin/env python3
"""
Ontology graph operations: create, query, relate, validate.

Usage:
    python ontology.py create --type Person --props '{"name":"Alice"}'
    python ontology.py get --id p_001
    python ontology.py query --type Task --where '{"status":"open"}'
    python ontology.py relate --from proj_001 --rel has_task --to task_001
    python ontology.py related --id proj_001 --rel has_task
    python ontology.py list --type Person
    python ontology.py delete --id p_001
    python ontology.py validate
"""

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_GRAPH_PATH = "memory/ontology/graph.jsonl"
DEFAULT_SCHEMA_PATH = "memory/ontology/schema.yaml"


def resolve_safe_path(
    user_path: str,
    *,
    root: Path | None = None,
    must_exist: bool = False,
    label: str = "path",
) -> Path:
    """Resolve user path within root and reject traversal outside it."""
    if not user_path or not user_path.strip():
        raise SystemExit(f"Invalid {label}: empty path")

    safe_root = (root or Path.cwd()).resolve()
    candidate = Path(user_path).expanduser()
    if not candidate.is_absolute():
        candidate = safe_root / candidate

    try:
        resolved = candidate.resolve(strict=False)
    except OSError as exc:
        raise SystemExit(f"Invalid {label}: {exc}") from exc

    try:
        resolved.relative_to(safe_root)
    except ValueError:
        raise SystemExit(
            f"Invalid {label}: must stay within workspace root '{safe_root}'"
        )

    if must_exist and not resolved.exists():
        raise SystemExit(f"Invalid {label}: file not found '{resolved}'")

    return resolved


def generate_id(type_name: str) -> str:
    """Generate a unique ID for an entity."""
    prefix = type_name.lower()[:4]
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{suffix}"


def load_graph(path: str) -> tuple[dict, list]:
    """Load entities and relations from graph file."""
    entities = {}
    relations = []
    
    graph_path = Path(path)
    if not graph_path.exists():
        return entities, relations
    
    with open(graph_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            op = record.get("op")
            
            if op == "create":
                entity = record["entity"]
                entities[entity["id"]] = entity
            elif op == "update":
                entity_id = record["id"]
                if entity_id in entities:
                    entities[entity_id]["properties"].update(record.get("properties", {}))
                    entities[entity_id]["updated"] = record.get("timestamp")
            elif op == "delete":
                entity_id = record["id"]
                entities.pop(entity_id, None)
            elif op == "relate":
                relations.append({
                    "from": record["from"],
                    "rel": record["rel"],
                    "to": record["to"],
                    "properties": record.get("properties", {})
                })
            elif op == "unrelate":
                relations = [r for r in relations 
                           if not (r["from"] == record["from"] 
                                  and r["rel"] == record["rel"] 
                                  and r["to"] == record["to"])]
    
    return entities, relations


def append_op(path: str, record: dict):
    """Append an operation to the graph file."""
    graph_path = Path(path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(graph_path, "a") as f:
        f.write(json.dumps(record) + "\n")


def create_entity(type_name: str, properties: dict, graph_path: str, entity_id: str = None) -> dict:
    """Create a new entity."""
    entity_id = entity_id or generate_id(type_name)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    entity = {
        "id": entity_id,
        "type": type_name,
        "properties": properties,
        "created": timestamp,
        "updated": timestamp
    }
    
    record = {"op": "create", "entity": entity, "timestamp": timestamp}
    append_op(graph_path, record)
    
    return entity


def get_entity(entity_id: str, graph_path: str) -> dict | None:
    """Get entity by ID."""
    entities, _ = load_graph(graph_path)
    return entities.get(entity_id)


def query_entities(type_name: str, where: dict, graph_path: str) -> list:
    """Query entities by type and properties."""
    entities, _ = load_graph(graph_path)
    results = []
    
    for entity in entities.values():
        if type_name and entity["type"] != type_name:
            continue
        
        match = True
        for key, value in where.items():
            if entity["properties"].get(key) != value:
                match = False
                break
        
        if match:
            results.append(entity)
    
    return results


def list_entities(type_name: str, graph_path: str) -> list:
    """List all entities of a type."""
    entities, _ = load_graph(graph_path)
    if type_name:
        return [e for e in entities.values() if e["type"] == type_name]
    return list(entities.values())


def update_entity(entity_id: str, properties: dict, graph_path: str) -> dict | None:
    """Update entity properties."""
    entities, _ = load_graph(graph_path)
    if entity_id not in entities:
        return None
    
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {"op": "update", "id": entity_id, "properties": properties, "timestamp": timestamp}
    append_op(graph_path, record)
    
    entities[entity_id]["properties"].update(properties)
    entities[entity_id]["updated"] = timestamp
    return entities[entity_id]


def delete_entity(entity_id: str, graph_path: str) -> bool:
    """Delete an entity."""
    entities, _ = load_graph(graph_path)
    if entity_id not in entities:
        return False
    
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {"op": "delete", "id": entity_id, "timestamp": timestamp}
    append_op(graph_path, record)
    return True


def create_relation(from_id: str, rel_type: str, to_id: str, properties: dict, graph_path: str):
    """Create a relation between entities."""
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "op": "relate",
        "from": from_id,
        "rel": rel_type,
        "to": to_id,
        "properties": properties,
        "timestamp": timestamp
    }
    append_op(graph_path, record)
    return record


def get_related(entity_id: str, rel_type: str, graph_path: str, direction: str = "outgoing") -> list:
    """Get related entities."""
    entities, relations = load_graph(graph_path)
    results = []
    
    for rel in relations:
        if direction == "outgoing" and rel["from"] == entity_id:
            if not rel_type or rel["rel"] == rel_type:
                if rel["to"] in entities:
                    results.append({
                        "relation": rel["rel"],
                        "entity": entities[rel["to"]]
                    })
        elif direction == "incoming" and rel["to"] == entity_id:
            if not rel_type or rel["rel"] == rel_type:
                if rel["from"] in entities:
                    results.append({
                        "relation": rel["rel"],
                        "entity": entities[rel["from"]]
                    })
        elif direction == "both":
            if rel["from"] == entity_id or rel["to"] == entity_id:
                if not rel_type or rel["rel"] == rel_type:
                    other_id = rel["to"] if rel["from"] == entity_id else rel["from"]
                    if other_id in entities:
                        results.append({
                            "relation": rel["rel"],
                            "direction": "outgoing" if rel["from"] == entity_id else "incoming",
                            "entity": entities[other_id]
                        })
    
    return results


def validate_graph(graph_path: str, schema_path: str) -> list:
    """Validate graph against schema constraints."""
    entities, relations = load_graph(graph_path)
    errors = []
    
    # Load schema if exists
    schema = load_schema(schema_path)
    
    type_schemas = schema.get("types", {})
    relation_schemas = schema.get("relations", {})
    global_constraints = schema.get("constraints", [])
    
    for entity_id, entity in entities.items():
        type_name = entity["type"]
        type_schema = type_schemas.get(type_name, {})
        
        # Check required properties
        required = type_schema.get("required", [])
        for prop in required:
            if prop not in entity["properties"]:
                errors.append(f"{entity_id}: missing required property '{prop}'")
        
        # Check forbidden properties
        forbidden = type_schema.get("forbidden_properties", [])
        for prop in forbidden:
            if prop in entity["properties"]:
                errors.append(f"{entity_id}: contains forbidden property '{prop}'")
        
        # Check enum values
        for prop, allowed in type_schema.items():
            if prop.endswith("_enum"):
                field = prop.replace("_enum", "")
                value = entity["properties"].get(field)
                if value and value not in allowed:
                    errors.append(f"{entity_id}: '{field}' must be one of {allowed}, got '{value}'")
    
    # Relation constraints (type + cardinality + acyclicity)
    rel_index = {}
    for rel in relations:
        rel_index.setdefault(rel["rel"], []).append(rel)
    
    for rel_type, rel_schema in relation_schemas.items():
        rels = rel_index.get(rel_type, [])
        from_types = rel_schema.get("from_types", [])
        to_types = rel_schema.get("to_types", [])
        cardinality = rel_schema.get("cardinality")
        acyclic = rel_schema.get("acyclic", False)
        
        # Type checks
        for rel in rels:
            from_entity = entities.get(rel["from"])
            to_entity = entities.get(rel["to"])
            if not from_entity or not to_entity:
                errors.append(f"{rel_type}: relation references missing entity ({rel['from']} -> {rel['to']})")
                continue
            if from_types and from_entity["type"] not in from_types:
                errors.append(
                    f"{rel_type}: from entity {rel['from']} type {from_entity['type']} not in {from_types}"
                )
            if to_types and to_entity["type"] not in to_types:
                errors.append(
                    f"{rel_type}: to entity {rel['to']} type {to_entity['type']} not in {to_types}"
                )
        
        # Cardinality checks
        if cardinality in ("one_to_one", "one_to_many", "many_to_one"):
            from_counts = {}
            to_counts = {}
            for rel in rels:
                from_counts[rel["from"]] = from_counts.get(rel["from"], 0) + 1
                to_counts[rel["to"]] = to_counts.get(rel["to"], 0) + 1
            
            if cardinality in ("one_to_one", "many_to_one"):
                for from_id, count in from_counts.items():
                    if count > 1:
                        errors.append(f"{rel_type}: from entity {from_id} violates cardinality {cardinality}")
            if cardinality in ("one_to_one", "one_to_many"):
                for to_id, count in to_counts.items():
                    if count > 1:
                        errors.append(f"{rel_type}: to entity {to_id} violates cardinality {cardinality}")
        
        # Acyclic checks
        if acyclic:
            graph = {}
            for rel in rels:
                graph.setdefault(rel["from"], []).append(rel["to"])
            
            visited = {}
            
            def dfs(node, stack):
                visited[node] = True
                stack.add(node)
                for nxt in graph.get(node, []):
                    if nxt in stack:
                        return True
                    if not visited.get(nxt, False):
                        if dfs(nxt, stack):
                            return True
                stack.remove(node)
                return False
            
            for node in graph:
                if not visited.get(node, False):
                    if dfs(node, set()):
                        errors.append(f"{rel_type}: cyclic dependency detected")
                        break
    
    # Global constraints (limited enforcement)
    for constraint in global_constraints:
        ctype = constraint.get("type")
        relation = constraint.get("relation")
        rule = (constraint.get("rule") or "").strip().lower()
        if ctype == "Event" and "end" in rule and "start" in rule:
            for entity_id, entity in entities.items():
                if entity["type"] != "Event":
                    continue
                start = entity["properties"].get("start")
                end = entity["properties"].get("end")
                if start and end:
                    try:
                        start_dt = datetime.fromisoformat(start)
                        end_dt = datetime.fromisoformat(end)
                        if end_dt < start_dt:
                            errors.append(f"{entity_id}: end must be >= start")
                    except ValueError:
                        errors.append(f"{entity_id}: invalid datetime format in start/end")
        if relation and rule == "acyclic":
            # Already enforced above via relations schema
            continue
    
    return errors


def load_schema(schema_path: str) -> dict:
    """Load schema from YAML if it exists."""
    schema = {}
    schema_file = Path(schema_path)
    if schema_file.exists():
        import yaml
        with open(schema_file) as f:
            schema = yaml.safe_load(f) or {}
    return schema


def write_schema(schema_path: str, schema: dict) -> None:
    """Write schema to YAML."""
    schema_file = Path(schema_path)
    schema_file.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(schema_file, "w") as f:
        yaml.safe_dump(schema, f, sort_keys=False)


def merge_schema(base: dict, incoming: dict) -> dict:
    """Merge incoming schema into base, appending lists and deep-merging dicts."""
    for key, value in (incoming or {}).items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = merge_schema(base[key], value)
        elif key in base and isinstance(base[key], list) and isinstance(value, list):
            base[key] = base[key] + [v for v in value if v not in base[key]]
        else:
            base[key] = value
    return base


def append_schema(schema_path: str, incoming: dict) -> dict:
    """Append/merge schema fragment into existing schema."""
    base = load_schema(schema_path)
    merged = merge_schema(base, incoming)
    write_schema(schema_path, merged)
    return merged


def main():
    parser = argparse.ArgumentParser(description="Ontology graph operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Create
    create_p = subparsers.add_parser("create", help="Create entity")
    create_p.add_argument("--type", "-t", required=True, help="Entity type")
    create_p.add_argument("--props", "-p", default="{}", help="Properties JSON")
    create_p.add_argument("--id", help="Entity ID (auto-generated if not provided)")
    create_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Get
    get_p = subparsers.add_parser("get", help="Get entity by ID")
    get_p.add_argument("--id", required=True, help="Entity ID")
    get_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Query
    query_p = subparsers.add_parser("query", help="Query entities")
    query_p.add_argument("--type", "-t", help="Entity type")
    query_p.add_argument("--where", "-w", default="{}", help="Filter JSON")
    query_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # List
    list_p = subparsers.add_parser("list", help="List entities")
    list_p.add_argument("--type", "-t", help="Entity type")
    list_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Update
    update_p = subparsers.add_parser("update", help="Update entity")
    update_p.add_argument("--id", required=True, help="Entity ID")
    update_p.add_argument("--props", "-p", required=True, help="Properties JSON")
    update_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Delete
    delete_p = subparsers.add_parser("delete", help="Delete entity")
    delete_p.add_argument("--id", required=True, help="Entity ID")
    delete_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Relate
    relate_p = subparsers.add_parser("relate", help="Create relation")
    relate_p.add_argument("--from", dest="from_id", required=True, help="From entity ID")
    relate_p.add_argument("--rel", "-r", required=True, help="Relation type")
    relate_p.add_argument("--to", dest="to_id", required=True, help="To entity ID")
    relate_p.add_argument("--props", "-p", default="{}", help="Relation properties JSON")
    relate_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Related
    related_p = subparsers.add_parser("related", help="Get related entities")
    related_p.add_argument("--id", required=True, help="Entity ID")
    related_p.add_argument("--rel", "-r", help="Relation type filter")
    related_p.add_argument("--dir", "-d", choices=["outgoing", "incoming", "both"], default="outgoing")
    related_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    
    # Validate
    validate_p = subparsers.add_parser("validate", help="Validate graph")
    validate_p.add_argument("--graph", "-g", default=DEFAULT_GRAPH_PATH)
    validate_p.add_argument("--schema", "-s", default=DEFAULT_SCHEMA_PATH)

    # Schema append
    schema_p = subparsers.add_parser("schema-append", help="Append/merge schema fragment")
    schema_p.add_argument("--schema", "-s", default=DEFAULT_SCHEMA_PATH)
    schema_p.add_argument("--data", "-d", help="Schema fragment as JSON")
    schema_p.add_argument("--file", "-f", help="Schema fragment file (YAML or JSON)")
    
    args = parser.parse_args()
    workspace_root = Path.cwd().resolve()

    if hasattr(args, "graph"):
        args.graph = str(
            resolve_safe_path(args.graph, root=workspace_root, label="graph path")
        )
    if hasattr(args, "schema"):
        args.schema = str(
            resolve_safe_path(args.schema, root=workspace_root, label="schema path")
        )
    if hasattr(args, "file") and args.file:
        args.file = str(
            resolve_safe_path(
                args.file, root=workspace_root, must_exist=True, label="schema file"
            )
        )
    
    if args.command == "create":
        props = json.loads(args.props)
        entity = create_entity(args.type, props, args.graph, args.id)
        print(json.dumps(entity, indent=2))
    
    elif args.command == "get":
        entity = get_entity(args.id, args.graph)
        if entity:
            print(json.dumps(entity, indent=2))
        else:
            print(f"Entity not found: {args.id}")
    
    elif args.command == "query":
        where = json.loads(args.where)
        results = query_entities(args.type, where, args.graph)
        print(json.dumps(results, indent=2))
    
    elif args.command == "list":
        results = list_entities(args.type, args.graph)
        print(json.dumps(results, indent=2))
    
    elif args.command == "update":
        props = json.loads(args.props)
        entity = update_entity(args.id, props, args.graph)
        if entity:
            print(json.dumps(entity, indent=2))
        else:
            print(f"Entity not found: {args.id}")
    
    elif args.command == "delete":
        if delete_entity(args.id, args.graph):
            print(f"Deleted: {args.id}")
        else:
            print(f"Entity not found: {args.id}")
    
    elif args.command == "relate":
        props = json.loads(args.props)
        rel = create_relation(args.from_id, args.rel, args.to_id, props, args.graph)
        print(json.dumps(rel, indent=2))
    
    elif args.command == "related":
        results = get_related(args.id, args.rel, args.graph, args.dir)
        print(json.dumps(results, indent=2))
    
    elif args.command == "validate":
        errors = validate_graph(args.graph, args.schema)
        if errors:
            print("Validation errors:")
            for err in errors:
                print(f"  - {err}")
        else:
            print("Graph is valid.")
    
    elif args.command == "schema-append":
        if not args.data and not args.file:
            raise SystemExit("schema-append requires --data or --file")
        
        incoming = {}
        if args.data:
            incoming = json.loads(args.data)
        else:
            path = Path(args.file)
            if path.suffix.lower() == ".json":
                with open(path) as f:
                    incoming = json.load(f)
            else:
                import yaml
                with open(path) as f:
                    incoming = yaml.safe_load(f) or {}
        
        merged = append_schema(args.schema, incoming)
        print(json.dumps(merged, indent=2))


if __name__ == "__main__":
    main()

```
