# Git Repository Anchor

This Odoo module provides a system for managing Git repositories using Nostr events. It allows users to create, update, and fork repositories, as well as manage branches and maintainers.

## Features

- Create, update, and fork Git repositories
- Manage repository maintainers
- Create and manage branches
- Log all actions as Nostr events
- Odoo views for easy management through the UI
- CLI for standalone usage

## Installation

1. Place the `git_repository_anchor` directory in your Odoo addons path.
2. Update your Odoo apps list.
3. Install the "Git Repository Anchor" module from the Odoo Apps menu.

## Usage

### Through Odoo Interface

1. Navigate to the "Git Repositories" menu item.
2. Use the provided views to manage repositories, branches, and maintainers.

### Using CLI

A CLI script is provided for standalone usage. Example usage:

```bash
python cli_script.py create --name "New Repo" --description "A new repository" --maintainers 1 2
python cli_script.py update --repo-id 1 --description "Updated description"
python cli_script.py fork --original-repo-id 1 --new-name "Forked Repo"
