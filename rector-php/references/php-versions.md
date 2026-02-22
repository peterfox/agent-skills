# PhpVersionFeature Constants Reference

Use with `MinPhpVersionInterface::provideMinPhpVersion()`.

```php
use Rector\ValueObject\PhpVersionFeature;
use Rector\VersionBonding\Contract\MinPhpVersionInterface;

public function provideMinPhpVersion(): int
{
    return PhpVersionFeature::ENUM; // only run on PHP 8.1+
}
```

## PHP 5.2 – 5.6

| Constant | PHP | Description |
|----------|-----|-------------|
| `SHORT_ARRAY` | 5.4 | `[...]` syntax |
| `EXP_OPERATOR` | 5.6 | `**` operator |
| `VARIADIC_PARAM` | 5.6 | `...$args` params |

## PHP 7.0 – 7.4

| Constant | PHP | Description |
|----------|-----|-------------|
| `SCALAR_TYPES` | 7.0 | `int`, `string`, `float`, `bool` type hints |
| `HAS_RETURN_TYPE` | 7.0 | Return type declarations |
| `NULL_COALESCE` | 7.0 | `??` operator |
| `SPACESHIP` | 7.0 | `<=>` operator |
| `THROWABLE_TYPE` | 7.0 | `Throwable` type |
| `VOID_TYPE` | 7.1 | `void` return type |
| `ITERABLE_TYPE` | 7.1 | `iterable` type |
| `NULLABLE_TYPE` | 7.1 | `?Type` nullable |
| `CONSTANT_VISIBILITY` | 7.1 | `public const` etc. |
| `ARRAY_DESTRUCT` | 7.1 | `[$a, $b] = $arr` |
| `MULTI_EXCEPTION_CATCH` | 7.1 | `catch (A\|B $e)` |
| `OBJECT_TYPE` | 7.2 | `object` type hint |
| `IS_COUNTABLE` | 7.3 | `is_countable()` |
| `ARRAY_KEY_FIRST_LAST` | 7.3 | `array_key_first/last()` |
| `JSON_EXCEPTION` | 7.3 | `JSON_THROW_ON_ERROR` |
| `ARROW_FUNCTION` | 7.4 | `fn() => ...` |
| `NULL_COALESCE_ASSIGN` | 7.4 | `??=` operator |
| `TYPED_PROPERTIES` | 7.4 | Typed class properties |
| `LITERAL_SEPARATOR` | 7.4 | `1_000_000` |
| `ARRAY_SPREAD` | 7.4 | `[...$array]` |

## PHP 8.0

| Constant | PHP | Description |
|----------|-----|-------------|
| `UNION_TYPES` | 8.0 | `A\|B` type hints |
| `NULLSAFE_OPERATOR` | 8.0 | `?->` |
| `NAMED_ARGUMENTS` (use `ATTRIBUTES`) | 8.0 | Named args |
| `MATCH_EXPRESSION` | 8.0 | `match()` |
| `PROPERTY_PROMOTION` | 8.0 | Constructor promotion |
| `ATTRIBUTES` | 8.0 | `#[Attribute]` |
| `STRINGABLE` | 8.0 | `Stringable` interface |
| `STATIC_RETURN_TYPE` | 8.0 | `static` return type |
| `MIXED_TYPE` | 8.0 | `mixed` type |
| `NON_CAPTURING_CATCH` | 8.0 | `catch (E)` without var |
| `STR_CONTAINS` | 8.0 | `str_contains()` |
| `STR_STARTS_WITH` | 8.0 | `str_starts_with()` |
| `STR_ENDS_WITH` | 8.0 | `str_ends_with()` |
| `GET_DEBUG_TYPE` | 8.0 | `get_debug_type()` |
| `CLASS_ON_OBJECT` | 8.0 | `$obj::class` |

## PHP 8.1

| Constant | PHP | Description |
|----------|-----|-------------|
| `READONLY_PROPERTY` | 8.1 | `readonly` property |
| `ENUM` | 8.1 | `enum` keyword |
| `NEVER_TYPE` | 8.1 | `never` return type |
| `INTERSECTION_TYPES` | 8.1 | `A&B` types |
| `FIRST_CLASS_CALLABLE_SYNTAX` | 8.1 | `strlen(...)` |
| `FINAL_CLASS_CONSTANTS` | 8.1 | `final const` |
| `NEW_INITIALIZERS` | 8.1 | `new` in defaults |
| `ARRAY_SPREAD_STRING_KEYS` | 8.1 | String key spread |
| `FIBERS` | N/A | (not in this file) |

## PHP 8.2

| Constant | PHP | Description |
|----------|-----|-------------|
| `READONLY_CLASS` | 8.2 | `readonly class` |
| `UNION_INTERSECTION_TYPES` | 8.2 | DNF types `(A&B)\|C` |
| `NULL_FALSE_TRUE_STANDALONE_TYPE` | 8.2 | `null`, `false`, `true` types |
| `DEPRECATE_DYNAMIC_PROPERTIES` | 8.2 | Dynamic props deprecated |

## PHP 8.3

| Constant | PHP | Description |
|----------|-----|-------------|
| `TYPED_CLASS_CONSTANTS` | 8.3 | Typed constants |
| `DYNAMIC_CLASS_CONST_FETCH` | 8.3 | `Foo::{$name}` |
| `OVERRIDE_ATTRIBUTE` | 8.3 | `#[Override]` |
| `JSON_VALIDATE` | 8.3 | `json_validate()` |
| `READONLY_ANONYMOUS_CLASS` | 8.3 | `readonly` on anonymous class |

## PHP 8.4

| Constant | PHP | Description |
|----------|-----|-------------|
| `PROPERTY_HOOKS` | 8.4 | Property get/set hooks |
| `DEPRECATED_ATTRIBUTE` | 8.4 | `#[Deprecated]` |
| `ARRAY_FIND` | 8.4 | `array_find()` |
| `ARRAY_ANY` | 8.4 | `array_any()` |
| `ARRAY_ALL` | 8.4 | `array_all()` |
| `NEW_METHOD_CALL_WITHOUT_PARENTHESES` | 8.4 | `new Foo->method()` |
| `ROUNDING_MODES` | 8.4 | `RoundingMode` enum |

## PHP 8.5

| Constant | PHP | Description |
|----------|-----|-------------|
| `ARRAY_FIRST_LAST` | 8.5 | `array_first()`, `array_last()` |
| `PIPE_OPERATOER` | 8.5 | `\|>` pipe operator |
| `OVERRIDE_ATTRIBUTE_ON_PROPERTIES` | 8.5 | `#[Override]` on props |