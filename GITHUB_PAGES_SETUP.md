# GitHub Pages Custom Domain Setup Guide for deepline.dev

This guide documents the steps to configure the custom domain `deepline.dev` for GitHub Pages.

## Status

✅ **Phase 3 Complete**: CNAME file has been added to the repository root with content `deepline.dev`

🔲 **Phase 2 Required**: DNS configuration (requires DNS admin access)
🔲 **Phase 4 Required**: GitHub Pages settings configuration (requires GitHub admin access)

## Variables

```
DOMAIN=deepline.dev
WWW=www.deepline.dev
GHPAGES_HOST=deepextrema.github.io
GITHUB_IPS=185.199.108.153,185.199.109.153,185.199.110.153,185.199.111.153
TTL=300
```

## Phase 2 - DNS Configuration (Manual Step Required)

### Option A: Generic DNS Provider (No Cloudflare)

Create the following DNS records:

```
# Apex/root -> four GitHub Pages A records
@     A     185.199.108.153   TTL 300
@     A     185.199.109.153   TTL 300
@     A     185.199.110.153   TTL 300
@     A     185.199.111.153   TTL 300

# www -> CNAME to your GitHub Pages host
www   CNAME deepextrema.github.io.   TTL 300
```

**Important:**
- Delete any conflicting A/AAAA/CNAME/URL-forward records for root or `www`
- Do NOT use a CNAME at apex unless your provider supports ALIAS/ANAME records

### Option B: Cloudflare DNS

1. Navigate to **DNS → Records** in Cloudflare dashboard
2. Add the following records:

```
Type  Name  Content                  Proxy Status        TTL
A     @     185.199.108.153          DNS only (grey)     300
A     @     185.199.109.153          DNS only (grey)     300
A     @     185.199.110.153          DNS only (grey)     300
A     @     185.199.111.153          DNS only (grey)     300
CNAME www   deepextrema.github.io.   DNS only (grey)     300
```

**Critical:** Proxy must be OFF (DNS only/grey cloud) for both apex and `www`. Orange cloud will cause `NotServedByPagesError`.

3. Remove any conflicting/legacy records
4. If CAA records exist, ensure Let's Encrypt is allowed:
   ```
   CAA 0 issue "letsencrypt.org"
   ```

## Phase 4 - GitHub Pages Configuration (Manual Step Required)

1. Go to GitHub repository: https://github.com/DeepExtrema/deepextrema
2. Navigate to **Settings → Pages**
3. Under **Custom domain**, enter: `deepline.dev`
4. Click **Save**
5. Wait for DNS check to pass (may take a few minutes)
6. Once certificate is issued, enable **Enforce HTTPS**

## Validation Commands

After DNS configuration, run these commands to verify:

```bash
# DNS should show GitHub IPs directly
dig +short A deepline.dev
# Expected: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153

# www should CNAME to GitHub Pages
dig +short CNAME www.deepline.dev
# Expected: deepextrema.github.io.

# www should resolve to GitHub IPs via CNAME
dig +short A www.deepline.dev
# Expected: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153

# HTTP/HTTPS checks
curl -I http://deepline.dev
curl -I https://deepline.dev
curl -I https://www.deepline.dev

# TLS certificate check
openssl s_client -connect deepline.dev:443 -servername deepline.dev </dev/null | openssl x509 -noout -subject -issuer -dates
```

## Acceptance Criteria

✅ **Repository**: CNAME file exists with `deepline.dev` (COMPLETE)
🔲 **DNS**: dig shows GitHub IPs for apex; www CNAME → deepextrema.github.io
🔲 **GitHub Pages**: DNS check passes (no `NotServedByPagesError`)
🔲 **HTTPS**: Works with valid Let's Encrypt certificate
🔲 **Redirects**: www.deepline.dev redirects to deepline.dev

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Cloudflare proxy left ON | Turn to DNS only (grey cloud) for apex and www |
| Wrong apex config | Use all four A records: 185.199.108-111.153 |
| Only www configured | Add apex A records |
| CAA blocks issuance | Allow letsencrypt.org (only if you use CAA) |

## Rollback

If issues occur, revert DNS to:
- `www` → CNAME `deepextrema.github.io.`
- apex → A records (185.199.108-111.153)

Remove any conflicting records and retry validation.
