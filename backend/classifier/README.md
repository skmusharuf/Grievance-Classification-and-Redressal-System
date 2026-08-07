# Versioned Indic classifier

The production classifier is intentionally local and versioned. Fine-tune `ai4bharat/IndicBERTv2-MLM-only` or `google/muril-base-cased` on a labelled dataset of complaint text, language, category, and severity. Store the model artifact under `artifacts/indicbert-v1/` and expose a small inference service that returns `{category, severity, confidence, model_version}`.

Routing rule: confidence >= 0.72 can be auto-routed; confidence below 0.72 is assigned to the ward review queue. Keep the original text, language, model version, prediction, and reviewer decision in an audit record. Do not train on personal identifiers or exact coordinates. Start with official municipal grievance datasets, Open Government Data (data.gov.in), city department taxonomies, and anonymised historical complaints; validate labels with two human reviewers before training.
