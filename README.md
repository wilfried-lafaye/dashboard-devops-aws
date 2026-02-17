# Dashboard & Labs DevOps Monorepo

Welcome to the monorepo for the Air Quality Dashboard and Labs DevOps Documentation.

## 📂 Project Structure

- **`apps/air-quality-dashboard/`**: The original Python/Flask application for visualizing air pollution in France.
- **`apps/labs-docs/`**: A Quartz-based documentation site for Labs DevOps practices.
- **`infrastructure/`**: Shared infrastructure code (Kubernetes manifests).

## 🚀 Getting Started

### Air Quality Dashboard

Navigate to `apps/air-quality-dashboard` to work on the dashboard.
See `apps/air-quality-dashboard/README.md` for specific instructions.

### Labs Documentation

Navigate to `apps/labs-docs` to work on the documentation.
Run `npx quartz build --serve` to start the local server.

## ☁️ Deployment

- **Air Quality Dashboard**: Deployed to **AWS (EKS)** via `.github/workflows/deploy-air-quality.yml`.
- **Labs Documentation**: Deployed to **Cloudflare Pages** at [dashboard-devops-aws.pages.dev](https://dashboard-devops-aws.pages.dev) via `.github/workflows/deploy-labs-docs-cloudflare.yml`.
