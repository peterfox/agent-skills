---
name: rector-developer
description: Build Rector PHP rules that transform PHP code via AST. Use when asked to create, modify, or explain Rector rules for PHP code transformations. Rector rules use the PHP-Parser AST and PHPStan type analysis. Triggers on requests like "write a Rector rule to...", "create a Rector rule that...", "add a Rector rule for...", or when working in a rector-src or rector-based project and asked to implement code transformation logic.
---

# Rector PHP Rule Builder

Rector transforms PHP code by traversing the PHP-Parser AST, matching node types, and returning modified nodes from `refactor()`.

## Workflow

1. **Check for an existing configurable rule first** — see references/configurable-rules.md. Renaming functions/methods/classes, converting call types, and removing arguments are all covered. Prefer `->withConfiguredRule()` over writing a custom rule for these cases.
2. Identify the PHP-Parser node type(s) to target (see references/node-types.md)
3. Write the rule class extending `AbstractRector`
4. If PHP version gated, implement `MinPhpVersionInterface`
5. If configurable, implement `ConfigurableRectorInterface`
6. Register the rule in rector.php config

## Rule Skeleton

```php
<?php

declare(strict_types=1);

namespace Rector\[Category]\Rector\[NodeType];

use PhpParser\Node;
use PhpParser\Node\Expr\FuncCall; // target node type
use Rector\Rector\AbstractRector;
use Symplify\RuleDocGenerator\ValueObject\CodeSample\CodeSample;
use Symplify\RuleDocGenerator\ValueObject\RuleDefinition;

/**
 * @see \Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\[RuleName]Test
 */
final class [RuleName]Rector extends AbstractRector
{
    public function getRuleDefinition(): RuleDefinition
    {
        return new RuleDefinition('[Description]', [
            new CodeSample(
                <<<'CODE_SAMPLE'
// before
CODE_SAMPLE
                ,
                <<<'CODE_SAMPLE'
// after
CODE_SAMPLE
            ),
        ]);
    }

    /** @return array<class-string<Node>> */
    public function getNodeTypes(): array
    {
        return [FuncCall::class];
    }

    /** @param FuncCall $node */
    public function refactor(Node $node): ?Node
    {
        if (! $this->isName($node, 'target_function')) {
            return null;
        }

        // transform and return modified $node, or return null for no change
        return $node;
    }
}
```

## `refactor()` Return Values

| Return | Effect |
|--------|--------|
| `null` | No change, continue traversal |
| `$node` (modified) | Replace with modified node |
| `Node[]` (non-empty) | Replace with multiple nodes |
| `NodeVisitor::REMOVE_NODE` | Delete the node |

**Never return an empty array** — throws `ShouldNotHappenException`.

## Protected Methods on AbstractRector

```php
// Name checking
$this->isName($node, 'functionName')         // exact name match
$this->isNames($node, ['name1', 'name2'])    // match any
$this->getName($node)                         // get name string or null

// Type checking (PHPStan-powered)
$this->getType($node)                         // returns PHPStan Type
$this->isObjectType($node, new ObjectType('ClassName'))

// Traversal
$this->traverseNodesWithCallable($nodes, function (Node $node): int|Node|null {
    return null; // continue
    // or return NodeVisitor::STOP_TRAVERSAL;
    // or return NodeVisitor::DONT_TRAVERSE_CURRENT_AND_CHILDREN;
});

// Misc
$this->mirrorComments($newNode, $oldNode);    // copy comments
```

## Creating Class Name Nodes

Always use `Node\Name\FullyQualified` (not `Node\Name`) when referencing class names in AST nodes. The string must not have a leading backslash — `FullyQualified` implies it.

```php
use PhpParser\Node\Name\FullyQualified;

// CORRECT
new FullyQualified('App\Something')   // represents \App\Something in PHP

// WRONG — never do this
new Name('\App\Something')            // incorrect: leading backslash in string
new Name('App\Something')             // incorrect: Name is for unqualified names only
```

This applies anywhere a class name appears as a `Name` node: `Expr\New_::$class`, `Expr\Instanceof_::$class`, `Expr\StaticCall::$class`, `Expr\ClassConstFetch::$class`, `Stmt\Class_::$extends`, `Stmt\Class_::$implements`, parameter types, return types, etc.

