# Nutrition5k Dataset

## About

**Nutrition5k** (Google Research, 2021) — 5,006 dishes with lab-grade ground truth.

- RGB overhead + side images
- Depth maps
- Ground truth: total weight (g), calories, fat, carb, protein
- Measured by: lab-grade electronic scales + calorimeter

## Download

1. Visit: https://github.com/google-research-datasets/Nutrition5k
2. Download the metadata CSV and place at: `raw/metadata.csv`
3. (Optional) Download RGB/depth images for visual testing

## Parse to InSight Format

```bash
python scripts/download_nutrition5k.py --max-samples 500
```

Output: `parsed/nutrition5k_subset.json`

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

## Citation

```
@inproceedings{thames2021nutrition5k,
  title={Nutrition5k: Towards Automatic Nutritional Understanding of Generic Food},
  author={Thames, Quin and others},
  booktitle={CVPR},
  year={2021}
}
```
