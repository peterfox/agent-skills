---
name: php-type-safety
description: >
  PHP type safety patterns using webmozarts/assert for runtime validation combined with
  PHPDoc annotations for static analysis. Use this skill whenever writing or reviewing PHP
  code that needs to pass PHPStan or Psalm at strict levels, when adding type assertions to
  method/function parameters, when typing complex array structures (shapes, maps, lists),
  when defining reusable type aliases, or when annotating anonymous objects and key/value
  arrays. Trigger on phrases like "add type assertions", "type this array properly",
  "make this pass PHPStan", "annotate with PHPDoc", "use webmozarts assert", "type hints
  for static analysis", "psalm types", or any request to improve type safety in PHP code.
---

# PHP Type Safety

Combine **runtime assertions** (webmozarts/assert) with **static analysis annotations**
(PHPDoc shapes, templates) to write PHP code that is safe at runtime *and* satisfies
PHPStan/Psalm at strict levels. The two approaches are complementary: PHPDoc narrows types
for the analyser, assertions enforce them at runtime where PHP's type system cannot.

## Setup

```bash
composer require webmozart/assert
composer require --dev phpstan/phpstan-webmozart-assert  # PHPStan users only
```

The PHPStan extension translates `Assert::*()` calls into type-narrowing expressions so
PHPStan refines variable types after each assertion. If you use `phpstan/extension-installer`
it registers automatically; otherwise add it to `phpstan.neon`:

```neon
includes:
    - vendor/phpstan/phpstan-webmozart-assert/extension.neon
```

Psalm users need no extra plugin — the Assert library ships with `@psalm-assert`
annotations on every method and Psalm reads them natively.

## Core workflow

1. **Annotate first** — write the PHPDoc shape or type hint so the analyser knows the expected type.
2. **Assert at boundaries** — use `Assert::*()` at the entry point of any method that receives data from outside your control (user input, deserialized data, external APIs, mixed-typed collections).
3. **Avoid redundant assertions** — if PHP's native type system or a previous assertion already guarantees the type, a second assertion adds noise.
4. **Define type aliases** for shapes used in more than one place.

## PHPDoc type annotations

### Scalar and object types

Prefer native type hints. Use PHPDoc only when native PHP cannot express the type:

```php
/** @param non-empty-string $slug */
public function findBySlug(string $slug): void {}

/** @param positive-int $count */
public function paginate(int $count): void {}

/** @param class-string<Entity> $class */
public function resolve(string $class): object {}
```

### Array shapes — exact structure

Use array shapes for arrays with a known, fixed set of keys:

```php
/**
 * @param array{id: int, name: string, email?: string} $user
 * @return array{token: string, expires_at: int}
 */
public function createSession(array $user): array {}
```

`email?: string` marks `email` as optional (may be absent).

### Generic arrays — maps and lists

Use generic notation for arrays where all values share a type:

```php
/** @param array<string, int> $scores */   // map: string keys, int values
/** @param list<User> $users */             // list: 0-indexed, sequential
/** @param non-empty-list<string> $tags */  // list with at least one item
```

Use `list<T>` (not `array<int, T>`) for sequential integer-indexed arrays — it carries
stronger guarantees that PHPStan/Psalm can leverage.

### Type aliases — reusable shapes

Define shapes once in the class that owns the data, import elsewhere:

```php
/**
 * @phpstan-type UserData array{id: int, name: string, roles: list<string>}
 * @psalm-type    UserData = array{id: int, name: string, roles: list<string>}
 */
class User {}

// In another class:
/**
 * @phpstan-import-type UserData from User
 * @psalm-import-type   UserData from User
 */
class UserRepository {
    /** @return list<UserData> */
    public function findAll(): array {}
}
```

PHPStan and Psalm have slightly different syntax; include both tags for cross-tool compatibility.

### Templates (generics)

```php
/**
 * @template T
 * @param list<T> $items
 * @param callable(T): bool $predicate
 * @return list<T>
 */
function filter(array $items, callable $predicate): array {
    return array_values(array_filter($items, $predicate));
}

/**
 * @template T of \Throwable
 * @param class-string<T> $exceptionClass
 * @param callable(): void $fn
 * @throws T
 */
function rethrowAs(string $exceptionClass, callable $fn): void
{
    try {
        $fn();
    } catch (\Throwable $e) {
        throw new $exceptionClass($e->getMessage(), 0, $e);
    }
}
```

## Runtime assertions with webmozarts/assert

### Basic usage

```php
use Webmozart\Assert\Assert;

public function setAge(int $age): void
{
    Assert::range($age, 0, 150);
    $this->age = $age;
}

public function handle(mixed $payload): void
{
    Assert::isArray($payload);
    Assert::keyExists($payload, 'type');
    Assert::string($payload['type']);
    Assert::inArray($payload['type'], ['create', 'update', 'delete']);
}
```

### Bulk assertions with `all*` and `nullOr*`

```php
/** @param list<string> $tags */
public function setTags(array $tags): void
{
    Assert::allStringNotEmpty($tags);   // every element is a non-empty string
    $this->tags = $tags;
}

/** @param array<string, int|null> $scores */
public function setScores(array $scores): void
{
    Assert::allNullOrInteger($scores);  // each value is int or null
}
```

### Combining with PHPDoc shapes

