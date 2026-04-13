# State Machines in Laravel — spatie/laravel-model-states

## Installation

```bash
composer require spatie/laravel-model-states
```

## Core Concepts

- **State**: a class representing one possible value of a status field
- **Transition**: optionally, a class representing the logic for moving between two states
- **`HasStates` trait**: added to the Eloquent model
- The package validates that transitions are allowed and will throw `CouldNotPerformTransition` if not

## Basic Setup

### 1. Create State classes

```php
// app/States/Order/OrderState.php (abstract base)
use Spatie\ModelStates\State;
use Spatie\ModelStates\StateConfig;

abstract class OrderState extends State
{
    abstract public function label(): string;

    public static function config(): StateConfig
    {
        return parent::config()
            ->default(Pending::class)
            ->allowTransition(Pending::class, Confirmed::class)
            ->allowTransition(Confirmed::class, Shipped::class)
            ->allowTransition(Confirmed::class, Cancelled::class)
            ->allowTransition(Shipped::class, Delivered::class);
    }
}

// app/States/Order/Pending.php
class Pending extends OrderState
{
    public static $name = 'pending';
    public function label(): string { return 'Pending'; }
}

// app/States/Order/Confirmed.php
class Confirmed extends OrderState
{
    public static $name = 'confirmed';
    public function label(): string { return 'Confirmed'; }
}

// (create Shipped, Delivered, Cancelled similarly)
```

### 2. Add to the model

```php
use Spatie\ModelStates\HasStates;

class Order extends Model
{
    use HasStates;

    protected $casts = [
        'status' => OrderState::class,
    ];
}
```

### 3. Create the migration

```php
$table->string('status')->default('pending');
```

## Performing Transitions

```php
$order = Order::find(1);

// Simple transition
$order->status->transitionTo(Confirmed::class);

// Or via the model
$order->transitioning('status')->to(Confirmed::class);

// Check if a transition is allowed
$order->status->canTransitionTo(Shipped::class); // bool
```

## Transition Classes (with logic)

When a transition needs to do work (send email, create records, fire events), extract it into a class:

```php
// app/States/Order/Transitions/PendingToConfirmed.php
use Spatie\ModelStates\Transition;

class PendingToConfirmed extends Transition
{
    public function __construct(
        private Order $order,
        private User $confirmedBy,
    ) {}

    public function handle(): Order
    {
        $this->order->confirmed_at = now();
        $this->order->confirmed_by = $this->confirmedBy->id;
        $this->order->save();

        event(new OrderConfirmed($this->order));

        return $this->order;
    }
}
```

Register in `StateConfig`:
```php
->allowTransition(Pending::class, Confirmed::class, PendingToConfirmed::class)
```

Invoke:
```php
$order->status->transitionTo(Confirmed::class, confirmedBy: $user);
// or
(new PendingToConfirmed($order, $user))->handle();
```

## Querying by State

```php
// Scope to a state
Order::whereState('status', Pending::class)->get();
Order::whereState('status', [Pending::class, Confirmed::class])->get();
Order::whereNotState('status', Cancelled::class)->get();
```

## State-specific Behavior

States are objects — put behavior on them:

```php
abstract class OrderState extends State
{
    abstract public function canBeEdited(): bool;
    abstract public function badgeColor(): string;
}

class Pending extends OrderState
{
    public function canBeEdited(): bool { return true; }
    public function badgeColor(): string { return 'yellow'; }
}

class Delivered extends OrderState
{
    public function canBeEdited(): bool { return false; }
    public function badgeColor(): string { return 'green'; }
}

// In a controller or view:
$order->status->canBeEdited(); // delegates to the state object
```

## Common Real-World State Machines

### Order lifecycle
```
pending → confirmed → shipped → delivered
                   ↘ cancelled
```

### Subscription lifecycle
```
trialing → active → past_due → cancelled
                 ↘ paused → active
```

### Job application
```
applied → screening → interview → offer_sent → accepted
                               ↘ rejected
```

### Support ticket
```
open → in_progress → pending_customer → resolved → closed
                                      ↗
```

## Testing

```php
// Assert current state
$this->assertEquals(Pending::class, $order->status::class);

// Assert transition succeeds
$order->status->transitionTo(Confirmed::class);
$order->refresh();
$this->assertInstanceOf(Confirmed::class, $order->status);

// Assert invalid transition throws
$this->expectException(\Spatie\ModelStates\Exceptions\CouldNotPerformTransition::class);
$order->status->transitionTo(Delivered::class); // skipping Shipped
```

## Alternatives

- **[symfony/workflow](https://symfony.com/doc/current/workflow.html)**: more powerful (supports Petri nets / parallel states), but no Eloquent integration out of the box. Worth it if you have very complex workflows with parallel states.
- **[asantibanez/laravel-eloquent-state-machines](https://github.com/asantibanez/laravel-eloquent-state-machines)**: similar to spatie, with history tracking built in.
- **Plain enum + match**: fine if transitions have no logic and you don't need enforcement. Don't reach for a package if a simple `enum Status { Pending, Confirmed }` with a service method covers your needs.
