# phpstan/phpstan-webmozart-assert Extension

This extension teaches PHPStan to perform **type narrowing** after `Assert::*()` calls,
so that code following an assertion is analysed with the refined type rather than the
original broad type.

## Installation

```bash
composer require --dev phpstan/phpstan-webmozart-assert
```

**With `phpstan/extension-installer`** (recommended): the extension registers itself
automatically — nothing else to do.

**Without `extension-installer`**: add it manually to `phpstan.neon`:

```neon
includes:
    - vendor/phpstan/phpstan-webmozart-assert/extension.neon
```

**Requirements:** PHP 7.4+, `webmozart/assert` 1.11.0 or 2.0+.

## How type narrowing works

The extension translates Assert calls into equivalent PHP expressions that PHPStan's own
type system already understands:

```
Assert::integer($a)         →  is_int($a)
Assert::stringNotEmpty($a)  →  is_string($a) && $a !== ''
Assert::isList($a)          →  array_is_list($a)
Assert::isInstanceOf($a, Foo::class)  →  $a instanceof Foo
```

Without the extension, PHPStan sees `Assert::integer($v)` as an opaque method call and
cannot infer that `$v` is `int` on the lines that follow. With it, the type is narrowed
immediately after the assertion.

```php
function process(mixed $value): int
{
    Assert::integer($value);
    return $value * 2;  // PHPStan knows $value is int here
}
```

## Assertions that perform type narrowing

Not every Assert method narrows the type — only those where the extension has explicit
mappings. The supported set covers all common use cases:

### Scalar / primitive types
`integer`, `positiveInteger`, `natural`, `float`, `numeric`, `integerish`,
`boolean`, `scalar`, `string`, `stringNotEmpty`, `object`, `resource`

### Collections and callables
`isCallable`, `isArray`, `isIterable`, `isTraversable`,
`isList`, `isNonEmptyList`, `isMap`, `isNonEmptyMap`,
`isCountable`, `isArrayAccessible`

### Null checks
`null`, `notNull`, `true`, `false`, `notFalse`

### Equality and comparison
`same`, `notSame`, `eq`, `notEq`,
`greaterThan`, `greaterThanEq`, `lessThan`, `lessThanEq`, `range`

### Values in set
`inArray`, `oneOf`

### String content
`contains`, `startsWith`, `email`, `uuid`, `length`

### Count assertions
`minCount`, `maxCount`, `countBetween`

### Instanceof / class hierarchy
`isInstanceOf`, `isInstanceOfAny`, `notInstanceOf`,
`isAOf`, `isAnyOf`, `isNotA`, `subclassOf`, `implementsInterface`,
`classExists`, `interfaceExists`

### Array structure
`keyExists`, `methodExists`, `propertyExists`

## Prefix variants are supported

The extension handles all prefix variants automatically:

```php
Assert::nullOrString($v);       // narrows to string|null
Assert::allInteger($values);    // narrows each element to int
Assert::allNullOrString($values); // each element narrows to string|null
```

## Psalm does not need this extension

Psalm works differently: the `webmozarts/assert` package itself ships with
`@psalm-assert` annotations on every method. No Psalm plugin is required.

```php
// In Assert source (simplified):
/** @psalm-assert string $value */
public static function string(mixed $value): void { ... }
```

If you're targeting both analysers, install the PHPStan extension and rely on the
built-in Psalm annotations — both will narrow types correctly from the same Assert calls.

## Assertions that do NOT narrow the type in PHPStan

Assertions outside the supported list (e.g. format validators like `Assert::email()`,
`Assert::uuid()`, `Assert::regex()`) do not cause PHPStan to narrow the variable — the
method call is treated as a void guard with no type effect. The runtime check still
happens; PHPStan just won't change its inferred type based on it.

If you need the analyser to know a string is non-empty after `Assert::email()`,
add an explicit `@var non-empty-string` annotation or use `Assert::stringNotEmpty()`
first (which _is_ supported).

## Verifying the extension is active

Run PHPStan on a minimal file that would only pass if narrowing works:

```php
<?php
use Webmozart\Assert\Assert;

function mustBeString(mixed $v): string {
    Assert::string($v);
    return $v; // PHPStan error without extension; clean with it
}
```

Without the extension PHPStan reports: _"Return type string is not compatible with mixed."_
With the extension: no error.
