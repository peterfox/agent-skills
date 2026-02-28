# Rector Configurable Rules Reference

Before writing a custom rule, check this list. Many common transformations are already implemented as configurable rules — use them with `->withConfiguredRule()` instead.

## Quick-match Index

| Task | Rule |
|------|------|
| Rename a function | `RenameFunctionRector` |
| Rename a method on a class | `RenameMethodRector` |
| Rename a static method (possibly moving class) | `RenameStaticMethodRector` |
| Rename a class / move a class | `RenameClassRector` |
| Rename a class constant | `RenameClassConstFetchRector` |
| Rename a global constant | `RenameConstantRector` |
| Rename a property on a class | `RenamePropertyRector` |
| Rename a PHP attribute | `RenameAttributeRector` |
| Convert function call → method call (inject service) | `FuncCallToMethodCallRector` |
| Convert function call → static call | `FuncCallToStaticCallRector` |
| Convert function call → `new ClassName(...)` | `FuncCallToNewRector` |
| Convert static call → function call | `StaticCallToFuncCallRector` |
| Convert static call → `new ClassName(...)` | `StaticCallToNewRector` |
| Convert static call → method call (inject service) | `StaticCallToMethodCallRector` |
| Convert method call → static call | `MethodCallToStaticCallRector` |
| Convert method call → function call | `MethodCallToFuncCallRector` |
| Remove a function call entirely | `RemoveFuncCallRector` |
| Remove an argument from a function call | `RemoveFuncCallArgRector` |
| Remove an argument from a method/static call | `ArgumentRemoverRector` |
| Replace string literal → class constant | `StringToClassConstantRector` |

---

## Renaming Rules

All in namespace `Rector\Renaming\Rector\...`

### `RenameFunctionRector`

Renames global function calls.

```php
->withConfiguredRule(RenameFunctionRector::class, [
    'view'  => 'Laravel\Templating\render',
    'debug' => 'dump',
])
```

### `RenameMethodRector`

Renames a method call on a specific class. Optionally change the class too.

```php
use Rector\Renaming\ValueObject\MethodCallRename;

->withConfiguredRule(RenameMethodRector::class, [
    new MethodCallRename('SomeClass', 'oldMethod', 'newMethod'),
    // Also supports MethodCallRenameWithArrayKey for method→array access conversions
])
```

### `RenameStaticMethodRector`

Renames a static method, optionally moving it to a different class.

```php
use Rector\Renaming\ValueObject\RenameStaticMethod;

->withConfiguredRule(RenameStaticMethodRector::class, [
    new RenameStaticMethod('OldClass', 'oldMethod', 'NewClass', 'newMethod'),
])
```

### `RenameClassRector`

Renames a class everywhere it's referenced (use statements, type hints, `instanceof`, `new`, docblocks).

```php
->withConfiguredRule(RenameClassRector::class, [
    'App\OldClass' => 'App\NewClass',
    'OldAlias'     => 'App\Proper\ClassName',
])
```

### `RenameClassConstFetchRector`

Renames a class constant, optionally moving it to a different class.

```php
use Rector\Renaming\ValueObject\RenameClassConstFetch;
use Rector\Renaming\ValueObject\RenameClassAndConstFetch;

->withConfiguredRule(RenameClassConstFetchRector::class, [
    new RenameClassConstFetch('SomeClass', 'OLD_CONST', 'NEW_CONST'),
    new RenameClassAndConstFetch('SomeClass', 'OTHER_CONST', 'OtherClass', 'NEW_CONST'),
])
```

### `RenameConstantRector`

Renames global (non-class) constants.

```php
->withConfiguredRule(RenameConstantRector::class, [
    'MYSQL_ASSOC' => 'MYSQLI_ASSOC',
])
```

### `RenamePropertyRector`

Renames a property access on a specific class.

```php
use Rector\Renaming\ValueObject\RenameProperty;

->withConfiguredRule(RenamePropertyRector::class, [
    new RenameProperty('SomeClass', 'oldProperty', 'newProperty'),
])
```

### `RenameAttributeRector`

Renames a PHP 8 `#[Attribute]` class name everywhere it is used.

```php
use Rector\Renaming\ValueObject\RenameAttribute;

->withConfiguredRule(RenameAttributeRector::class, [
    new RenameAttribute('SimpleRoute', 'BasicRoute'),
])
```

---

## Transform Rules

All in namespace `Rector\Transform\Rector\...`

### `FuncCallToMethodCallRector`

Converts a global function call into a method call on an injected service.

