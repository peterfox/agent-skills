# GritQL Refactoring Examples

## Table of Contents
1. [Logging / Console](#logging--console)
2. [Import Rewrites](#import-rewrites)
3. [API Migrations](#api-migrations)
4. [React Modernization](#react-modernization)
5. [Function/Variable Renaming](#functionvariable-renaming)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Multi-step Transforms](#multi-step-transforms)
8. [File Creation / Splitting](#file-creation--splitting)
9. [Python Patterns](#python-patterns)
10. [Multi-language / Polyglot](#multi-language--polyglot)

---

## Logging / Console

Replace all `console.log` with a logger:
```grit
`console.log($msg)` => `logger.debug($msg)`
```

Replace specific console methods, mapping to different log levels:
```grit
`console.$method($args)` => `logger.$method($args)` where {
  $method <: or {
    `log` => `debug`,
    `warn` => `warning`,
    `error` => `error`
  }
}
```

Only replace console.log inside catch blocks (context-aware):
```grit
`console.log($msg)` => `logger.error($msg)` where {
  `console.log($msg)` <: within `catch ($e) { $_ }`
}
```

Remove all debug logging:
```grit
`console.log($__)` => .
```

---

## Import Rewrites

Rename a package:
```grit
`import $imports from 'old-package'` => `import $imports from 'new-package'`
```

Move a named export to a different package:
```grit
`import { $_, Router, $_ } from 'react-router'` => `import { $_, Router, $_ } from 'react-router-dom'`
```

Add a missing import if a symbol is used but not imported:
```grit
`useEffect($__)` where {
  $program <: not contains `import { $_, useEffect, $_ } from 'react'`,
  $program <: contains `import { $existing } from 'react'`
} where {
  $existing => `$existing, useEffect`
}
```

Remove an unused import:
```grit
`import $_ from 'deprecated-lib'` => .
```

Convert default import to named import:
```grit
`import Foo from 'foo'` => `import { Foo } from 'foo'`
```

---

## API Migrations

Callback to Promise (Node.js style):
```grit
`$obj.$method($args, function($err, $result) { $body })` => 
  `$obj.$method($args).then(($result) => { $body }).catch(($err) => { throw $err })`
```

jQuery to vanilla DOM:
```grit
`$('$selector').on('$event', $handler)` =>
  `document.querySelector('$selector').addEventListener('$event', $handler)`
```

Fetch with `.then()` to async/await:
```grit
`$fn().then($callback)` => `await $fn()` where {
  $callback <: `($result) => { $body }`
}
```

Moment.js to date-fns:
```grit
`moment($date).format($fmt)` => `format(new Date($date), $fmt)` where {
  $program <: not contains `import { format } from 'date-fns'`,
  $new_files += file(name=`date-fns-imports.js`, body=`import { format } from 'date-fns';\n`)
}
```

---

## React Modernization

Replace React namespace with named imports (React 17+):
```grit
any {
  `React.useState` => `useState`,
  `React.useEffect` => `useEffect`,
  `React.useCallback` => `useCallback`,
  `React.useMemo` => `useMemo`,
  `React.useRef` => `useRef`,
  `React.useContext` => `useContext`
}
```

Class component method to arrow function (remove `.bind(this)`):
```grit
`this.$method = this.$method.bind(this)` => . where {
  $method <: not `constructor`
}
```

PropTypes migration — remove PropTypes usage:
```grit
or {
  `$Component.propTypes = $_` => .,
  `import PropTypes from 'prop-types'` => .
}
```

Replace `React.FC` with plain function type:
```grit
`const $name: React.FC<$props> = ($params) => { $body }` =>
  `function $name($params: $props) { $body }`
```

---

## Function/Variable Renaming

Rename a function and all its callsites:
```grit
or {
  `function getUserData($args) { $body }` => `function fetchUser($args) { $body }`,
  `getUserData($args)` => `fetchUser($args)`
}
```

Rename a method on a specific class (using `within` for scope):
```grit
`this.$method($args)` => `this.newMethodName($args)` where {
  $method <: `oldMethodName`,
  `this.$method($args)` <: within `class MyClass { $_ }`
}
```

Snake_case to camelCase variable rename:
```grit
`$old_name` where {
  $old_name <: r"^([a-z]+)_([a-z]+)$"($prefix, $suffix),
  $new_name = join(list=[$prefix, capitalize(string=$suffix)], separator="")
} => `$new_name`
```

---

## Error Handling Patterns

Wrap unguarded async calls in try/catch:
```grit
`async function $name($params) { $body }` where {
  not $body <: contains `try { $_ } catch ($_) { $_ }`
} => `async function $name($params) {
  try {
    $body
  } catch (error) {
    logger.error(error);
    throw error;
  }
}`
```

Replace bare `throw` with typed error:
```grit
`throw '$message'` => `throw new Error('$message')`
`throw "$message"` => `throw new Error("$message")`
```

---

## Multi-step Transforms

Two-pass migration (use `sequential`):
```grit
sequential {
  // Pass 1: rename the import
  bubble file($body) where $body <: contains 
    `import $x from 'old-lib'` => `import $x from 'new-lib'`,
  // Pass 2: update the API usage
  bubble file($body) where $body <: contains
    `$x.oldMethod($args)` => `$x.newMethod($args)`
}
```

Accumulate and deduplicate imports across files:
```grit
multifile {
  bubble($seen) file($name, $body) where {
    $body <: contains `import { $sym } from 'shared'`,
    not $seen <: some `$sym`,
    $seen += $sym
  }
}
```

---

## File Creation / Splitting

Extract test functions to separate test files:
```grit
`function $name($_) { $_ }` as $fn where {
  $name <: r"^test",
  $fn => .,
  $new_files += file(name=`$name.test.js`, body=$fn)
}
```

Generate an index file that re-exports everything:
```grit
file($name, $body) where {
  $body <: contains `export function $fn($_) { $_ }`,
  $new_files += file(name=`index.js`, body=`export { $fn } from './$name'`)
}
```

---

## Python Patterns

```grit
language python

// Replace print with logging
`print($msg)` => `logger.info($msg)`

// Rename method
`$obj.old_method($args)` => `$obj.new_method($args)`

// f-string migration from .format()
`"$template".format($args)` => `f"$template"`

// Add type hints to function parameters
`def $name($params):` where {
  $params <: not contains `: `
}
```

---

## Multi-language / Polyglot

Run different rewrites per language in the same `.grit` file:

```grit
// In your .grit/patterns/ directory, create per-language files
// or use language-specific snippet prefixes:

or {
  js`console.log($msg)` => js`logger.debug($msg)`,
  py`print($msg)` => py`logger.debug($msg)`
}
```

Match TypeScript-specific syntax:
```grit
language typescript

`interface $name { $fields }` where {
  $fields <: contains `$prop: string`
} => `type $name = { $fields }`
```

---

## Tips for Writing New Patterns

1. **Start with the simplest possible match** — add constraints only when you see false positives
2. **Use `--dry-run`** to preview changes: `grit apply my-pattern --dry-run`
3. **Test on a single file first**: `grit apply my-pattern path/to/file.js`
4. **Combine `not contains` + `within`** to scope changes to specific areas
5. **Use `limit N`** for staged rollouts of large-scale changes
6. **`as $var`** lets you reference the whole matched node in the `where` clause
