# Contributing to ZERO DOOR

First off, thank you for contributing to the **ZERO DOOR** project! This document outlines the standards and workflows for our development process.

## 🛠 Development Workflow
We follow the **GitHub Flow** and **Scrumban** methodology:
1. **Pick a Task:** Select an issue from the [GitHub Project Board](https://github.com/EurusDevSec/Zero-Door/projects).
2. **Branching:** Create a new branch from `main` using the naming convention below.
3. **Development:** Implement your changes, ensuring code follows the project's tech stack (Java/Go).
4. **Commit:** Use **Conventional Commits** for all messages.
5. **Pull Request:** Open a PR against `main` using our PR Template.

## 🌿 Branch Naming Conventions
Branches must follow this format: `<type>/<task-id>-<short-description>`

* **feature/**: New features (e.g., `feature/s3-gaia-core`)
* **bugfix/**: Fixing issues (e.g., `bugfix/s10-kafka-connection`)
* **infra/**: Infrastructure and K8s setup (e.g., `infra/s1-repo-setup`)
* **docs/**: Documentation changes (e.g., `docs/s11-final-report`)

## 💬 Commit Message Conventions
We enforce **Conventional Commits** to maintain a clean and readable history:

Format: `<type>: <description>`

* **feat**: A new feature (e.g., `feat: implement anomaly detection in Gaia`)
* **fix**: A bug fix (e.g., `fix: resolve memory leak in Chaos Worker`)
* **docs**: Documentation only changes (e.g., `docs: update README with K8s guide`)
* **style**: Changes that do not affect the meaning of the code (white-space, formatting)
* **refactor**: A code change that neither fixes a bug nor adds a feature
* **test**: Adding missing tests or correcting existing tests
* **chore**: Changes to the build process or auxiliary tools/libraries

Example: `feat: add Spring AI integration for Nemesis payload generation`

## 🔎 Pull Request Process
1. Ensure your code compiles successfully (`mvn compile` or `go build`).
2. Update the `docs/` or `README.md` if your changes introduce new functionality.
3. Link your PR to the corresponding issue (e.g., `Fixes #1`).
4. Wait for a review from the Project Lead (Hoàng) or assigned teammate.

## 🛡️ Coding Standards
* **Java**: Follow standard Spring Boot coding styles.
* **Go**: Use `gofmt` for consistent formatting.
* **K8s**: Ensure all manifests are valid YAML.