```php
use Rector\Transform\ValueObject\FuncCallToMethodCall;

->withConfiguredRule(FuncCallToMethodCallRector::class, [
    new FuncCallToMethodCall('view', 'Namespaced\SomeRenderer', 'render'),
    // view('tpl') → $this->someRenderer->render('tpl')
])
```

### `FuncCallToStaticCallRector`

Converts a global function call into a static method call.

```php
use Rector\Transform\ValueObject\FuncCallToStaticCall;

->withConfiguredRule(FuncCallToStaticCallRector::class, [
    new FuncCallToStaticCall('view', 'SomeClass', 'render'),
    // view('tpl') → SomeClass::render('tpl')
])
```

### `FuncCallToNewRector`

Converts a function call into a `new ClassName(...)` instantiation.

```php
->withConfiguredRule(FuncCallToNewRector::class, [
    'collection' => 'Collection',
    // collection([]) → new Collection([])
])
```

### `StaticCallToFuncCallRector`

Converts a static method call into a global function call.

```php
use Rector\Transform\ValueObject\StaticCallToFuncCall;

->withConfiguredRule(StaticCallToFuncCallRector::class, [
    new StaticCallToFuncCall('OldClass', 'oldMethod', 'new_function'),
    // OldClass::oldMethod('x') → new_function('x')
])
```

### `StaticCallToNewRector`

Converts a static factory method into a constructor call.

```php
use Rector\Transform\ValueObject\StaticCallToNew;

->withConfiguredRule(StaticCallToNewRector::class, [
    new StaticCallToNew('JsonResponse', 'create'),
    // JsonResponse::create(...) → new JsonResponse(...)
])
```

### `StaticCallToMethodCallRector`

Converts a static method call into an injected service method call.

```php
use Rector\Transform\ValueObject\StaticCallToMethodCall;

->withConfiguredRule(StaticCallToMethodCallRector::class, [
    new StaticCallToMethodCall('Nette\Utils\FileSystem', 'write', 'App\SmartFileSystem', 'dumpFile'),
    // FileSystem::write(...) → $this->smartFileSystem->dumpFile(...)
])
```

### `MethodCallToStaticCallRector`

Converts an instance method call into a static method call.

```php
use Rector\Transform\ValueObject\MethodCallToStaticCall;

->withConfiguredRule(MethodCallToStaticCallRector::class, [
    new MethodCallToStaticCall('SomeDep', 'process', 'StaticCaller', 'anotherMethod'),
    // $this->someDep->process('x') → StaticCaller::anotherMethod('x')
])
```

### `MethodCallToFuncCallRector`

Converts a method call into a global function call.

```php
use Rector\Transform\ValueObject\MethodCallToFuncCall;

->withConfiguredRule(MethodCallToFuncCallRector::class, [
    new MethodCallToFuncCall('SomeClass', 'render', 'view'),
    // $this->render('tpl') → view('tpl')
])
```

### `StringToClassConstantRector`

Replaces a specific string literal with a class constant reference.

```php
use Rector\Transform\ValueObject\StringToClassConstant;

->withConfiguredRule(StringToClassConstantRector::class, [
    new StringToClassConstant('compiler.post_dump', 'Yet\AnotherClass', 'CONSTANT'),
    // 'compiler.post_dump' → \Yet\AnotherClass::CONSTANT
])
```

---

## Removing Rules

All in namespace `Rector\Removing\Rector\...`

### `RemoveFuncCallRector`

Removes entire calls to specified functions (statement is deleted).

```php
->withConfiguredRule(RemoveFuncCallRector::class, [
    'var_dump',
    'dump',
    'dd',
])
```

### `RemoveFuncCallArgRector`

Removes a specific argument (by position) from a function call.

```php
use Rector\Removing\ValueObject\RemoveFuncCallArg;

->withConfiguredRule(RemoveFuncCallArgRector::class, [
    new RemoveFuncCallArg('remove_last_arg', 1),
    // remove_last_arg(1, 2) → remove_last_arg(1)
])
```

### `ArgumentRemoverRector`

Removes a specific argument from a method or static call, optionally only when it matches a given value.

```php
use Rector\Removing\ValueObject\ArgumentRemover;

->withConfiguredRule(ArgumentRemoverRector::class, [
    new ArgumentRemover('SomeClass', 'someMethod', 0, [true]),
    // $obj->someMethod(true) → $obj->someMethod()
    // (only removes when the arg value is `true`)
])
```

---

## When to Write a Custom Rule Instead

Use a configurable rule when the transformation is a **mechanical rename or call-shape change** with no logic. Write a custom rule when:

- The change depends on runtime-style logic (e.g. argument count, types, surrounding context)
- The transformation produces structurally new code, not just a rename
- You need to combine multiple node changes in a single pass
- None of the above rules cover the node types involved
