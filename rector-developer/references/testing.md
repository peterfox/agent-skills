# Rector Rule Testing Reference

## Table of Contents
1. [Test Class Structure](#test-class-structure)
2. [Config Files](#config-files)
3. [Fixture Format](#fixture-format)
4. [Directory Layout](#directory-layout)
5. [Testing Configurable Rules](#testing-configurable-rules)
6. [Special Cases](#special-cases)

---

## Test Class Structure

All rule tests extend `AbstractRectorTestCase`. The pattern is identical for every rule type:

```php
<?php

declare(strict_types=1);

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName];

use Iterator;
use PHPUnit\Framework\Attributes\DataProvider;
use Rector\Testing\PHPUnit\AbstractRectorTestCase;

final class [RuleName]RectorTest extends AbstractRectorTestCase
{
    #[DataProvider('provideData')]
    public function test(string $filePath): void
    {
        $this->doTestFile($filePath);
    }

    public static function provideData(): Iterator
    {
        return self::yieldFilesFromDirectory(__DIR__ . '/Fixture');
    }

    public function provideConfigFilePath(): string
    {
        return __DIR__ . '/config/configured_rule.php';
    }
}
```

**The three required pieces:**

| Method | Purpose |
|--------|---------|
| `test(string $filePath)` | Called once per fixture file; calls `$this->doTestFile($filePath)` |
| `provideData(): Iterator` | Returns fixture file paths via `self::yieldFilesFromDirectory()` |
| `provideConfigFilePath(): string` | Returns absolute path to the config file registering the rule |

**Fixture auto-updater:** When a test fails due to changed output, `FixtureFileUpdater` automatically updates the expected section in the `.php.inc` file. This means you can write the fixture with only the input section first, run the test, and the expected output is filled in automatically.

---

## Config Files

Config files live in `[RuleName]/config/configured_rule.php`. Two supported formats:

### Simple rule (no configuration)

```php
<?php

declare(strict_types=1);

use Rector\Config\RectorConfig;
use Rector\[Category]\Rector\[NodeType]\[RuleName]Rector;

return RectorConfig::configure()
    ->withRules([[RuleName]Rector::class]);
```

### Configurable rule (with configuration)

```php
<?php

declare(strict_types=1);

use Rector\Config\RectorConfig;
use Rector\[Category]\Rector\[NodeType]\[RuleName]Rector;

return static function (RectorConfig $rectorConfig): void {
    $rectorConfig->ruleWithConfiguration([RuleName]Rector::class, [
        [RuleName]Rector::SOME_OPTION => 'value',
        [RuleName]Rector::ANOTHER_OPTION => true,
    ]);
};
```

### Configurable rule with value objects

```php
return static function (RectorConfig $rectorConfig): void {
    $rectorConfig->ruleWithConfiguration(ArgumentAdderRector::class, [
        new ArgumentAdder(SomeClass::class, 'methodName', 0, 'paramName', null, new ObjectType('SomeType')),
        new ArgumentAdder(SomeClass::class, 'otherMethod', 1, 'flag', false),
    ]);
};
```

---

## Fixture Format

Fixtures are `.php.inc` files with **two sections separated by `-----`** on its own line:

```php
<?php

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\Fixture;

// INPUT: code before the rule runs

?>
-----
<?php

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\Fixture;

// EXPECTED OUTPUT: code after the rule runs

?>
```

**Rules:**
- Extension is always `.php.inc` (prevents IDE from treating them as real PHP)
- Separator is exactly `-----` on its own line
- Both sections use `<?php` / `?>` tags
- Namespaces must match the fixture file location (so autoloading works for type analysis)
- File ends with `?>` followed by a newline

### No-change fixture (rule should not apply)

When the rule should make no changes, omit the separator entirely — use a single section:

```php
<?php

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\Fixture;

class SomeClass
{
    // This code should NOT be changed by the rule
    public function alreadyCorrect(): void {}
}
```

---

## Directory Layout

```
rules-tests/
└── [Category]/
    └── Rector/
        └── [NodeType]/
            └── [RuleName]Rector/
                ├── [RuleName]RectorTest.php      ← main test
                ├── Fixture/                       ← default fixture dir
                │   ├── fixture.php.inc            ← main/happy-path case
                │   ├── some_edge_case.php.inc
                │   └── skip_some_case.php.inc     ← no-change fixture
                └── config/
                    └── configured_rule.php
```

**Fixture file naming:**
- `fixture.php.inc` — the main general case
- Descriptive snake_case names for specific cases: `with_variable.php.inc`, `static_call.php.inc`, `nested_class.php.inc`
- No-change cases often prefixed or named to indicate skipping: `skip_already_correct.php.inc`

---

## Testing Configurable Rules

To test the same rule with **different configurations**, create separate test classes — one per configuration variant:

```
[RuleName]Rector/
├── [RuleName]RectorTest.php               ← default config
├── UpperCaseSnakeCaseTest.php             ← variant config
├── Fixture/                               ← fixtures for default
│   └── fixture.php.inc
├── FixtureUpperCaseSnakeCase/             ← fixtures for variant
│   └── fixture.php.inc
└── config/
    ├── configured_rule.php                ← default config
    └── configured_rule_uppercase_snake_case.php  ← variant config
```

**Variant test class:**

```php
final class UpperCaseSnakeCaseTest extends AbstractRectorTestCase
{
    #[DataProvider('provideData')]
    public function test(string $filePath): void
    {
        $this->doTestFile($filePath);
    }

    public static function provideData(): Iterator
    {
        return self::yieldFilesFromDirectory(__DIR__ . '/FixtureUpperCaseSnakeCase');
    }

    public function provideConfigFilePath(): string
    {
        return __DIR__ . '/config/configured_rule_uppercase_snake_case.php';
    }
}
```

**Naming convention:** fixture directory = `Fixture` + PascalCase variant name; config file = `configured_rule_` + snake_case variant name `.php`.

---

## Special Cases

### Including whole fixture directory as source

When a rule needs to analyse multiple files together (e.g., cross-file type info), pass `true` to `doTestFile`:

```php
public function test(string $filePath): void
{
    $this->doTestFile($filePath, true); // whole Fixture/ dir added as source
}
```

### Testing with source support classes

Place helper classes the fixture needs in a `Source/` directory:

```
[RuleName]Rector/
├── Fixture/
│   └── fixture.php.inc       ← uses SomeClass from Source/
├── Source/
│   └── SomeClass.php         ← not a fixture, just a support class
└── config/
    └── configured_rule.php
```

The config file can autoload the `Source/` directory:

```php
return RectorConfig::configure()
    ->withRules([MyRector::class])
    ->withPaths([__DIR__ . '/../Source']);
```

### Testing expected warnings

When a rule applies but produces no code change (e.g., already-correct code that still triggers), use:

```php
public function test(string $filePath): void
{
    $this->doTestFileExpectingWarningAboutRuleApplied(
        $filePath,
        MyRector::class
    );
}
```

### Quickly scaffolding a fixture

Write only the input section, run the test, and `FixtureFileUpdater` fills in the expected output automatically:

```php
<?php

namespace Rector\Tests\MyCategory\Rector\FuncCall\MyRector\Fixture;

echo sprintf('hello');

?>
```

After the test runs (and "fails"), the file becomes:

```php
<?php

namespace Rector\Tests\MyCategory\Rector\FuncCall\MyRector\Fixture;

echo sprintf('hello');

?>
-----
<?php

namespace Rector\Tests\MyCategory\Rector\FuncCall\MyRector\Fixture;

echo 'hello';

?>
```