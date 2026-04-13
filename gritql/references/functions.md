# GritQL Functions Reference

## Built-in Functions

### String Functions

```grit
capitalize(string=$s)        // "hello" -> "Hello"
uppercase(string=$s)         // "hello" -> "HELLO"
lowercase(string=$s)         // "HELLO" -> "hello"
trim(string=$s)              // remove leading/trailing whitespace
trim(string=$s, trim_chars=",")  // remove specific chars
join(list=$items, separator=", ")  // ["a","b"] -> "a, b"
split(string=$s, separator=",")   // "a,b" -> ["a", "b"]
```

Example — capitalize a method name during rename:
```grit
`get$_Prop` where {
  $propName = capitalize(string=$prop)
} => `get$propName`
```

### List Functions

```grit
length(target=$list)         // number of elements
shuffle(target=$list)        // randomize order
distinct(list=$list)         // remove duplicates
```

### Code Utility Functions

```grit
text($node)                  // get current source text of a node as a string
todo(target=$code, message="needs review")   // mark for manual follow-up
log(message="debug", variable=$var)          // debug logging during pattern execution
```

`text()` is useful when you need the string value to compute something, not just match:
```grit
`$fn($args)` where {
  $fn_text = text($fn),
  $new_name = uppercase(string=$fn_text)
} => `$new_name($args)`
```

### Utility Functions

```grit
random()                     // float 0.0–1.0
random(min=1, max=10)        // int in range
resolve(path="./utils.js")   // resolve relative path to absolute
```

---

## Custom Functions

Define reusable transformation logic:

```grit
function to_camel_case($name) {
  // $name.text gives the string value
  // return must be a stringable value
  return capitalize(string=$name)
}

`get_$prop_name` where {
  $camel = to_camel_case($prop_name)
} => `get$camel`
```

**JavaScript functions** (for complex logic):
```grit
function pluralize($word) js {
  const w = $word.text;
  return w.endsWith('y') ? w.slice(0, -1) + 'ies' : w + 's';
}
```

Note: JS functions receive GritQL node objects; use `.text` to get string value.

---

## Custom Predicates

Predicates are boolean-returning functions — they succeed or fail rather than returning a value. Use them to encapsulate reusable conditions:

```grit
predicate is_react_component($name) {
  $name <: r"^[A-Z]",
  $name <: not r"^(HTML|SVG|Math)"
}

predicate has_side_effects($body) {
  $body <: or {
    contains `fetch($__)`,
    contains `localStorage.$_($_)`,
    contains `document.$_`
  }
}

// Usage:
`function $name($_) { $body }` where {
  is_react_component($name),
  not has_side_effects($body)
}
```

---

## Accumulation Pattern

Use `+=` to build up lists or strings across multiple matches (common in `multifile` or `bubble` patterns):

```grit
`export { $names }` where {
  $collected_names = [],
  $names <: some bubble($collected_names) `$name` where {
    $collected_names += $name
  },
  $joined = join(list=$collected_names, separator=", ")
} => `export { $joined }`
```

Accumulation with `$GLOBAL_` for cross-match state:
```grit
`import { $_ } from '$pkg'` where {
  $GLOBAL_IMPORTS += $pkg
}
```
