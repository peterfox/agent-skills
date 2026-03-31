# Assert Method Reference

Full reference for `Webmozart\Assert\Assert`. All methods throw `InvalidArgumentException`
on failure with a descriptive message. Every method has a `nullOr*` and `all*` prefix variant.

## Prefix variants

| Prefix | Effect |
|--------|--------|
| `nullOr*($value, ...)` | Passes silently if `$value === null`, otherwise runs the assertion |
| `all*($values, ...)` | Applies the assertion to every element of an array or `Traversable` |
| `allNullOr*($values, ...)` | Combination: each element may be null or must satisfy the assertion |

## Type assertions

| Method | Narrows to (PHPStan/Psalm) |
|--------|---------------------------|
| `string($v)` | `string` |
| `stringNotEmpty($v)` | `non-empty-string` |
| `integer($v)` | `int` |
| `positiveInteger($v)` | `positive-int` |
| `natural($v)` | `non-negative-int` (≥0) |
| `float($v)` | `float` |
| `numeric($v)` | `numeric-string\|int\|float` |
| `integerish($v)` | value is integer-like (works on strings too) |
| `boolean($v)` | `bool` |
| `scalar($v)` | `scalar` |
| `object($v)` | `object` |
| `array($v)` | `array` |
| `isArray($v)` | `array` (alias) |
| `isList($v)` | `list` |
| `isNonEmptyList($v)` | `non-empty-list` |
| `isMap($v)` | `array<string, mixed>` (string keys only) |
| `isNonEmptyMap($v)` | non-empty string-keyed map |
| `isCountable($v)` | `array\|Countable` |
| `isIterable($v)` | `iterable` |
| `isTraversable($v)` | `Traversable` |
| `isCallable($v)` | `callable` |
| `resource($v)` | `resource` |
| `null($v)` | `null` |
| `notNull($v)` | `T` (removes null) |
| `true($v)` | `true` |
| `false($v)` | `false` |

## Instance / class assertions

| Method | Notes |
|--------|-------|
| `isInstanceOf($v, $class)` | Narrows `$v` to `$class`; preferred over casting |
| `isInstanceOfAny($v, $classes)` | `$v` is one of the listed classes |
| `notInstanceOf($v, $class)` | Negative — `$v` is not `$class` |
| `isAOf($v, $class)` | True if `$v` is `$class` or a subtype (uses `is_a`) |
| `isAnyOf($v, $classes)` | `$v` is_a any of `$classes` |
| `isNotA($v, $class)` | Negative is_a check |
| `subclassOf($v, $class)` | `$v` is a subclass (not `$class` itself) |
| `implementsInterface($v, $iface)` | `$v` implements `$iface` |
| `classExists($v)` | `$v` is a valid class name (`class-string`) |
| `interfaceExists($v)` | `$v` is a valid interface name |

```php
Assert::isInstanceOf($repository, UserRepository::class);
// $repository is now UserRepository for the analyser
```

## Comparison and range assertions

| Method | Description |
|--------|-------------|
| `eq($v, $expect)` | `$v == $expect` (loose) |
| `notEq($v, $expect)` | `$v != $expect` |
| `same($v, $expect)` | `$v === $expect` (strict) |
| `notSame($v, $expect)` | `$v !== $expect` |
| `greaterThan($v, $limit)` | `$v > $limit` |
| `greaterThanEq($v, $limit)` | `$v >= $limit` |
| `lessThan($v, $limit)` | `$v < $limit` |
| `lessThanEq($v, $limit)` | `$v <= $limit` |
| `range($v, $min, $max)` | `$min <= $v <= $max` |
| `inArray($v, $array)` | `$v` is in the array (strict) |
| `oneOf($v, $values)` | Alias for `inArray` |

## String assertions

| Method | Description |
|--------|-------------|
| `contains($v, $sub)` | String contains substring |
| `notContains($v, $sub)` | String does not contain substring |
| `startsWith($v, $prefix)` | Starts with prefix |
| `startsWithLetter($v)` | First char is a letter |
| `endsWith($v, $suffix)` | Ends with suffix |
| `regex($v, $pattern)` | Matches regex |
| `notRegex($v, $pattern)` | Does not match regex |
| `alpha($v)` | Only alphabetic characters |
| `digits($v)` | Only digit characters |
| `alnum($v)` | Only alphanumeric characters |
| `lower($v)` | All lowercase |
| `upper($v)` | All uppercase |
| `uuid($v)` | Valid UUID |
| `ip($v)` | Valid IPv4 or IPv6 |
| `ipv4($v)` | Valid IPv4 |
| `ipv6($v)` | Valid IPv6 |
| `email($v)` | Valid email format |
| `url($v)` | Valid URL |
| `length($v, $len)` | Exact length |
| `minLength($v, $min)` | Minimum length |
| `maxLength($v, $max)` | Maximum length |
| `lengthBetween($v, $min, $max)` | Length within range |
| `unicodeLetters($v)` | Unicode letter characters only |
| `locale($v)` | Valid locale string |

## Array / collection assertions

| Method | Description |
|--------|-------------|
| `count($v, $n)` | Exact count |
| `minCount($v, $min)` | At least `$min` elements |
| `maxCount($v, $max)` | At most `$max` elements |
| `countBetween($v, $min, $max)` | Count within range |
| `keyExists($v, $key)` | Key present in array |
| `keyNotExists($v, $key)` | Key absent from array |
| `validArrayKey($v)` | `$v` is int or string (valid key) |
| `notEmpty($v)` | Not empty (works on string, array, Countable) |

## Logical / miscellaneous

| Method | Description |
|--------|-------------|
| `true($v)` | Strictly true |
| `false($v)` | Strictly false |
| `notFalse($v)` | Not strictly false |
| `throws(callable $fn, $class)` | Callable throws exception of `$class` |
| `satisfy($v, callable $fn)` | Custom predicate: `$fn($v)` returns true |

## Custom error messages

Every assertion accepts an optional last parameter for a custom message. Use `%s` as a
placeholder for the actual value:

```php
Assert::stringNotEmpty($name, 'Product name must not be empty, got %s');
Assert::positiveInteger($quantity, 'Quantity must be positive, got %s');
Assert::isInstanceOf($handler, Handler::class, 'Expected Handler, got %s');
```

## Extending Assert

Subclass `Assert` to add domain-specific assertions while keeping the same API:

```php
use Webmozart\Assert\Assert;

class DomainAssert extends Assert
{
    public static function validStatus(string $status): void
    {
        static::inArray($status, ['draft', 'published', 'archived'], sprintf(
            'Invalid status "%s". Expected one of: draft, published, archived.',
            $status,
        ));
    }
}
```

All prefix variants (`nullOrValidStatus`, `allValidStatus`) are generated automatically.
