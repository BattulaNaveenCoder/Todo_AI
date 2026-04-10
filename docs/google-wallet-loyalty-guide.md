# Krust — Google Wallet Loyalty Card Implementation Guide

> A complete, beginner-friendly, production-ready guide to adding a Google Wallet Loyalty Card to a restaurant app built with **ASP.NET Core** + **ReactJS**, deployed on **Azure**.

---

## Table of Contents
1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Backend Implementation (ASP.NET Core)](#3-backend-implementation-aspnet-core)
4. [Frontend Implementation (ReactJS)](#4-frontend-implementation-reactjs)
5. [End-to-End User Flow](#5-end-to-end-user-flow)
6. [Updating the Loyalty Card](#6-updating-the-loyalty-card)
7. [Architecture](#7-architecture)
8. [Security & Best Practices](#8-security--best-practices)
9. [Folder Structure](#9-folder-structure)
10. [Files to Create / Modify](#10-files-to-create--modify)
11. [Verification](#11-verification)

---

## 1. Overview

### 1.1 What is a Google Wallet Loyalty Card?
A Google Wallet **Loyalty Card** is a digital pass stored in the user's Google Wallet app on Android. It can show:

- Program name & logo (Krust branding)
- Member name & ID, barcode/QR code
- **Points balance** (e.g. "320 Krust Points")
- **Tier** (Bronze / Silver / Gold)
- Offers, hero image, expiry, terms

The pass updates **server-side** — when Krust changes the points value via the Google Wallet API, the user's wallet refreshes automatically. No re-install needed.

### 1.2 The Class + Object model (the single most important concept)
Google Wallet uses a **Class + Object** model, similar to an OOP class and instance:

| Concept | What it is | How many | Example |
|---|---|---|---|
| **Loyalty Class** | Template / program definition | **1 per program** | "Krust Rewards" — logo, colors, T&Cs |
| **Loyalty Object** | One user's specific card | **1 per user** | "Naveen — 320 pts — Silver" |

You create the class **once**. You create one object **per user** the first time they save a pass. Then you `PATCH` that object whenever points change.

### 1.3 End-to-end flow
```
1. (One-time) Krust creates a Loyalty Class in Google Wallet.
2. User logs into Krust web app and clicks "Add to Google Wallet".
3. React calls Krust API: POST /api/wallet/loyalty/save-link
4. Krust API:
     a. Looks up user, builds loyalty object payload (points, name, etc.)
     b. Inserts/updates the Loyalty Object via Google Wallet REST API
     c. Signs a JWT with the service account private key
     d. Returns https://pay.google.com/gp/v/save/<JWT>
5. React renders the official "Add to Google Wallet" button linking to that URL.
6. User taps it → Google Wallet opens → user confirms → pass saved.
7. Later, when user earns/redeems points:
     Krust backend → PATCH /loyaltyObject/{id} → Google pushes update to device.
```

---

## 2. Prerequisites

### 2.1 Google Pay & Wallet Console
1. Go to **https://pay.google.com/business/console** and sign in with the Google account that will own Krust's wallet program.
2. Request access to the **Google Wallet API** (left nav → "Google Wallet API"). Approval is usually instant for the test environment, manual for production publishing.
3. Note your **Issuer ID** — a numeric value (e.g. `3388000000022xxxxxx`). You will use this in every class and object ID.

### 2.2 Google Cloud project
1. Go to **https://console.cloud.google.com**, create a project (e.g. `krust-wallet-prod`).
2. **APIs & Services → Library →** enable **Google Wallet API**.
3. **IAM & Admin → Service Accounts →** create a service account (e.g. `krust-wallet-sa`).
4. On the service account → **Keys → Add Key → JSON →** download. This is `krust-wallet-sa.json`. **Treat this like a password.**
5. Back in **Google Pay & Wallet Console → Users**, add the service account's email (`krust-wallet-sa@krust-wallet-prod.iam.gserviceaccount.com`) as a **Developer** on your Issuer account.

> ⚠️ **Step 5 is the #1 thing beginners miss.** Without it, the API returns `403` even though the credentials are valid.

### 2.3 Required permissions
- The service account needs **no GCP IAM roles** for Wallet — its authority comes from being added in the Wallet Console (step 2.2.5).
- Scope used at runtime: `https://www.googleapis.com/auth/wallet_object.issuer`.

### 2.4 Local dev secrets
Store `krust-wallet-sa.json` **outside the repo**. Use **.NET User Secrets** in dev:

```bash
dotnet user-secrets init
dotnet user-secrets set "GoogleWallet:ServiceAccountJsonPath" "C:\\secrets\\krust-wallet-sa.json"
dotnet user-secrets set "GoogleWallet:IssuerId" "3388000000022xxxxxx"
dotnet user-secrets set "GoogleWallet:ClassId"  "3388000000022xxxxxx.krust_loyalty_v1"
```

In production: upload the JSON contents to **Azure Key Vault** as a secret and reference it from App Service via Key Vault references.

---

## 3. Backend Implementation (ASP.NET Core)

### 3.1 NuGet packages
```bash
dotnet add package Google.Apis.Walletobjects.v1
dotnet add package Google.Apis.Auth
```
- `Google.Apis.Auth` — handles OAuth + JWT signing.
- `Google.Apis.Walletobjects.v1` — typed REST client for Wallet.

### 3.2 Configuration model

`appsettings.json` (non-secret values only):
```json
{
  "GoogleWallet": {
    "IssuerId": "REPLACE_IN_KEYVAULT",
    "ClassId": "REPLACE_IN_KEYVAULT.krust_loyalty_v1",
    "ProgramName": "Krust Rewards",
    "Origins": [ "https://app.krust.com" ]
  }
}
```

`GoogleWalletOptions.cs`:
```csharp
public class GoogleWalletOptions
{
    public string IssuerId { get; set; } = "";
    public string ClassId { get; set; } = "";
    public string ProgramName { get; set; } = "";
    public string[] Origins { get; set; } = Array.Empty<string>();
}
```

Bind in `Program.cs`:
```csharp
builder.Services.Configure<GoogleWalletOptions>(
    builder.Configuration.GetSection("GoogleWallet"));
builder.Services.AddSingleton<GoogleWalletService>();
```

### 3.3 Service: `GoogleWalletService.cs`

Responsibilities:
1. Load service account credentials **once** (singleton).
2. `EnsureClassExistsAsync()` — idempotent class create.
3. `UpsertLoyaltyObjectAsync(KrustUser user)` — create or PATCH the object.
4. `BuildSaveJwt(string objectId)` — return the signed save URL.

```csharp
using System.Net;
using System.Text.Json;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Services;
using Google.Apis.Walletobjects.v1;
using Google.Apis.Walletobjects.v1.Data;
using Microsoft.Extensions.Options;

public class GoogleWalletService
{
    private readonly WalletobjectsService _wallet;
    private readonly ServiceAccountCredential _credential;
    private readonly GoogleWalletOptions _opts;
    private bool _classEnsured;

    public GoogleWalletService(IOptions<GoogleWalletOptions> opts, IConfiguration cfg)
    {
        _opts = opts.Value;
        var json = cfg["GoogleWallet:ServiceAccountJson"]; // pulled from Key Vault in prod

        _credential = (ServiceAccountCredential)GoogleCredential
            .FromJson(json)
            .CreateScoped("https://www.googleapis.com/auth/wallet_object.issuer")
            .UnderlyingCredential;

        _wallet = new WalletobjectsService(new BaseClientService.Initializer
        {
            HttpClientInitializer = _credential,
            ApplicationName = "Krust"
        });
    }

    public async Task EnsureClassExistsAsync()
    {
        if (_classEnsured) return;
        try
        {
            await _wallet.Loyaltyclass.Get(_opts.ClassId).ExecuteAsync();
        }
        catch (Google.GoogleApiException ex) when (ex.HttpStatusCode == HttpStatusCode.NotFound)
        {
            var newClass = new LoyaltyClass
            {
                Id = _opts.ClassId,
                IssuerName = "Krust",
                ProgramName = _opts.ProgramName,
                ReviewStatus = "UNDER_REVIEW", // becomes APPROVED after Google review
                ProgramLogo = new Image
                {
                    SourceUri = new ImageUri { Uri = "https://app.krust.com/logo.png" }
                },
                HexBackgroundColor = "#b71c1c"
            };
            await _wallet.Loyaltyclass.Insert(newClass).ExecuteAsync();
        }
        _classEnsured = true;
    }

    public async Task<LoyaltyObject> UpsertLoyaltyObjectAsync(KrustUser user)
    {
        var objectId = $"{_opts.IssuerId}.user-{user.Id}";

        var loyaltyObject = new LoyaltyObject
        {
            Id = objectId,
            ClassId = _opts.ClassId,
            State = "ACTIVE",
            AccountId = user.Id.ToString(),
            AccountName = user.FullName,
            LoyaltyPoints = new LoyaltyPoints
            {
                Label = "Points",
                Balance = new LoyaltyPointsBalance { Int__ = user.Points }
            },
            Barcode = new Barcode { Type = "QR_CODE", Value = user.LoyaltyCode }
        };

        try
        {
            await _wallet.Loyaltyobject.Get(objectId).ExecuteAsync();
            return await _wallet.Loyaltyobject.Patch(loyaltyObject, objectId).ExecuteAsync();
        }
        catch (Google.GoogleApiException ex) when (ex.HttpStatusCode == HttpStatusCode.NotFound)
        {
            return await _wallet.Loyaltyobject.Insert(loyaltyObject).ExecuteAsync();
        }
    }

    public string BuildSaveJwt(string objectId)
    {
        var payload = new
        {
            iss = _credential.Id,                      // service account email
            aud = "google",
            typ = "savetowallet",
            iat = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            origins = _opts.Origins,
            payload = new
            {
                loyaltyObjects = new[] { new { id = objectId } }
            }
        };

        // Google.Apis.Auth can sign assertions directly:
        return _credential.CreateAssertionFromPayload(JsonSerializer.Serialize(payload));
    }
}
```

> The JWT can also be built with a third-party library like `JWT.Net` and `RS256Algorithm`. The `CreateAssertionFromPayload` route shown above keeps you to a single Google package.

### 3.4 API endpoint: `WalletController.cs`
```csharp
[ApiController]
[Route("api/wallet/loyalty")]
[Authorize] // user must be logged into Krust
public class WalletController : ControllerBase
{
    private readonly GoogleWalletService _wallet;
    private readonly IUserService _users;

    public WalletController(GoogleWalletService wallet, IUserService users)
    {
        _wallet = wallet;
        _users = users;
    }

    [HttpPost("save-link")]
    public async Task<ActionResult<SaveLinkResponse>> CreateSaveLink()
    {
        var user = await _users.GetCurrentAsync(User);
        await _wallet.EnsureClassExistsAsync();
        var obj = await _wallet.UpsertLoyaltyObjectAsync(user);
        var jwt = _wallet.BuildSaveJwt(obj.Id);
        return Ok(new SaveLinkResponse($"https://pay.google.com/gp/v/save/{jwt}"));
    }
}

public record SaveLinkResponse(string SaveUrl);
```

### 3.5 Secure API design checklist
- `[Authorize]` — only the authenticated user can create their own pass. **Never accept a `userId` from the client**; pull it from `User.Identity`.
- Rate-limit `/save-link` (e.g. 10/min/user) via ASP.NET Core's `AddRateLimiter`.
- Log issuer/object IDs but **never** the JWT contents or service-account JSON.
- Cache `EnsureClassExistsAsync()` after first success to avoid an extra GET each call.
- Return 5xx as opaque "Wallet temporarily unavailable" — don't leak Google error bodies.

---

## 4. Frontend Implementation (ReactJS)

### 4.1 API client

```ts
// src/api/wallet.ts
export async function getLoyaltySaveLink(): Promise<string> {
  const res = await fetch("/api/wallet/loyalty/save-link", {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) throw new Error("Wallet link failed");
  const data = await res.json();
  return data.saveUrl;
}
```

### 4.2 Save button component

Download the official **Add to Google Wallet** badge from Google's brand guidelines page and place it in `public/google-wallet/`.

```tsx
// src/components/loyalty/AddToGoogleWalletButton.tsx
import { useState } from "react";
import { getLoyaltySaveLink } from "../../api/wallet";

export function AddToGoogleWalletButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      const url = await getLoyaltySaveLink();
      window.location.href = url; // Android Chrome opens Google Wallet
    } catch (e) {
      setError("Could not generate your pass. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={loading}
        aria-label="Add Krust Rewards to Google Wallet"
        style={{ background: "none", border: 0, padding: 0, cursor: "pointer" }}
      >
        <img
          src="/google-wallet/enUS_add_to_google_wallet_add-wallet-badge.png"
          alt="Add to Google Wallet"
          height={48}
        />
      </button>
      {error && <p role="alert">{error}</p>}
    </div>
  );
}
```

### 4.3 Where to mount it
Inside the user's Loyalty page (e.g. `src/pages/LoyaltyPage.tsx`), below the points-balance display.

Optionally hide the button if the user is **not** on Android:
```ts
const isAndroid = /Android/.test(navigator.userAgent);
```
On desktop the link still works (Google shows a QR/email handoff), but you may prefer to hide it for the MVP since the target surface is Android Chrome.

---

## 5. End-to-End User Flow

```
[User logs in to Krust]
   ↓ JWT cookie set on Krust API
[Loyalty page loads]
   ↓ React fetches /api/loyalty/me  →  shows points balance
[User taps "Add to Google Wallet"]
   ↓ POST /api/wallet/loyalty/save-link
   ↓ Backend: ensure class → upsert object → sign JWT → return save URL
[Browser navigates to pay.google.com/gp/v/save/<jwt>]
   ↓ Google Wallet app opens, asks the user to confirm
[Pass saved on device]
   ↓
[User makes a purchase in store]
   ↓ POS hits Krust /api/loyalty/award { userId, +30 }
   ↓ Krust updates DB and calls GoogleWalletService.UpsertLoyaltyObjectAsync(user)
[Google pushes silent update → user's pass shows new balance within seconds]
```

---

## 6. Updating the Loyalty Card

There is **only one update mechanism**: `PATCH` the `LoyaltyObject` by ID. The `UpsertLoyaltyObjectAsync` from §3.3 handles both creation and updates.

**Wrap it behind a domain event** so any code path that changes points triggers a wallet sync:
```csharp
// In your existing PointsService
public async Task AwardPointsAsync(Guid userId, int delta)
{
    var user = await _users.AddPointsAsync(userId, delta);
    _bus.Publish(new LoyaltyPointsChanged(userId)); // handler calls _wallet.UpsertLoyaltyObjectAsync
}
```
The handler should retry with exponential backoff and dead-letter on repeated failure. Decoupling like this ensures that a Google API blip never blocks the in-store transaction.

**Tier / offer changes** use the same PATCH:
- Per-user offers → set `LoyaltyObject.TextModulesData`
- Program-wide changes (new logo, T&Cs) → update the `LoyaltyClass` once and it propagates to all users

**Bulk push notifications** (e.g. *"Double points weekend!"*) use `LoyaltyClass.messages[]` with `messageType = TEXT_AND_NOTIFY`.

---

## 7. Architecture

```
┌────────────────────┐    HTTPS / cookie auth   ┌────────────────────────────┐
│  React (Krust UI)  │ ───────────────────────▶ │  ASP.NET Core API          │
│  Loyalty page      │                          │  WalletController          │
│  AddToGoogleWallet │ ◀───── saveUrl ────────  │  GoogleWalletService       │
└────────────────────┘                          │  (singleton, cached)       │
        │                                       └─────────────┬──────────────┘
        │ window.location = saveUrl                           │ HTTPS + OAuth2
        ▼                                                     ▼
┌────────────────────┐                          ┌────────────────────────────┐
│ Google Wallet app  │ ◀──── push update ──────│  Google Wallet REST API    │
│ on user's Android  │                          │  walletobjects.v1          │
└────────────────────┘                          └────────────────────────────┘

Secrets (service account JSON, Issuer ID, Class ID)
   stored in Azure Key Vault, mounted into App Service via Key Vault references.
```

Key properties:
- **Frontend never touches Google.** All Google calls happen server-side.
- **Single source of truth** for points = Krust DB. The Wallet object is a *projection*.
- **Idempotent operations** — replaying any sync is safe because object IDs are deterministic (`{issuerId}.user-{userId}`).

---

## 8. Security & Best Practices

### 8.1 Protecting credentials
- **Never** commit `krust-wallet-sa.json`. Add `*sa*.json` to `.gitignore`.
- **Dev:** .NET User Secrets.
- **Prod:** **Azure Key Vault** secret named `GoogleWallet--ServiceAccountJson`, referenced from App Service config:
  ```
  @Microsoft.KeyVault(SecretUri=https://krust-kv.vault.azure.net/secrets/GoogleWallet--ServiceAccountJson/)
  ```
- Grant only the App Service's **managed identity** `Get` access on that secret.
- Rotate the service account key annually; the Wallet Console supports adding a second key during rotation.

### 8.2 Common mistakes to avoid
| Mistake | Symptom | Fix |
|---|---|---|
| Forgot to add SA email in Wallet Console | 403 on every call | Wallet Console → Users → add SA email as Developer |
| Class ID without issuer prefix | 400 invalid resource name | Always `{issuerId}.{suffix}` |
| Reusing object IDs across users | Pass overwrites another user's | Make object ID derived from `userId`, not random |
| Trusting `userId` from the client | Account takeover | Always read from `User.Identity` |
| Building JWT per request from disk | Slow + leaks file handles | Singleton credential, in-memory cache |
| Exposing raw Google errors to client | Info disclosure | Translate to generic messages, log details server-side |
| Putting Class in `APPROVED` for testing | Test passes go live | Keep `UNDER_REVIEW` until ready to publish |

### 8.3 Test vs Production
- **Test environment:** any class with `reviewStatus: UNDER_REVIEW` is only visible to **users you've explicitly added as testers** in the Wallet Console. Use this for all dev work.
- **Production:** submit the class for review. Until approved, public users will get an error saving the pass.
- Use **two separate issuer IDs and Cloud projects** for staging vs. production so test data never pollutes real users.

---

## 9. Folder Structure

```
Krust.Api/
├── Controllers/
│   └── WalletController.cs
├── Services/
│   └── Wallet/
│       ├── GoogleWalletService.cs
│       ├── GoogleWalletOptions.cs
│       └── LoyaltyPointsChangedHandler.cs
├── Contracts/
│   └── Wallet/
│       └── SaveLinkResponse.cs
├── appsettings.json                 (non-secret config)
└── Program.cs                       (DI: AddSingleton<GoogleWalletService>)

krust-web/
├── src/
│   ├── api/
│   │   └── wallet.ts
│   ├── components/
│   │   └── loyalty/
│   │       └── AddToGoogleWalletButton.tsx
│   └── pages/
│       └── LoyaltyPage.tsx
└── public/
    └── google-wallet/
        └── enUS_add_to_google_wallet_add-wallet-badge.png
```

---

## 10. Files to Create / Modify

### Backend (ASP.NET Core)
- `Krust.Api/Services/Wallet/GoogleWalletOptions.cs` *(new)*
- `Krust.Api/Services/Wallet/GoogleWalletService.cs` *(new — code in §3.3)*
- `Krust.Api/Services/Wallet/LoyaltyPointsChangedHandler.cs` *(new — calls upsert on event)*
- `Krust.Api/Controllers/WalletController.cs` *(new — code in §3.4)*
- `Krust.Api/Contracts/Wallet/SaveLinkResponse.cs` *(new)*
- `Krust.Api/Program.cs` *(modify — register service, options, rate limiter)*
- `Krust.Api/appsettings.json` *(modify — add `GoogleWallet` section)*
- Wherever points are awarded today *(modify — publish `LoyaltyPointsChanged`)*

### Frontend (React)
- `krust-web/src/api/wallet.ts` *(new)*
- `krust-web/src/components/loyalty/AddToGoogleWalletButton.tsx` *(new)*
- `krust-web/src/pages/LoyaltyPage.tsx` *(modify — mount the button)*
- `krust-web/public/google-wallet/...` *(new — official badge image)*

### Infra / secrets
- Azure Key Vault secret `GoogleWallet--ServiceAccountJson`
- App Service config entry referencing it
- `.gitignore` *(modify — add `*sa*.json`)*

---

## 11. Verification

End-to-end smoke test (test environment, before any production work):

1. **Console & SA:** Confirm the SA email appears under Wallet Console → Users → Developers.
2. **Class create:** Boot the API locally, hit `POST /api/wallet/loyalty/save-link` once with a test user. Expect `200` with a `pay.google.com/gp/v/save/...` URL. Then in the Wallet Console verify the class `{issuerId}.krust_loyalty_v1` exists.
3. **Save flow:** From an Android phone (added as a tester), log into the staging Krust web app, tap the button, confirm pass appears in Wallet.
4. **Update flow:** From a backend tool / Swagger, award points to that user. Within ~10 seconds the points on the device should refresh.
5. **Auth check:** `POST /save-link` without a logged-in cookie → expect `401`. With a different user's cookie → expect that user's own object ID, never another's.
6. **Failure injection:** Temporarily revoke the SA in the Wallet Console → expect `5xx` with a generic message and no Google error body in the client response.
7. **Rate limit:** Hammer `/save-link` 20 times in a minute → expect `429` after the 10th.

Once 1–7 pass, the feature is ready for the Google Wallet Console review submission and production rollout.

---

*End of guide.*