## Preventing Duplicate Attributes

When a rule adds a PHP attribute (`#[...]`), whether to guard against duplicates depends on whether the attribute allows multiple instances:

- **Non-repeatable attribute** (no `Attribute::IS_REPEATABLE`) — adding it twice is a PHP error. Always guard and skip if already present.
- **Repeatable attribute** (`Attribute::IS_REPEATABLE`) — multiple instances are valid. Do not skip blindly; only skip if the specific instance you'd add is already there (or always add, depending on the rule's intent).

Check whether the target attribute class is defined with `IS_REPEATABLE` before deciding your guard strategy. When in doubt, check the attribute's declaration.

Use `PhpAttributeAnalyzer` (inject via constructor) to check for existing attributes:

```php
use Rector\Php80\NodeAnalyzer\PhpAttributeAnalyzer;

public function __construct(
    private readonly PhpAttributeAnalyzer $phpAttributeAnalyzer,
) {}
```

```php
// Returns true if the node already has the given attribute
$this->phpAttributeAnalyzer->hasPhpAttribute($node, 'Symfony\Component\Routing\Attribute\Route');

// Returns true if the node has any of the given attributes
$this->phpAttributeAnalyzer->hasPhpAttributes($node, [
    'Doctrine\ORM\Mapping\Column',
    'Doctrine\ORM\Mapping\Id',
]);
```

For a **non-repeatable** attribute, return `null` early if already present:

```php
public function refactor(Node $node): ?Node
{
    if ($this->phpAttributeAnalyzer->hasPhpAttribute($node, 'App\MyAttribute')) {
        return null;
    }

    // ... add attribute
    return $node;
}
```

**Every rule that adds attributes must have skip fixtures** covering the relevant cases:
- `skip_attribute_already_present.php.inc` — for non-repeatable attributes, confirms the rule does not add a duplicate
- For repeatable attributes, add skip fixtures for any other condition that should prevent the rule from applying

```php
<?php
// skip_attribute_already_present.php.inc
// Non-repeatable attribute already present — rule must not add it again

namespace Rector\Tests\Category\Rector\NodeType\MyRule\Fixture;

use App\MyAttribute;

#[MyAttribute]
class AlreadyHasAttribute
{
}
```

## Reducing Rule Risk

Before transforming a class or its members, consider whether the change is safe in an inheritance context. Rector rules run against arbitrary codebases, so a transformation that looks correct on a standalone class may break subclasses or consumers.

### Non-final classes

If the class being transformed is not `final`, it may be extended. A rule that adds, removes, or changes a method/property/constant on a non-final class could silently break subclasses (e.g. method signature change, new abstract requirement, changed return type).

**Ask: could subclasses be affected by this transformation?**

- If yes and the risk is real, guard with `isFinal()` and skip non-final classes. Add a `skip_non_final_class.php.inc` fixture.
- If the rule is intentionally broad and the risk is accepted, document that reasoning in the rule's `getRuleDefinition()` description.
- Some rules legitimately target non-final classes (e.g. adding a type declaration to a public method) — in those cases consider whether it's safe to apply on `public`/`protected` members (see below).

```php
// Skip if class is not final
$classNode = $this->betterNodeFinder->findParentType($node, Class_::class);
if (! $classNode instanceof Class_) {
    return null;
}
if (! $classNode->isFinal()) {
    return null;
}
```

### Public and protected members

Public and protected methods, properties, and constants form the class's API contract — both for external callers and for subclasses. Changing them (renaming, adding/removing parameters, changing types, adding attributes) carries more risk than changing private members.

**Ask: is this member `public` or `protected`?**

- `private` members — safe to transform; no external or inheritance contract.
- `protected` members — subclasses may override or depend on the original signature. Consider skipping, or at minimum add skip fixtures for protected cases.
- `public` members — broadest risk. Weigh whether the rule should be limited to `private`, opt-in via configuration, or require the class to be `final`.

```php
// Example: only transform private methods
if (! $node->isPrivate()) {
    return null;
}

// Example: skip public/protected properties
if ($node->isPublic() || $node->isProtected()) {
    return null;
}
```

### Required skip fixtures for risky scenarios

When a rule targets class members, add skip fixtures for the cases it consciously avoids:

