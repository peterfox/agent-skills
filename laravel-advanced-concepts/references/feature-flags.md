# Feature Flags in Laravel — Laravel Pennant

## Installation

```bash
composer require laravel/pennant
php artisan vendor:publish --provider="Laravel\Pennant\PennantServiceProvider"
php artisan migrate
```

## Defining Features

Define features in a service provider's `boot()` method (or a dedicated `AppServiceProvider`):

```php
use Laravel\Pennant\Feature;

// Simple boolean flag — resolves based on user
Feature::define('new-checkout', fn (User $user) => $user->isInBetaProgram());

// Percentage rollout
Feature::define('new-dashboard', fn (User $user) =>
    $user->id % 10 === 0  // 10% of users
);

// Always on/off (useful for kill switches)
Feature::define('maintenance-mode', false);

// Multiple variants (A/B test)
Feature::define('checkout-button-color', fn (User $user) =>
    $user->id % 2 === 0 ? 'blue' : 'green'
);
```

## Checking Features

```php
// Boolean check
if (Feature::active('new-checkout')) {
    // show new checkout
}

// Blade directive
@feature('new-checkout')
    <x-new-checkout />
@endfeature

// Check for specific variant
$color = Feature::value('checkout-button-color'); // 'blue' or 'green'

// Check for a specific user (not the authenticated user)
Feature::for($user)->active('new-checkout');

// Deactivate for a specific user
Feature::for($user)->deactivate('new-checkout');

// Activate for a specific user
Feature::for($user)->activate('new-checkout');
```

## Scope

Pennant evaluates flags against a **scope** — the entity the flag is evaluated for. By default this is `Auth::user()`.

```php
// Evaluate against a team instead of the user
Feature::for($team)->active('team-feature');

// Evaluate against a custom model
Feature::for($tenant)->active('enterprise-feature');
```

## Storing State

Pennant has two drivers:

- **`database`** (default for production): stores each resolved value per scope in the `features` table. Once resolved, the value is cached. This means the closure runs once per scope/feature combination and the result is persisted.
- **`array`** (default for testing): in-memory, resets between requests. Great for tests.

> **Important**: Because values are stored after first resolution, changing the closure logic won't affect users who already have a stored value. Use `Feature::forget('feature-name')` or `Feature::purge()` to clear stored values when you update feature logic.

## Activating / Deactivating in Bulk

```php
// Activate for all users
Feature::activateForEveryone('new-checkout');

// Deactivate for all users
Feature::deactivateForEveryone('new-checkout');

// Purge all stored values (forces re-evaluation)
Feature::purge('new-checkout');
```

## Class-based Features

For complex feature logic, use a class:

```php
// app/Features/NewCheckout.php
class NewCheckout
{
    public function resolve(User $user): bool
    {
        return $user->hasSubscription('pro') && $user->region === 'EU';
    }
}

// Register
Feature::define(NewCheckout::class);

// Check
Feature::active(NewCheckout::class);
```

## Testing

```php
use Laravel\Pennant\Feature;

// Force a feature on/off in tests
Feature::activate('new-checkout');
Feature::deactivate('new-checkout');

// Or define it directly in the test
Feature::define('new-checkout', true);
Feature::define('new-checkout', false);
```

## Common Patterns

### Gradual Rollout by User ID
```php
Feature::define('new-search', fn (User $user) =>
    ($user->id % 100) < 20  // 20% rollout
);
```

### Staff / Internal Preview
```php
Feature::define('admin-panel-v2', fn (User $user) =>
    $user->hasRole('staff') || app()->environment('local', 'staging')
);
```

### Opt-in Beta
```php
// User signs up for beta — activate manually
Feature::for($user)->activate('beta-feature');

// Check in feature definition
Feature::define('beta-feature', fn (User $user) => false); // closed by default
```

### Kill Switch
```php
Feature::define('new-payment-processor', fn (User $user) =>
    config('features.new_payment_processor', false)
);
```

## When to Consider Alternatives

- **LaunchDarkly / Flagsmith / Unleash**: if you need targeting rules defined in a UI without code deploys, multi-environment management, real-time flag updates, or advanced analytics. Pennant has PHP SDK integrations for some of these.
- **Simple `config()` values**: for flags that never need per-user state and only change between deploys.
