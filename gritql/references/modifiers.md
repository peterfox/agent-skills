# GritQL Modifiers Reference

## Tree Traversal

### `contains`
Match a node that contains the given pattern somewhere in its subtree (searches downward):
```grit
`function $name($_) { $_ }` where {
  $name <: contains `async`
}

// More common: find code within a containing structure
`$fn()` where {
  $fn <: within `try { $_ } catch ($_) { $_ }`
}
```

**`contains ... until`** — stop traversal at a boundary node:
```grit
contains `$x = $_` until `function $_($_) { $_ }`
```

### `within`
Match a node only when it appears inside the given pattern (searches upward):
```grit
`console.log($msg)` => `console.error($msg)` where {
  `console.log($msg)` <: within `catch ($e) { $_ }`
}
```

---

## Logical Operators

### `and`
All conditions must match (same as comma-separated conditions in `where`):
```grit
`$fn($args)` where {
  $fn <: and {
    contains `fetch`,
    not `fetchUser`
  }
}
```

### `or`
First matching branch wins (short-circuits). Can include rewrites:
```grit
$level <: or {
  `"info"` => `"debug"`,
  `"warn"` => `"warning"`,
  `"error"` => `"critical"`
}
```

### `any`
Like `or` but does **not** short-circuit — all matching branches execute. Use when you want multiple rewrites to apply in a single pass:
```grit
any {
  `React.useState` => `useState`,
  `React.useEffect` => `useEffect`,
  `React.useMemo` => `useMemo`
}
```

### `not`
Negates a pattern or condition:
```grit
`$fn($args)` where {
  not $fn <: `console.log`
}
```

### `maybe`
Succeeds even if the inner pattern doesn't match. Useful for optional transformations:
```grit
`import $name from '$src'` where {
  maybe $name <: `React` => `React_renamed`
}
```

---

## List Operators

### `some`
At least one element in a list matches:
```grit
`[$items]` where {
  $items <: some `null`
}
```

### `every`
All elements in a list match:
```grit
`[$items]` where {
  $items <: every r"\d+"
}
```

---

## Execution Control

### `sequential`
Apply patterns in order — each step sees the output of the previous. Useful for multi-pass transforms:
```grit
sequential {
  bubble file($body) where $body <: contains `var ` => `let `,
  bubble file($body) where $body <: contains `let $x = $fn()` where {
    $fn <: `fetch`
  } => `const $x = await $fn()`
}
```

### `multifile`
Operate across multiple files with shared state (e.g., collecting imports globally):
```grit
multifile {
  bubble($exports) file($name, $body) where {
    $body <: contains `export function $fn($_) { $_ }`,
    $exports += $fn
  },
  bubble($exports) file($name, $body) where {
    $name <: `index.ts`,
    $body => `export { $exports }`
  }
}
```

---

## Scope Control

### `bubble`
Isolates metavariable scope so each match is independent. Without `bubble`, a bound `$name` in one match prevents other matches with different values:

```grit
// Without bubble: $x binds once, all matches must have same $x
`foo($x)` => `bar($x)`

// With bubble: each match gets its own $x binding
bubble `foo($x)` => `bar($x)`
```

Automatically applied when a pattern is used at top level (file-level auto-wrap), but must be explicit inside `sequential` or `multifile`.

**`bubble(args)`** — pass variables through the bubble boundary:
```grit
bubble($shared_var) `foo($x)` where {
  $shared_var += $x
}
```

---

## Position Operators

### `after`
Match nodes that appear directly after a given pattern, or retrieve the next sibling:
```grit
`$b` where {
  $b <: after `const $a = $_`
}
```

### `before`
Match nodes that appear directly before a given pattern, or retrieve the previous sibling:
```grit
`$a` where {
  $a <: before `return $_`
}
```

---

## `limit`
Restrict total matches globally (useful for incremental rollouts):
```grit
`console.log($msg)` => `logger.log($msg)` limit 10
```

---

## `range`
Match by source location (line/column):
```grit
range(start_line=1, end_line=50)
```
