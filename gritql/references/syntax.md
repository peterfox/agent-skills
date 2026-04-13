# GritQL Syntax Reference

## Pattern Types

### Code Snippet Patterns (most common)
Backtick patterns match AST nodes structurally — whitespace and formatting are ignored:
```grit
`console.log($message)`
`foo($a, $b)`
`import $name from '$source'`
```

Language-annotated snippets (for polyglot files or explicit clarity):
```grit
js`console.log($msg)`
py`print($msg)`
```

Raw output (skip validation, useful for generating non-parseable fragments):
```grit
raw`/* generated code */`
```

### AST Node Patterns
Match by syntax tree node type (language-specific):
```grit
call_expression(callee=$fn, arguments=$args)
arrow_function($body)
import_declaration()
```

Find available node types via `grit list` or the tree-sitter grammar for the target language.

### Regular Expressions
```grit
r"pattern"                    // match text
r"Hello, (.*)"($greeting)    // named capture group
```

Used in `where` clauses to assert on metavariable values:
```grit
`function $name($_) { $_ }` where {
  $name <: r"test.*"
}
```

---

## Metavariables

| Syntax | Meaning |
|--------|---------|
| `$name` | Binds to matched node; reuse enforces same value |
| `$_` | Anonymous — matches anything, no binding |
| `$...args` | Spread — matches 0+ nodes (for argument lists, statement sequences) |
| `$GLOBAL_name` | Global scope — shared across the whole file in multifile patterns |

Reserved: `$filename`, `$new_files`, `$program`, any `$grit_*` prefix.

**Important**: once `$name` is bound in a file, it must match the same value wherever it appears in that pattern. Use `bubble` to reset scope per match.

---

## Rewrites

Basic rewrite:
```grit
`console.log($msg)` => `logger.debug($msg)`
```

Delete a node (right-hand side only):
```grit
`debugger` => .
```

Rewrite inside `where` clause (also acts as a condition — fails if rewrite can't apply):
```grit
`$obj.$method($args)` where {
  $method => `newMethod`
}
```

Rewrite a metavariable conditionally:
```grit
`console.$method($msg)` => `winston.$method($msg)` where {
  $method <: or {
    `log` => `debug`,
    `error` => `warn`,
    `warn` => `info`
  }
}
```

---

## Where Clauses

```grit
pattern where {
  condition1,
  condition2   // comma = AND
}
```

**Match operator** (`<:`):
```grit
$x <: `"some literal"`
$name <: r"^use[A-Z]"    // React hook name check
$x <: not `null`
```

**Assignment**:
```grit
$new_var = "computed value"
$list += $item             // accumulate into list
$str += " appended"        // accumulate into string
```

**If/else**:
```grit
if ($condition) {
  $var => `true_branch`
} else {
  $var => `false_branch`
}
```

---

## Primitive Types

**Strings** (language-agnostic):
```grit
"hello"
```

**Numbers**:
```grit
42        // int
3.14      // double
```

**Lists**:
```grit
[1, 2, 3]
$list[0]    // index access
$list[-1]   // last element
```

**Maps**:
```grit
{ key: "value", other: 42 }
$map.key    // dot access
```

---

## File and Program Patterns

Match across a whole file:
```grit
file($name, $body) where {
  $name <: r".*\.test\.js",
  $body <: contains `describe($_, $_)`
}
```

Access entire program as a string:
```grit
`import $_ from '$src'` where {
  $program <: not contains `export default`
}
```

Create new files:
```grit
`function $name($_) { $_ }` as $fn where {
  $name <: r"test.*",
  $fn => .,
  $new_files += file(name=`$name.test.js`, body=$fn)
}
```

---

## Pattern Definitions and Reuse

Named patterns (reusable across a codebase via `.grit/` config):
```grit
pattern replace_console_with_logger() {
  `console.$method($args)` => `logger.$method($args)`
}
```

Parameterized patterns:
```grit
pattern rename_import($old, $new) {
  `import $x from '$old'` => `import $x from '$new'`
}

// Usage:
rename_import(old=`"react-router"`, new=`"react-router-dom"`)
```

**Predicate definitions** (boolean-returning):
```grit
predicate is_test_file() {
  $filename <: r".*\.test\.[jt]sx?"
}

`console.log($msg)` where {
  is_test_file()
}
```

---

## `as` Binding

Bind the entire matched node to a variable for later use:
```grit
`function $name($args) { $body }` as $fn where {
  $fn => `const $name = ($args) => { $body }`
}
```
