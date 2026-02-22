# Agent Skills

A collection of Claude Code skills for PHP development workflows.

## Available Skills

| Skill | Description |
|-------|-------------|
| [composer-upgrade](composer-upgrade/) | Upgrading PHP projects with Composer — `outdated`, `why-not`, `bump` |
| [rector-developer](rector-developer/) | Building Rector PHP rules for AST-based code transformations |

## Installing Skills

### Via npx (recommended)

Install all skills from this repo directly into Claude Code:

```bash
npx skills add peterfox/agent-skills
```

Install a single skill by name:

```bash
npx skills add peterfox/agent-skills --skill composer-upgrade
```

### From a release

Download the `.skill` file for the skill you want from the [releases page](https://github.com/peterfox/agent-skills/releases), then install it:

```bash
claude skill install composer-upgrade.skill
```

## Building Locally

Clone the repo and run the packaging script to generate `.skill` files:

```bash
git clone https://github.com/peterfox/agent-skills.git
cd agent-skills
./package-all.sh
```

This requires the [skill-creator](https://github.com/anthropics/claude-code) skill to be installed locally.

## License

[MIT](LICENSE)
