# PHPDoc Shape & Type Annotation Reference

Deep reference for PHPDoc annotations understood by PHPStan and Psalm. Both tools share
most syntax; differences are called out explicitly.

## Array shapes

Use array shapes to describe arrays with a **known, fixed set of keys**:

```php
/** @param array{id: int, name: string} $user */
```

### Optional keys

```php
/** @param array{id: int, name: string, bio?: string} $user */
// bio may be absent; if present, it is string
```

### Nested shapes

```php
/**
 * @param array{
 *     user: array{id: int, name: string},
 *     meta: array{created_at: string, source?: string}
 * } $payload
 */
```

### Open shapes (allow extra unknown keys)

**Psalm 5+:**
```php
/** @param array{id: int, name: string, ...} $data */
// Known keys are id and name; additional keys of any type may be present
```

**PHPStan:** Array shapes are sealed (closed) by default. To allow extra keys, document
with prose or use `array<string, mixed>` for the "rest" with an intersection or use a
broader return type.

### Sealed vs open in practice

If you control the data shape, use a sealed shape (it gives better error detection). If
you're receiving external data you may not fully control, Psalm's open shape or a `mixed`
value type gives you room.

---

## List types

`list<T>` guarantees a 0-indexed sequential integer array. Prefer this over `array<int, T>`
because PHPStan and Psalm track `list` separately and can prove properties like non-emptiness
more reliably.

```php
/** @param list<string> $tags */
/** @return non-empty-list<int> */
/** @param list<array{id: int, label: string}> $options */
```

**Psalm list shapes** (Psalm-specific, for fixed-length tuples):
```php
/** @return list{string, int, bool} */
// A 3-element list: first element string, second int, third bool
```

---

## Generic arrays

For arrays where all values share a type but keys are arbitrary:

```php
/** @param array<string, User> $userMap */       // string keys, User values
/** @param array<int, float> $prices */           // int keys, float values
/** @param array<array-key, mixed> $anything */   // any key, any value
```

`array-key` is the union `int|string` and is valid anywhere a key type is needed.

---

## Specialised scalar types

Both PHPStan and Psalm understand these beyond the base PHP types:

| Type | Meaning |
|------|---------|
| `non-empty-string` | string that is not `""` |
| `numeric-string` | string that passes `is_numeric()` |
| `class-string` | fully-qualified class/interface name |
| `class-string<T>` | class name that is a subtype of T |
| `callable-string` | string that is a valid callable |
| `interface-string` | string that is an interface name |
| `positive-int` | integer > 0 |
| `negative-int` | integer < 0 |
| `non-negative-int` | integer ≥ 0 |
| `non-positive-int` | integer ≤ 0 |
| `int<0, 100>` | integer in range [0, 100] (PHPStan) |
| `literal-string` | string known at compile time (Psalm) |
| `non-empty-array<K, V>` | array with at least one element |
| `non-empty-list<T>` | list with at least one element |

---

## Type aliases

Define a shape once, reference it by name everywhere.

### PHPStan

```php
/**
 * @phpstan-type Address array{
 *     street: string,
 *     city: string,
 *     postcode: string,
 *     country?: string
 * }
 */
class Order {}

// Import and use in another file:
/**
 * @phpstan-import-type Address from Order
 */
class Checkout {
    /** @param Address $billingAddress */
    public function setBillingAddress(array $billingAddress): void {}
}
```

### Psalm

```php
/**
 * @psalm-type Address = array{
 *     street: string,
 *     city: string,
 *     postcode: string,
 *     country?: string
 * }
 */
class Order {}

/**
 * @psalm-import-type Address from Order
 */
class Checkout {
    /** @param Address $billingAddress */
    public function setBillingAddress(array $billingAddress): void {}
}
```

### Cross-tool compatibility

Include both `@phpstan-type` and `@psalm-type` (they can coexist in the same docblock):

```php
/**
 * @phpstan-type Address array{street: string, city: string, postcode: string}
 * @psalm-type   Address = array{street: string, city: string, postcode: string}
 */
```

---

## Template annotations (generics)

### Basic template

```php
/**
 * @template T
 * @param T $value
 * @return T
 */
function identity(mixed $value): mixed { return $value; }
```

### Bounded template (constrained to a type hierarchy)

```php
/**
 * @template T of \DateTimeInterface
 * @param T $date
 * @return T
 */
function cloneDate(\DateTimeInterface $date): \DateTimeInterface {}
```

### Templates on classes

```php
/**
 * @template T
 */
class Collection
{
    /** @var list<T> */
    private array $items = [];

    /**
     * @param T $item
     */
    public function add(mixed $item): void { $this->items[] = $item; }

    /**
     * @return list<T>
     */
    public function all(): array { return $this->items; }
}

/**
 * @extends Collection<User>
 */
class UserCollection extends Collection {}
```

### Covariant templates (Psalm)

```php
/**
 * @template-covariant T
 */
interface ReadableCollection
{
    /** @return T */
    public function first(): mixed;
}
```

Covariance means `ReadableCollection<Cat>` is assignable to `ReadableCollection<Animal>`
when `Cat extends Animal`. Only safe for read-only collections.

---

## Callable annotations

```php
/** @param callable(int, string): bool $fn */
/** @param \Closure(User): void $handler */
/** @param callable(non-empty-string): positive-int $scorer */
```

---

## Conditional return types (PHPStan)

```php
/**
 * @template T of object
 * @param class-string<T>|null $class
 * @return ($class is null ? mixed : T)
 */
public function get(?string $class): mixed {}
```

---

## Assertion annotations (Psalm-specific)

When writing a custom guard function, tell Psalm what it asserts:

```php
/**
 * @psalm-assert string $value
 */
function assertString(mixed $value): void
{
    if (!is_string($value)) {
        throw new \InvalidArgumentException('Expected string.');
    }
}

/**
 * @psalm-assert-if-true string $value
 */
function isString(mixed $value): bool
{
    return is_string($value);
}
```

After `assertString($x)`, Psalm knows `$x` is `string`. After `if (isString($x))`,
the true branch knows `$x` is `string`.

---

## Intersection types

Combine two object types:

```php
/** @param Serializable&\Countable $obj */
```

Arrays cannot be intersected with objects; use interface constraints or shapes instead.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `@param array $items` | Use `array<K, V>` or `list<T>` or a shape |
| `@param mixed[] $items` | Use `list<mixed>` for sequential, `array<string, mixed>` for maps |
| `@return array` | Always specify what the array contains |
| `@param object $obj` | Use `@param ClassName $obj` or a template bound |
| Defining the same shape inline in 5 places | Extract to a `@phpstan-type` / `@psalm-type` alias |
| Missing `@extends` on a generic subclass | Add `@extends ParentClass<ConcreteType>` |
