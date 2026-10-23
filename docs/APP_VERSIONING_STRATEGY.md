# Architectural Decision Record: Application Versioning & Locator Management

* **Status:** Pending Decision / Under Review (TODO)
* **Date:** 2026-10-23
* **Context:** Multi-Environment UI Testing with Heterogeneous Application Versions

---

## 1. Problem Statement

In automated end-to-end testing, different environments (e.g. Local, QA, Staging, Production) often run different versions of the application under test (e.g., Staging runs `v2.1.0` with redesigned UI and new `data-test` attributes, while Production runs `v1.9.0` with legacy DOM structure).

Currently, UI locators (XPath and CSS selectors) are written directly into high-level business keywords (`resources/keywords/BStackDemoKeywords.resource`).

### Risks of Hardcoding Selectors in Keywords:
1. **Version Incompatibility**: Updating a locator for `v2` in a keyword breaks tests running against `v1`.
2. **Code Duplication**: Duplicating entire keyword resource files (`BStackDemoKeywords_v1.resource`, `BStackDemoKeywords_v2.resource`) duplicates business logic and violates DRY principles.

---

## 2. Evaluated Architectural Options

### Concept 1: Versioned Locator Repository with Delta Inheritance (Recommended)

#### Overview:
Separate **Workflow Logic** (`*.resource`) from **DOM Locators** (`resources/locators/*.yaml`).

```
resources/
├── locators/
│   ├── base.yaml              # Complete selector map for base/v1
│   └── v2.yaml                # ONLY selectors that changed in v2 (Delta overrides)
└── config/
    └── environments/
        ├── default/
        │   └── env.yaml       # AppVersion: "v1"
        └── staging/
            └── env.yaml       # AppVersion: "v2"
```

#### Mechanism:
1. `resources/locators/base.yaml` defines the full baseline DOM map:
   ```yaml
   buy_btn: "xpath=//p[text()='{product_name}']/ancestor::div[contains(@class, 'shelf-item')]//div[contains(@class, 'shelf-item__buy-btn')]"
   cart_close_btn: ".float-cart__close-btn"
   checkout_btn: ".buy-btn"
   cart_badge_closed: ".bag--float-cart-closed"
   ```
2. `resources/locators/v2.yaml` defines only the overrides:
   ```yaml
   buy_btn: "css=[data-test='add-to-cart-{product_name}']"
   checkout_btn: "id=checkout-proceed-btn"
   ```
3. `DataLoader.py` reads `AppVersion` from the active environment's `env.yaml`. It loads `base.yaml` and merges `v2.yaml` on top, injecting `${LOC}` into the suite scope.
4. Business keywords stay 100% version-agnostic:
   ```robot
   Add Product To Cart
       [Arguments]    ${product_name}
       ${locator}=    Format String    ${LOC['buy_btn']}    product_name=${product_name}
       Click    ${locator}
   ```

* **Pros**: Zero keyword duplication; delta inheritance means `v2.yaml` only defines the 2–3 selectors that changed; environment-driven.
* **Cons**: Requires one dictionary lookup step during keyword execution.

---

### Concept 2: Resilient Union / Fallback Selectors (Zero-Config)

#### Overview:
Use CSS comma lists or XPath unions (`|`) to match both versions simultaneously without version flags:

```robot
${buy_btn}=    css=[data-test='add-to-cart'], .shelf-item__buy-btn
${checkout}=   css=#checkout-proceed-btn, .buy-btn
```

* **Pros**: Zero configuration; works across versions automatically.
* **Cons**: Only works for simple selector renaming. Fails when interaction workflows or element hierarchies change (e.g. sliding drawer vs modal dialog vs page redirect). Can mask regressions.

---

### Concept 3: Strategy Pattern with Dynamic Resource Imports

#### Overview:
When both **locators** AND **workflow steps** differ fundamentally between versions (e.g. v1 has a 3-step checkout wizard, v2 has a 1-page accordion checkout):

```
resources/keywords/
├── common/BaseKeywords.resource
├── v1/VersionKeywords.resource
└── v2/VersionKeywords.resource
```

`DataLoader` dynamically registers the matching version resource file into the suite AST based on `AppVersion`.

* **Pros**: Handles radical redesigns where user interaction steps differ between versions.
* **Cons**: Higher maintenance; risks duplicate keyword code for shared actions.

---

## 3. Comparison Matrix

| Criteria | Concept 1: Locator Repo (Delta Inheritance) | Concept 2: Union Fallback Selectors | Concept 3: Dynamic Version Strategy |
| :--- | :---: | :---: | :---: |
| **Code Duplication** | **Zero (Deltas only)** | Zero | Medium (Duplicate keywords) |
| **Maintenance Burden** | **Very Low** | Medium (Complex selector strings) | High |
| **DOM Redesign Handling** | **Excellent** | Poor | Excellent |
| **Workflow Step Changes** | Good | None | **Excellent** |
| **LEGO Architecture Fit** | **100% (Config-driven)** | 50% (Hardcoded in keywords) | 80% |

---

## 4. Decision & Next Steps (TODO)

* **Decision Status**: Parked for evaluation.
* **Next Action**:
  - [ ] Review options with the team.
  - [ ] Choose primary approach (Concept 1 recommended for standard locator differences).
  - [ ] When ready to implement, add `resources/locators/` and extend `DataLoader.py` to merge delta locators.
