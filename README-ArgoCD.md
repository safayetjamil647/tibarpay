# Deploying Tibarpay with ArgoCD

This guide provides step-by-step instructions on how to deploy the **Tibarpay** project using [ArgoCD](https://argo-cd.readthedocs.io/). Based on the repository's structure, you can deploy the application using either **Kustomize** (via the `k8s` directory) or **Helm** (via the `helm/tibarpay` directory).

## Prerequisites

1. A running Kubernetes cluster.
2. [ArgoCD installed](https://argo-cd.readthedocs.io/en/stable/getting_started/#1-install-argo-cd) on your Kubernetes cluster.
3. The ArgoCD CLI installed (optional, but useful for managing applications via terminal).
4. The Tibarpay Git repository must be accessible by your ArgoCD instance.

---

## Method 1: Deployment via Kustomize (`k8s/` directory)

The `k8s/` directory contains standard Kubernetes manifests and a `kustomization.yaml` file, which ArgoCD natively supports.

### Option A: Using the ArgoCD UI

1. Open the ArgoCD Web UI and log in.
2. Click **+ NEW APP**.
3. Fill in the following details:
   - **Application Name**: `tibarpay-kustomize`
   - **Project Name**: `default`
   - **Sync Policy**: `Automatic` (or `Manual` if you prefer to sync manually)
   - **Repository URL**: `<Your-Tibarpay-Git-Repo-URL>`
   - **Revision**: `HEAD` (or your preferred branch/tag, e.g., `main`)
   - **Path**: `k8s`
   - **Cluster URL**: `https://kubernetes.default.svc`
   - **Namespace**: `default` (or your preferred namespace, e.g., `tibarpay`)
4. ArgoCD will automatically detect the Kustomize configuration. Click **CREATE**.
5. Once created, click **SYNC** (if not set to automatic) to apply the manifests to your cluster.

### Option B: Using an `Application` CRD (Declarative)

You can create an `Application` custom resource to deploy via Kustomize declaratively. Save the following to a file named `argocd-app-kustomize.yaml` and apply it to the cluster:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: tibarpay-kustomize
  namespace: argocd
spec:
  project: default
  source:
    repoURL: '<Your-Tibarpay-Git-Repo-URL>'
    targetRevision: HEAD
    path: k8s
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Apply it using:
```bash
kubectl apply -f argocd-app-kustomize.yaml
```

---

## Method 2: Deployment via Helm (`helm/tibarpay` directory)

The `helm/tibarpay` directory contains a Helm chart, which is also natively supported by ArgoCD.

### Option A: Using the ArgoCD UI

1. Open the ArgoCD Web UI and log in.
2. Click **+ NEW APP**.
3. Fill in the following details:
   - **Application Name**: `tibarpay-helm`
   - **Project Name**: `default`
   - **Sync Policy**: `Automatic`
   - **Repository URL**: `<Your-Tibarpay-Git-Repo-URL>`
   - **Revision**: `HEAD`
   - **Path**: `helm/tibarpay`
   - **Cluster URL**: `https://kubernetes.default.svc`
   - **Namespace**: `default` (or your preferred namespace)
4. ArgoCD will detect it as a Helm chart. You can override variables from `values.yaml` directly in the UI under the **Parameters** section if needed.
5. Click **CREATE**, then **SYNC**.

### Option B: Using an `Application` CRD (Declarative)

Save the following as `argocd-app-helm.yaml` to deploy the Helm chart declaratively:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: tibarpay-helm
  namespace: argocd
spec:
  project: default
  source:
    repoURL: '<Your-Tibarpay-Git-Repo-URL>'
    targetRevision: HEAD
    path: helm/tibarpay
    helm:
      # Optional: Override Helm values here
      values: |
        # someValue: override
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Apply it using:
```bash
kubectl apply -f argocd-app-helm.yaml
```

---

## Verifying the Deployment

1. Check the ArgoCD UI. The application status should change to `Healthy` and `Synced`.
2. Verify the pods are running in your cluster:
   ```bash
   kubectl get pods -n <your-namespace>
   ```
3. You should see all the expected microservices running (`postgres`, `apisix`, `api-gateway`, `user-service`, `market-service`, etc.).