- `skip_non_final_class.php.inc` — rule skips classes that are not final
- `skip_public_method.php.inc` — rule skips public members
- `skip_protected_property.php.inc` — rule skips protected members

These fixtures document the rule's intended scope and prevent regressions if the guard is accidentally removed.

## Injected Services

Inject via constructor (autowired by DI container):

```php
public function __construct(
    private readonly BetterNodeFinder $betterNodeFinder,
    // ... other services
) {}
```

- **`$this->nodeFactory`** — create nodes (see references/helpers.md)
- **`$this->nodeComparator`** — compare nodes structurally
- **`$this->betterNodeFinder`** — search within nodes (inject via constructor)
- PHPDoc manipulation: inject `PhpDocInfoFactory` + `DocBlockUpdater`

## Configurable Rules

```php
use Rector\Contract\Rector\ConfigurableRectorInterface;
use Symplify\RuleDocGenerator\ValueObject\CodeSample\ConfiguredCodeSample;

final class MyRector extends AbstractRector implements ConfigurableRectorInterface
{
    private string $targetClass = 'OldClass';

    public function configure(array $configuration): void
    {
        $this->targetClass = $configuration['target_class'] ?? $this->targetClass;
    }

    public function getRuleDefinition(): RuleDefinition
    {
        return new RuleDefinition('...', [
            new ConfiguredCodeSample('before', 'after', ['target_class' => 'OldClass']),
        ]);
    }
}
```

## PHP Version Gating

```php
use Rector\VersionBonding\Contract\MinPhpVersionInterface;
use Rector\ValueObject\PhpVersionFeature;

final class MyRector extends AbstractRector implements MinPhpVersionInterface
{
    public function provideMinPhpVersion(): int
    {
        return PhpVersionFeature::ENUM; // PHP 8.1+
    }
}
```

See references/php-versions.md for all `PhpVersionFeature` constants.

## rector.php Registration

```php
use Rector\Config\RectorConfig;

return RectorConfig::configure()
    ->withRules([MyRector::class])
    // configurable rule:
    ->withConfiguredRule(MyConfigurableRector::class, ['key' => 'value']);
```

## Namespace Convention

Rules live at: `rules/[Category]/Rector/[NodeType]/[RuleName]Rector.php`
Tests live at: `rules-tests/[Category]/Rector/[NodeType]/[RuleName]Rector/`

Categories: `CodeQuality`, `CodingStyle`, `DeadCode`, `EarlyReturn`, `Naming`, `Php52`–`Php85`, `Privatization`, `Removing`, `Renaming`, `Strict`, `Transform`, `TypeDeclaration`

## Writing Tests

Every rule needs a test class extending `AbstractRectorTestCase` and at least one fixture file.

**Minimal test class** (`rules-tests/[Category]/Rector/[NodeType]/[RuleName]/[RuleName]RectorTest.php`):

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

**Fixture file** (`Fixture/fixture.php.inc`):

```php
<?php

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\Fixture;

// INPUT code before rule runs

?>
-----
<?php

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\Fixture;

// EXPECTED code after rule runs

?>
```

**Tip:** Write only the input section, run the test, and `FixtureFileUpdater` auto-fills the expected output.

**Skip fixtures (rule should not apply):** Create a separate file per skip scenario, named with a `skip_` prefix. Each file contains a single section only — no `-----` separator. Never put multiple skip scenarios in one file.

```php
<?php

namespace Rector\Tests\[Category]\Rector\[NodeType]\[RuleName]\Fixture;

// Code that should NOT be changed — one scenario per file

?>
```

Examples: `skip_already_correct.php.inc`, `skip_static_call.php.inc`, `skip_inside_interface.php.inc`

See **references/testing.md** for: config file formats, configurable rule variants, multi-config test classes, fixture naming, Source/ support classes, and fixture auto-update behaviour.

## Reference Files

- **references/configurable-rules.md** — All built-in configurable rules with config examples (check this before writing a custom rule)
- **references/node-types.md** — PhpParser node type quick reference (FuncCall, MethodCall, Class_, etc.)
- **references/helpers.md** — NodeFactory methods, BetterNodeFinder, NodeComparator, PhpDocInfo
- **references/php-versions.md** — PhpVersionFeature constants by PHP version
- **references/testing.md** — Full test structure, fixture format, configurable rule testing, special cases
