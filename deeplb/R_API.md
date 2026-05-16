# DeepLB R API (Script Interfaces)

DeepLB currently exposes R functionality through executable scripts in Part1.

## Runtime model

- Run scripts with `Rscript`.
- Arguments are positional via `commandArgs(trailingOnly = TRUE)`.
- Orchestration is handled by `Scripts/DeepLB_pipeline.sh`.

## Script contracts

### `1.1_reformat_TCGA.R`

Path: `Scripts/Part1.Marker_Selection/1.1_reformat_TCGA.R`

Arguments:

1. `current_path` (DeepLB root)
2. `tumor_type` (for example `LIHC`)

```bash
Rscript Scripts/Part1.Marker_Selection/1.1_reformat_TCGA.R /path/to/DeepLB LIHC
```

### `1.1_prepare_sample_annotation.R`

Path: `Scripts/Part1.Marker_Selection/1.1_prepare_sample_annotation.R`

Arguments:

1. `current_path`
2. `meta` (for example `all_WGBS_sample_metadata.xlsx`)
3. `tumor`
4. `bgfile` (for example `background_for_train.txt`)

```bash
Rscript Scripts/Part1.Marker_Selection/1.1_prepare_sample_annotation.R /path/to/DeepLB all_WGBS_sample_metadata.xlsx LIHC background_for_train.txt
```

### `1.1_subsample_for_tumorOnly.R`

Path: `Scripts/Part1.Marker_Selection/1.1_subsample_for_tumorOnly.R`

Arguments:

1. `root_dir`
2. `tumor`
3. `group` (`TH` or `MH`)
4. `select_number`

```bash
Rscript Scripts/Part1.Marker_Selection/1.1_subsample_for_tumorOnly.R /path/to/DeepLB LIHC TH 30
```

### `1.2_define_blocks_according_CancerLocator_method.R`

Path: `Scripts/Part1.Marker_Selection/1.2_define_blocks_according_CancerLocator_method.R`

Arguments:

1. `current_path`
2. `window.size`
3. `min.probe.number`

```bash
Rscript Scripts/Part1.Marker_Selection/1.2_define_blocks_according_CancerLocator_method.R /path/to/DeepLB 100 3
```

### `1.3.1_get_methylation_ratio_blocks_TCGA_paired.R`

Path: `Scripts/Part1.Marker_Selection/1.3.1_get_methylation_ratio_blocks_TCGA_paired.R`

Arguments:

1. `root.dir`
2. `target_tumor`

```bash
Rscript Scripts/Part1.Marker_Selection/1.3.1_get_methylation_ratio_blocks_TCGA_paired.R /path/to/DeepLB LIHC
```

### `1.3.2_get_methylation_ratio_blocks_TCGA_tumorOnly.R`

Path: `Scripts/Part1.Marker_Selection/1.3.2_get_methylation_ratio_blocks_TCGA_tumorOnly.R`

Arguments:

1. `root.dir`
2. `target_tumor`
3. `group`
4. `select_sample`
5. `sampleList`

```bash
Rscript Scripts/Part1.Marker_Selection/1.3.2_get_methylation_ratio_blocks_TCGA_tumorOnly.R /path/to/DeepLB LIHC TH top30 all_samples_annotation.txt
```

### `1.3.4_get_methylation_ratio_blocks_normal_plasma.R`

Path: `Scripts/Part1.Marker_Selection/1.3.4_get_methylation_ratio_blocks_normal_plasma.R`

Arguments:

1. `root.dir`
2. `sample_list`

```bash
Rscript Scripts/Part1.Marker_Selection/1.3.4_get_methylation_ratio_blocks_normal_plasma.R /path/to/DeepLB background_for_train.txt
```

### `1.5_para_est_mom_mc.R`

Path: `Scripts/Part1.Marker_Selection/1.5_para_est_mom_mc.R`

Arguments:

1. training table path
2. output directory
3. core count

```bash
Rscript Scripts/Part1.Marker_Selection/1.5_para_est_mom_mc.R /path/to/train.tsv /path/to/out 8
```
