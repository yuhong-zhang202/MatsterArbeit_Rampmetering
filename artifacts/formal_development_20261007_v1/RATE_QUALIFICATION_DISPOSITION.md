# Rate qualification disposition — 2026-10-07

Classification: authorized development, not formal.

Independent engineering replay found zero pulse-accounting differences and exact window credit closure. The rate limitation is produced by the registered guards and deliberate credit discard; no ordinary implementation bug is evidenced. Engineering requested a hold until scientific reconciliation. Scientific reviewer subsequently permitted completion of the locked, authorized development coverage as characterization of the actual constrained policy. This resolves the sequencing hold without changing parameters, acceptance gates or treatment definition.

R900/S17 T2: rules, safety, paired data and cohort accounting PASS; continuously requested 900 veh/h capability NOT_QUALIFIED (six windows fail the original 10% gate). Preserve this negative qualification in every final summary. Traffic effects are descriptive results of the implemented constrained policy; they do not establish ideal 900 service or a sweet spot. No repeat, retuning, guard relaxation or credit change is authorized.

Scientific exact-card disposition: release R750/S17 T1 SHA 02446edf7096e87ddfc09b5f6685929e1677476ac745c06b4841c2aafa9c451a now; R750/S17 T2 SHA f0aad816eb2e82a4a95f0638959b515f4518754b64e39dde179ea863d95105a1 remains conditional on independent T1 implementation/data checks. Real code/data issues still stop the sequence. Later seeds require unchanged design and exact-card review.

Sources: engineering/RATE_SHORTFALL_DIAGNOSIS.md and .json; data/processed/formal_development_20261007_v1/T2_R900_S17_A02/T2_DATA_GATE.json; read-only scientific reviewer disposition returned to primary agent on 2026-10-07.
