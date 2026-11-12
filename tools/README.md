# Workshop pages (GitHub Pages)

The workshop site is served by GitHub Pages from the `docs/` folder of the `main` branch:
<https://iterorganization.github.io/IMAS-Data-Mapping/>

```
docs/
  .nojekyll                 # serve files as-is (no Jekyll processing)
  index.html                # landing page listing all editions
  workshops/<YYYY-MM>/      # cleaned Indico export of one edition
```

Presentation files are not stored in git. They are uploaded as assets of one GitHub
Release per edition (tag `workshop-<YYYY-MM>`), and the pages link to the release
download URLs.

## Adding a new edition

1. In the Indico event management area, create an "offline copy" of the event and
   download the zip.
2. Unzip it outside the repository, e.g. in `/scratch/users/$USER/workshop-<id>/src`.
3. Run the cleanup script from the repository root:

   ```bash
   python3 -I tools/clean_indico_export.py \
       /scratch/users/$USER/workshop-<id>/src/OfflineWebsite-<event_title> \
       docs/workshops/<YYYY-MM> \
       /scratch/users/$USER/workshop-<id>/release-assets \
       --release-tag workshop-<YYYY-MM>
   ```

   The script:
   - copies the pages to `docs/workshops/<YYYY-MM>`, but not the `material/` folder;
   - copies the attachments to the assets folder under URL-safe names
     (`<attachment id>-<name>.<ext>`) and points the page links at
     `https://github.com/iterorganization/IMAS-Data-Mapping/releases/download/workshop-<YYYY-MM>/<name>`;
   - removes the "Registration" section of the event description, the Indico
     header toolbar and footer (login, timezone, language, management links) and
     adds a banner linking back to the list of editions;
   - reports local links that do not resolve. Links to `../../index.html` are only
     reported if the landing page does not exist yet.

   Check the report and the pages (`python3 -m http.server 8000 -d docs`). Each
   Indico export may differ a bit, so adapt the regular expressions at the top of
   the script if something was not cleaned.
4. Create the release and upload the assets:

   ```bash
   gh release create workshop-<YYYY-MM> \
       --title "<Nth> IMAS Data Mapping Workshop (<Month YYYY>) – material" \
       --notes "Presentations of the workshop, see https://iterorganization.github.io/IMAS-Data-Mapping/workshops/<YYYY-MM>/" \
       /scratch/users/$USER/workshop-<id>/release-assets/*
   ```

5. Add an entry at the top of the "Editions" list in `docs/index.html`, then
   commit `docs/` and open a pull request.

Release assets are limited to 2 GB per file. Updating a presentation later means
uploading a new asset (`gh release upload --clobber`) with the same name.