Assertions narrow types for runtime; PHPDoc shapes narrow them for the analyser.
Use both together at the boundary of untrusted data:

```php
/**
 * @phpstan-type RawConfig array{dsn: string, pool: int, timeout?: float}
 * @param array<string, mixed> $raw
 * @return RawConfig
 */
private function validateConfig(array $raw): array
{
    Assert::keyExists($raw, 'dsn');
    Assert::string($raw['dsn']);
    Assert::keyExists($raw, 'pool');
    Assert::positiveInteger($raw['pool']);
    if (isset($raw['timeout'])) {
        Assert::float($raw['timeout']);
    }

    /** @var RawConfig $raw */
    return $raw;
}
```

The `@var` cast is a forced assertion — it tells the analyser to treat `$raw` as `RawConfig`
from that point on. The analyser trusts it; the assertions above are what actually enforce it
at runtime.

## Legacy inference mode

Use this mode when asked to "infer types", "annotate without changing the API", or
improve type visibility in existing code where modifying method signatures would risk
breaking callers.

**The constraint:** add type information only through PHPDoc and internal assertions.
Never add or change native PHP type hints (`string $name`, `: int`, `?Foo`), never
alter a method or function signature in any way.

### What you may add

| Addition | Example |
|----------|---------|
| `@param` / `@return` PHPDoc on methods | `/** @param list<int> $ids */` |
| `@var` on class properties | `/** @var array<string, User> */` |
| `@var` on local variables | `/** @var non-empty-string $slug */` |
| `Assert::*()` inside method bodies | After receiving or unpacking a value |
| Type alias definitions (`@phpstan-type`) | On the class, not on the signature |

### What you must not touch

- Native parameter types (`string $x`, `int $x`, `?Foo $x`)
- Native return types (`: string`, `: void`, `: ?int`)
- Anything else that changes the method or function signature

### Inference workflow

1. **Read the method body** — trace how each parameter and return value is actually used.
   Assignment to a typed property, a method call that requires a specific type, a
   comparison — all give clues.
2. **Check callers** — if accessible, read call sites to see what values are passed.
3. **Annotate conservatively** — if you cannot determine the type with confidence, use
   `mixed` or the broadest type you can prove. Do not guess.
4. **Add assertions where the inferred type is not guaranteed** — if callers could pass
   anything and the body assumes a `string`, guard it with `Assert::string()` at the top.
5. **Use `@var` for local ambiguity** — when a variable is assigned from a source the
   analyser cannot follow (e.g. `array_shift`, casting, `unserialize`), annotate inline.

### Example

Before — legacy code, no type information:

```php
class OrderService
{
    private $repository;
    private $items = [];

    public function add($product, $qty)
    {
        $this->items[] = ['product' => $product, 'qty' => $qty];
    }

    public function total()
    {
        $sum = 0;
        foreach ($this->items as $line) {
            $sum += $line['product']->price * $line['qty'];
        }
        return $sum;
    }
}
```

After — annotated in inference mode (signatures untouched):

```php
/**
 * @phpstan-type LineItem array{product: Product, qty: positive-int}
 */
class OrderService
{
    /** @var ProductRepository */
    private $repository;

    /** @var list<LineItem> */
    private $items = [];

    /**
     * @param Product $product
     * @param positive-int $qty
     */
    public function add($product, $qty)
    {
        Assert::isInstanceOf($product, Product::class);
        Assert::positiveInteger($qty);

        $this->items[] = ['product' => $product, 'qty' => $qty];
    }

    /**
     * @return float
     */
    public function total()
    {
        $sum = 0;
        foreach ($this->items as $line) {
            $sum += $line['product']->price * $line['qty'];
        }
        return $sum;
    }
}
```

The public API is identical. PHPStan/Psalm now understands the property types, the
expected parameter contracts, and the return type — and the assertions catch violations
at runtime during development.

## Decision rules

- **Do not assert what PHP already enforces.** If a parameter has `string $name`, don't add `Assert::string($name)`.
- **Assert at boundaries, not everywhere.** Internal private methods working with already-typed data don't need assertions.
- **Use `Assert::isInstanceOf()` instead of a cast.** It produces a cleaner error than a failed cast and narrows the type for PHPStan/Psalm.
- **Prefer specific assertions over generic ones.** `Assert::positiveInteger()` communicates intent better than `Assert::integer()` + a manual range check.
- **Open shapes for extensible structures.** When a shape may contain extra keys you don't control, Psalm users can use `array{known: type, ...}`; PHPStan users should document this in the PHPDoc prose or use `array<string, mixed>`.
- **In inference mode, annotate conservatively.** A `mixed` annotation you can prove is safer than a specific type you cannot. Incorrect PHPDoc is worse than missing PHPDoc — it misleads the analyser and future readers.

## Reference files

- **`references/assert-methods.md`** — Full categorised reference for all Assert methods; read when you need a specific assertion or the `nullOr`/`all` prefix variants.
- **`references/phpdoc-shapes.md`** — Deep reference for array shapes, list types, conditional types, and cross-tool differences between PHPStan and Psalm; read when annotating complex structures.
- **`references/phpstan-extension.md`** — Installation, configuration, and the exact list of assertions that cause PHPStan type narrowing; read when debugging why PHPStan is not narrowing a type after an assertion, or when verifying the extension is working.
