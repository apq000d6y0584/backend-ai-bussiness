# TODO - Fix Netlify Next.js chunk 404 / MIME type errors

- [ ] Inspect and update `netlify.toml` to avoid rewriting `_next/*` assets to `/index.html`.
- [ ] Remove the broad `from = "/*" to = "/index.html" status = 200 force = true` redirect or narrow it to only app routes.
- [ ] Ensure SPA fallback does not interfere with `_next/static/*`.
- [ ] Redeploy on Netlify.
- [ ] Verify failing chunk URL returns JS (Content-Type: application/javascript) and no longer 404.
- [ ] If needed, run `npm run build` locally and compare that `_next/static/chunks/webpack-*.js` exists in build output.

