# 🔍 HolmHz - Synthetic Image Detection System

> **Triển khai và đánh giá các phương pháp CNN cho bài toán phát hiện ảnh tổng hợp**  
> Thời gian: 11/2025 - 05/2026 (7 tháng)  
> Thực hiện: Lê Văn Hoàng (Chính) | Ngô Huỳnh Bảo Luân (Hỗ trợ)  
> Loại hình: Nghiên cứu ứng dụng (Applied Research)
>
> 📌 **Cập nhật 10/02/2026**: Kế hoạch đã được điều chỉnh dựa trên kết quả chạy thử thực tế 3 dự án benchmark (CNNDetection, UniversalFakeDetect, DeepfakeBench). Xem chi tiết tại [RUN_EXISTING_PROJECTS.md](RUN_EXISTING_PROJECTS.md) và [docs/research/](research/).  
> 📌 **Cập nhật 24/02/2026**: Điều chỉnh timeline thực tế + thay nguồn data dễ tiếp cận hơn cho SV + thêm Kaggle GPU thay Colab free. Xem [Rủi ro & Giải pháp](#12-rủi-ro--giải-pháp).
>
> 📌 **Phân công vai trò**:
>
> - **Hoàng**: Toàn bộ kỹ thuật (model, training, code, API)
> - **Luân** (SV năm 1): Hỗ trợ nhẹ (download data, viết báo cáo, test UI)

---

## 📋 Mục lục

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Định vị nghiên cứu](#2-định-vị-nghiên-cứu)
3. [Dataset Sources](#3-dataset-sources)
4. [Tech Stack](#4-tech-stack)
5. [Kiến trúc hệ thống](#5-kiến-trúc-hệ-thống)
6. [Roadmap & Sprints](#6-roadmap--sprints)
7. [Chi tiết Tasks](#7-chi-tiết-tasks)
8. [KPIs & Metrics](#8-kpis--metrics)
9. [Evaluation Protocol](#9-evaluation-protocol)
10. [Cấu trúc thư mục](#10-cấu-trúc-thư-mục)
11. [Hướng mở rộng](#11-hướng-mở-rộng)

---

## 1. Tổng quan dự án

### 1.1. Bối cảnh & Động lực

Phát hiện ảnh tổng hợp (Synthetic Image Detection) là bài toán đã được nghiên cứu rộng rãi từ 2019 với hàng trăm công bố khoa học. Tuy nhiên:

- **Thách thức hiện tại**: Cross-dataset generalization vẫn chưa được giải quyết triệt để
- **Khoảng trống tại Việt Nam**: Thiếu nghiên cứu và đánh giá trong ngữ cảnh Việt Nam
- **Nhu cầu giáo dục**: Cần công cụ demo để nâng cao nhận thức cộng đồng

### 1.2. Mục tiêu dự án

**Mục tiêu chính**: Triển khai, đánh giá và so sánh các phương pháp CNN hiện đại cho bài toán phát hiện ảnh chân dung tổng hợp, **đặc biệt tập trung vào ảnh sinh bởi Diffusion Models (Stable Diffusion, Flux, Gemini)**.

**Mục tiêu cụ thể**:
| # | Mục tiêu | Đo lường | Ghi chú (Cập nhật 02/2026) |
|---|----------|----------|----------------------------|
| 1 | Train EfficientNet-B0 trên dataset đa nguồn (GAN + Diffusion) | AUC ≥ 0.90 in-domain | Dataset PHẢI có Diffusion, không chỉ GAN |
| 2 | Đánh giá cross-dataset generalization | AUC ≥ 0.75 OOD | OOD bao gồm Flux/Gemini - thách thức lớn nhất |
| 3 | So sánh với 3 SOTA methods (đã chạy thực tế) | Bảng comparison | CNNDetection, UniversalFakeDetect, DeepfakeBench ✅ |
| 4 | Tích hợp XAI (Grad-CAM) | Heatmap visualization | Giữ nguyên |
| 5 | Web demo proof-of-concept | Latency ≤ 2s/ảnh | Giữ nguyên |

### 1.3. Phạm vi (Scope)

#### ✅ Trong phạm vi (Phase 1 - Ảnh tĩnh)

- Ảnh tĩnh chân dung người (static face images)
- Phát hiện ảnh từ GAN (StyleGAN, ProGAN) và Diffusion (Stable Diffusion)
- Benchmark với các methods có sẵn
- Web demo proof-of-concept

#### 🔜 Mở rộng tương lai (Phase 2 - Video/Audio)

- Video deepfake detection
- Audio deepfake detection
- Real-time processing

#### ❌ Ngoài phạm vi

- Forensic-grade accuracy cho pháp lý
- Commercial deployment at scale
- Adversarial robustness testing

### 1.4. Đóng góp dự kiến (Contributions)

> ⚠️ **Lưu ý**: Đây là nghiên cứu **ứng dụng**, không claim novelty về kiến trúc mới.

| Contribution  | Loại        | Mô tả                                              |
| ------------- | ----------- | -------------------------------------------------- |
| Reproduction  | Engineering | Triển khai lại baseline CNN cho deepfake detection |
| Benchmark     | Evaluation  | So sánh hiệu năng các methods trên dataset chuẩn   |
| XAI Demo      | Application | Tích hợp Grad-CAM với giao diện người dùng         |
| Documentation | Education   | Tài liệu hướng dẫn chi tiết cho người học          |

---

## 2. Định vị nghiên cứu

### 2.1. Prior Art - Các công trình liên quan

| Paper/Project              | Năm  | Phương pháp                  | AUC In-domain | AUC OOD (Paper) | Kết quả test thực tế (02/2026)                     |
| -------------------------- | ---- | ---------------------------- | ------------- | --------------- | -------------------------------------------------- |
| Wang et al. (CNNDetection) | 2020 | ResNet50 + blur augmentation | 0.99          | 0.78            | ✅ GAN: 94.6% / ❌ Gemini: 6% (thất bại hoàn toàn) |
| UniversalFakeDetect        | 2023 | CLIP ViT-L/14 + Linear       | 0.95          | 0.82            | ✅ GAN: 100% / ❌ Flux/Gemini: <10% (thất bại)     |
| DeepfakeBench (EffNetB4)   | 2023 | EfficientNet-B4 (FF++ train) | 0.95          | -               | ⚠️ Gemini: 50.7% (đoán mò) / Real: 18.8% (đúng)    |
| Frank et al. (Frequency)   | 2020 | DCT analysis                 | 0.95          | 0.72            | Chưa test                                          |
| NPR-DeepfakeDetection      | 2024 | CNN + NPR preprocessing      | 0.97          | 0.84            | Chưa test                                          |
| **HolmHz (Ours)**          | 2026 | EfficientNet-B0 + Grad-CAM   | Target: 0.90  | Target: 0.75    | **Phải train trên Diffusion data**                 |

> ⚠️ **Phát hiện quan trọng (02/2026)**: Tất cả 3 project đã test đều **thất bại** trước ảnh Diffusion hiện đại (Gemini, Flux). Nguyên nhân: training data chỉ chứa GAN cũ (ProGAN, StyleGAN). **HolmHz bắt buộc phải đưa GenImage/Diffusion data vào training** để tránh lặp lại thất bại này.

### 2.2. Vị trí của dự án

```
                    ┌─────────────────────────────────────────┐
                    │         LANDSCAPE NGHIÊN CỨU            │
                    └─────────────────────────────────────────┘

     Novel Research          Applied Research         Engineering
     (Kiến trúc mới)         (Ứng dụng/Đánh giá)      (Sản phẩm)
           │                        │                      │
           │                        │                      │
    ┌──────┴──────┐          ┌──────┴──────┐        ┌──────┴──────┐
    │ LAA-Net     │          │             │        │ Sensity     │
    │ DRCT        │          │  HolmHz ◄───┼────────│ Deepware    │
    │ UCF         │          │  (Dự án)    │        │ Hive        │
    └─────────────┘          └─────────────┘        └─────────────┘

    Đóng góp:                Đóng góp:               Đóng góp:
    - Kiến trúc mới          - Benchmark             - Sản phẩm thực
    - SOTA performance       - Documentation         - Scalability
    - Publication            - Education             - UX/UI
```

### 2.3. Baseline Methods để so sánh (Đã xác nhận chạy được)

| Method                     | Source                                                                  | Lý do chọn                              | Trạng thái             |
| -------------------------- | ----------------------------------------------------------------------- | --------------------------------------- | ---------------------- |
| **ResNet50 (Wang et al.)** | [CNNDetection](https://github.com/PeterWang512/CNNDetection)            | Baseline chuẩn, đã reproduce thành công | ✅ Đã chạy, có kết quả |
| **CLIP ViT-L/14**          | [UniversalFakeDetect](https://github.com/Yuheng-Li/UniversalFakeDetect) | SOTA generalization, kiến trúc đơn giản | ✅ Đã chạy, có kết quả |
| **EfficientNet-B4**        | [DeepfakeBench](https://github.com/SCLBD/DeepfakeBench)                 | Benchmark framework, modular            | ✅ Đã chạy, có kết quả |
| **EfficientNet-B0 (Ours)** | timm library                                                            | Nhẹ, phù hợp web demo                   | 🔄 Sẽ train            |

> 📝 **Ghi chú**: Đã bỏ **Frequency (DCT)** khỏi danh sách so sánh chính. Thay vào đó tập trung vào 3 methods đã chạy thực tế + model HolmHz. Frequency branch vẫn là optional nếu còn thời gian.

---

## 3. Dataset Sources (Cập nhật 02/2026)

> ⚠️ **Bài học #1 từ benchmark**: Training data quan trọng hơn kiến trúc model.
> Cả 3 SOTA đều fail trên Diffusion vì chỉ train trên GAN → HolmHz **PHẢI** có Diffusion data trong training.

### 3.1. Nguồn dữ liệu công khai

#### A. Ảnh thật (Real Images)

> ⚠️ **Cập nhật 24/02/2026**: Giảm scope — không cần tất cả, chọn 1-2 nguồn dễ download nhất.

| Dataset         | Số ảnh | Link                                                                                             | Sử dụng     | Ưu tiên    | Ghi chú                       |
| --------------- | ------ | ------------------------------------------------------------------------------------------------ | ----------- | ---------- | ----------------------------- |
| **CIFAKE Real** | 60,000 | [Kaggle](https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images) | Train + Val | ⭐ Rất cao | Cùng package với CIFAKE fake  |
| **FFHQ**        | 70,000 | [GitHub](https://github.com/NVlabs/ffhq-dataset)                                                 | Train + Val | Cao        | Dùng Kaggle mirror, subset 5k |
| ~~CelebA-HQ~~   | 30,000 | -                                                                                                | -           | -          | ❌ Bỏ — CIFAKE đủ dùng        |
| ~~DFFD (Real)~~ | 58,703 | -                                                                                                | -           | -          | ❌ Bỏ — khó xin access        |

#### B. Ảnh GAN (Fake)

> ⚠️ **Cập nhật 24/02/2026**: Giảm scope GAN — Diffusion quan trọng hơn.

| Dataset            | Nguồn                                                                                 | Số ảnh   | Sử dụng | Ghi chú                       |
| ------------------ | ------------------------------------------------------------------------------------- | -------- | ------- | ----------------------------- |
| **StyleGAN Faces** | [thispersondoesnotexist.com](https://thispersondoesnotexist.com) hoặc Kaggle datasets | 3-5k     | Train   | Download thủ công hoặc script |
| **ProGAN Faces**   | [tkarras](https://github.com/tkarras/progressive_growing_of_gans)                     | 1-2k     | Val     | Subset nhỏ cho validation     |
| ~~DFFD (Fake)~~    | -                                                                                     | ~~240k~~ | -       | ❌ Bỏ — quá lớn, khó access   |

#### C. Ảnh Diffusion (Fake) ⭐ QUAN TRỌNG NHẤT

> Đây là phần training data **quyết định** thành bại của HolmHz.
> Từ kết quả benchmark: model nào train trên GAN cũ → fail hoàn toàn trên Diffusion.
>
> ⚠️ **Cập nhật 24/02/2026**: Thay GenImage (~50GB, khó download cho SV) bằng nguồn nhỏ gọn hơn.

| Dataset                   | Nguồn                                                                                            | Số ảnh          | Sử dụng         | Ưu tiên     | Ghi chú                         |
| ------------------------- | ------------------------------------------------------------------------------------------------ | --------------- | --------------- | ----------- | ------------------------------- |
| **CIFAKE**                | [Kaggle](https://www.kaggle.com/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images) | 120k (60k fake) | **Train** + Val | ⭐ Rất cao  | ~500MB, dễ download, đã chuẩn   |
| **AI vs Real Faces**      | [Kaggle](https://www.kaggle.com/datasets/tags/ai-generated)                                      | 5-10k           | **Train**       | ⭐ Cao      | Nhiều dataset faces trên Kaggle |
| **Stable Diffusion v1.5** | HuggingFace `diffusers` (self-generate trên Colab)                                               | 3-5k            | **Train**       | ⭐ Cao      | Miễn phí, chạy trên Colab       |
| **SDXL**                  | Self-generate                                                                                    | 500-1k          | Test OOD        | Cao         | Nice-to-have                    |
| ~~**GenImage**~~          | ~~GitHub~~                                                                                       | ~~20k~~         | ~~Train~~       | ~~Rất cao~~ | ❌ Quá lớn (~50GB), bỏ          |

#### D. Ảnh OOD Hiện đại (Test only) 🆕

> Bộ test này để đo khả năng generalize sang nguồn **chưa hề thấy khi train**.
> Đây là thước đo quan trọng nhất cho application thực tế.

| Dataset                | Nguồn                | Số ảnh  | Ghi chú                         |
| ---------------------- | -------------------- | ------- | ------------------------------- |
| **Gemini-generated**   | gemini.google.com    | 100-200 | Đã có mẫu trong imgs/, tạo thêm |
| **Flux-generated**     | replicate.com (free) | 100-200 | Free tier đủ generate 100+ ảnh  |
| **DALL-E 3**           | OpenAI API           | 50-100  | Nice-to-have, tốn phí           |
| **Real camera photos** | Chụp thật / Internet | 200     | Đối chứng                       |

### 3.2. Chiến lược chia tập dữ liệu

```
┌──────────────────────────────────────────────────────────────────────────┐
│              DATASET SPLIT STRATEGY (Revised 24/02/2026)                │
│              Giảm scope phù hợp SV + free GPU                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  TRAIN (70%)                VAL (15%)             TEST ID (15%)         │
│  ─────────────              ─────────             ─────────             │
│  Real:                      Real:                 Real:                 │
│  • CIFAKE Real (5k)         • CIFAKE Real (1k)    • CIFAKE Real (1k)    │
│  • FFHQ subset (3k)         • FFHQ (500)                               │
│                                                                        │
│  Fake (GAN):                Fake (GAN):           Fake (GAN):           │
│  • StyleGAN faces (3k)      • ProGAN (500)        • StyleGAN (500)      │
│                                                                        │
│  Fake (Diffusion):          Fake (Diffusion):     Fake (Diff):          │
│  • CIFAKE Fake (5k)         • CIFAKE Fake (1k)    • CIFAKE Fake (1k)    │
│  • SD v1.5 self-gen (2k)                                                │
│                                                                        │
│  Total: ~18k                Total: ~3k            Total: ~2.5k          │
│                                                                        │
│  ⚠️ Giảm từ 45k → 18k: vẫn đủ cho EfficientNet-B0 (nhẹ, ít params)   │
│  ⚠️ Nếu AUC thấp → tăng data sau (FFHQ 70k, thêm SD generation)      │
│                                                                        │
│  OOD TEST (riêng — QUAN TRỌNG NHẤT):                                  │
│  • Gemini-generated (100-200)                                          │
│  • Flux-generated (100-200)                                            │
│  • Real camera (200)                                                   │
│  ➜ Đây là thước đo QUAN TRỌNG NHẤT cho hội đồng                       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.3. Data Augmentation Strategy

```python
# Training augmentations (mô phỏng điều kiện thực tế)
train_transform = A.Compose([
    A.Resize(224, 224),
    A.HorizontalFlip(p=0.5),
    A.OneOf([
        A.ImageCompression(quality_lower=60, quality_upper=100),  # JPEG
        A.GaussianBlur(blur_limit=(3, 7)),
        A.GaussNoise(var_limit=(10, 50)),
    ], p=0.3),
    A.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.05),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])

# Validation/Test - no augmentation
val_transform = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])
```

---

## 4. Tech Stack

### 4.1. Core ML/DL

| Thành phần        | Công nghệ            | Phiên bản | Lý do chọn                          | Ghi chú (02/2026)             |
| ----------------- | -------------------- | --------- | ----------------------------------- | ----------------------------- |
| Framework         | **PyTorch**          | 2.1+      | Linh hoạt, ecosystem mạnh           | Giữ nguyên                    |
| Vision            | **timm**             | 1.0+      | Pre-trained models đa dạng          | Đã cài, dùng cho EfficientNet |
| Backbone chính    | **EfficientNet-B0**  | -         | Balance accuracy/speed              | Train trên Diffusion data     |
| Backbone fallback | **CLIP ViT-L/14**    | -         | SOTA generalization (đã kiểm chứng) | Dùng nếu EffNet OOD < 0.70    |
| XAI               | **pytorch-grad-cam** | 1.4+      | Grad-CAM, Grad-CAM++                | Giữ nguyên                    |
| Optimization      | **ONNX Runtime**     | 1.16+     | Inference optimization              | Giữ nguyên                    |

> ⚠️ **Bài học từ benchmark**: Không nên chỉ dựa vào 1 backbone. Kết quả thực tế cho thấy CLIP generalize tốt hơn CNN thuần túy trên GAN, nhưng cả hai đều fail trên Diffusion mới. **Chìa khóa là TRAINING DATA, không phải kiến trúc.**

### 4.2. Data Processing

| Thành phần       | Công nghệ                | Mục đích           |
| ---------------- | ------------------------ | ------------------ |
| Image Processing | **Pillow**, **OpenCV**   | Load, resize       |
| Augmentation     | **Albumentations**       | Data augmentation  |
| Dataset          | **HuggingFace Datasets** | Dataset management |

### 4.3. Training Infrastructure

| Thành phần          | Công nghệ                    | Mục đích               | Ghi chú (24/02/2026)                     |
| ------------------- | ---------------------------- | ---------------------- | ---------------------------------------- |
| Experiment Tracking | **Weights & Biases**         | Logging, visualization |                                          |
| Config              | **Hydra** / **yaml**         | Configuration          |                                          |
| GPU (Primary)       | **Kaggle Notebooks** (T4 ×2) | Training               | 30h/tuần miễn phí, không disconnect      |
| GPU (Backup)        | **Google Colab Free** (T4)   | Training               | Dùng khi hết quota Kaggle                |
| GPU (Local)         | RTX 3050 4GB VRAM            | Dev & debug            | batch_size=8-16 + mixed precision (fp16) |

### 4.4. Web Application

| Layer         | Công nghệ        | Mục đích            |
| ------------- | ---------------- | ------------------- |
| Backend       | **FastAPI**      | REST API            |
| Frontend      | **Gradio**       | Rapid prototyping   |
| Model Serving | **ONNX Runtime** | Optimized inference |

### 4.5. Development Tools

| Công cụ          | Mục đích             |
| ---------------- | -------------------- |
| **uv** / **pip** | Package management   |
| **Ruff**         | Linting + Formatting |
| **pytest**       | Unit testing         |

---

## 5. Kiến trúc hệ thống

### 5.1. Model Architecture (Phased Approach)

#### Phase 1: Single-Branch Baseline (Bắt đầu với cái này)

```
┌─────────────────────────────────────────────────────────────┐
│                    BASELINE ARCHITECTURE                    │
│                    (EfficientNet-B0)                        │
└─────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────┐
        │              INPUT IMAGE                │
        │              (224 x 224 x 3)            │
        └─────────────────┬───────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │          PREPROCESSING                  │
        │   • Resize to 224x224                   │
        │   • Normalize (ImageNet stats)          │
        │   • JPEG augmentation (train only)      │
        └─────────────────┬───────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │         EFFICIENTNET-B0                 │
        │         (Pretrained ImageNet)           │
        │                                         │
        │   • Conv Stem                           │
        │   • MBConv Blocks (x16)                 │
        │   • Global Average Pooling              │
        │   • Feature: 1280-dim                   │
        └─────────────────┬───────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │         CLASSIFICATION HEAD             │
        │                                         │
        │   • Dropout(0.3)                        │
        │   • Linear(1280 → 1)                    │
        │   • Sigmoid                             │
        └─────────────────┬───────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │              OUTPUT                     │
        │    P(Fake) ∈ [0, 1]                     │
        │    + Grad-CAM Heatmap                   │
        └─────────────────────────────────────────┘
```

#### Phase 1.5: Optional Frequency Branch (Nếu còn thời gian)

```
┌─────────────────────────────────────────────────────────────┐
│              OPTIONAL: DUAL-BRANCH ARCHITECTURE             │
└─────────────────────────────────────────────────────────────┘

                    INPUT IMAGE (224 x 224 x 3)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌───────────────────┐           ┌───────────────────┐
    │  SPATIAL BRANCH   │           │ FREQUENCY BRANCH  │
    │  (EfficientNet)   │           │   (SRM + DCT)     │
    │                   │           │                   │
    │  Features: 1280   │           │  Features: 256    │
    └─────────┬─────────┘           └─────────┬─────────┘
              │                               │
              └───────────┬───────────────────┘
                          ▼
                ┌───────────────────┐
                │  CONCAT + FC      │
                │  (1536 → 512 → 1) │
                └─────────┬─────────┘
                          ▼
                      P(Fake)
```

### 5.2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEB APPLICATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (Gradio)                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │ Image Upload │  │  Result View │  │  Heatmap Visualization   │   │   │
│  │  │              │  │  (Real/Fake) │  │  (Grad-CAM overlay)      │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      BACKEND (FastAPI)                              │   │
│  │                                                                     │   │
│  │  POST /api/predict    → Inference + probability                     │   │
│  │  POST /api/explain    → Grad-CAM heatmap                           │   │
│  │  GET  /api/health     → Service health check                       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       MODEL SERVICE                                 │   │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────┐     │   │
│  │  │ Preprocessor│  │  ONNX Runtime   │  │   Grad-CAM Engine   │     │   │
│  │  │             │  │  (INT8 quant)   │  │                     │     │   │
│  │  └─────────────┘  └─────────────────┘  └─────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Roadmap theo Phase

### 6.1. Tổng quan Timeline (Cập nhật 10/02/2026)

```
2025                                              2026
Nov          Dec          Jan          Feb          Mar          Apr          May
 |────────────|────────────|────────────|────────────|────────────|────────────|
 │◄─ PHASE 0 ─►│          │◄─────────── PHASE 1 (REVISED 24/02) ──────────►│
 │  Research   │          │  Data + Baseline + Benchmark                    │
 │  3 Projects │          │                                                 │
 │  ✅ DONE    │          │◄── Sprint 1 ──────►│◄──── Sprint 2 ────────────►│
 │             │          │ Env✅+Data+Pipeline │ Train+Eval+XAI+Benchmark  │
 │             │          │ +Model Architecture│ +Export                    │
 │             │          │                    │                            │
 │             │          │                    │  │◄──── PHASE 2 ──────────►│
 │             │          │                    │  │  Web Demo + Report       │
 │             │          │                    │  │  (Chồng lấn Sprint 2)    │
 │             │          │                    │  │◄Sprint 3►│◄Sprint 4────►│
 │             │          │                    │  │ Web Demo  │ Report+Def  │
```

> **Thay đổi 24/02/2026 so với plan cũ (10/02):**
>
> - Task 1.1 ĐÃ XONG ✅. Sprint 1 bắt đầu data collection từ 24/02.
> - Sprint 2 overlap với Phase 2 để tiết kiệm 2 tuần.
> - Web demo bắt đầu song song ngay khi có model checkpoint (không cần đợi benchmark xong).
> - Report viết dần từ tháng 3, không dồn hết tháng 5.

> **Thay đổi lớn so với kế hoạch ban đầu:**
>
> - Phase 0 (Research) đã hoàn thành ✅ (11/2025 - 02/2026): Chạy 3 dự án benchmark, thu thập insights.
> - Phase 1 gộp Foundation + Model Dev vì đã có kiến thức nền từ Phase 0.
> - Phase 2 gộp Web Demo + Report vì timeline đã dùng hết cho Research.
> - Bỏ Frequency Branch (Phase 1.5 cũ) để tập trung vào core.

### 6.2. Chi tiết các Phase

---

## 📦 PHASE 0: Research & Benchmarking (T11/2025 - T02/2026) ✅ HOÀN THÀNH

> **Mục tiêu Phase**: Chạy thử 3 dự án benchmark để hiểu landscape và thu thập insights
> **Thời gian**: 4 tháng (thực tế, bao gồm học nền tảng)
> **Trạng thái**: ✅ **ĐÃ HOÀN THÀNH** (10/02/2026)

### Kết quả Phase 0

| Dự án                      | Trạng thái    | Kết quả chính                                | Tài liệu                                   |
| -------------------------- | ------------- | -------------------------------------------- | ------------------------------------------ |
| CNNDetection (Wang 2020)   | ✅ Hoàn thành | GAN: 94.6% đúng / Diffusion: 6% (thất bại)   | `research/CNNDetection_DeepDive.md`        |
| UniversalFakeDetect (2023) | ✅ Hoàn thành | GAN: 100% / Flux/Gemini: <10% (thất bại)     | `research/UniversalFakeDetect_DeepDive.md` |
| DeepfakeBench (2023)       | ✅ Hoàn thành | Gemini: 50.7% (đoán mò) / Real: 18.8% (đúng) | `research/DeepfakeBench_DeepDive.md`       |

### Insights quan trọng rút ra

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BÀI HỌC TỪ 3 DỰ ÁN BENCHMARK                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. TRAINING DATA > ARCHITECTURE                                        │
│     Model mạnh (EfficientNet-B4, CLIP) vẫn thất bại nếu train trên     │
│     GAN cũ mà test trên Diffusion mới (Gemini, Flux).                   │
│     → HolmHz PHẢI train trên GenImage/Diffusion data.                   │
│                                                                         │
│  2. PREPROCESSING LÀ CRITICAL                                           │
│     Mỗi backbone có normalization riêng (ImageNet vs CLIP).             │
│     Face alignment (dlib) là bắt buộc cho DeepfakeBench.                │
│     → HolmHz cần pipeline preprocessing linh hoạt.                      │
│                                                                         │
│  3. BINARY CLASSIFICATION (num_classes=1) + SIGMOID                     │
│     Cả CNNDetection và UniversalFakeDetect đều dùng pattern này.        │
│     Output: P(Fake) ∈ [0,1]. Đơn giản và hiệu quả hơn 2-class.        │
│     → HolmHz sẽ dùng pattern này.                                       │
│                                                                         │
│  4. TRANSFER LEARNING LÀ CHÌA KHÓA                                     │
│     UniversalFakeDetect chỉ train 1 layer Linear trên CLIP features     │
│     mà đạt OOD 0.82. Không cần train from scratch.                      │
│     → HolmHz sẽ freeze backbone + fine-tune head.                       │
│                                                                         │
│  5. ĐỘ TIN CẬY KẾT QUẢ                                                │
│     Cần chạy trên DATASET CHUẨN (không chỉ 1-2 ảnh đơn lẻ)            │
│     để có AUC/Accuracy có ý nghĩa thống kê cho hội đồng.               │
│     → Sprint 2 sẽ thiết lập evaluation protocol chuẩn.                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**📊 Phase 0 Deliverables**: ✅

- [x] Chạy thành công 3 dự án benchmark
- [x] 3 bài Deep Dive phân tích chi tiết (docs/research/)
- [x] File RUN_EXISTING_PROJECTS.md cập nhật kết quả thực tế
- [x] Xác định rõ hướng đi cho HolmHz

---

## 📦 PHASE 1: Data + Model Development (T02-T03/2026)

> **Mục tiêu Phase**: Thu thập dữ liệu, train baseline, benchmark với 3 SOTA đã chạy
> **Thời gian**: 2 tháng (02/2026 - 03/2026)
> **Hoàng**: Environment, Model, Training | **Luân**: Download data theo hướng dẫn
>
> ⚠️ **Thay đổi quan trọng so với kế hoạch cũ:**
>
> - Gộp Sprint cũ 1.1 + 1.2 + 2.1 thành Phase 1 mới (vì Phase 0 research đã chiếm timeline).
> - Bỏ Frequency/Fusion branch (Phase 1.5 cũ) để tập trung vào core.
> - Thêm bước benchmark chuẩn trên dataset chung (không chỉ test 1-2 ảnh).

### Sprint 1: Data + Baseline Training (T02-T03/2026)

**Mục tiêu Sprint**: Setup environment, thu thập data, train EfficientNet-B0

| Task ID | Task                   | Subtasks                                                              | Assignee     | Target       | Status |
| ------- | ---------------------- | --------------------------------------------------------------------- | ------------ | ------------ | ------ |
| 1.1     | **Environment Setup**  |                                                                       | Hoàng        | ~~17/02~~ ✅ | ✅     |
|         |                        | 1.1.1 Setup cấu trúc thư mục src/ chuẩn                               |              |              | ✅     |
|         |                        | 1.1.2 Cấu hình pyproject.toml + requirements                          |              |              | ✅     |
|         |                        | 1.1.3 Setup Weights & Biases project                                  |              |              | ✅     |
|         |                        | 1.1.4 Tạo Colab/Kaggle notebook template                              |              |              | ✅     |
| 1.2     | **Data Collection** ✨ |                                                                       | Hoàng + Luân | ~~02/03~~ ✅ | ✅     |
|         |                        | 1.2.1 Download CIFAKE dataset (Real+Fake, Kaggle)                     | Luân         |              | ✅     |
|         |                        | 1.2.2 Download FFHQ subset (5k real, Kaggle mirror)                   | Luân         |              | ✅     |
|         |                        | 1.2.3 Download/scrape StyleGAN faces (5k)                             | Hoàng        |              | ✅     |
|         |                        | 1.2.4 Self-generate SD v1.5 ảnh trên Colab (2.5k)                     | Hoàng        |              | ✅     |
|         |                        | 1.2.5 Chuẩn bị OOD: Flux (80) + Real camera (100) + tristanzhang (1k) | Hoàng        |              | ✅     |
| 1.3     | **Data Pipeline**      |                                                                       | Hoàng        | **07/03**    | ✅     |
|         |                        | 1.3.1 Implement Dataset class (PyTorch)                               |              |              | ✅     |
|         |                        | 1.3.2 Implement augmentation pipeline (Albumentations)                |              |              | ✅     |
|         |                        | 1.3.3 Train/Val/Test-OOD split + manifest files                       |              |              | ✅     |
| 1.4     | **Model Architecture** |                                                                       | Hoàng        | **07/03**    | ✅     |
|         |                        | 1.4.1 Implement EfficientNet-B0 classifier (timm + Linear head)       |              |              | ✅     |
|         |                        | 1.4.2 Implement model factory (Registry pattern từ DeepfakeBench)     |              |              | ✅     |
|         |                        | 1.4.3 Unit test model forward pass                                    |              |              | ✅     |
| 1.5     | **Training Pipeline**  |                                                                       | Hoàng        | **14/03**    | ✅     |
|         |                        | 1.5.1 Implement Trainer class                                         |              |              | ✅     |
|         |                        | 1.5.2 Setup BCE Loss (Binary, num_classes=1, Sigmoid)                 |              |              | ✅     |
|         |                        | 1.5.3 LR scheduler (CosineAnnealing)                                  |              |              | ✅     |
|         |                        | 1.5.4 Early stopping + Wandb logging + **checkpoint resume**          |              |              | ✅     |
| 1.6     | **Baseline Training**  |                                                                       | Hoàng        | **21/03**    | ✅     |
|         |                        | 1.6.1 Train EfficientNet-B0 (freeze backbone + train head)            |              |              | ✅     |
|         |                        | 1.6.2 Fine-tune toàn bộ model (unfreeze)                              |              |              | ✅     |
|         |                        | 1.6.3 Hyperparameter tuning (LR, batch)                               |              |              | ✅     |
|         |                        | 1.6.4 Save best checkpoint                                            |              |              | ✅     |
| 1.7     | **OOD Improvement**    |                                                                       | Hoàng        |              | ⬜     |
|         |                        | 1.7.1 Subset 3,000 diverse real từ 140k dataset                       |              |              | ⬜     |
|         |                        | 1.7.2 Split real_pexels 300 train / 200 OOD test                      |              |              | ⬜     |
|         |                        | 1.7.3 Resize + rebuild manifests                                      |              |              | ⬜     |
|         |                        | 1.7.4 Tăng cường augmentation v2                                      |              |              | ⬜     |
|         |                        | 1.7.5 Retrain trên Kaggle T4                                          |              |              | ⬜     |
|         |                        | 1.7.6 Re-evaluate OOD AUC ≥ 0.75                                      |              |              | ⬜     |

**✅ Milestone 1**: Dataset v1 (≥15k ảnh, bao gồm Diffusion) + Baseline AUC ≥ 0.85 (in-domain)

> ⚠️ **Điều chỉnh 24/02**: Giảm target từ 25k→15k ảnh và AUC 0.88→0.85 cho Milestone 1.
> Lý do: dataset nhỏ hơn (CIFAKE thay GenImage), nhưng nếu đạt 0.85 vẫn có giá trị khoa học.
> Nếu đạt sớm → tăng data + retrain để nâng lên 0.90.

---

### Sprint 2: Evaluation + XAI + Benchmark Chuẩn (T03/2026)

**Mục tiêu Sprint**: Đánh giá model, tích hợp XAI, so sánh chuẩn với 3 SOTA

| Task ID | Task                       | Subtasks                                                            | Assignee | Status |
| ------- | -------------------------- | ------------------------------------------------------------------- | -------- | ------ |
| 2.1     | **Evaluation Pipeline**    |                                                                     | Hoàng    | ✅     |
|         |                            | 2.1.1 Compute metrics (AUC, Acc, F1) trên test set                  |          | ✅     |
|         |                            | 2.1.2 Per-source accuracy breakdown (GAN vs Diffusion vs Real)      |          | ✅     |
|         |                            | 2.1.3 OOD evaluation (Flux, Gemini, SDXL)                           |          | ✅     |
|         |                            | 2.1.4 Generate confusion matrix + ROC curve                         |          | ✅     |
| 2.2     | **Benchmark chuẩn 3 SOTA** |                                                                     | Hoàng    | ⬜     |
|         |                            | 2.2.1 Chạy CNNDetection trên test set chung (Docker/chuẩn pipeline) |          | ⬜     |
|         |                            | 2.2.2 Chạy UniversalFakeDetect trên test set chung                  |          | ⬜     |
|         |                            | 2.2.3 Chạy DeepfakeBench (EffNetB4) trên test set chung             |          | ⬜     |
|         |                            | 2.2.4 Tạo bảng so sánh AUC/Acc chính thức cho báo cáo               |          | ⬜     |
| 2.3     | **Grad-CAM Integration**   |                                                                     | Hoàng    | ⬜     |
|         |                            | 2.3.1 Integrate pytorch-grad-cam                                    |          | ⬜     |
|         |                            | 2.3.2 Implement heatmap overlay function                            |          | ⬜     |
|         |                            | 2.3.3 Generate XAI gallery (50 samples)                             |          | ⬜     |
| 2.4     | **Model Export**           |                                                                     | Hoàng    | ⬜     |
|         |                            | 2.4.1 Export to ONNX format                                         |          | ⬜     |
|         |                            | 2.4.2 Validate ONNX output matches PyTorch                          |          | ⬜     |

**✅ Milestone 2**: Final model (AUC ≥ 0.90 ID, ≥ 0.75 OOD) + Bảng so sánh chính thức + XAI gallery

**📊 Phase 1 Deliverables**:

- [ ] Dataset v1 với manifest files (bao gồm Diffusion data)
- [ ] Baseline model checkpoint (.pt + .onnx)
- [ ] Training logs trên W&B
- [ ] Bảng so sánh정식 với 3 SOTA (chạy trên cùng test set)
- [ ] XAI gallery (50 heatmap samples)
- [ ] Báo cáo kết quả Phase 1

---

## 📦 PHASE 2: Web Application & Report (T04-T05/2026)

> **Mục tiêu Phase**: Xây dựng Web Demo và hoàn thiện báo cáo khoa học
> **Thời gian**: 2 tháng (04/2026 - 05/2026)
> **Hoàng**: Backend, API, Integration, Báo cáo kỹ thuật | **Luân**: Test UI, Viết Chương 1-2
>
> ⚠️ **Thay đổi**: Gộp Phase 3 cũ vào đây. Bỏ Robustness Testing chi tiết (nice-to-have).

---

### Sprint 3: Web Demo Development (T04/2026)

**Mục tiêu Sprint**: Xây dựng ứng dụng web hoàn chỉnh

| Task ID | Task                        | Subtasks                                        | Assignee | Status |
| ------- | --------------------------- | ----------------------------------------------- | -------- | ------ |
| 3.1.1   | **Backend API**             |                                                 | Hoàng    | ⬜     |
|         |                             | 3.1.1.1 Setup FastAPI project                   |          | ⬜     |
|         |                             | 3.1.1.2 Implement POST /api/predict             |          | ⬜     |
|         |                             | 3.1.1.3 Implement POST /api/explain             |          | ⬜     |
|         |                             | 3.1.1.4 Implement GET /api/health               |          | ⬜     |
|         |                             | 3.1.1.5 Add request validation                  |          | ⬜     |
| 3.1.2   | **Model Service**           |                                                 | Hoàng    | ⬜     |
|         |                             | 3.1.2.1 Load ONNX model on startup              |          | ⬜     |
|         |                             | 3.1.2.2 Implement preprocessing pipeline        |          | ⬜     |
|         |                             | 3.1.2.3 Implement Grad-CAM service              |          | ⬜     |
|         |                             | 3.1.2.4 Add error handling                      |          | ⬜     |
| 3.1.3   | **Frontend UI**             |                                                 | Hoàng    | ⬜     |
|         |                             | 3.1.3.1 Setup Gradio interface                  |          | ⬜     |
|         |                             | 3.1.3.2 Image upload component                  |          | ⬜     |
|         |                             | 3.1.3.3 Result display (Real/Fake + confidence) |          | ⬜     |
|         |                             | 3.1.3.4 Heatmap visualization                   |          | ⬜     |
|         |                             | 3.1.3.5 UI styling và UX polish                 |          | ⬜     |
| 3.1.4   | **UI Testing** ✨           |                                                 | Luân     | ⬜     |
|         | _(Test và góp ý cho Hoàng)_ | 3.1.4.1 Test upload nhiều loại ảnh              |          | ⬜     |
|         |                             | 3.1.4.2 Ghi nhận lỗi và feedback                |          | ⬜     |
|         |                             | 3.1.4.3 Test trên nhiều thiết bị                |          | ⬜     |
| 3.1.5   | **Integration**             |                                                 | Hoàng    | ⬜     |
|         |                             | 3.1.5.1 End-to-end testing                      |          | ⬜     |
|         |                             | 3.1.5.2 Latency optimization (target ≤ 2s)      |          | ⬜     |
|         |                             | 3.1.5.3 Error case handling                     |          | ⬜     |
|         |                             | 3.1.5.4 Deploy to local/Colab                   |          | ⬜     |

**✅ Milestone 3.1**: Working web demo (latency ≤ 2s/ảnh)

---

### Sprint 4: Documentation & Defense Prep (T04-T05/2026)

**Mục tiêu Sprint**: Hoàn thiện tài liệu và chuẩn bị bảo vệ

| Task ID | Task                            | Subtasks                                    | Assignee | Status |
| ------- | ------------------------------- | ------------------------------------------- | -------- | ------ |
| 3.2.1   | **Báo cáo - Chương 1-2** ✨     |                                             | Luân     | ⬜     |
|         | _(Viết theo outline của Hoàng)_ | 3.2.1.1 Chương 1: Mở đầu (theo mẫu)         |          | ⬜     |
|         |                                 | 3.2.1.2 Chương 2: Tổng quan (theo tài liệu) |          | ⬜     |
|         |                                 | 3.2.1.3 Gửi Hoàng review                    |          | ⬜     |
| 3.2.2   | **Báo cáo - Chương 3-4-5**      |                                             | Hoàng    | ⬜     |
|         |                                 | 3.2.2.1 Chương 3: Phương pháp và Xây dựng   |          | ⬜     |
|         |                                 | 3.2.2.2 Chương 4: Kết quả thực nghiệm       |          | ⬜     |
|         |                                 | 3.2.2.3 Chương 5: Kết luận                  |          | ⬜     |
|         |                                 | 3.2.2.4 Tạo bảng, biểu đồ, hình ảnh         |          | ⬜     |
| 3.2.3   | **Tổng hợp báo cáo**            |                                             | Hoàng    | ⬜     |
|         |                                 | 3.2.3.1 Merge Chương 1-2 của Luân           |          | ⬜     |
|         |                                 | 3.2.3.2 Format theo mẫu trường              |          | ⬜     |
|         |                                 | 3.2.3.3 Review với GVHD                     |          | ⬜     |
| 3.2.4   | **Defense Preparation**         |                                             | Hoàng    | ⬜     |
|         |                                 | 3.2.4.1 Tạo slide thuyết trình              |          | ⬜     |
|         |                                 | 3.2.4.2 Quay video demo                     |          | ⬜     |
|         |                                 | 3.2.4.3 Chuẩn bị Q&A                        |          | ⬜     |
| 3.2.5   | **Hỗ trợ Defense** ✨           |                                             | Luân     | ⬜     |
|         | _(Hỗ trợ nhẹ)_                  | 3.2.5.1 Chuẩn bị ảnh test cho demo          |          | ⬜     |
|         |                                 | 3.2.5.2 Luyện tập thuyết trình cùng Hoàng   |          | ⬜     |
| 3.2.6   | **Final Deliverables**          |                                             | Hoàng    | ⬜     |
|         |                                 | 3.2.6.1 Đóng gói source code                |          | ⬜     |
|         |                                 | 3.2.6.2 Tạo README hướng dẫn                |          | ⬜     |
|         |                                 | 3.2.6.3 Export model weights                |          | ⬜     |
|         |                                 | 3.2.6.4 Chuẩn bị hồ sơ nghiệm thu           |          | ⬜     |

**✅ Milestone 3.2**: Hồ sơ nghiệm thu đầy đủ

**📊 Phase 2 Deliverables**:

- [ ] Web application hoạt động
- [ ] Báo cáo tổng kết (Docx + PDF)
- [ ] Slide thuyết trình
- [ ] Video demo
- [ ] Source code đóng gói + README
- [ ] Model weights (.pt + .onnx)

---

## 7. Tổng hợp Task Tracking

### 7.1. Task Summary by Phase

| Phase                 | Sprints | Trạng thái                     |
| --------------------- | ------- | ------------------------------ |
| Phase 0: Research     | -       | ✅ Đã xong (11/2025 - 02/2026) |
| Phase 1: Data + Model | 2       | ⬜ Sắp bắt đầu                 |
| Phase 2: Web + Report | 2       | ⬜ Chưa bắt đầu                |

### 7.2. Task Status Legend

| Symbol | Meaning     |
| ------ | ----------- |
| ⬜     | Not Started |
| 🔄     | In Progress |
| ✅     | Completed   |
| ⏸️     | Blocked     |
| ❌     | Cancelled   |

### 7.3. Milestone Summary

| Milestone              | Phase   | Target Date    | KPI                              | Status |
| ---------------------- | ------- | -------------- | -------------------------------- | ------ |
| M0: Research Complete  | Phase 0 | 10/02/2026     | 3 projects chạy + documented     | ✅     |
| M1: Dataset + Baseline | Phase 1 | **21/03/2026** | ≥15k ảnh + AUC ≥ 0.85 (ID)       | ⬜     |
| M2: Benchmark + XAI    | Phase 1 | **07/04/2026** | Bảng so sánh chuẩn + XAI gallery | ⬜     |
| M3: Web Demo           | Phase 2 | **28/04/2026** | Latency ≤ 2s                     | ⬜     |
| M4: Defense Ready      | Phase 2 | **15/05/2026** | Full package                     | ⬜     |

### 7.4. Weekly Progress Template

```markdown
## Week X Progress (DD/MM/YYYY)

### Completed

- [ ] Task X.X.X.X: Description

### In Progress

- [ ] Task X.X.X.X: Description (XX% done)

### Blockers

- Issue: Description
- Action needed: ...

### Next Week Plan

- [ ] Task X.X.X.X: Description
```

---

## 8. KPIs & Metrics

### 8.1. Model Performance KPIs (Cập nhật dựa trên benchmark)

| Metric       | In-Domain | OOD (GAN khác) | OOD (Diffusion mới) | Priority    | Ghi chú                  |
| ------------ | --------- | -------------- | ------------------- | ----------- | ------------------------ |
| **AUC-ROC**  | ≥ 0.90    | ≥ 0.75         | ≥ 0.70              | 🔴 Critical | Target mới cho Diffusion |
| **Accuracy** | ≥ 88%     | ≥ 75%          | ≥ 65%               | 🔴 Critical | Gemini/Flux là rất khó   |
| **F1-Score** | ≥ 0.88    | ≥ 0.75         | ≥ 0.65              | 🟡 High     |                          |

> ⚠️ **Thực tế**: Cả 3 SOTA đều AUC < 0.50 trên Gemini/Flux. Nếu HolmHz đạt **≥ 0.70** trên Diffusion OOD, đó đã là đóng góp có giá trị.

### 8.2. Robustness KPIs

| Condition    | Max AUC Drop |
| ------------ | ------------ |
| JPEG q=60    | ≤ 8%         |
| JPEG q=80    | ≤ 3%         |
| Resize 0.75x | ≤ 5%         |

### 8.3. System KPIs

| Metric        | Target     |
| ------------- | ---------- |
| Latency (CPU) | ≤ 2s/image |
| Model Size    | ≤ 50MB     |

### 8.4. Comparison KPIs

| Requirement      | Target |
| ---------------- | ------ |
| Methods compared | ≥ 3    |
| OOD evaluation   | Yes    |

---

## 9. Evaluation Protocol

### 9.1. Comparison Table Template (Cập nhật với dữ liệu thực tế)

| Method                     | Year | In-domain AUC (Paper) | OOD AUC (Paper) | Test trên Gemini/Flux (02/2026) | Params |
| -------------------------- | ---- | --------------------- | --------------- | ------------------------------- | ------ |
| Wang et al. (CNNDetection) | 2020 | 0.99                  | 0.78            | ❌ ~6% (thất bại)               | 25M    |
| UniversalFakeDetect (CLIP) | 2023 | 0.95                  | 0.82            | ❌ <10% (thất bại)              | 300M   |
| DeepfakeBench (EffNetB4)   | 2023 | 0.95                  | -               | ⚠️ ~50% (đoán mò)               | 19M    |
| **HolmHz (Ours)**          | 2026 | Target: 0.90          | Target: 0.75    | **Target: >70%**                | ~5M    |

> 📝 **Ghi chú cho hội đồng**: Cột "Test trên Gemini/Flux" là kết quả test sơ bộ trên ảnh đơn lẻ (02/2026). Kết quả chính thức sẽ được tính trên test set chuẩn (≥500 ảnh) với AUC metric ở Sprint 2.

### 9.2. Per-Source Breakdown

| Source        | Type          | AUC (HolmHz) | AUC (CNNDetection) | AUC (UniversalFakeDetect) | Notes                     |
| ------------- | ------------- | ------------ | ------------------ | ------------------------- | ------------------------- |
| StyleGAN2     | GAN (seen)    | ?            | ~0.95 (paper)      | ~0.99 (paper)             | In-domain                 |
| ProGAN        | GAN (seen)    | ?            | ~0.94 (đã test)    | ~1.00 (đã test)           | In-domain                 |
| GenImage (SD) | Diff (seen)   | ?            | Fail               | Fail                      | Train data mới cho HolmHz |
| SDXL          | Diff (unseen) | ?            | Fail               | Fail                      | OOD                       |
| Gemini        | Diff (unseen) | ?            | ~0.06              | <0.10                     | OOD - Thách thức chính    |
| Flux          | Diff (unseen) | ?            | N/A                | <0.10                     | OOD                       |

---

## 10. Cấu trúc thư mục (Revised - Best Practice từ 3 SOTA projects)

> Thiết kế dựa trên phân tích cấu trúc CNNDetection, UniversalFakeDetect, DeepfakeBench.
> Lấy separation of concerns của DeepfakeBench, sự đơn giản của CNNDetection,
> và two-tier model pattern của UniversalFakeDetect.

```
HolmHz/
├── README.md
├── LICENSE
├── pyproject.toml                  # Single source of truth (deps + metadata + entry points)
├── Makefile                        # Shortcuts: make train, make test, make serve, make export
├── Dockerfile                      # Reproducible environment (bài học từ DeepfakeBench)
├── .env.example                    # Dataset paths, API keys, wandb key
│
├── configs/                        # ★ YAML-driven config (pattern từ DeepfakeBench)
│   ├── train.yaml                  #   Default training hyperparams
│   ├── test.yaml                   #   Default eval settings
│   ├── export.yaml                 #   ONNX export settings
│   └── detectors/                  #   Per-detector overrides
│       └── efficientnet_b0.yaml    #   LR, batch, augmentation riêng cho EffNet
│
├── src/                            # ★ Installable Python package
│   └── holmhz/                     #   `pip install -e .` → import holmhz
│       ├── __init__.py
│       │
│       ├── backbones/              # ★ Pure architectures (từ UniversalFakeDetect models/)
│       │   ├── __init__.py         #   Registry + factory function
│       │   ├── base.py             #   Abstract backbone class
│       │   └── efficientnet.py     #   EfficientNet-B0 wrapper (timm)
│       │
│       ├── detectors/              # ★ Full detector = backbone + head + pre/post
│       │   ├── __init__.py         #   (pattern từ DeepfakeBench detectors/)
│       │   ├── base.py             #   Abstract detector (base_detector.py)
│       │   └── efficientnet_detector.py  # EffNet-B0 + Linear(1280→1) + Sigmoid
│       │
│       ├── data/                   # ★ Data pipeline (common pattern cả 3 project)
│       │   ├── __init__.py
│       │   ├── base_dataset.py     #   Abstract dataset (từ DeepfakeBench abstract_dataset.py)
│       │   ├── image_dataset.py    #   Image-level dataset cho train/val/test
│       │   ├── transforms.py       #   Albumentations augmentation (bài học: cần hỗ trợ
│       │   │                       #   nhiều normalization: ImageNet, CLIP, [0.5,0.5,0.5])
│       │   └── utils.py            #   Face crop, alignment helpers
│       │
│       ├── losses/                 # ★ Pluggable loss functions (từ DeepfakeBench loss/)
│       │   ├── __init__.py
│       │   └── bce.py              #   BCEWithLogitsLoss (pattern chung CNNDetection + UFD)
│       │
│       ├── metrics/                # ★ Pluggable metrics (từ DeepfakeBench metrics/)
│       │   ├── __init__.py
│       │   ├── auc.py              #   AUC-ROC computation
│       │   └── accuracy.py         #   Accuracy, F1, confusion matrix
│       │
│       ├── training/               # ★ Training engine
│       │   ├── __init__.py
│       │   ├── trainer.py          #   Main loop (từ DeepfakeBench trainer/trainer.py)
│       │   ├── early_stopping.py   #   (từ CNNDetection earlystop.py)
│       │   └── lr_schedulers.py    #   CosineAnnealing, etc.
│       │
│       ├── evaluation/             # ★ Evaluation engine
│       │   ├── __init__.py
│       │   ├── evaluator.py        #   Unified eval: ID + OOD + per-source breakdown
│       │   └── benchmark.py        #   So sánh cross-model trên cùng test set
│       │
│       ├── xai/                    # ★ Explainability (HolmHz core feature)
│       │   ├── __init__.py
│       │   ├── gradcam.py          #   pytorch-grad-cam wrapper
│       │   └── utils.py            #   Heatmap overlay, gallery generation
│       │
│       ├── export/                 # ★ Model export pipeline
│       │   ├── __init__.py
│       │   ├── onnx_export.py      #   PyTorch → ONNX
│       │   └── validate.py         #   Verify ONNX output matches PyTorch
│       │
│       └── utils/                  # ★ Shared utilities
│           ├── __init__.py
│           ├── logger.py           #   (từ DeepfakeBench logger.py)
│           ├── registry.py         #   Component registry pattern (detector, backbone, loss)
│           ├── io.py               #   Checkpoint save/load
│           └── visualization.py    #   ROC curve, confusion matrix plotting
│
├── scripts/                        # ★ CLI entry points (pattern từ CNNDetection root scripts)
│   ├── train.py                    #   python scripts/train.py --config configs/train.yaml
│   ├── test.py                     #   python scripts/test.py --config configs/test.yaml
│   ├── predict.py                  #   Single image / batch prediction (demo.py + demo_dir.py)
│   ├── explain.py                  #   Generate Grad-CAM heatmaps
│   ├── export_onnx.py              #   Export model to ONNX
│   └── download_weights.sh         #   (pattern từ CNNDetection weights/)
│
├── app/                            # ★ Web demo (tách serving khỏi ML logic)
│   ├── __init__.py
│   ├── api.py                      #   FastAPI endpoints (POST /predict, /explain)
│   ├── gradio_ui.py                #   Gradio frontend
│   └── schemas.py                  #   Pydantic request/response models
│
├── preprocessing/                  # ★ Data prep (top-level, từ DeepfakeBench preprocessing/)
│   ├── preprocess.py               #   Face extraction, alignment, resize
│   ├── build_splits.py             #   Tạo train/val/test JSON manifests
│   └── config.yaml                 #   Preprocessing settings
│
├── analysis/                       # ★ Research analysis tools (từ DeepfakeBench analysis/)
│   ├── compute_auc.py              #   Tính AUC từ predictions
│   ├── plot_roc.py                 #   Vẽ ROC curve so sánh
│   ├── tsne.py                     #   t-SNE feature visualization
│   └── frequency_analysis.py       #   DCT/frequency inspection
│
├── tests/                          # ★ Unit + integration tests
│   ├── conftest.py
│   ├── test_backbones.py
│   ├── test_detectors.py
│   ├── test_data.py
│   └── test_api.py
│
├── notebooks/                      # Jupyter exploration / demos
│   ├── 01_data_exploration.ipynb
│   └── 02_gradcam_demo.ipynb
│
├── weights/                        # Pretrained checkpoints (.gitignored)
│   └── .gitkeep
│
├── outputs/                        # Training outputs (.gitignored)
│   ├── checkpoints/                #   Model .pt files
│   ├── logs/                       #   W&B / tensorboard logs
│   └── exports/                    #   ONNX files
│
├── data/                           # Dataset (.gitignored)
│   ├── raw/                        #   Original downloaded data
│   ├── processed/                  #   Cropped, aligned, resized
│   │   ├── train/
│   │   ├── val/
│   │   └── test_ood/
│   └── manifests/                  #   JSON split files (tracked in git)
│
└── docs/
    ├── PROJECT_PLAN.md
    ├── CHANGELOG.md
    └── research/                   #   Deep dive analyses
```

### Thiết kế dựa trên bài học từ 3 project:

| Quyết định                                 | Lý do                                                                   | Nguồn                                 |
| ------------------------------------------ | ----------------------------------------------------------------------- | ------------------------------------- |
| `backbones/` tách khỏi `detectors/`        | Backbone tái sử dụng được; detector là task-specific. Dễ swap backbone. | DeepfakeBench + UniversalFakeDetect   |
| YAML configs per-detector                  | Scale tốt khi thêm model mới, không cần sửa argparse. Dễ reproduce.     | DeepfakeBench (`config/detector/`)    |
| `src/holmhz/` installable package          | `pip install -e .` → import sạch, không cần `sys.path` hack.            | Python best practice                  |
| `scripts/` cho CLI, `src/` cho library     | Entry points không lẫn với importable code.                             | CNNDetection (root scripts)           |
| `losses/` + `metrics/` riêng               | Thêm loss/metric mới không cần sửa code cũ (Open/Closed).               | DeepfakeBench                         |
| `preprocessing/` top-level                 | Data prep independent, chạy trước training, có config riêng.            | DeepfakeBench (`preprocessing/`)      |
| `analysis/` top-level                      | Research tools (t-SNE, ROC) tách khỏi production code.                  | DeepfakeBench (`analysis/`)           |
| `transforms.py` hỗ trợ nhiều normalization | Mỗi backbone cần normalization khác nhau (ImageNet vs CLIP vs [0.5]).   | Bài học từ cả 3 project               |
| Registry pattern trong `__init__.py`       | Config chỉ cần ghi tên detector → factory tự tạo object.                | DeepfakeBench `detectors/__init__.py` |
| `base.py` abstract class ở mỗi package     | Đảm bảo interface thống nhất, dễ thêm implementation mới.               | Pattern chung cả 3 project            |

---

## 11. Hướng mở rộng

### 11.1. Phase 2: Video (Sau T05/2026)

```
Nếu Phase 1 hoàn thành sớm:
├── Frame extraction (1 FPS)
├── Frame-level → Video-level aggregation
├── Datasets: FaceForensics++, Celeb-DF
└── New KPIs: Video-level AUC
```

### 11.2. Phase 3: Audio (Tương lai)

```
├── Mel-spectrogram / MFCC
├── Models: RawNet2, AASIST
├── Datasets: ASVspoof, WaveFake
└── Applications: Voice verification
```

### 11.3. Roadmap dài hạn

```
2025-2026         2026-2027          2027+
─────────         ─────────          ─────
Phase 1: Image    Phase 2: Video     Phase 3: Multi-modal
• CNN baseline    • Temporal         • Audio + Video
• Benchmark       • FaceForensics++  • Real-time
• XAI             • Video demo       • Mobile
```

---

## ⚠️ Disclaimer

1. **Nghiên cứu ứng dụng** - Không claim novelty về kiến trúc mới
2. **Kết quả tham khảo** - Không thay thế giám định pháp lý
3. **OOD là open problem** - Cross-dataset generalization chưa giải quyết được
4. **Proof-of-concept** - Không phải sản phẩm thương mại

---

## ✅ Tiêu chí thành công

| Tiêu chí           | Mức đạt | Mức vượt | Ghi chú (24/02)          |
| ------------------ | ------- | -------- | ------------------------ |
| In-domain AUC      | ≥ 0.85  | ≥ 0.92   | Giảm từ 0.88 do data nhỏ |
| OOD AUC            | ≥ 0.65  | ≥ 0.78   | Giảm từ 0.70, vẫn > SOTA |
| Comparison methods | ≥ 2     | ≥ 4      |                          |
| Web demo           | Working | + Docker |                          |

---

---

## 12. Rủi ro & Giải pháp

> Mục mới thêm 24/02/2026 — đánh giá rủi ro thực tế cho SV năm 4 NCKH cấp trường.

### 12.1. Dataset khó download (Rủi ro CAO)

| Vấn đề                   | Mức độ  | Giải pháp                                                               |
| ------------------------ | ------- | ----------------------------------------------------------------------- |
| GenImage ~50GB           | 🔴 Cao  | ❌ **Bỏ GenImage** → Thay bằng CIFAKE (~500MB, Kaggle 1-click download) |
| DFFD cần xin access      | 🟡 TB   | ❌ **Bỏ DFFD** → CIFAKE + FFHQ đủ dùng                                  |
| Flux/Gemini API tốn tiền | 🟡 TB   | ✅ Generate thủ công trên web (miễn phí) 100-200 ảnh                    |
| FFHQ 70k quá lớn         | 🟢 Thấp | ✅ Dùng Kaggle mirror, subset 3-5k                                      |

**Chiến lược data mới (tiết kiệm + thực tế):**

```
CIFAKE (Kaggle, 1 click):  Real 60k + AI-generated 60k  → Backbone dataset
FFHQ (Kaggle mirror):      Subset 3-5k real faces        → Bổ sung faces
StyleGAN (web scrape):     3k GAN faces                  → Đa dạng nguồn
SD v1.5 (self-gen Colab):  2-3k Diffusion faces          → Đa dạng Diffusion
OOD (thủ công):            Gemini 100-200, Flux 100-200   → Test generalization
─────────────────────────────────────────────────────────
Tổng: ~15-20k train + ~500 OOD test
```

### 12.2. GPU hạn chế — SV dùng free tier (Rủi ro TRUNG BÌNH)

| Platform                | GPU               | Thời gian      | Disconnect? | Khuyến nghị         |
| ----------------------- | ----------------- | -------------- | ----------- | ------------------- |
| **Kaggle** (Primary)    | T4 ×2 (hoặc P100) | **30h/tuần**   | ❌ Không    | ⭐ **Dùng chính**   |
| **Colab Free** (Backup) | T4                | ~4h/session    | ✅ Có       | Dùng khi hết Kaggle |
| **Local RTX 3050**      | 4GB VRAM          | Không giới hạn | ❌ Không    | Dev & debug only    |

**Chiến lược training:**

```
1. Develop + debug code trên local (RTX 3050, batch=8, 100 ảnh test)
2. Train chính trên Kaggle (batch=32, full dataset, 30h/tuần)
3. LUÔN save checkpoint mỗi epoch + resume từ checkpoint
4. Nếu hết Kaggle → chuyển sang Colab free (đã có checkpoint resume)
```

**Ước tính thời gian training (18k images, Kaggle T4):**

```
Freeze backbone + train head:   ~2h  (10 epochs × 12 min)
Fine-tune full model:           ~4h  (20 epochs × 12 min)
Hyperparameter search (3 runs): ~12h (mỗi run ~4h)
─────────────────────────────────────────────────
Tổng: ~18h → vừa đủ 1 tuần Kaggle quota (30h)
```

### 12.3. Timeline chặt (Rủi ro TRUNG BÌNH)

**Nguyên tắc: Overlap tasks thay vì sequential**

```
Tuần  | 24/02  01/03  08/03  15/03  22/03  29/03  05/04  12/04  19/04  26/04  ...  15/05
──────┼──────────────────────────────────────────────────────────────────────────────────
1.2   │ ████████████                                                Data Collection
1.3   │      ████████████                                           Data Pipeline
1.4   │      ████████████                                           Model Arch
1.5   │           ████████████                                      Training Pipeline
1.6   │                ████████████                                  Baseline Training
2.1   │                     ████████████                             Evaluation
2.2   │                          ████████████                        Benchmark
2.3   │                          ████████████                        Grad-CAM
2.4   │                               ████████                      Export
3.1   │                               ████████████                   Backend API
3.2   │                                    ████████████              Frontend
4.1   │                          ████████████████████████████████    Report
4.2   │                                              ████████████   Defense
```

**Điểm cắt giảm nếu chậm:**
| Nếu... | Thì cắt... |
|---|---|
| Training xong muộn (sau 28/03) | Giảm hyperparameter search: 3 runs → 1 run |
| Benchmark 3 SOTA mất quá lâu | Chỉ benchmark 2 SOTA (bỏ DeepfakeBench — khó setup nhất) |
| Web demo không kịp | Dùng Gradio standalone (không cần FastAPI backend) |
| Report chậm | Luân viết Ch1-2 song song từ tháng 3, không đợi xong hết |

---

**Last Updated:** 24/02/2026  
**Author:** Lê Văn Hoàng  
**Version:** 4.0 (Revised: realistic timeline + accessible data sources + Kaggle GPU + risk mitigation)
