# Phase 3 upstream code audit

Audit basis: the repository was clean before Phase 3 changes and `HEAD` was exactly `9c575c617dd399dda73996e4e7e6e1f5614ee0d1`. The fixed Stage 2 protocol raw SHA-256 is `4a15ae6697081098973998f7340702368403fa81f39d6c8ed43172b74a55b5b3`. The candidate leaves `phase3_source_commit` null; the later non-self-referential frozen protocol records source commit A.

## Frozen execution paths

- `dataset/stage2_dataset.py::build_token_record` canonicalizes a conversation, requires one `<image>`, expands it to exactly 64 `<|image_pad|>` tokens, independently builds the no-image tokenization, locates the single assistant interval, requires its final EOS, rejects overlength VLM sequences, and proves the VLM/LM assistant targets identical.
- `Stage2CaptionDataset` creates labels by masking all positions except the Stage 2 assistant target, pads IDs to 450 with the tokenizer pad ID, pads labels with `-100`, and `stage2_collate` returns no attention mask. Phase 3 reuses its interval and expansion logic but narrows labels to caption plus EOS.
- For M1–M3, correct and none take the same tokenized VLM record and labels. Correct supplies Stage 2-preprocessed pixels; none supplies `pixel_values=None` while retaining the multimodal placeholders. Image bytes flow through `normalized_image` (Pillow decode, EXIF transpose, RGB) and `MiniMindVLM.image2tensor` with the frozen processor.
- M0 is constructed by `experiments.stage2_model.build_stage2_model` as `MiniMindForCausalLM`. Its Phase 3 conversation contains no image marker and follows `canonical_conversation`, `_full_ids`, and `_target_interval` directly, so `_replace_image` and `build_token_record` are not invoked.
- The tokenizer chat template produces the automatic `<think>\n\n</think>\n\n` assistant prefix and a newline after EOS. Phase 3 keeps both in `input_ids`; it masks the empty-think prefix and everything after the unique EOS. The only valid labels are caption tokens plus that EOS.
- `experiments.evaluate_stage2_risk.sample_risk_bits` and the VLM loss both use causal next-token alignment: logits at all but the final position score labels shifted left by one. Phase 3 mirrors `logits[:, :-1]`, `labels[:, 1:]`, a `-100` mask, and safe labels before gather.

## Model reconstruction and MMS2 authority

- `experiments.stage2_model.build_stage2_model` constructs M0/M1/M2/M3 from protocol-bound initial LLM and vision assets, validates exact initial-language tensor loading, injects only the declared coordinate parameterization, and rejects trainable parameters outside those coordinates.
- `experiments.quantize_stage2_adapter.decode_mms2` validates the MMS2 header, version, 3-bit label, method/root identity, compressed and uncompressed lengths, coordinate group order/dimensions, symbol range, finite nonnegative scales, and trailing bytes. Phase 3 decodes from the same safely snapshotted raw bytes whose size and SHA are checked against the expected registry.
- Phase 3 v4 retains the user-approved `stage2-v2-rerun-20260721` batch: rerun source commit `07eff239d965f644e3207925ddac446a803ee45e`, recovery verification SHA `529d08bd940229642492025f5aa2c7ed83900957c675c688d2ea228458ab33c1`, pipeline plan SHA `048ce0382157d4aeafa67e737858106521878febbce58fc37c22cd8cae6f4583`, pipeline progress SHA `d3488021db66517ce4a0d573cb02d0975c37d4b731673299ea4d0e921d64c711`, decoder source SHA `d42a0f0eecfd3c6977d04a3f446c48369e9505dd65d1c5f577b4e92ccc6cf785`, and the ten rerun MMS2 size/SHA/method/root rows. The v1 authority remains disclosed as superseded history and is not used as the expected model batch. The static authority and expected registry are separate from the dynamic verification receipt.

## Integrity conclusion

The audited Stage 2 paths provide the required correct/no-pixel behavior, M0 construction, tokenizer/template authority, EOS and padding semantics, causal shift, model reconstruction, and MMS2 decoding. Phase 3 imports these frozen primitives rather than altering Stage 2 files. Runtime artifact, data, image, overlap, protocol, approval, and bundle checks remain explicit gates; absence of an external resource is recorded as blocked and is not replaced with a substitute.
