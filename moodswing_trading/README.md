## Prediction

Each prediction row stores the mean (`µ`) and standard deviation (`σ`) returned by
the ONNX‑optimised LSTM model. The `model_version` string is formatted as
`<date>-<git_sha>` so multiple versions can run in parallel for A/B testing.

Predictions are generated hourly and at the end of each trading day. The
``hourly_predict`` Celery task runs every hour with ``run_type: "HOURLY"`` and
again at **21:05 UTC** with ``run_type: "EOD"``. Each run upserts the day's
prediction row so only the final EOD result persists. Once an ``"EOD"``
prediction is stored, no further predictions are made until the next trading
day begins. Both hourly and EOD results are broadcast on the ``prediction``
Redis channel.