# PhpParser Node Types Reference

## Table of Contents
1. [Expression Nodes](#expression-nodes)
2. [Statement Nodes](#statement-nodes)
3. [Call Nodes](#call-nodes)
4. [Class Structure Nodes](#class-structure-nodes)
5. [Type & Name Nodes](#type--name-nodes)
6. [Accessing Node Data](#accessing-node-data)

---

## Expression Nodes

| Node Class | Represents | Key Properties |
|------------|-----------|----------------|
| `Expr\Variable` | `$var` | `->name` (string or Expr) |
| `Expr\Assign` | `$a = $b` | `->var`, `->expr` |
| `Expr\AssignOp\*` | `$a += $b` etc. | `->var`, `->expr` |
| `Expr\BinaryOp\*` | `$a + $b`, `$a === $b` etc. | `->left`, `->right` |
| `Expr\UnaryMinus` | `-$a` | `->expr` |
| `Expr\UnaryPlus` | `+$a` | `->expr` |
| `Expr\BooleanNot` | `!$a` | `->expr` |
| `Expr\Instanceof_` | `$a instanceof B` | `->expr`, `->class` |
| `Expr\Ternary` | `$a ? $b : $c` | `->cond`, `->if`, `->else` |
| `Expr\NullsafePropertyFetch` | `$a?->prop` | `->var`, `->name` |
| `Expr\PropertyFetch` | `$a->prop` | `->var`, `->name` |
| `Expr\StaticPropertyFetch` | `A::$prop` | `->class`, `->name` |
| `Expr\ClassConstFetch` | `A::CONST` or `A::class` | `->class`, `->name` |
| `Expr\ArrayDimFetch` | `$a['key']` | `->var`, `->dim` |
| `Expr\Array_` | `['a', 'b']` | `->items` (ArrayItem[]) |
| `Expr\New_` | `new Foo($a)` | `->class`, `->args` |
| `Expr\Clone_` | `clone $a` | `->expr` |
| `Expr\Cast\*` | `(int) $a` etc. | `->expr` |
| `Expr\Closure` | `function() {}` | `->params`, `->stmts`, `->uses` |
| `Expr\ArrowFunction` | `fn() => $expr` | `->params`, `->expr` |
| `Expr\Match_` | `match($a) {}` | `->subject`, `->arms` |
| `Expr\Throw_` | `throw $e` (as expr) | `->expr` |

---

## Statement Nodes

| Node Class | Represents | Key Properties |
|------------|-----------|----------------|
| `Stmt\Expression` | Expression as statement | `->expr` |
| `Stmt\Return_` | `return $val` | `->expr` |
| `Stmt\If_` | `if (...) {}` | `->cond`, `->stmts`, `->elseifs`, `->else` |
| `Stmt\While_` | `while (...) {}` | `->cond`, `->stmts` |
| `Stmt\For_` | `for (;;) {}` | `->init`, `->cond`, `->loop`, `->stmts` |
| `Stmt\Foreach_` | `foreach ($a as $k => $v)` | `->expr`, `->keyVar`, `->valueVar`, `->stmts` |
| `Stmt\Switch_` | `switch ($a) {}` | `->cond`, `->cases` |
| `Stmt\TryCatch` | `try {} catch {}` | `->stmts`, `->catches`, `->finally` |
| `Stmt\Throw_` | `throw $e` (as stmt) | `->expr` |
| `Stmt\Echo_` | `echo $a` | `->exprs` |
| `Stmt\Unset_` | `unset($a)` | `->vars` |
| `Stmt\Declare_` | `declare(strict_types=1)` | `->declares`, `->stmts` |
| `Stmt\Namespace_` | `namespace Foo;` | `->name`, `->stmts` |
| `Stmt\Use_` | `use Foo\Bar;` | `->uses` |

---

## Call Nodes

| Node Class | Represents | Key Properties |
|------------|-----------|----------------|
| `Expr\FuncCall` | `strlen($str)` | `->name` (Name or Expr), `->args` |
| `Expr\MethodCall` | `$obj->method($a)` | `->var`, `->name`, `->args` |
| `Expr\NullsafeMethodCall` | `$obj?->method($a)` | `->var`, `->name`, `->args` |
| `Expr\StaticCall` | `Class::method($a)` | `->class`, `->name`, `->args` |

**Getting args safely:**
```php
$args = $node->getArgs();        // only unpacked Arg nodes (no named/unpack)
$allArgs = $node->args;          // raw Arg[] including named args

// Check first arg exists
if (! isset($args[0])) { return null; }
$firstValue = $args[0]->value;   // the Expr

// Check first-class callable (not a call)
if ($node->isFirstClassCallable()) { return null; }
```

---

## Class Structure Nodes

| Node Class | Represents | Key Properties |
|------------|-----------|----------------|
| `Stmt\Class_` | Class definition | `->name`, `->stmts`, `->extends`, `->implements`, `->attrGroups` |
| `Stmt\Interface_` | Interface definition | `->name`, `->stmts`, `->extends` |
| `Stmt\Trait_` | Trait definition | `->name`, `->stmts` |
| `Stmt\Enum_` | Enum definition | `->name`, `->stmts`, `->scalarType` |
| `Stmt\ClassMethod` | Method | `->name`, `->params`, `->stmts`, `->returnType`, `->flags` |
| `Stmt\Property` | Property declaration | `->props`, `->type`, `->flags` |
| `PropertyItem` | Single property | `->name`, `->default` |
| `Node\Param` | Method/function param | `->var`, `->type`, `->default`, `->flags` (promoted) |
| `Stmt\ClassConst` | Class constant | `->consts`, `->flags` |
| `Stmt\TraitUse` | `use Trait;` inside class | `->traits` |

**Class flags (use `Modifiers::*` or `$node->isPublic()`, etc.):**
```php
$node->isPublic()    // Modifiers::PUBLIC
$node->isProtected() // Modifiers::PROTECTED
$node->isPrivate()   // Modifiers::PRIVATE
$node->isStatic()    // Modifiers::STATIC
$node->isAbstract()  // Modifiers::ABSTRACT
$node->isFinal()     // Modifiers::FINAL
$node->isReadonly()  // Modifiers::READONLY (PHP 8.1+)

// Promoted property param
$param->isPromoted() // has visibility flag set

// Get method by name
$class->getMethod('methodName'); // returns ClassMethod|null
$class->getTraitUses();          // returns TraitUse[]
```

---

## Type & Name Nodes

| Node Class | Represents | Example |
|------------|-----------|---------|
| `Node\Name` | Unqualified name | `Foo` |
| `Node\Name\FullyQualified` | FQN | `\Foo\Bar` |
| `Node\Name\Relative` | Relative name | `namespace\Foo` |
| `Node\Identifier` | Identifier | method/property names |
| `Node\NullableType` | `?Type` | `->type` |
| `Node\UnionType` | `A\|B` | `->types` |
| `Node\IntersectionType` | `A&B` | `->types` |
| `Scalar\String_` | `'hello'` | `->value` |
| `Scalar\Int_` | `42` | `->value` |
| `Scalar\Float_` | `3.14` | `->value` |
| `Expr\ConstFetch` | `true`, `false`, `null`, `MY_CONST` | `->name` |

---

## Accessing Node Data

### Working with Names
```php
// $node->name can be string, Identifier, Name, or Expr
// Use helpers:
$this->getName($node)        // string|null
$this->isName($node, 'foo')  // bool

// For FuncCall/MethodCall, check for dynamic names:
if ($node->name instanceof Expr) { return null; } // dynamic name
```

### Creating Class Name Nodes

**Always use `FullyQualified` instead of `Name` for class references** (new, instanceof, extends, type hints, etc.)

`FullyQualified` represents the fully-qualified class name — the leading `\` is implicit, so do not include it in the string.

```php
use PhpParser\Node\Name\FullyQualified;

// CORRECT — use FullyQualified for class names
new FullyQualified('App\Something')        // represents \App\Something
new FullyQualified('Foo\Bar\Baz')          // represents \Foo\Bar\Baz

// WRONG — never prefix with backslash or use plain Name for class refs
new Name('\App\Something')                 // incorrect
new Name('App\Something')                  // incorrect
```

Use `FullyQualified` when constructing nodes whose class/type property holds a class name:
- `Expr\New_` → `->class`
- `Expr\Instanceof_` → `->class`
- `Expr\StaticCall` → `->class`
- `Expr\ClassConstFetch` → `->class`
- `Stmt\Class_` → `->extends`, `->implements[]`
- `Node\Param` / `Stmt\ClassMethod` → `->type` / `->returnType`

```php
// create "new App\Foo()"
$new = new Expr\New_(new FullyQualified('App\Foo'));

// create "App\Foo::bar()"
$staticCall = new Expr\StaticCall(new FullyQualified('App\Foo'), 'bar');
```

### Working with Args
```php
// Named arguments (PHP 8.0+)
foreach ($node->args as $arg) {
    if ($arg instanceof VariadicPlaceholder) { continue; }
    $arg->name;   // Identifier|null (for named args)
    $arg->value;  // Expr
    $arg->unpack; // bool (for ...$spread)
}
```

### AttributeKey
```php
use Rector\NodeTypeResolver\Node\AttributeKey;

$scope = $node->getAttribute(AttributeKey::SCOPE);   // PHPStan Scope
$original = $node->getAttribute(AttributeKey::ORIGINAL_NODE);
```

See **helpers.md** (NodeTypeResolver section) for `getType()`, `isObjectType()`, and common PHPStan type classes.