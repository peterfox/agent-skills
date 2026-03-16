# Rector Helper Services Reference

## Table of Contents
1. [NodeFactory](#nodefactory)
2. [BetterNodeFinder](#betternodefinder)
3. [NodeComparator](#nodecomparator)
4. [PhpDocInfo / DocBlock](#phpdocinfo--docblock)
5. [NodeNameResolver](#nodenameresolver)
6. [NodeTypeResolver](#nodetyperesolver)
7. [VisibilityManipulator](#visibilitymanipulator)
8. [PhpAttributeAnalyzer](#phpattributeanalyzer)
9. [ValueObject Helpers](#valueobject-helpers)

---

## NodeFactory

**Available as `$this->nodeFactory`** (no constructor injection needed).

```php
use Rector\PhpParser\Node\NodeFactory;
```

### Creating Expressions

```php
// Class constant fetch: SomeClass::CONSTANT
$this->nodeFactory->createClassConstFetch('SomeClass', 'CONSTANT');

// Class constant reference: SomeClass::class
$this->nodeFactory->createClassConstReference('SomeClass');

// Use ObjectReference::* for self/static/parent:
use Rector\Enum\ObjectReference;
$this->nodeFactory->createClassConstFetch(ObjectReference::SELF, 'CONSTANT');

// Array: ['a', 'b']
$this->nodeFactory->createArray(['a', 'b']);
$this->nodeFactory->createArray(['key' => $valueExpr]);

// Args array from values
$this->nodeFactory->createArgs([$expr1, $expr2]);
$this->nodeFactory->createArg($expr);  // single Arg

// Property fetch: $this->property
$this->nodeFactory->createPropertyFetch('this', 'propertyName');
$this->nodeFactory->createPropertyFetch($varExpr, 'propertyName');

// Method call: $this->method($args)
$this->nodeFactory->createLocalMethodCall('methodName');
$this->nodeFactory->createLocalMethodCall('methodName', [$arg1]);
$this->nodeFactory->createMethodCall($varOrName, 'method', $args);

// Assignment: $this->property = $variable
$this->nodeFactory->createPropertyAssignment('propertyName');
$this->nodeFactory->createPropertyAssignmentWithExpr('propertyName', $expr);

// declare(strict_types=1);
$this->nodeFactory->createDeclaresStrictType();
```

### Creating Declarations

```php
// Public method stub
$classMethod = $this->nodeFactory->createPublicMethod('methodName');

// Param from name and PHPStan type
$param = $this->nodeFactory->createParamFromNameAndType('paramName', $phpstanType);

// Private property
$property = $this->nodeFactory->createPrivatePropertyFromNameAndType('propName', $phpstanType);
$property = $this->nodeFactory->createPrivateProperty('propName');  // no type
```

---

## BetterNodeFinder

**Must be injected via constructor.**

```php
use Rector\PhpParser\Node\BetterNodeFinder;

public function __construct(
    private readonly BetterNodeFinder $betterNodeFinder,
) {}
```

### Finding Nodes

```php
// Find all instances of a type within nodes
/** @var FuncCall[] $funcCalls */
$funcCalls = $this->betterNodeFinder->findInstanceOf($nodes, FuncCall::class);

// Find multiple types at once
$calls = $this->betterNodeFinder->findInstancesOf($nodes, [FuncCall::class, MethodCall::class]);

// Find first instance of a type
$firstFunc = $this->betterNodeFinder->findFirstInstanceOf($nodes, FuncCall::class);

// Find first matching a condition
$found = $this->betterNodeFinder->findFirst($nodes, function (Node $node): bool {
    return $node instanceof FuncCall && $this->isName($node, 'strlen');
});

// Find first instance of type BEFORE current position in statements
$stmt = $this->betterNodeFinder->findFirstPreviousOfNode($node, function (Node $n): bool {
    return $n instanceof Variable;
});
```

---

## NodeComparator

**Available as `$this->nodeComparator`** (no constructor injection needed).

```php
// Check if two nodes are structurally equal (ignores comments)
$this->nodeComparator->areNodesEqual($node1, $node2);   // bool

// Check if a node equals any in a list
$this->nodeComparator->isNodeEqual($singleNode, [$node1, $node2]);  // bool

// Check if nodes are the same object (including clones via identity)
$this->nodeComparator->areSameNode($node1, $node2);   // bool

// Print node without comments (for equality via string comparison)
$this->nodeComparator->printWithoutComments($node);   // string
```

---

## PhpDocInfo / DocBlock

**Inject `PhpDocInfoFactory` and `DocBlockUpdater` via constructor.**

```php
use Rector\BetterPhpDocParser\PhpDocInfo\PhpDocInfoFactory;
use Rector\Comments\NodeDocBlock\DocBlockUpdater;

public function __construct(
    private readonly PhpDocInfoFactory $phpDocInfoFactory,
    private readonly DocBlockUpdater $docBlockUpdater,
) {}
```

### Reading PhpDoc

```php
$phpDocInfo = $this->phpDocInfoFactory->createFromNodeOrEmpty($node);

// Get @var tag
$varTagValue = $phpDocInfo->getVarTagValueNode();  // VarTagValueNode|null

// Get @param tags
$paramTags = $phpDocInfo->getParamTagValueByName('paramName');

// Get @return tag
$returnTag = $phpDocInfo->getReturnTagValue();

// Get tags by name
$tags = $phpDocInfo->getTagsByName('@deprecated');

// Check if has tag
$phpDocInfo->hasByName('@readonly');

// Get PHPStan type from @var
$type = $phpDocInfo->getVarType();     // returns PHPStan Type
$type = $phpDocInfo->getReturnType();  // returns PHPStan Type
```

### Modifying PhpDoc

```php
// Remove tag
$phpDocInfo->removeByName('@readonly');
$phpDocInfo->removeReturnTagValueNode();

// Add tag
$phpDocInfo->addPhpDocTagNode($tagNode);

// ALWAYS call this after modifications to persist changes:
$this->docBlockUpdater->updateRefactoredNodeWithPhpDocInfo($node);
```

---

## NodeNameResolver

Used internally — access via AbstractRector protected methods:

```php
$this->getName($node)                          // string|null
$this->isName($node, 'name')                   // bool (exact match)
$this->isNames($node, ['name1', 'name2'])       // bool (any match)
```

For FQN resolution, check if name is `FullyQualified`:
```php
use PhpParser\Node\Name\FullyQualified;

if ($node->class instanceof FullyQualified) {
    $fqn = $node->class->toString();  // 'Foo\Bar\Baz'
}
```

---

## NodeTypeResolver

Used internally — access via AbstractRector protected methods:

```php
$type = $this->getType($node);   // returns PHPStan\Type\Type
$this->isObjectType($node, new ObjectType('Foo\Bar'));
```

### Common PHPStan Types

```php
use PHPStan\Type\ObjectType;
use PHPStan\Type\StringType;
use PHPStan\Type\IntegerType;
use PHPStan\Type\NullType;
use PHPStan\Type\UnionType;
use PHPStan\Type\ArrayType;
use PHPStan\Type\MixedType;
use PHPStan\Type\BooleanType;
use PHPStan\Type\ObjectWithoutClassType;
use PHPStan\Type\Generic\GenericClassStringType;
use PHPStan\Type\VoidType;
use PHPStan\Type\NeverType;

// Check type
if ($type instanceof ObjectType) {
    $type->getClassName();  // 'Foo\Bar'
}
if ($type instanceof UnionType) {
    $type->getTypes();  // Type[]
}
```

---

## VisibilityManipulator

**Inject via constructor.**

```php
use Rector\NodeManipulator\VisibilityManipulator;

public function __construct(
    private readonly VisibilityManipulator $visibilityManipulator,
) {}
```

```php
$this->visibilityManipulator->makePublic($node);
$this->visibilityManipulator->makeProtected($node);
$this->visibilityManipulator->makePrivate($node);
$this->visibilityManipulator->makeStatic($node);
$this->visibilityManipulator->makeReadonly($node);   // PHP 8.1+
$this->visibilityManipulator->removeFinal($node);
```

---

## PhpAttributeAnalyzer

**Inject via constructor.** Use this to check whether a PHP 8 attribute already exists on a node.

```php
use Rector\Php80\NodeAnalyzer\PhpAttributeAnalyzer;

public function __construct(
    private readonly PhpAttributeAnalyzer $phpAttributeAnalyzer,
) {}
```

```php
// Check for a single attribute by FQN
$this->phpAttributeAnalyzer->hasPhpAttribute($node, 'Symfony\Component\Routing\Attribute\Route');

// Check for any of multiple attributes
$this->phpAttributeAnalyzer->hasPhpAttributes($node, [
    'Doctrine\ORM\Mapping\Column',
    'Doctrine\ORM\Mapping\Id',
]);
```

Works on any node that can carry attributes: `Stmt\Class_`, `Stmt\ClassMethod`, `Stmt\Property`, `Node\Param`, `Stmt\Function_`, `Stmt\ClassConst`.

**Whether to guard depends on the attribute's repeatability:**

- **Non-repeatable** (no `Attribute::IS_REPEATABLE`) — adding it twice is a PHP fatal error. Always guard and return `null` if already present.
- **Repeatable** (`Attribute::IS_REPEATABLE`) — multiple instances are valid. Only guard if the specific instance you would add is already there, or if the rule's intent requires it.

Check the target attribute class declaration to confirm which case applies.

```php
// Guard for a non-repeatable attribute
public function refactor(Node $node): ?Node
{
    if ($this->phpAttributeAnalyzer->hasPhpAttribute($node, 'App\MyAttribute')) {
        return null; // already present, skip
    }

    // ... add the attribute
    return $node;
}
```

**Add a skip fixture** (`skip_attribute_already_present.php.inc`) for non-repeatable attributes to confirm the rule does not produce a duplicate. For repeatable attributes, add skip fixtures for any other condition that should prevent the rule from applying.

---

## ValueObject Helpers

### MethodName (`Rector\ValueObject\MethodName`)

```php
MethodName::CONSTRUCT      // '__construct'
MethodName::DESTRUCT       // '__destruct'
MethodName::CLONE          // '__clone'
MethodName::TO_STRING      // '__toString'
MethodName::INVOKE         // '__invoke'
MethodName::CALL           // '__call'
MethodName::CALL_STATIC    // '__callStatic'
MethodName::SET_UP         // 'setUp'
```

Usage: `$class->getMethod(MethodName::CONSTRUCT)`

### ObjectReference (`Rector\Enum\ObjectReference`)

```php
ObjectReference::SELF      // 'self'
ObjectReference::STATIC    // 'static'
ObjectReference::PARENT    // 'parent'
```

Usage: `$this->nodeFactory->createClassConstFetch(ObjectReference::SELF, 'CONSTANT')`